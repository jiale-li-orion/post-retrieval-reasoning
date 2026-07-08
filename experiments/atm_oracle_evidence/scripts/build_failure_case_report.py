#!/usr/bin/env python3
"""Build a readable SGM-vs-Raw failure-case report from ATM-Bench outputs."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parents[1]
ATM_ROOT = REPO_ROOT / "ATM-Bench"
sys.path.insert(0, str(ATM_ROOT))

from memqa.qa_agent_baselines.oracle.oracle_baseline import (  # noqa: E402
    IMAGE_EXTENSIONS,
    VIDEO_EXTENSIONS,
    collect_text_evidence,
    resolve_media_file,
)


QA_PATH = ATM_ROOT / "data/atm-bench/atm-bench-hard.json"
IMAGE_BATCH_PATH = ATM_ROOT / "output/image/qwen3vl2b/batch_results.json"
VIDEO_BATCH_PATH = ATM_ROOT / "output/video/qwen3vl2b/batch_results.json"
EMAIL_PATH = ATM_ROOT / "data/raw_memory/email/emails.json"
IMAGE_ROOT = ATM_ROOT / "data/raw_memory/image"
VIDEO_ROOT = ATM_ROOT / "data/raw_memory/video"

SGM_RUN = EXPERIMENT_ROOT / "runs/mimo_v25_sgm_hard"
RAW_RUN = EXPERIMENT_ROOT / "runs/mimo_v25_raw_hard"
OUTPUT_PATH = EXPERIMENT_ROOT / "reports/failure_cases.md"

BATCH_FIELDS = [
    "type",
    "timestamp",
    "location",
    "short_caption",
    "caption",
    "ocr",
    "tags",
]


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def index_batch(rows: list[dict[str, Any]], path_field: str) -> dict[str, dict[str, Any]]:
    return {Path(row[path_field]).stem: row for row in rows}


def score_text(score: Any) -> str:
    if isinstance(score, bool):
        return "正确" if score else "错误"
    return f"{float(score):.3f}"


def display_score(row: dict[str, Any]) -> str:
    score = row["accuracy"]
    if row["qtype"] != "list_recall":
        return score_text(score)
    gold = parse_id_list(row["ground_truth"])
    predicted = parse_id_list(row["prediction"])
    matched = len(gold & predicted)
    return f"命中 {matched}/{len(gold)}（{float(score):.1%}）"


def is_full_score(score: Any) -> bool:
    return bool(score) if isinstance(score, bool) else float(score) == 1.0


def has_raw_media(evidence_ids: list[str]) -> bool:
    return any(not evidence_id.startswith("email") for evidence_id in evidence_ids)


def classify_change(
    sgm_score: Any, raw_score: Any, evidence_ids: list[str] | None = None
) -> str:
    if is_full_score(raw_score):
        if evidence_ids is not None and not has_raw_media(evidence_ids):
            return "重复运行答对（输入相同）"
        return "Raw 修复"
    if float(raw_score) > float(sgm_score):
        return "Raw 改善但未修复"
    if float(raw_score) < float(sgm_score):
        return "Raw 退化"
    return "Raw 未改善"


def type_text(qtype: str) -> str:
    return {
        "list_recall": "证据 ID 列举",
        "number": "数值计算",
        "open_end": "开放式组合",
    }.get(qtype, qtype)


def parse_id_list(text: str) -> set[str]:
    values = {part.strip().strip(".;") for part in text.split(",")}
    return {value for value in values if value and value.lower() != "unknown"}


def list_difference(row: dict[str, Any]) -> tuple[list[str], list[str]]:
    gold = parse_id_list(row["ground_truth"])
    predicted = parse_id_list(row["prediction"])
    return sorted(gold - predicted), sorted(predicted - gold)


def result_summary(
    sgm: dict[str, Any], raw: dict[str, Any], evidence_ids: list[str]
) -> str:
    if sgm["qtype"] == "list_recall":
        sgm_missing, sgm_extra = list_difference(sgm)
        raw_missing, raw_extra = list_difference(raw)
        parts = [
            "SGM "
            + (f"漏掉 {', '.join(f'`{item}`' for item in sgm_missing)}" if sgm_missing else "没有漏项")
            + (f"，多报 {', '.join(f'`{item}`' for item in sgm_extra)}" if sgm_extra else "")
            + "。"
        ]
        if is_full_score(raw["accuracy"]):
            parts.append("查看原始图片/视频后，全部 ID 回答正确。")
        else:
            parts.append(
                "Raw "
                + (f"仍漏掉 {', '.join(f'`{item}`' for item in raw_missing)}" if raw_missing else "没有漏项")
                + (f"，仍多报 {', '.join(f'`{item}`' for item in raw_extra)}" if raw_extra else "")
                + "。"
            )
        return " ".join(parts)

    if is_full_score(raw["accuracy"]):
        if not has_raw_media(evidence_ids):
            return (
                "两次运行收到的都是同一批邮件文本：第一次回答错误，第二次回答正确。"
                "这里没有发生 evidence view 变化，不能作为 Raw 修复 SGM 的证据，只能视为生成波动。"
            )
        return (
            "SGM 压缩文本下回答错误；查看原始图片/视频后回答正确。"
            "这说明该例优先检查 SGM 是否遗漏了关键视觉信息。"
        )
    return (
        "SGM 和 Raw 都回答错误。原始媒体没有修复该例，因此不能只归因于 SGM 压缩；"
        "还需检查变量绑定、运算步骤、时序/状态判断或标注本身。"
    )


def table_cell(text: Any, limit: int = 180) -> str:
    value = " ".join(str(text or "").split())
    if len(value) > limit:
        value = value[: limit - 1] + "…"
    return value.replace("|", "\\|")


def concise_evidence_rows(
    evidence_ids: list[str],
    email_index: dict[str, dict[str, Any]],
    image_index: dict[str, dict[str, Any]],
    video_index: dict[str, dict[str, Any]],
) -> list[str]:
    rows = [
        "| Evidence ID | 类型 | 时间 | 地点 | SGM 中最直接的内容 |",
        "|---|---|---|---|---|",
    ]
    for evidence_id in evidence_ids:
        if evidence_id.startswith("email"):
            item = email_index.get(evidence_id, {})
            rows.append(
                f"| `{evidence_id}` | 邮件 | {table_cell(item.get('timestamp'))} |  | "
                f"{table_cell(item.get('short_summary'))} |"
            )
            continue
        item = image_index.get(Path(evidence_id).stem)
        evidence_type = "图片"
        if not item:
            item = video_index.get(Path(evidence_id).stem, {})
            evidence_type = "视频"
        content = item.get("short_caption") or item.get("ocr_text") or item.get("caption")
        rows.append(
            f"| `{evidence_id}` | {evidence_type} | {table_cell(item.get('timestamp'))} | "
            f"{table_cell(item.get('location_name'), 90)} | {table_cell(content)} |"
        )
    return rows


def load_judge_explanations(run: Path) -> dict[str, str]:
    path = run / "eval_ds/llm_judge_deepseek-v4-flash.json"
    if not path.exists():
        return {}
    return {
        row["id"]: row.get("explanation", "")
        for row in load_json(path)
        if row.get("id")
    }


def find_raw_source(evidence_id: str) -> Path | None:
    image = resolve_media_file(IMAGE_ROOT, evidence_id, IMAGE_EXTENSIONS)
    if image:
        return image
    return resolve_media_file(VIDEO_ROOT, evidence_id, VIDEO_EXTENSIONS)


def fenced(text: str) -> str:
    return f"```text\n{text.rstrip()}\n```"


def main() -> None:
    qas = load_json(QA_PATH)
    qa_index = {row["id"]: row for row in qas}
    qa_order = {row["id"]: index + 1 for index, row in enumerate(qas)}

    sgm_rows = load_json(SGM_RUN / "eval_ds/atm_deepseek-v4-flash.json")
    raw_rows = load_json(RAW_RUN / "eval_ds/atm_deepseek-v4-flash.json")
    sgm_index = {row["id"]: row for row in sgm_rows}
    raw_index = {row["id"]: row for row in raw_rows}
    sgm_judges = load_judge_explanations(SGM_RUN)
    raw_judges = load_judge_explanations(RAW_RUN)

    image_index = index_batch(load_json(IMAGE_BATCH_PATH), "image_path")
    video_index = index_batch(load_json(VIDEO_BATCH_PATH), "video_path")
    email_index = {row["id"]: row for row in load_json(EMAIL_PATH)}

    failures = [row for row in sgm_rows if not is_full_score(row["accuracy"])]
    failures.sort(key=lambda row: qa_order[row["id"]])

    counts: dict[str, int] = {}
    for row in failures:
        evidence_ids = [str(item) for item in qa_index[row["id"]].get("evidence_ids", [])]
        label = classify_change(
            row["accuracy"], raw_index[row["id"]]["accuracy"], evidence_ids
        )
        counts[label] = counts.get(label, 0) + 1

    lines = [
        "# ATM-Bench Hard 失败案例逐例复核",
        "",
        "本报告收录 MiMo-V2.5 在 **SGM Oracle** 条件下没有完全答对的 22 道题，并与 **Raw Oracle** 的回答逐题对照。案例保持 ATM-Bench-Hard 原始顺序。",
        "",
        "- **SGM Oracle**：已经给定正确 evidence IDs，但模型只看到这些图片/视频被压缩后的时间、地点、caption、OCR 和 tags。",
        "- **Raw Oracle**：evidence IDs 完全相同；图片和视频改为直接查看原始媒体，邮件证据保持不变。",
        "- **阅读目的**：先判断错误是否由 SGM 丢失信息造成；若 Raw 仍然错误，再检查绑定、计算、时序、状态判断或标注问题。",
        "- 列举题的“命中 x/y”表示 gold evidence IDs 中答对了多少个；开放式和数值题采用 DeepSeek judge 的正确/错误结论。",
        "",
        "## 索引",
        "",
        f"共 {len(failures)} 例："
        + "；".join(f"{label} {count} 例" for label, count in counts.items())
        + "。",
        "",
        "| 案例 | 原题 | 问题类型 | SGM 结果 | Raw 结果 | 最直接的观察 |",
        "|---:|---:|---|---:|---:|---|",
    ]

    for report_index, sgm in enumerate(failures, start=1):
        raw = raw_index[sgm["id"]]
        evidence_ids = [str(item) for item in qa_index[sgm["id"]].get("evidence_ids", [])]
        question = sgm["question"].replace("\n", " ").replace("|", "\\|")
        lines.append(
            f"| [{report_index}](#case-{report_index}) | {qa_order[sgm['id']]} | "
            f"{type_text(sgm['qtype'])} | {display_score(sgm)} | "
            f"{display_score(raw)} | "
            f"{classify_change(sgm['accuracy'], raw['accuracy'], evidence_ids)}：{question} |"
        )

    for report_index, sgm in enumerate(failures, start=1):
        qa = qa_index[sgm["id"]]
        raw = raw_index[sgm["id"]]
        evidence_ids = [str(item) for item in qa.get("evidence_ids", [])]
        evidence_chunks = collect_text_evidence(
            evidence_ids,
            email_index,
            image_index,
            video_index,
            BATCH_FIELDS,
        )

        lines.extend(
            [
                "",
                f'<a id="case-{report_index}"></a>',
                f"## 案例 {report_index}：原题 {qa_order[sgm['id']]}，{type_text(sgm['qtype'])}",
                "",
                f"**这一例发生了什么：** {result_summary(sgm, raw, evidence_ids)}",
                "",
                f"**问题原文：** {sgm['question']}",
                "",
                "**标准答案：**",
                "",
                fenced(sgm["ground_truth"]),
                "",
                f"**只看 SGM 压缩文本时，模型回答（{display_score(sgm)}）：**",
                "",
                fenced(sgm["prediction"]),
            ]
        )
        if sgm_judges.get(sgm["id"]):
            lines.extend(["", f"**裁判理由：** {sgm_judges[sgm['id']]}" ])

        lines.extend(
            [
                "",
                f"**直接查看原始图片/视频时，模型回答（{display_score(raw)}）：**",
                "",
                fenced(raw["prediction"]),
            ]
        )
        if raw_judges.get(sgm["id"]):
            lines.extend(["", f"**Raw 裁判理由：** {raw_judges[sgm['id']]}" ])

        lines.extend(
            [
                "",
                f"**这道题给模型的正确证据 IDs（共 {len(evidence_ids)} 条）：** "
                + ", ".join(f"`{item}`" for item in evidence_ids),
                "",
                "**先看精简证据表：**",
                "",
                *concise_evidence_rows(
                    evidence_ids, email_index, image_index, video_index
                ),
                "",
                "<details>",
                "<summary>需要核查具体字段时，展开完整 SGM 输入</summary>",
                "",
                fenced("\n\n".join(evidence_chunks)),
                "",
                "</details>",
                "",
                "<details>",
                "<summary>需要看原图或视频时，展开原始文件路径</summary>",
                "",
            ]
        )

        for evidence_id in evidence_ids:
            if evidence_id.startswith("email"):
                lines.append(f"- `{evidence_id}`：邮件正文见 SGM evidence view")
                continue
            source = find_raw_source(evidence_id)
            if source:
                lines.append(f"- [{source.name}]({source.resolve()})")
            else:
                lines.append(f"- `{evidence_id}`：未找到原始文件")

        lines.extend(
            [
                "",
                "</details>",
                "",
                "**你的逐例判断**",
                "",
                "- 这道题实际需要完成哪些步骤：",
                "- SGM 是否缺少必要信息；具体缺什么：",
                "- 如果 SGM 信息足够，模型在哪一步做错：",
                "- Raw 为什么修复/仍未修复：",
                "- 备注：",
            ]
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(failures)} cases to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
