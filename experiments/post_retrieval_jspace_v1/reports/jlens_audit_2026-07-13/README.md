# J-lens Fit Audit, 2026-07-13

This directory is a review bundle for completed calibration work. It is not an
ATM result bundle and does not establish a paper-facing mechanism claim.

## Qwen3-8B-ms n256

The completed run fitted a global Jacobian lens from all 35 source layers to
target layer 35 on the frozen first 256 WikiText-103 calibration windows.

- Status: complete
- Runtime: 38,615.79 seconds (10.73 hours)
- Model: BF16, full weight, unquantized
- Hidden size: 4,096
- Lens matrices: 35 matrices of shape 4,096 x 4,096
- Lens file size: 1,174,412,600 bytes
- Lens SHA256: `5c89b4c3cce86e86bcc2574370666de870b46d0d7d471c5df9a1507de07080df`
- Artifact location: `/home/lab/lab/research_artifacts/jlens_fits/qwen3_8b_ms/wikitext103-n256-v1/lens.pt`
- Numerical audit: every matrix is finite; sampled matrix norms and maxima are
  recorded below.

| Layer | Frobenius norm | Maximum absolute value |
| --- | ---: | ---: |
| 0 | 241.7274 | 8.5547 |
| 1 | 225.9141 | 8.3438 |
| 17 | 158.1088 | 11.3281 |
| 34 | 69.8771 | 6.8086 |

The run produced a calibration lens only. The following protocol requirements
remain incomplete for this model:

- n512 fit and n256/n512 stability comparison;
- held-out top-25 overlap evaluation;
- ATM-position J-lens and same-activation logit-lens readouts;
- dual-slot, silent-position, and generated-token leakage checks;
- rank, MRR, margin, entropy, emergence, and persistence outputs.

Consequently, this run does not pass Gate C and cannot by itself support claims
about ATM failures, evidence use, reasoning state, or J-lens superiority.

The current n512 runner recomputes the first 256 calibration windows rather
than extending an FP32 running-sum checkpoint. Running it unchanged would cost
approximately twice the n256 runtime and violate the execution plan's intended
continuation optimization, although the resulting nested estimate would remain
scientifically comparable.

## Qwen3-VL-2B-Instruct stability

This model has both nested fits and a completed held-out stability evaluation.

- n256 runtime: 1.36 hours
- n512 runtime: 2.73 hours
- Matrix cosine median: 0.9999695
- Minimum layer matrix cosine: 0.9986418
- Held-out top-25 overlap median: 0.96
- Matrix threshold: 0.98
- Top-25 overlap threshold: 0.90
- Stability gate: passed

This supports using the n256 lens for this model under the frozen sample-size
criterion. It still does not constitute an ATM readout or a complete Gate C
result.

## Included files

- `qwen3_8b_ms/n256_manifest.json`: immutable run provenance and lens hash.
- `qwen3_8b_ms/n256_fit.log`: per-prompt fit diagnostics.
- `qwen3_vl_2b_instruct/n256_manifest.json`: n256 run provenance.
- `qwen3_vl_2b_instruct/n512_manifest.json`: n512 run provenance.
- `qwen3_vl_2b_instruct/stability.json`: complete per-layer and per-prompt
  stability measurements.
- `qwen3_vl_2b_instruct/stability_manifest.json`: stability provenance and
  input hashes.

The large lens files are deliberately excluded from Git. New token readouts or
matrix-level analyses require access to those external artifacts.
