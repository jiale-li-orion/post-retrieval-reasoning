# Post-Retrieval Reasoning v1.0

This is the formal experiment line for the paper. It supersedes the old
Verbal-Annotation-only protocol as the top-level experimental contract while
reusing its annotation code as a component.

## Authority

Read these documents in order:

1. `../../FINAL_EXPERIMENTAL_PROTOCOL_v1.0.md`
2. `../../EXPERIMENT_DESIGN_AND_EXECUTION_PLAN_v1.0.md`
3. `PROTOCOL_ADDENDUM_v1.0.md`
4. `OPENCODE_SETUP.md`

If the addendum conflicts with either v1.0 document, the addendum governs the
items it explicitly changes. Everything else remains frozen by the final
protocol.

## Current Stage

- Phase 0: code/model/data bootstrap complete
- Gate A: passed on 2026-07-12
- Phase 2 canonical VA cache: `canonical-e1/local-v1` is running locally with
  resume and a 5-second cooling interval. The cache is append-only and remains
  outside Git. The interval was raised from 3 seconds after the notebook GPU
  approached the 82 C thermal stop line.
- E1 open-weight control inference: Qwen3-VL-2B Hard C3-C5 is complete and C6
  is running on the remote 4090 as the final item in a fail-fast serial queue.
  These NIAH controls reuse the exact generation path of the frozen
  Qwen3-VL-2B C0/C1 runs and require neither VA nor a judge.
- Qwen3-VL-2B Hard C0/C1 primary judge: complete as a Phase 1 behavior
  closure. This is not yet Gate B because the full E1 matrix, API extensions,
  and secondary judge agreement remain incomplete.
- Gate B: not passed
- Gate C: in progress; Qwen3-VL-2B calibration stability passed
- E2-E4: blocked until explicit human approval after Gate C

Gate A verified state as of 2026-07-12:

- Remote branch and GitHub origin are synchronized.
- Root `pyproject.toml` and `uv.lock` manage the single project environment.
- ATM Full/Hard hashes and all four fixed NIAH pools are validated.
- All five frozen open-weight models pass BF16 CUDA load and adapter checks.
  Qwen3-VL-8B generated successfully with 36 text layers and approximately
  16.7 GiB peak allocated GPU memory.
- Qwen3-VL-2B completed the two-question C0 vertical smoke with the official
  SGM formatter and evaluator. This smoke is infrastructure-only.
- The canonical `reranker3b-sft` snapshot is complete, revision- and
  hash-frozen, and passes the two-question/ten-evidence VA cache preflight.
- A fresh paired C0/C1 two-question smoke confirms identical evidence IDs and
  order and a rendered-prompt diff containing only the annotation blocks.
- Inference and deterministic ATM evaluation run as separate immutable stages
  without judge credentials; both stages wrote complete manifests.
- The remote test suite passes 54 tests; warnings are limited to third-party
  SWIG deprecation messages.
- The five-model suite is `Qwen3-8B-ms`, `DeepSeek-R1-Distill-Llama-8B`,
  `Qwen2.5-7B-Instruct`, `Qwen3-VL-2B-Instruct`, and
  `Qwen3-VL-8B-Instruct`; it supersedes the earlier Mistral slot.
- The WikiText-103 source revision and five model-specific 512-window corpora
  are frozen and hash-registered. Their first 256 rows are the nested stability
  subsets. No lens fit has completed yet.
- Qwen3-VL-2B completed both nested fits. Its matrix-cosine median is
  `0.9999695`, held-out top-25 overlap median is `0.96`, and the frozen
  stability gate passed. The n256 lens is the selected first ATM readout lens.
- Qwen3-8B completed an n256 calibration lens, but it has not passed a nested
  stability gate and remains exploratory. Qwen2.5-7B is paused at the atomic
  prompt-64 checkpoint while the first ATM readout closes the scientific loop.
- A two-question Hard C0/C1 readout smoke completed across 28 layers and all
  `P_evidence_end_i`, `P_q`, and `P_a0` positions. It confirmed exact paired
  J/logit output and also confirmed that the automatic targets for those two
  questions are all multi-token; token-set coverage remains secondary.
- A rule-frozen Hard-31 diagnostic using single-token `Unknown`/`known` aliases
  completed for C0/C1. At C1's last evidence position and layer 24, the
  `Unknown-known` margin predicts an eventual exact `Unknown` with AUC 0.852
  for J-lens and 0.752 for logit lens. The paired bootstrap interval for the
  +0.10 AUC difference crosses zero, so this establishes diagnostic
  readability but not J-lens superiority. Full lightweight results are in
  `reports/jlens_diagnostic_2026-07-13/`.
- The official ATM prompt places the question before evidence. The implemented
  `P_q` is consequently a pre-evidence negative control; evidence-conditioned
  silent-state claims use `P_evidence_end_i` and `P_a0`. Small BF16 prefix
  drift between unequal-length C0/C1 prompts is tracked as a numerical control.
- ATM Full and Hard use disjoint QA identifiers. Hard C1 therefore uses the
  independently frozen 194-row `oracle-hard/local-v1` annotation cache, not
  the 1,457-row Full cache. All 194 Hard evidence pairs and SGM hashes match.
- The Hard 31 decision-program review packet is generated under
  `/home/orion/research_artifacts/decision_program_review/hard31-v1/`.
  Formal trajectories remain blocked until every program is human-reviewed
  and marked `frozen`.
- Five model-specific sets of 32 held-out stability prompts are frozen at
  stream offset 512. The judge-free matrix-cosine and final-position top-25
  overlap evaluator is implemented and tested.
- Immutable behavior shards now support strict-prefix recovery, guarded GPU
  queues, and deterministic shard merging. Canonical VA generation has its own
  GPU-locked entry point.
- Full target manifests and 31 explicitly unreviewed Hard decision-program
  drafts are generated under the artifact root. Formal trajectories remain
  blocked until the drafts are reviewed and frozen.
- API inference for MiMo V2.5, MiniMax M3, and Kimi K2.5 is implemented as a
  resumable, judge-free local stage restricted to Hard C1/C7-C10.
- GPT-5-mini primary judging for the frozen Qwen3-VL-2B Hard C0/C1 predictions
  completed with fallback disabled and no failed rows. C0 ATM is `0.3484`; C1
  ATM is `0.2007`. The decline comes entirely from `list_recall`. The paired
  behavior report is tracked at
  `reports/behavior_pair_qwen3vl2b_hard_c0_c1_primary_v2/`.
- Hard-31 decision-program enrichment is complete. The editable review packet
  is under
  `/home/orion/research_artifacts/decision_program_review/hard31-v2-enriched-review/`.
  Its Qwen3-VL-2B expressibility audit found A/B mechanism targets for only
  9/31 questions (`29.0%`), so the pre-registered phrase/sequence extension is
  triggered. Formal gold/operand/intermediate trajectories remain blocked until
  all 31 entries are human-reviewed and marked `frozen` and the extension is
  designed.
- Legacy MiMo V2.5 Hard Oracle SGM and Raw predictions now have complete
  GPT-5-mini primary evaluations in a frozen local snapshot. Their ATM scores
  are `0.4408` and `0.5811`, respectively; both evaluations cover 31/31 rows
  with no judge failure or fallback.
- A Qwen3-8B Hard C0 preflight was stopped after eight rows because native
  reasoning repeatedly consumed the full 1,000-token answer budget before a
  final answer was emitted. The partial artifact is invalid for formal E1 and
  must not be resumed until the reasoning-output contract is frozen; see
  `BEHAVIOR_INCIDENTS.md`.

## Machine Roles

- Remote WSL `/home/lab/lab` with RTX 4090: the only code-writing environment;
  open-weight behavior, canonical Verbal Annotation cache, J-lens fitting,
  readout, and later causal experiments.
- Local notebook: checks out a frozen commit and runs API answerers and the
  official ATM judge only. API keys stay in local environment variables.
- GitHub branch: `experiment/post-retrieval-jspace-v1`.

Large data, model weights, predictions, annotation caches, lens artifacts, and
trajectories are not committed. Git stores configs, manifests, hashes, summary
tables, and reports.

Behavior generation and judging are separate immutable stages. Generation
writes `predictions.jsonl`, token usage, latency, and an inference manifest; it
does not require judge credentials. `behavior/evaluate.py` later consumes that
frozen run and writes a separate evaluation directory and manifest. Only a run
containing `open_end` items requires `OPENAI_API_KEY`. J-lens fitting, readout,
and trajectory analysis never invoke the judge.

## E1 Operations

These commands run on the remote 4090 only after the active stability gate
permits E1. The wrappers hold the shared GPU lock, refuse overlapping jobs,
and never invoke a judge.

```bash
# Generate the answerer-independent canonical Full+NIAH annotation union once.
experiments/post_retrieval_jspace_v1/scripts/run_va_cache.sh canonical-e1-v1

# Example single-condition queue; interrupted shards resume in place.
experiments/post_retrieval_jspace_v1/scripts/run_behavior_queue.sh \
  qwen3_vl_2b_instruct C0 hard e1-qwen3vl2b-c0-v1 1

# After explicit stability approval, launch a complete text/VA queue in tmux.
experiments/post_retrieval_jspace_v1/scripts/experimentctl \
  start-queue e1-hard --tmux
experiments/post_retrieval_jspace_v1/scripts/experimentctl \
  start-queue e1-full --tmux
```

The aggregate Hard queue covers C0/C1/C3-C10. C2 Raw is intentionally excluded
until its dedicated multimodal runner passes official ATM parity checks.

Target generation is CPU-safe and can run while a fit occupies the GPU:

```bash
experiments/post_retrieval_jspace_v1/scripts/run_target_generation.sh atm-targets-v1
```

## Local API Inference

Copy the frozen canonical VA `annotations.jsonl` to the notebook, check out the
same commit, and set provider values only in the local environment. MiMo is
fixed to `https://api.xiaomimimo.com/v1`, `mimo-v2.5`, and disabled thinking;
only its key is required. MiniMax and Kimi aliases/endpoints are deliberately
not guessed.

```bash
export MIMO_API_KEY=...
# or:
export MINIMAX_API_KEY=...
export MINIMAX_BASE_URL=...
export MINIMAX_MODEL=...
# or KIMI_API_KEY, KIMI_BASE_URL, KIMI_MODEL

experiments/post_retrieval_jspace_v1/scripts/run_api_behavior_queue.sh \
  mimo_v25 /path/to/annotations.jsonl api-mimo-v25-v1
```

The API queue runs Hard C1/C7-C10, records returned model IDs and token usage,
and stops on the first failure. It does not run C0/C3-C6 or any judge.

The project uses the root `pyproject.toml` and `uv.lock`; all commands run via
`uv run`. ATM-Bench remains a pinned source checkout and is exposed through
`PYTHONPATH` rather than installed with its optional vLLM dependency stack.

## Stop Rule

The first implementation cycle ends at Gate C. Do not start E2, E3, E4, or an
adaptive extension until the Gate C review bundle has been inspected and the
user explicitly approves continuation.

## J-lens Operations

中文夜间运行步骤见 `EVENING_JLENS_RUNBOOK.md`。

Run these commands only on the remote project checkout. Each fit wrapper
refuses to overlap another known GPU experiment and writes an immutable fit
directory plus a persistent log.

```bash
cd /home/lab/lab/post-retrieval-reasoning

# Read-only status.
experiments/post_retrieval_jspace_v1/scripts/check_jlens_status.sh

# After both Qwen3-VL-2B fits are complete.
experiments/post_retrieval_jspace_v1/scripts/run_jlens_stability.sh \
  qwen3_vl_2b_instruct wikitext103-n256-v2 wikitext103-n512-v1 \
  stability-n256-n512-v1
```

The stability report decides whether the remaining models use 256 or 512
prompts. Substitute the approved count for `N` below and run one command at a
time:

```bash
experiments/post_retrieval_jspace_v1/scripts/run_jlens_fit.sh \
  qwen3_8b_ms N wikitext103-nN-v1
experiments/post_retrieval_jspace_v1/scripts/run_jlens_fit.sh \
  deepseek_r1_distill_llama_8b N wikitext103-nN-v1
experiments/post_retrieval_jspace_v1/scripts/run_jlens_fit.sh \
  qwen2_5_7b_instruct N wikitext103-nN-v1
experiments/post_retrieval_jspace_v1/scripts/run_jlens_fit.sh \
  qwen3_vl_8b_instruct N wikitext103-nN-v1
```

To resume an interrupted running fit, repeat its exact command with
`--resume` as the fourth argument. A completed or differently configured fit
cannot be resumed or overwritten.
