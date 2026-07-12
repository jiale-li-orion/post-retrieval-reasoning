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
- Phase 2 canonical VA cache: preflight passed; formal cache not generated
- Gate B: not started
- Gate C: not started
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
- The first primary fit, Qwen3-VL-2B on the 256-window subset, completed from
  code commit `1d20bda` with 256 prompts, 27 source layers, and a frozen lens
  hash. Its nested 512-window fit is running; all other models remain gated on
  the resulting stability report.
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
