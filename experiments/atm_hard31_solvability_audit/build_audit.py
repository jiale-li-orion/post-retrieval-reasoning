#!/usr/bin/env python3
"""Build the reproducible ATM Hard-31 SGM solvability audit artifacts."""

from __future__ import annotations

import hashlib
import html
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
EXPERIMENT_ROOT = PROJECT_ROOT / "experiments/post_retrieval_jspace_v1"
ATM_ROOT = PROJECT_ROOT / "other_repo_references/ATM-Bench"
if str(EXPERIMENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT_ROOT))

from adapters.atm import ATMAdapter  # noqa: E402


def main() -> int:
    labels = json.loads((HERE / "audit_labels.json").read_text(encoding="utf-8"))
    atm = ATMAdapter(ATM_ROOT)
    items = atm.load_split("hard")
    if len(items) != 31 or set(labels) != {item.qa_id for item in items}:
        raise ValueError("audit labels must cover exactly the canonical Hard 31")

    rows: list[dict[str, Any]] = []
    for index, item in enumerate(items, start=1):
        chunks = atm.collect_sgm_chunks(item.evidence_ids)
        if len(chunks) != len(item.evidence_ids):
            raise ValueError(f"missing SGM evidence for {item.qa_id}")
        evidence = atm._official_oracle_module().build_text_evidence_block(chunks)
        rows.append(
            {
                "index": index,
                "id": item.qa_id,
                "qtype": item.qtype,
                "question": item.question,
                "gold_answer": item.gold_answer,
                "evidence_ids": list(item.evidence_ids),
                "gold_evidence": evidence,
                **labels[item.qa_id],
            }
        )

    counts = Counter(row["class"] for row in rows)
    summary = {
        "dataset": "ATM-Bench Hard 31",
        "view": "official SGM Oracle",
        "atm_commit": git_commit(ATM_ROOT),
        "hard_sha256": file_sha256(atm.split_path("hard")),
        "labels_sha256": file_sha256(HERE / "audit_labels.json"),
        "counts": {key: counts.get(key, 0) for key in "ABCDE"},
        "cde_count": sum(counts.get(key, 0) for key in "CDE"),
        "audit_rule": "Question + fully rendered SGM evidence only; hidden notes excluded",
    }
    write_json(HERE / "audit_rows.json", {"summary": summary, "rows": rows})
    (HERE / "HARD31_SOLVABILITY_AUDIT.md").write_text(
        render_markdown(summary, rows), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def render_markdown(summary: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    lines = [
        "# ATM Hard-31 可解性审计",
        "",
        "> 审计对象：ATM 官方 SGM Oracle answerer 实际获得的 `Question + Evidence`。",
        "> 判定时不使用数据集 hidden `notes`，也不假设正确 evidence ID 自动等于可解。",
        "",
        "## 结论摘要",
        "",
        f"- A：{summary['counts']['A']} 题",
        f"- B：{summary['counts']['B']} 题",
        f"- C：{summary['counts']['C']} 题",
        f"- D：{summary['counts']['D']} 题",
        f"- E：{summary['counts']['E']} 题",
        f"- **C+D+E：{summary['cde_count']}/31**",
        "",
        f"当前严格审计中，C/D/E 已达到 {summary['cde_count']} 题。因此，在逐题复核完成前，",
        "Hard-31 不应直接被视为纯粹的 post-retrieval evidence-use 主评测。",
        "",
        "## 总表",
        "",
        "| # | 类别 | qtype | Question | 指代表达 | 指代可恢复 | 联合可答 | 单项充分 | Gold 可推出 | Failure type |",
        "|---:|:---:|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        cells = [
            str(row["index"]),
            row["class"],
            row["qtype"],
            row["question"],
            row["referential_expression"],
            row["referent_recoverable"],
            row["jointly_answerable"],
            row["individually_sufficient"],
            row["gold_answer_justified"],
            row["failure_type"],
        ]
        lines.append("| " + " | ".join(table_cell(cell) for cell in cells) + " |")

    lines.extend(["", "## 逐题证据与判定", ""])
    for row in rows:
        lines.extend(
            [
                f"### {row['index']:02d}. `{row['id']}` — {row['class']}",
                "",
                f"- **Question:** {row['question']}",
                f"- **Gold answer:** {row['gold_answer']}",
                f"- **Referential expression:** {row['referential_expression']}",
                f"- **Referent recoverable?:** {row['referent_recoverable']}",
                f"- **Missing state:** {row['missing_state']}",
                f"- **Jointly answerable?:** {row['jointly_answerable']}",
                f"- **Individually sufficient?:** {row['individually_sufficient']}",
                f"- **Gold answer justified?:** {row['gold_answer_justified']}",
                f"- **Failure type:** {row['failure_type']}",
                f"- **Rationale:** {row['rationale']}",
                "",
                "<details>",
                "<summary>Gold evidence（模型实际看到的完整 SGM evidence）</summary>",
                "",
                "<pre>",
                strip_line_endings(html.escape(row["gold_evidence"])),
                "</pre>",
                "</details>",
                "",
            ]
        )
    lines.extend(
        [
            "## Provenance",
            "",
            f"- ATM commit: `{summary['atm_commit']}`",
            f"- Hard split SHA256: `{summary['hard_sha256']}`",
            f"- Audit labels SHA256: `{summary['labels_sha256']}`",
            "- Evidence formatter: ATM `oracle_baseline.build_text_evidence_block`",
            "- Hidden notes: excluded",
            "",
        ]
    )
    return "\n".join(lines)


def table_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def strip_line_endings(value: str) -> str:
    return "\n".join(line.rstrip() for line in value.splitlines())


def git_commit(path: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
    ).strip()


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
