# Behavior Run Incidents

## BI-001: Qwen3-8B native reasoning exhausted the answer budget

Date: 2026-07-13

The first Qwen3-8B-ms Hard C0 preflight used the current open-weight behavior
runner with `max_new_tokens=1000`. The model's chat template enabled native
`<think>` generation. Four of the first seven inspected rows reached exactly
1,000 completion tokens before emitting a final answer. The runner also stored
the full reasoning trace in the `answer` field rather than separating reasoning
from the answer supplied to the ATM evaluator.

The queue was stopped after eight rows. This artifact is an invalid preflight,
not a formal baseline:

```text
/home/lab/lab/research_artifacts/runs/C0/hard/qwen3_8b_ms/
  e1-hard-qwen3_8b_ms-C0-v1-shard-0-of-1/
```

Do not resume it. Before any reasoning-capable answerer is rerun, freeze and
test all of the following together:

- native reasoning enabled or disabled per model;
- reasoning budget versus final-answer budget;
- extraction and separate storage of reasoning and final answer;
- the exact text passed to the ATM evaluator;
- temperature, seed, and maximum-token settings.

Until that contract is resolved, Qwen3-8B-ms and
DeepSeek-R1-Distill-Llama-8B behavior queues are blocked. Their J-lens
calibration artifacts are unaffected.
