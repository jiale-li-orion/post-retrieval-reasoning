# Session Log: ATM-Bench Setup & Analysis

**Date:** 2026-06-10  
**Working Directory:** `/home/orion/research/agent_memory_paper/ATM-Bench`

---

## 1. Repository Cloning

- **Repo:** https://github.com/JingbiaoMei/ATM-Bench
- **Target:** `/home/orion/research/agent_memory_paper/ATM-Bench/`
- **Status:** ✅ Done

---

## 2. Documents Reviewed

| Document | Key Content |
|----------|-------------|
| `README.md` | Repo overview, leaderboard snapshots, experiment structure |
| `README_zh.md` | Chinese version |
| `docs/baseline.md` | 7 baseline definitions: Oracle, MMRAG, HippoRAG2, MemoryOS, A-Mem, mem0, MemPalace, NIAH. Design rationale, CLI flags |
| `docs/data.md` | Data layout, schemas for QA/email/batch_results |
| `docs/niah.md` | NIAH protocol: how niah_evidence_ids is constructed |
| arXiv 2603.01990 (PDF) | Full paper, Table 3/4/5, Section 5 Experiments, Appendix |

---

## 3. Experiment Structure Analysis (3 rounds of refinement)

### Round 1: Initial tree
- Mixed data from paper `[P]`, README `[R]`, and runnable scripts `[S]` without labeling
- Called it "7 systems" when it's actually system families + variant rows

### Round 2: Correction by user (GPT judgment)
Key issues identified:
- Separate `[P]` / `[R]` / `[S]` sources
- Qwen3-VL-2B is memory processor (not 8B)
- SGM vs Raw need separate context depths in NIAH
- MemoryOS/MemPalace/SimpleMem are README additions, not in paper
- General-purpose agents are separate experiment group
- Fix A-Mem Piled encoding time claim

### Round 3: Final calibrated tree
- 5-layer diagnostic structure: Oracle → NIAH → Retrieval/RAG → Full System → General Agent
- Each node labeled with source `[P]` / `[R]` / `[S]`
- Separated Paper Table 3 vs README snapshot vs runnable scripts

**Key discrepancy found:**
- Paper ATM-RAG Hard QS = 16.3 (with raw visual inputs)
- README ATM-RAG Hard QS = 8.4 (with batch_results text-only, different release set)
- Difference explained by: `--media-source` flag, different dataset release version, FP8 quantization

---

## 4. Multimodal Necessity Analysis

Three categories identified:

| Category | Paths | Source |
|----------|-------|--------|
| 🔴 **Must be multimodal** | Memory Processor (Qwen3-VL-2B), Oracle Raw, NIAH Raw, w/o SGM agents | Raw images/video in input |
| 🟡 **Conditionally multimodal** | Paper Table 3 (paper=yes, scripts default=no), MMRAG, A-Mem raw mode | Controlled by `--media-source` flag |
| 🟢 **Text-only** | Oracle SGM, NIAH SGM, all baseline scripts default, text retrievers | `--media-source batch_results` |

---

## 5. Data Download (HuggingFace: `Jingbiao/ATM-Bench`)

| File | Size | Status |
|------|------|--------|
| `data/atm-bench/atm-bench.json` | 312 KB | ✅ (1,013 QA) |
| `data/atm-bench/atm-bench-hard.json` | 21 KB | ✅ (31 QA) |
| `data/atm-bench/niah/*.json` (k=25,50,100,200) | ~16 KB each | ✅ (all 4 files) |
| `data/raw_memory/email/emails.json` | 4.9 MB | ✅ (6,742 emails) |
| `data/raw_memory/geocoding_cache/image/*.json` | — | ✅ (GPS cache) |
| `output/image/qwen3vl2b/batch_results.json` | 27 MB | ✅ (3,759 items) |
| `output/video/qwen3vl2b/batch_results.json` | 1.7 MB | ✅ (533 items) |
| `data/raw_memory/image/` | ~2.3 GB | ⏳ Not downloaded (leave for lab machine) |
| `data/raw_memory/video/` | ~700 MB | ⏳ Not downloaded |

### Data Validation
```
ATM-Bench:       1,013 QA  (open_end:514, number:360, list_recall:139)
ATM-Bench-Hard:  31 QA     (open_end:13, number:6, list_recall:12)
NIAH pools:      4 files, all with niah_evidence_ids
```

> Note: Paper says 1,038 QA. Release has 1,013. Use release count.

---

## 6. Hardware Setup Plan

| Machine | GPU | VRAM | Role |
|---------|-----|------|------|
| Local (this machine) | RTX 5050 | 8 GB | Data exploration, evaluation, script orchestration |
| Lab server | RTX 4090 | 24 GB | vLLM serving Qwen3-VL-8B-Instruct-FP8 |

Connection: `VLLM_ENDPOINT=http://<lab-ip>:8000/v1/chat/completions`

---

## 7. Pending Tasks

- [ ] Download raw images/videos on lab machine
- [ ] Install dependencies (conda + pip) on lab machine
- [ ] Start vLLM on lab machine (Qwen3-VL-8B-Instruct-FP8)
- [ ] Run text-only experiments locally (MMRAG batch_results)
- [ ] Run raw-mode experiments on lab machine
