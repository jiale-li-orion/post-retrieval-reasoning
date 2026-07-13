# C0/C1 Primary Behavior Audit

- Questions: 31 (all Hard question types)
- C0 ATM mean: 0.3484
- C1 ATM mean: 0.2007
- Behavior strata: `{'stable_non_abstention': 19, 'error_to_abstain': 3, 'partial_to_abstain': 1, 'correct_to_abstain': 3, 'non_abstention_degradation': 2, 'stable_abstention': 3}`
- Exact-Unknown transitions: `{'N->N': 21, 'N->U': 8, 'U->U': 2}`
- ATM-abstention transitions: `{'N->N': 21, 'N->U': 7, 'U->U': 3}`
- Positive / negative deltas: 0 / 6

This report is behavioral and does not infer an internal mechanism. Broad-only abstention rows remain human-review items.

## Degraded Questions

| QA | Type | C0 | C1 | Delta | Stratum | C1 abstains | Low annotations |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| `53ea4267-419b-4769-817c-add406463462` | list_recall | 1.000 | 0.000 | -1.000 | correct_to_abstain | True | 10 |
| `580a4fee-8595-4453-8368-f52eec0a3954` | list_recall | 1.000 | 0.000 | -1.000 | correct_to_abstain | True | 2 |
| `ef912ea0-634f-4c1f-88d5-9e0543708258` | list_recall | 1.000 | 0.000 | -1.000 | correct_to_abstain | True | 5 |
| `30be4a0e-8708-42fe-9a21-c73254c78270` | list_recall | 0.800 | 0.000 | -0.800 | partial_to_abstain | True | 6 |
| `716095fa-6f76-4f19-95e4-3c8bf079fbdd` | list_recall | 1.000 | 0.375 | -0.625 | non_abstention_degradation | False | 4 |
| `afa4bf6a-c459-4173-9de9-2aac6183a4a7` | list_recall | 1.000 | 0.846 | -0.154 | non_abstention_degradation | False | 13 |
