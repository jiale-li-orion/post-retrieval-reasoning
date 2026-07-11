# OpenCode Setup Handoff

## Scope

OpenCode performs environment, authentication, repository, model, and dataset
preparation only. It must not implement experiment runners, modify either
protocol, generate scientific results, or start formal runs.

## Target Layout

```text
/home/lab/lab/post-retrieval-reasoning/    # project clone
/home/lab/.cache/huggingface/              # Hugging Face cache
/home/lab/lab/research_data/               # models and datasets
/home/lab/lab/research_artifacts/          # runs, VA cache, lenses, trajectories
```

Use exactly one project virtual environment:

```text
/home/lab/lab/post-retrieval-reasoning/.venv
```

Do not create virtual environments under `experiments/` or external repos.

## 1. Git and GitHub

1. Configure Git `user.name` and `user.email` for the lab account.
2. Configure a GitHub SSH key for `/home/lab/.ssh`.
3. Verify `ssh -T git@github.com` authenticates successfully.
4. Clone `git@github.com:jiale-li-orion/post-retrieval-reasoning.git` to
   `/home/lab/lab/post-retrieval-reasoning`.
5. Check out `experiment/post-retrieval-jspace-v1`.
6. Verify a dry Git round trip without changing scientific files: fetch,
   branch status, and remote visibility.

Never commit `.lab_login`, credentials, API keys, model weights, datasets,
caches, predictions, lens files, or trajectories.

## 2. System and Python Environment

Record, but do not silently change:

- WSL and Linux version
- GPU, driver, and CUDA runtime
- Python version
- available disk space

Use the root `pyproject.toml` and `uv.lock` as the only Python dependency
contract. Create/synchronize `.venv` with `uv sync`. Do not use ad-hoc `pip`
installs. ATM-Bench is imported from its pinned source checkout rather than
installed as a project dependency because its package metadata pulls in the
optional vLLM serving stack.

The environment must support:

- ATM-Bench at its pinned commit
- Verbal-R3 inference
- Anthropic Jacobian Lens
- PyTorch BF16 inference on RTX 4090
- Transformers model loading and hidden-state hooks
- YAML, JSONL, Parquet, and chunked array storage
- pytest

Write the fully resolved package list to
`/home/lab/lab/research_artifacts/environment/uv-freeze.txt`. Do not commit it
until Codex has reviewed it for secrets and machine-local paths.

Acceptance commands must prove:

- PyTorch sees one RTX 4090 with approximately 24GB VRAM.
- BF16 matrix multiplication succeeds on CUDA.
- the project interpreter is the only interpreter used by experiment scripts.

## 3. External Source Repositories

Clone into the project's ignored `other_repo_references/` directory and check
out exact revisions:

| Repository | Revision |
|---|---|
| `https://github.com/JingbiaoMei/ATM-Bench` | `3a1a606b872c4502e5efc632dcd1c076a220ed4a` |
| `https://github.com/0k9d0h1/VerbalR3` | `62c88a67c13d05cafbc5b7dbbd9ebe436d1d4e92` |
| `https://github.com/anthropics/jacobian-lens` | resolve and record exact HEAD; do not track a moving branch |

Do not download the community E4 repository in the first cycle.

For every repository, record URL, requested revision, resolved commit, dirty
status, and license path in a machine-readable setup report.

## 4. Model Checkpoints

Keep all five formal model directories together under
`/home/lab/lab/research_data/`. Three user-provided snapshots already exist and
must not be moved, deleted, renamed, or downloaded again:

```text
Qwen3-8B-ms
DeepSeek-R1-Distill-Llama-8B
Qwen2.5-7B-Instruct
```

Download the remaining formal models into the same parent directory and record
their resolved immutable Hugging Face revisions:

```text
Qwen/Qwen3-VL-2B-Instruct
Qwen/Qwen3-VL-8B-Instruct
```

Download the intervention model separately under the same parent directory:

```text
0k9d0h1/reranker3b-sft
```

The reranker revision is fixed:

```text
cdf46c85892ebb715cbd6a0b582af35ad5caa96b
```

For the user-provided snapshots, record config metadata and deterministic file
hashes as their local provenance. For downloaded models, resolve the snapshot
commit and never leave `main` or `latest` as the final registry value. Use
original weights suitable for BF16 mechanism runs; do not substitute 4-bit
weights.

For each checkpoint, verify tokenizer loading, chat-template availability,
architecture class, layer count, hidden size, vocabulary size, and one-token
CUDA forward pass. Do not run ATM questions.

## 5. Datasets

Prepare, without regenerating benchmark content:

- ATM-Bench Full and Hard release files
- fixed NIAH-25/50/100/200 files
- image and video SGM batch results
- email evidence
- Raw media required by Hard C2
- WikiText-103 raw train

Place canonical data under `/home/lab/lab/research_data/` and expose paths through
environment variables or symlinks expected by the pinned ATM repository. Do not
copy datasets into Git-tracked directories.

Validate the frozen ATM hashes:

```text
Full: ab6eaa9df62fb4162e0f5eecd98768a7e3ae721e32d2db2cf227ff41e3295762
Hard: acd35f2a172a9741d970d2cf21184ff0af8d79a8bf59967fc8aa33d619f6af4a
```

Run ATM's NIAH `--validate-only` command. Do not rebuild or reshuffle pools.

For WikiText-103, record dataset source, revision/config, split, cache path, and
the hash of the index list that will later define calibration windows. Do not
fit a lens.

## 6. Local Notebook API Environment

Do not copy API secrets to the remote machine. The user will configure local
environment variables for:

- MiMo V2.5 provider key and endpoint
- MiniMax M3 provider key and endpoint
- Kimi K2.5 provider key and endpoint
- OpenAI `gpt-5-mini` judge
- DeepSeek V4 Flash secondary judge

Only verify that required variable names are present. Never print their values.
The experiment manifest records variable names, requested model aliases,
provider endpoints without credentials, and returned model IDs.

## 7. Required Setup Report

Return one report containing:

- GitHub authentication success and checked-out branch/commit
- Python/CUDA/PyTorch/Transformers versions
- GPU and disk information
- external repository commits and dirty status
- model repository and resolved snapshot revisions
- data paths and SHA256 values
- NIAH validation result
- failures, substitutions, or missing assets

Do not claim setup complete if any revision is moving, any expected hash differs,
or GitHub push authentication is unavailable. Stop and report the exact blocker.
