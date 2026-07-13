# API Incidents

## AI-001: Kimi C1 Used `moonshot-v1-auto`

Date: 2026-07-13

The first local artifact under provider ID `kimi_k25` requested
`moonshot-v1-auto`. The API returned a mixture of `moonshot-v1-8k` and
`moonshot-v1-32k`. The artifact therefore does not measure Kimi K2.5 and is
excluded from every formal comparison.

The Moonshot `/v1/models` endpoint for the configured account explicitly lists
`kimi-k2.5`. The provider registry now freezes that exact model ID instead of
accepting a model alias from the environment. The invalid artifact is retained
outside Git under a directory prefixed with `invalid-wrong-model-alias-` and
must not be passed to evaluation.
