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

- Phase 0: in progress
- Gate A: not started
- Gate B: not started
- Gate C: not started
- E2-E4: blocked until explicit human approval after Gate C

## Machine Roles

- Remote WSL `/home/lab` with RTX 4090: the only code-writing environment;
  open-weight behavior, canonical Verbal Annotation cache, J-lens fitting,
  readout, and later causal experiments.
- Local notebook: checks out a frozen commit and runs API answerers and the
  official ATM judge only. API keys stay in local environment variables.
- GitHub branch: `experiment/post-retrieval-jspace-v1`.

Large data, model weights, predictions, annotation caches, lens artifacts, and
trajectories are not committed. Git stores configs, manifests, hashes, summary
tables, and reports.

## Stop Rule

The first implementation cycle ends at Gate C. Do not start E2, E3, E4, or an
adaptive extension until the Gate C review bundle has been inspected and the
user explicitly approves continuation.
