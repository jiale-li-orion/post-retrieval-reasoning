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
- The remote test suite passes 42 tests; warnings are limited to third-party
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

The project uses the root `pyproject.toml` and `uv.lock`; all commands run via
`uv run`. ATM-Bench remains a pinned source checkout and is exposed through
`PYTHONPATH` rather than installed with its optional vLLM dependency stack.

## Stop Rule

The first implementation cycle ends at Gate C. Do not start E2, E3, E4, or an
adaptive extension until the Gate C review bundle has been inspected and the
user explicitly approves continuation.
