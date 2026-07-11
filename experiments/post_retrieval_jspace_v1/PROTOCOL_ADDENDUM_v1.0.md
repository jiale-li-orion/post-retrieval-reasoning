# Post-Retrieval Reasoning Protocol Addendum v1.0

Date: 2026-07-11

This addendum records decisions made after reviewing
`FINAL_EXPERIMENTAL_PROTOCOL_v1.0.md` and
`EXPERIMENT_DESIGN_AND_EXECUTION_PLAN_v1.0.md`. It changes only the items below.

## 1. API Behavioral Matrix

The API answerers are MiMo V2.5, MiniMax M3, and Kimi K2.5. They run only on
ATM-Bench-Hard under the new Verbal Annotation conditions:

- C1: Oracle SGM + VA
- C7: NIAH-25 SGM + VA
- C8: NIAH-50 SGM + VA
- C9: NIAH-100 SGM + VA
- C10: NIAH-200 SGM + VA

C0 and C3-C6 are reused from a frozen snapshot of the ATM-Bench live
leaderboard. Reused API aggregates are contextual/quasi-comparative references.
They must not support paired transitions, McNemar tests, internal-state
correspondence, or causal claims. API Full, API Raw, and repeated API baselines
are outside v1.0.

The live leaderboard snapshot is authoritative over a stale repository README.
Its retrieval timestamp, URL, page SHA256, and every imported cell must be
recorded in `official_atm_reference.yaml` before any comparison is generated.

## 2. Open-Weight Suite

All five open-weight models rerun their required baselines and paired
conditions. Mistral is fixed to:

```text
mistralai/Mistral-7B-Instruct-v0.3
```

GPT is not an answerer in the first-cycle matrix. Primary mechanism runs use
BF16 full weights. Quantized runs cannot support primary mechanism claims.

## 3. Judge Contract

ATM/QS uses the official evaluator:

- `number`: normalized Exact Match
- `list_recall`: normalized Jaccard, with precision/recall reported separately
- `open_end`: official prompt, `gpt-5-mini`, `reasoning_effort=minimal`

DeepSeek V4 Flash is a secondary agreement judge only. It never replaces or
changes the primary ATM/QS score.

## 4. Failure Taxonomy

The primary taxonomy contains one external and five internal labels:

- V0: view insufficiency
- F1: formation / workspace entry
- F2: binding / competition
- F3: composition / operator execution
- F4: downstream consumption
- F5: answer realization / output

The A-J taxonomy remains secondary and may express uncertainty or multiple
candidate mechanisms.

## 5. Reasoning-Model Slot Contract

Reasoning-capable models use a dual-slot baseline from Gate C onward:

1. natural reasoning slots and the native final-answer boundary;
2. an assistant-side `Final answer:` prefill control.

The prefill control tests reportability at an answer-conditioned slot. A high
rank after prefill is not evidence that the answer representation formed in the
natural silent state. Generated reasoning positions, native answer positions,
and silent prompt positions must be tagged separately. J-lens and logit-lens
comparisons use the same activation, layer, and position.

## 6. Execution and Storage

- Remote WSL RTX 4090 is the sole code-writing environment after bootstrap.
- The local notebook runs API inference and judging from a frozen commit.
- The canonical VA cache is generated once on the remote machine and copied to
  the local notebook with its manifest and SHA256.
- Git tracks only lightweight provenance and reports. Model weights, datasets,
  caches, predictions, lenses, and trajectories stay outside Git.
- STALE remains a gated secondary track.
- The first cycle stops after Gate C for human review.
