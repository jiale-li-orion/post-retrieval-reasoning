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

Both recovery probes completed with BF16 weights, all 35 source layers, and
the same 256-token prompt:

| dim_batch | elapsed | peak allocated | peak reserved | result |
| ---: | ---: | ---: | ---: | --- |
| 4 | 143.76 s | 20.86 GiB | 20.93 GiB | complete |
| 2 | 149.84 s | 18.07 GiB | 18.11 GiB | complete |

`dim_batch=2` is selected for Qwen3-8B. It is approximately 4.2% slower per
prompt than 4 while retaining about 2.8 GiB more allocator headroom. At the
observed rate, an n256 fit is expected to take approximately 10.7 hours. This
is a model-specific resource override; all other models retain the default
`dim_batch=8` unless they independently fail their own resource probe.

The formal n256 fit was restarted from a clean artifact at commit `7b0821d`.
Its first prompt completed in 150 seconds, matching the `dim_batch=2` probe,
while the process used approximately 19.3 GiB according to `nvidia-smi` and
drew approximately 406 W. This first-prompt parity is the operational gate that
distinguishes the recovered run from the failed residency-thrashing run.
