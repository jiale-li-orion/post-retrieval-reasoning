#!/usr/bin/env python3
"""Cross-check the Hard-31 solvability audit against frozen model answers."""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ARTIFACT_ROOT = Path("/home/orion/research_artifacts/frozen_behavior")
RUNS = {
    "qwen3vl2b_sgm": ARTIFACT_ROOT / "qwen3vl2b-hard-c0-c1-v1/C0",
    "mimo_v25_sgm": ARTIFACT_ROOT / "mimo-v25-legacy-oracle-v1/sgm",
    "mimo_v25_raw": ARTIFACT_ROOT / "mimo-v25-legacy-oracle-v1/raw",
}
EVAL_RELATIVE = Path(
    "evaluations/atm-primary-gpt5mini-stable-v1/atm_gpt-5-mini_stable.json"
)


def main() -> int:
    audit = read_json(HERE / "audit_rows.json")
    findings = read_json(HERE / "model_answer_findings.json")
    run_data = {name: load_run(root) for name, root in RUNS.items()}

    rows: list[dict[str, Any]] = []
    for audit_row in audit["rows"]:
        qid = audit_row["id"]
        answers = {}
        for run_name, run in run_data.items():
            prediction = run["predictions"].get(qid)
            evaluation = run["evaluations"].get(qid)
            if prediction is None or evaluation is None:
                raise ValueError(f"{run_name} does not cover {qid}")
            answers[run_name] = {
                "answer": prediction["answer"],
                "atm_score": normalize_score(evaluation["accuracy"]),
                "judge_explanation": evaluation.get("explanation"),
            }
        rows.append(
            {
                "index": audit_row["index"],
                "id": qid,
                "class": audit_row["class"],
                "qtype": audit_row["qtype"],
                "question": audit_row["question"],
                "gold_answer": audit_row["gold_answer"],
                "answers": answers,
                "finding": findings.get(qid),
            }
        )

    summary = make_summary(audit, rows, run_data)
    write_json(HERE / "model_answer_rows.json", {"summary": summary, "rows": rows})
    (HERE / "MODEL_ANSWER_CROSSCHECK.md").write_text(
        render_markdown(summary, rows), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def load_run(root: Path) -> dict[str, Any]:
    prediction_path = root / "predictions.jsonl"
    evaluation_path = root / EVAL_RELATIVE
    predictions = {}
    for line in prediction_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        qid = item.get("id") or item.get("qa_id")
        if qid in predictions:
            raise ValueError(f"duplicate prediction: {qid}")
        predictions[qid] = item
    evaluations = {item["id"]: item for item in read_json(evaluation_path)}
    return {
        "predictions": predictions,
        "evaluations": evaluations,
        "prediction_path": str(prediction_path),
        "prediction_sha256": file_sha256(prediction_path),
        "evaluation_path": str(evaluation_path),
        "evaluation_sha256": file_sha256(evaluation_path),
    }


def make_summary(
    audit: dict[str, Any], rows: list[dict[str, Any]], run_data: dict[str, Any]
) -> dict[str, Any]:
    by_class: dict[str, dict[str, list[float]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for row in rows:
        for run_name, answer in row["answers"].items():
            by_class[row["class"]][run_name].append(answer["atm_score"])
    class_means = {
        label: {
            run_name: round(sum(scores) / len(scores), 4)
            for run_name, scores in runs.items()
        }
        for label, runs in sorted(by_class.items())
    }
    return {
        "dataset": audit["summary"]["dataset"],
        "audit_counts": dict(Counter(row["class"] for row in rows)),
        "class_mean_atm_score": class_means,
        "finding_count": sum(row["finding"] is not None for row in rows),
        "source_runs": {
            name: {
                key: value
                for key, value in data.items()
                if key.endswith("path") or key.endswith("sha256")
            }
            for name, data in run_data.items()
        },
        "interpretation_rule": (
            "Model answers are diagnostic observations, not labels of solvability. "
            "A correct score cannot repair missing semantics, and a wrong score does not "
            "by itself prove that an item is unsolvable."
        ),
    }


def render_markdown(summary: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    lines = [
        "# ATM Hard-31 模型回答对照复查",
        "",
        "> 本报告不运行新模型，只读取三份冻结产物：Qwen3-VL-2B SGM、MiMo V2.5 SGM、MiMo V2.5 Raw。",
        "> 模型回答只用于检验审计判断，不以答对/答错反推题目是否可解。",
        "",
        "## 修订结论",
        "",
        "- 第 3 题由 B 改为 D：三种回答都纳入 gold 排除的 transit/airport cities，暴露未声明的 visit/city ontology。",
        "- 第 21 题由 B 改为 D：模型识别两次访问后将 `last visit` 解释为最近一次，gold 却要求返回两次日期。",
        "- 修订后 A=10、B=9、C=3、D=3、E=6，C+D+E=12/31。",
        "- 第 10、26 题的满分不能证明语义可恢复：Oracle list-recall 允许直接复制全部 evidence IDs。",
        "- 第 16、25、30 题暴露 answer prompt 的输出合同干扰：qtype 是 `open_end`，模型却可能受 `recall/list items -> IDs` 指令影响输出 IDs；第 16 题在 Qwen SGM 与 MiMo SGM 中都出现。",
        "- 第 29 题 judge 理由有误：它把 evidence 中的酒店正式名称称为错误；但模型没有明确给出 timelapse 与酒店的关系，因此本轮不据此改类。",
        "",
        "## 按类别的实际 ATM 均分",
        "",
        "| 类别 | 题数 | Qwen3-VL-2B SGM | MiMo SGM | MiMo Raw |",
        "|:---:|---:|---:|---:|---:|",
    ]
    counts = summary["audit_counts"]
    means = summary["class_mean_atm_score"]
    for label in "ABCDE":
        lines.append(
            f"| {label} | {counts[label]} | {means[label]['qwen3vl2b_sgm']:.4f} | "
            f"{means[label]['mimo_v25_sgm']:.4f} | {means[label]['mimo_v25_raw']:.4f} |"
        )

    lines.extend(
        [
            "",
            "这些均分仅作 sanity check。尤其是 list-recall Oracle 条件存在全量 ID 复制捷径，",
            "因此 C/E 类得到高分并不构成可解性证据。",
            "",
            "## 31 题回答总表",
            "",
            "| # | 类 | qtype | Qwen SGM | MiMo SGM | MiMo Raw | 复查标记 |",
            "|---:|:---:|---|---|---|---|---|",
        ]
    )
    for row in rows:
        answer_cells = []
        for run_name in ("qwen3vl2b_sgm", "mimo_v25_sgm", "mimo_v25_raw"):
            answer = row["answers"][run_name]
            answer_cells.append(
                f"{compact(answer['answer'])}<br>**score={answer['atm_score']:.4f}**"
            )
        finding = row["finding"]
        finding_cell = "-" if finding is None else (
            f"`{finding['effect']}`<br>{finding['note']}"
        )
        cells = [
            str(row["index"]), row["class"], row["qtype"], *answer_cells, finding_cell
        ]
        lines.append("| " + " | ".join(table_cell(cell) for cell in cells) + " |")

    lines.extend(["", "## 关键病例完整对照", ""])
    for row in rows:
        if row["finding"] is None:
            continue
        lines.extend(
            [
                f"### {row['index']:02d}. `{row['id']}` — {row['class']}",
                "",
                f"- **Question:** {row['question']}",
                f"- **Gold:** {row['gold_answer']}",
                f"- **复查结论:** {row['finding']['note']}",
            ]
        )
        for run_name in ("qwen3vl2b_sgm", "mimo_v25_sgm", "mimo_v25_raw"):
            answer = row["answers"][run_name]
            lines.append(
                f"- **{run_name} ({answer['atm_score']:.4f}):** "
                f"{markdown_multiline(answer['answer'])}"
            )
            if answer["judge_explanation"]:
                lines.append(f"  - Judge: {answer['judge_explanation']}")
        lines.append("")

    lines.extend(["## Provenance", ""])
    for run_name, source in summary["source_runs"].items():
        lines.extend(
            [
                f"- `{run_name}` predictions: `{source['prediction_path']}`",
                f"  - SHA256: `{source['prediction_sha256']}`",
                f"- `{run_name}` evaluation: `{source['evaluation_path']}`",
                f"  - SHA256: `{source['evaluation_sha256']}`",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def normalize_score(value: Any) -> float:
    if isinstance(value, bool):
        return float(value)
    return float(value)


def compact(value: Any, limit: int = 180) -> str:
    text = " ".join(str(value).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def table_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def markdown_multiline(value: Any) -> str:
    return "<br>\n".join(line.rstrip() for line in str(value).splitlines())


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


if __name__ == "__main__":
    raise SystemExit(main())
