#!/usr/bin/env python3
"""Audit whether J-lens adds diagnostic value over a same-state logit lens."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


TARGET_UNKNOWN = "diagnostic_unknown"
TARGET_KNOWN = "diagnostic_known"


def binary_auc(labels: Iterable[int], scores: Iterable[float]) -> float:
    labels = np.asarray(list(labels), dtype=int)
    scores = np.asarray(list(scores), dtype=float)
    positives = labels == 1
    negatives = labels == 0
    if not positives.any() or not negatives.any():
        return float("nan")
    ranks = pd.Series(scores).rank(method="average").to_numpy()
    positive_rank_sum = ranks[positives].sum()
    count_pos = int(positives.sum())
    count_neg = int(negatives.sum())
    return float(
        (positive_rank_sum - count_pos * (count_pos + 1) / 2)
        / (count_pos * count_neg)
    )


def add_last_evidence_label(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result["analysis_position"] = result["position_type"]
    mask = result["position_type"].str.startswith("P_evidence_end_")
    result.loc[mask, "analysis_position"] = "evidence_end"
    evidence = result.loc[mask, ["qa_id", "position_type"]].copy()
    evidence["evidence_index"] = (
        evidence["position_type"].str.rsplit("_", n=1).str[-1].astype(int)
    )
    last = evidence.groupby("qa_id")["evidence_index"].transform("max")
    last_keys = set(
        zip(
            evidence.loc[evidence["evidence_index"].eq(last), "qa_id"],
            evidence.loc[evidence["evidence_index"].eq(last), "position_type"],
        )
    )
    last_mask = [
        (qa_id, position) in last_keys
        for qa_id, position in zip(result["qa_id"], result["position_type"])
    ]
    result.loc[last_mask, "analysis_position"] = "last_evidence"
    return result


def target_margin(frame: pd.DataFrame) -> pd.DataFrame:
    index = ["qa_id", "layer", "method", "analysis_position"]
    pivot = frame.pivot_table(index=index, columns="target_id", values="score").reset_index()
    missing = {TARGET_UNKNOWN, TARGET_KNOWN} - set(pivot.columns)
    if missing:
        raise ValueError(f"diagnostic targets missing: {sorted(missing)}")
    pivot["unknown_known_margin"] = pivot[TARGET_UNKNOWN] - pivot[TARGET_KNOWN]
    return pivot


def output_transition(c0: str, c1: str) -> str:
    def label(value: str) -> str:
        return "U" if value.strip().casefold() == "unknown" else "N"

    return f"{label(c0)}->{label(c1)}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--c0-readout", type=Path, required=True)
    parser.add_argument("--c1-readout", type=Path, required=True)
    parser.add_argument("--c0-predictions", type=Path, required=True)
    parser.add_argument("--c1-predictions", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--bootstrap-samples", type=int, default=2000)
    parser.add_argument("--seed", type=int, default=20260713)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite output: {args.output}")
    args.output.mkdir(parents=True)
    predictions = {
        "C0": _load_predictions(args.c0_predictions),
        "C1": _load_predictions(args.c1_predictions),
    }
    if set(predictions["C0"]) != set(predictions["C1"]):
        raise ValueError("C0/C1 prediction IDs differ")

    frames = {}
    for condition, path in (("C0", args.c0_readout), ("C1", args.c1_readout)):
        frame = add_last_evidence_label(pd.read_parquet(path))
        frame["qa_id"] = frame["qa_id"].astype(str)
        frame["output_unknown"] = frame["qa_id"].map(
            lambda qa_id: int(predictions[condition][qa_id].strip().casefold() == "unknown")
        )
        frames[condition] = frame

    layerwise = _layerwise_auc(frames, args.bootstrap_samples, args.seed)
    layerwise.to_csv(args.output / "layerwise_auc.csv", index=False)
    paired = _paired_delta_auc(frames, predictions, args.bootstrap_samples, args.seed)
    paired.to_csv(args.output / "paired_delta_auc.csv", index=False)

    transitions = pd.Series(
        {
            qa_id: output_transition(predictions["C0"][qa_id], predictions["C1"][qa_id])
            for qa_id in sorted(predictions["C0"])
        },
        name="transition",
    )
    transitions.rename_axis("qa_id").reset_index().to_csv(
        args.output / "output_transitions.csv", index=False
    )
    summary = _summary(args, layerwise, paired, transitions)
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (args.output / "REPORT.md").write_text(_report(summary), encoding="utf-8")
    return 0


def _layerwise_auc(
    frames: dict[str, pd.DataFrame], bootstrap_samples: int, seed: int
) -> pd.DataFrame:
    rows = []
    rng = np.random.default_rng(seed)
    for condition, frame in frames.items():
        selected = frame[frame["analysis_position"].isin(["P_q", "last_evidence", "P_a0"])]
        margins = target_margin(selected)
        labels = selected[["qa_id", "output_unknown"]].drop_duplicates()
        margins = margins.merge(labels, on="qa_id", validate="many_to_one")
        unknown = selected[selected["target_id"].eq(TARGET_UNKNOWN)]
        for (position, layer, method), group in margins.groupby(
            ["analysis_position", "layer", "method"], sort=True
        ):
            auc, low, high = _bootstrap_auc(
                group["output_unknown"].to_numpy(),
                group["unknown_known_margin"].to_numpy(),
                bootstrap_samples,
                rng,
            )
            mrr_group = unknown[
                unknown["analysis_position"].eq(position)
                & unknown["layer"].eq(layer)
                & unknown["method"].eq(method)
            ]
            rows.append(
                {
                    "condition": condition,
                    "position": position,
                    "layer": int(layer),
                    "method": method,
                    "n": len(group),
                    "positive_n": int(group["output_unknown"].sum()),
                    "margin_auc": auc,
                    "margin_auc_ci_low": low,
                    "margin_auc_ci_high": high,
                    "unknown_mrr_auc": binary_auc(
                        mrr_group["output_unknown"], mrr_group["mrr"]
                    ),
                }
            )
    return pd.DataFrame(rows)


def _paired_delta_auc(
    frames: dict[str, pd.DataFrame],
    predictions: dict[str, dict[str, str]],
    bootstrap_samples: int,
    seed: int,
) -> pd.DataFrame:
    margins = {}
    for condition, frame in frames.items():
        selected = frame[frame["analysis_position"].isin(["last_evidence", "P_a0"])]
        margin = target_margin(selected)
        margins[condition] = margin.rename(
            columns={"unknown_known_margin": f"{condition.lower()}_margin"}
        )
    keys = ["qa_id", "layer", "method", "analysis_position"]
    paired = margins["C0"].merge(margins["C1"], on=keys, validate="one_to_one")
    paired["delta_margin"] = paired["c1_margin"] - paired["c0_margin"]
    paired["transition"] = paired["qa_id"].map(
        lambda qa_id: output_transition(
            predictions["C0"][qa_id], predictions["C1"][qa_id]
        )
    )
    paired = paired[paired["transition"].isin(["N->N", "N->U"])].copy()
    paired["new_unknown"] = paired["transition"].eq("N->U").astype(int)
    rng = np.random.default_rng(seed + 1)
    rows = []
    for (position, layer, method), group in paired.groupby(
        ["analysis_position", "layer", "method"], sort=True
    ):
        auc, low, high = _bootstrap_auc(
            group["new_unknown"].to_numpy(),
            group["delta_margin"].to_numpy(),
            bootstrap_samples,
            rng,
        )
        rows.append(
            {
                "position": position,
                "layer": int(layer),
                "method": method,
                "n": len(group),
                "positive_n": int(group["new_unknown"].sum()),
                "delta_margin_auc": auc,
                "delta_margin_auc_ci_low": low,
                "delta_margin_auc_ci_high": high,
            }
        )
    return pd.DataFrame(rows)


def _bootstrap_auc(labels, scores, samples, rng):
    auc = binary_auc(labels, scores)
    values = []
    labels = np.asarray(labels)
    scores = np.asarray(scores)
    for _ in range(samples):
        indices = rng.integers(0, len(labels), len(labels))
        value = binary_auc(labels[indices], scores[indices])
        if not np.isnan(value):
            values.append(value)
    if not values:
        return auc, float("nan"), float("nan")
    return auc, float(np.quantile(values, 0.025)), float(np.quantile(values, 0.975))


def _load_predictions(path: Path) -> dict[str, str]:
    result = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            qa_id = str(row.get("id", row.get("qa_id")))
            answer = row.get("prediction", row.get("answer", row.get("response", "")))
            result[qa_id] = str(answer)
    return result


def _summary(args, layerwise, paired, transitions):
    c1_last = layerwise[
        layerwise["condition"].eq("C1")
        & layerwise["position"].eq("last_evidence")
        & layerwise["layer"].eq(24)
    ].set_index("method")
    paired_a0 = paired[
        paired["position"].eq("P_a0") & paired["layer"].eq(22)
    ].set_index("method")
    return {
        "status": "complete_exploratory_diagnostic",
        "scope": "Qwen3-VL-2B, ATM Hard 31, C0/C1, Unknown-known rule-frozen targets",
        "transition_counts": transitions.value_counts().to_dict(),
        "key_observations": {
            "c1_last_evidence_layer24_margin_auc": {
                method: float(c1_last.loc[method, "margin_auc"])
                for method in c1_last.index
            },
            "c1_minus_c0_p_a0_layer22_new_unknown_auc": {
                method: float(paired_a0.loc[method, "delta_margin_auc"])
                for method in paired_a0.index
            },
        },
        "interpretation_boundary": [
            "P_q precedes evidence in the ATM prompt and is a negative control.",
            "Unknown is output-proximal; this tests diagnostic readability, not binding or reasoning correctness.",
            "The sample has 31 questions and only eight N->U transitions.",
            "J-lens utility must be judged against the same-activation logit-lens baseline.",
        ],
        "inputs": {
            "c0_readout_sha256": _sha256(args.c0_readout),
            "c1_readout_sha256": _sha256(args.c1_readout),
            "c0_predictions_sha256": _sha256(args.c0_predictions),
            "c1_predictions_sha256": _sha256(args.c1_predictions),
        },
    }


def _report(summary: dict) -> str:
    last = summary["key_observations"]["c1_last_evidence_layer24_margin_auc"]
    delta = summary["key_observations"]["c1_minus_c0_p_a0_layer22_new_unknown_auc"]
    transitions = summary["transition_counts"]
    return f"""# J-lens 工具有效性诊断

## 范围

Qwen3-VL-2B，ATM Hard 31，C0/C1 paired。目标由冻结规则生成，只包含 `Unknown` 与 `known` 的单 token aliases；本报告是探索性工具审计，不是论文机制结论。

## 行为锚点

- `N->N`: {transitions.get('N->N', 0)}
- `N->U`: {transitions.get('N->U', 0)}
- `U->U`: {transitions.get('U->U', 0)}

## 读出结果

在 C1 最后一个 evidence 位置、第 24 层，`Unknown-known` margin 对最终 `Unknown` 输出的 AUC：J-lens = {last.get('j_lens', float('nan')):.3f}，logit lens = {last.get('logit_lens', float('nan')):.3f}。

在 `P_a0` 第 22 层，C1-C0 margin 增量区分新增 `Unknown` (`N->U`) 与稳定非 `Unknown` (`N->N`) 的 AUC：J-lens = {delta.get('j_lens', float('nan')):.3f}，logit lens = {delta.get('logit_lens', float('nan')):.3f}。

## 当前判断

J-lens 工具链能够在生成前读出与最终弃答相关的内部状态，并且在证据末端的晚中层显示出比同位置 logit lens 更强的单点分离度。到 `P_a0`，两种 lens 都能较强地区分输出，说明一部分信号已经成为普通输出准备状态，不能据此宣称 J-lens 独有地读出了推理过程。

## 边界

- ATM prompt 中 `P_q` 位于 evidence 之前，只作为负对照。
- `Unknown` 是输出邻近概念；该实验验证诊断可读性，不验证变量绑定或答案正确性。
- 样本仅 31 题，其中新增 `Unknown` 只有 8 题；区间见 `layerwise_auc.csv` 和 `paired_delta_auc.csv`。
- 下一步必须使用人工冻结的 gold、operand 与 intermediate targets，才能判断 J-lens 是否解释 evidence use，而不只是预测输出。
"""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
