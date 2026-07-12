# Resource Incidents

## RI-001: Qwen3-8B J-lens WSL Residency OOM

Date: 2026-07-12

The first formal Qwen3-8B n256 fit used the globally frozen configuration
`dim_batch=8`, BF16 weights, all 35 source layers, and 256-token windows. It
failed to complete the first prompt after approximately 3 hours 51 minutes.
No checkpoint was created and the log stopped at the first autograd call.

The GPU reported approximately 24.1 GiB used, 100% SM utilization, 0% memory
utilization, and only about 98 W power draw. At the start of the first backward
pass, the WSL kernel recorded:

```text
dxgkio_make_resident: Ioctl failed: -12
```

The timing and `-ENOMEM` result identify WSL/WDDM GPU-residency failure rather
than ordinary slow execution. The process remained active inside a CUDA kernel
without producing scientific progress.

The failed artifact is retained outside Git at:

```text
/home/lab/lab/research_artifacts/jlens_fits/qwen3_8b_ms/failed/
  wikitext103-n256-v1-wsl-residency-oom/
```

The primary protocol remains BF16, full weight, all source layers, and
256-token windows. Resource recovery may reduce `dim_batch` because this
changes batching and backward-pass count, not the Jacobian estimator. A formal
fit may restart only after a one-prompt probe completes with recorded peak
memory and practical throughput. The probe order is `dim_batch=4`, then 2 if
4 is not viable. Quantization is not an admissible recovery.
