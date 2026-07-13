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
conditions. The suite is fixed to:

```text
Qwen3-8B-ms
DeepSeek-R1-Distill-Llama-8B
Qwen2.5-7B-Instruct
Qwen3-VL-2B-Instruct
Qwen3-VL-8B-Instruct
```

The first three entries are user-provided local snapshots under the shared
remote model directory. Their source metadata and file hashes must be recorded
before formal runs. The two Qwen3-VL snapshots are downloaded into the same
directory and pinned to immutable Hugging Face revisions.

This list supersedes every occurrence of `Mistral-7B-Instruct` in the original
v1.0 protocol and execution plan. `Qwen3-8B-ms` occupies that experimental
slot. The registry, rather than a model alias in prose, is authoritative for
the exact snapshot and file hash.

GPT is not an answerer in the first-cycle matrix. Primary mechanism runs use
BF16 full weights. Quantized runs cannot support primary mechanism claims.

## 3. Judge Contract

ATM/QS uses the official evaluator:

- `number`: normalized Exact Match
- `list_recall`: normalized Jaccard, with precision/recall reported separately
- `open_end`: official prompt, `gpt-5-mini`, `reasoning_effort=minimal`

DeepSeek V4 Flash is a secondary agreement judge only. It never replaces or
changes the primary ATM/QS score.

Inference and evaluation are separate immutable stages. Inference always saves
predictions, usage, latency, and an inference manifest without requiring judge
credentials. Evaluation later consumes a frozen prediction artifact and writes
its own manifest and cache. Only evaluation batches containing `open_end`
questions require the primary judge API key. J-lens fitting, readout, and
causal mechanism experiments do not depend on judge availability.

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

## 7. J-lens Calibration Corpus

The calibration source is the complete WikiText-103 raw train split. Empty
records are removed, the remaining original record indices are fully shuffled
with seed 17, and each document is independently tokenized with the target
model tokenizer. Each document is divided into consecutive, non-overlapping
256-token windows. Incomplete tails are dropped and windows never cross
document boundaries. Windows that do not survive an exact
decode/re-tokenize token-ID round trip are excluded. The first 512 valid
windows in shuffled-record order are frozen for each model; the first 256 are
the nested stability subset. Every row records its source record index,
within-document window index, token count, and token-ID hash.

The reference fitter targets the final residual layer and jointly fits every
preceding source layer. The final layer itself uses the identity readout. A
Qwen3-VL-2B resource probe showed that fitting all 27 source layers jointly
costs approximately the same GPU time as fitting one layer, so layer-wise
repeated fits are not used. Primary settings are BF16 model weights,
`dim_batch=8`, `max_seq_len=256`, `skip_first=16`, and an atomic checkpoint
every eight prompts. Completed fits retain the lens and manifest and remove the
redundant running-sum checkpoint.

`dim_batch` is a resource batching parameter rather than a change to the
Jacobian estimator. A WSL residency OOM on Qwen3-8B established a
model-specific `dim_batch=2` override through one-prompt full-layer probes;
the incident and measurements are recorded in `RESOURCE_INCIDENTS.md`. The
model remains BF16, full weight, all-layer, and 256-token.

For the top-25 stability criterion, the next 32 valid windows from the same
model-specific shuffled stream (offset 512, i.e. windows 513-544) are frozen as
held-out prompts and never included in either fit. At every source layer, the
n256 and n512 lenses are compared at the final token position of each held-out
prompt. Top-25 set overlap is aggregated by the median over all
`prompt × layer` pairs.

## 8. Hard Verbal-Annotation Cache

ATM Full and Hard are separate QA collections rather than a nested identifier
subset. Hard C1 must use the independently generated `oracle-hard` cache. Its
frozen contract is 194 `(qa_id, evidence_id)` rows with annotation SHA256
`11f78d25f1142fa4839ab58452141129b3f431707d8f43e56c672339a1436eeb`.
Using the Full cache for Hard is invalid even though both caches use the same
Verbal-R3 model, prompt, and decoding contract.

## 9. Multi-Token Readout Boundary

The first ATM smoke confirmed that automatic gold targets can be entirely
multi-token. Token-set top-k coverage is retained only as a secondary basic
metric. Primary vanilla J-lens rank and margin require frozen single-token
aliases. Hard decision-program review must additionally freeze useful operands,
entities, phrase aliases, and decoys. If derived targets remain predominantly
multi-token, the pre-registered next branch is concept-set aggregation followed
by phrase/sequence functional lens; first-token rank is not an allowed proxy.
