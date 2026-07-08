# ATM-Bench 受控证据使用实验协议

版本：2026-07-05  
状态：Oracle 与 NIAH 协议已确定；误差分析另行制定

## 1. 总体目标

本实验研究的不是检索器能否找到证据，而是：当评测系统已经控制证据来源后，answerer 能否利用给定证据完成回答，以及 query-conditioned Verbal Annotation 是否改善这种 post-access evidence use。

实验分为三部分：

1. **Oracle evidence**：只提供数据集标注的标准证据，隔离检索失败；
2. **Needle In A Haystack (NIAH)**：在标准证据中混入固定数量的干扰记忆项，考察长证据视图下的证据使用；
3. **误差机制分析**：后续独立实验；基于前两组结果另行制定协议。

前两组实验统一比较：

$$
\text{controlled SGM evidence}
\rightarrow
\begin{cases}
\text{ATM-Bench 已报告的 SGM-only answer}\\
\text{SGM + query-conditioned Verbal Annotation answer}
\end{cases}
$$

新增实验只运行 `SGM + Verbal Annotation`。ATM-Bench 已报告的 SGM-only 结果作为 baseline，不重复运行。本文不优化 retrieval、reranking 或 top-$k$，也不训练 Verbal-R3 generator。

## 2. ATM-Bench 评测对象

### 2.1 数据划分

ATM-Bench 只使用以下两个数据 split：

| Split | 路径 | 题数 | Question type 分布 | SHA256 |
|---|---|---:|---|---|
| Full | `ATM-Bench/data/atm-bench/atm-bench.json` | 1013 | open_end 514；number 360；list_recall 139 | `ab6eaa9df62fb4162e0f5eecd98768a7e3ae721e32d2db2cf227ff41e3295762` |
| Hard | `ATM-Bench/data/atm-bench/atm-bench-hard.json` | 31 | open_end 13；number 6；list_recall 12 | `acd35f2a172a9741d970d2cf21184ff0af8d79a8bf59967fc8aa33d619f6af4a` |

Oracle 与 NIAH 是评测条件，不是新的数据 split。二者均从数据集的 ground-truth `evidence_ids` 构造受控输入。

### 2.2 证据表示

主实验使用 ATM-Bench 的 Schema-Guided Memory (SGM)：

```text
type,timestamp,location,short_caption,caption,ocr,tags
```

固定输入：

| 输入 | 路径 | SHA256 |
|---|---|---|
| Image SGM | `ATM-Bench/output/image/qwen3vl2b/batch_results.json` | `7204e8b4ab1a0fea97f2003058213742d47589e09636941f8d83b2e77c33e0a1` |
| Video SGM | `ATM-Bench/output/video/qwen3vl2b/batch_results.json` | `88ed14ce32afde1a4d54d5b77a0e7f84305b543186307be6c9bc34119342727a` |
| Email evidence | `ATM-Bench/data/raw_memory/email/emails.json` | `5c82c38e7f18923a9eba3af321663a8a5bd70e94e0d5e59e987141c71219a8af` |

Raw 表示可能保留更多原始信息，但其载荷和上下文成本随干扰项增加而迅速上升。ATM-Bench 已通过 Raw/SGM 对比研究这一 trade-off。本实验不运行 `Raw + Verbal Annotation`；Raw 只用于已有结果引用和 failure analysis。

DM 不进入实验。公开实现没有提供可独立复现的 DM 实验路径，相关比较按 ATM-Bench 实际实现解释为 Raw 对照。

### 2.3 官方回答提示

System prompt：

```text
You are a QA assistant. Use ONLY the provided evidence to answer. If the evidence is insufficient, answer 'Unknown'. Respond with only the answer. If the question asks to recall or list items (photos/emails/videos), respond with the corresponding evidence IDs only, comma-separated, with no extra text.
```

User prompt：

```text
Question: {question}

Evidence:
{evidence}

Provide the answer based solely on the evidence.
```

Verbal Annotation 只能附加在对应 evidence item 内。除 annotation block 外，不修改 ATM-Bench 的问题、提示词、证据顺序或答案格式要求。

### 2.4 评测指标

ATM/QS 是按 question type 选择评分函数后的汇总分数：

| Question type | 评分方式 |
|---|---|
| `number` | Exact Match |
| `list_recall` | 归一化 Jaccard similarity |
| `open_end` | `gpt-5-mini` LLM judge |

Open-end judge 固定使用：

- ATM-Bench 官方 `LLM_JUDGE_PROMPT`；
- `gpt-5-mini`；
- `reasoning_effort=minimal`；
- 主 judge 连续失败三次后使用官方 `gpt-4o-mini` fallback，并逐题记录。

不得用 LLM judge 替代 number EM 或 list_recall Jaccard。

### 2.5 固定源码版本

| 组件 | 版本 |
|---|---|
| ATM-Bench | commit `3a1a606b872c4502e5efc632dcd1c076a220ed4a` |
| Verbal-R3 | commit `62c88a67c13d05cafbc5b7dbbd9ebe436d1d4e92` |
| Verbal Reranker 3B | `0k9d0h1/reranker3b-sft`，revision `cdf46c85892ebb715cbd6a0b582af35ad5caa96b` |

本地 ATM-Bench 对 Oracle answerer 和 evaluator 的 API 兼容性修改必须记录在 manifest 中。不得修改数据构造、官方 prompt 或评分逻辑。

## 3. 实验一：Oracle Evidence

### 3.1 研究问题

在只给出 ground-truth evidence 的条件下，Verbal Annotation 是否提高 answerer 对 SGM evidence 的使用能力？

Oracle 排除了检索遗漏和干扰项选择错误。该条件下的失败主要用于观察 evidence view 与 answerer 之间的 post-access gap。

### 3.2 模型范围

Oracle 阶段使用四个模型：

1. `Qwen3-VL-2B-Instruct`；
2. `Qwen3-VL-8B-Instruct`；
3. `MiMo V2.5`；
4. `MiniMax M3`。



### 3.3 输入构造

对每道题：

1. 读取数据集标注的 `evidence_ids`；
2. 按数据集原始顺序读取对应 SGM items；
3. 不加入额外干扰项，不重新排序，不筛选，不截断；
4. 对每个 SGM item 生成 query-conditioned annotation；
5. 保留原始 SGM item，并附加 annotation；
6. 使用 ATM-Bench 官方 Oracle prompt 调用 answerer。

形式化表示为：

$$
\text{Oracle SGM evidence}
\rightarrow
\begin{cases}
\text{published SGM baseline}\\
\text{SGM + Verbal Annotation}
\end{cases}
$$

### 3.4 运行矩阵

| Split | Qwen3-VL-2B | Qwen3-VL-8B | MiMo V2.5 | MiniMax M3 |
|---|---|---|---|---|
| Hard | SGM+VA | SGM+VA | SGM+VA | SGM+VA |
| Full | SGM+VA | SGM+VA | SGM+VA | SGM+VA |

运行顺序：先完成 Hard；确认数据、annotation、answer 和 judge 均有效后，再运行 Full。

### 3.5 Baseline 使用规则

SGM-only baseline 复用 ATM-Bench 已有结果，不同期重跑。报告时必须为每个 baseline 标注来源：paper、官方 leaderboard 或本地已有正式输出。

不同来源的模型 alias、服务版本或隐藏解码参数无法完全恢复时，应在实验限制中披露，但不因此重新运行 baseline。

## 4. 实验二：Needle In A Haystack

### 4.1 研究问题

当 ground-truth evidence 仍然存在、但 evidence view 中加入大量干扰记忆项时，Verbal Annotation 是否提高 answerer 定位并使用支撑证据的能力？这种效果是否随 evidence load 增长而变化？

NIAH 仍然不是传统 retrieval 实验。干扰集合由 benchmark 构造，实验不训练或替换检索器，也不调整 top-$k$。它控制 evidence availability，同时改变 answerer 面前的证据负载。

### 4.2 模型范围

NIAH 阶段使用四个模型：

1. `Qwen3-VL-8B-Instruct`；
2. `MiMo V2.5`；
3. `MiniMax M3`；
4. `Kimi K2.5`。

不在 NIAH 阶段运行 Qwen3-VL-2B-Instruct。

### 4.3 干扰规模

每道题的 ground-truth evidence 被混入：

$$
k \in \{25,50,100,200\}
$$

个干扰 memory items。必须复用 ATM-Bench 已生成的 NIAH 标注数据或官方构造脚本的固定输出；不得为实验组重新采样干扰项。

在相同模型和 $k$ 下，新增结果与 ATM-Bench 已报告的 SGM-only baseline 使用相同题目、ground-truth evidence、干扰集合及顺序。若官方产物不能恢复某个条件的具体干扰集合，该条件只能与官方 aggregate baseline 比较，不能开展逐题 transition 分析。

### 4.4 运行矩阵

| NIAH 条件 | Qwen3-VL-8B | MiMo V2.5 | MiniMax M3 | Kimi K2.5 |
|---|---|---|---|---|
| NIAH-25 | SGM+VA | SGM+VA | SGM+VA | SGM+VA |
| NIAH-50 | SGM+VA | SGM+VA | SGM+VA | SGM+VA |
| NIAH-100 | SGM+VA | SGM+VA | SGM+VA | SGM+VA |
| NIAH-200 | SGM+VA | SGM+VA | SGM+VA | SGM+VA |

NIAH 主表使用 ATM-Bench-Hard。只有在官方 Full NIAH 数据与 baseline 均可验证时，才增加 Full 结果；不得把 Hard 和 Full 混在同一列比较。

### 4.5 官方 Hard-SGM Baseline

以下数值来自 ATM-Bench Live Leaderboard（2026-07-05），直接作为 SGM-only baseline：

| Model | Oracle | NIAH-25 | NIAH-50 | NIAH-100 | NIAH-200 |
|---|---:|---:|---:|---:|---:|
| MiniMax M3 | 60.5 | 45.9 | 55.1 | 43.4 | 50.6 |
| Kimi K2.5 | 44.5 | 47.9 | 39.6 | 33.5 | 37.7 |
| MiMo V2.5 | 44.6 | 39.1 | 34.5 | 31.8 | 26.8 |
| Qwen3-VL-8B-Instruct | 28.0 | 16.3 | 15.8 | 12.7 | 未报告 |

来源：<https://atmbench.github.io/leaderboard.html>。

Qwen3-VL-8B 的 NIAH-200 没有官方 baseline，不计算该格的 VA improvement；可以报告新增绝对分数，但必须标记为“无可比 baseline”。

### 4.6 Raw 结果的角色

Raw baseline 只用于说明 SGM 的表示与预算 trade-off：Oracle 条件下 Raw 可能更强，但随着干扰项和载荷增加，Raw 会退化或因上下文限制失败。该现象不构成本实验的干预变量。

本阶段不运行：

- Raw + Verbal Annotation；
- SGM + image/video source；
- annotation 后按需读取 Raw；
- 新的 retrieval 或 reranking 方法。

按需 source inspection 可作为后续扩展，用于研究系统能否在判断 SGM 信息不足后，在预算内回读原始模态。

## 5. Verbal Annotation 干预合同

### 5.1 干预定义

主实验使用 Verbal-R3 的 train-free Verbal Reranker 生成 query-conditioned annotation。它不是完整 Verbal-R3 pipeline，也不改变 evidence selection。

固定配置：

运行时配置以 `configs/verbal_r3_official.json` 为单一事实源；下表是该文件的论文侧说明，不在 Bash 或 Python 中另设默认值。

| 项目 | 决定 |
|---|---|
| Annotation model | `0k9d0h1/reranker3b-sft` |
| Checkpoint revision | `cdf46c85892ebb715cbd6a0b582af35ad5caa96b` |
| Prompt | `VerbalR3/utils/reranker_server.py` 中的 server prompt，逐字复用 |
| Evidence 接入 | 保留原始 SGM，附加 verbal `comment` 和 relevance `score` |
| Temperature | `0.6` |
| Top-p | `0.95` |
| Max new tokens | `1024` |
| Seed | `0` |
| Parse failure | 重试；达到上限后终止对应 run |

模型与参数依据：论文 Section 5.1/A1.3 固定使用 3B Verbal Reranker，并规定 reranker inference 使用 temperature 0.6、top-p 0.95；官方 `scripts/serving.sh` 将最大输出设为 1024。Prompt 以固定 commit 中实际执行的 `reranker_server.py` 为准。

Reranker system prompt 固定为：

```text
You are an evaluator that judges how informative a document is for answering a given question. You will receive a Question and a Document.

Carefully assess relevance and usefulness (reason internally), then output only a score and a brief, evidence-based comment that supports downstream filtering (mention concrete entities/claims/dates/metrics when helpful).

Scoring rubric (1-5):
1 — Unrelated: The document has nothing to do with the question. It does not contain any potentially relevant information or an answer to the question.
2 — Loosely related: Contains information that might potentially help or include the answer to the question, but is unlikely to do so.
3 — Partially informative: Contains information that can potentially help answer the question in some way.
4 — Substantively informative: Related to the question and includes information that is relevant to it.
5 — Direct answer: Clearly related and includes key information that can be used to directly answer the question.

Output format (exactly):
Comment: <concise justification citing specific evidence from the document; e.g., “Since the document states A and B, it is relevant to the question about C.”>
Score: <1-5>
```

Reranker 原始输出仍按官方格式解析：

```text
Comment: {comment}
Score: {score}
```

论文 Section 4.2 将 verbal annotation 与 relevance score 一并加入 Generator context。本实验保持每个 SGM item 原文不变，并在末尾追加：

```text
Verbal Annotation: {comment}
Relevance score: {score}
```

本实验只移植该 evidence presentation，不移植论文的 top-$k$ reranking：`score` 不用于筛选、删除或重排，所有 evidence items 均按 ATM 原顺序进入 answer prompt。

### 5.2 Answerer 配置

| 项目 | 决定 |
|---|---|
| Thinking/reasoning | 使用默认非 thinking 模式；MiMo 请求不传 `thinking` 字段 |
| Temperature | `0.2` |
| Max output tokens | `1000` |
| Prompt | ATM-Bench 官方 Oracle/NIAH answer prompt |
| Answer format | 沿用 ATM-Bench 要求 |

若 provider 不支持某参数，manifest 必须记录“unsupported”，不得静默换成其他值。API alias、请求 model identifier 和响应中的实际 model identifier 均须保存。

### 5.3 Token 与成本

每个请求至少记录：

- annotation prompt tokens；
- annotation completion tokens；
- answerer prompt tokens；
- answerer completion tokens；
- cache tokens（若 API 返回）；
- annotation 和 answerer 各自延迟；
- 单题与整组估算成本；
- provider 未返回 usage 时采用的 tokenizer 与估算方法。

成本报告必须将 annotation 开销与 answerer 开销分开，不只报告总 token。

## 6. 实验三：误差机制分析（后续实验）

本实验待办。Oracle 和 NIAH 结果完成后，再根据实际 failure cases 与论文中的误差假设制定独立协议。目前不预设分类、方法或统计结论。

为支持后续分析，前两项实验保留逐题 question、qtype、evidence、annotation、answer、分项得分和 token 记录。

## 7. 结果记录

### 7.1 Annotation 输出

`annotations.jsonl` 每行对应一个 evidence item，必须包含：

```json
{
  "qa_id": "...",
  "evidence_id": "...",
  "evidence_index": 0,
  "question": "...",
  "sgm_text": "...",
  "raw_output": "...",
  "comment": "...",
  "score": 0,
  "parse_ok": true,
  "retry_count": 0,
  "prompt_tokens": 0,
  "completion_tokens": 0,
  "total_tokens": 0,
  "latency_ms": 0,
  "model": "...",
  "checkpoint_revision": "..."
}
```

`sgm_text` 保存 annotation 之前的原始 evidence chunk，用于验证实验没有改写或遗漏 SGM。解析失败不得写入伪造的空 comment 或 `score=0` 后继续运行；达到重试上限后该 run 失败。

### 7.2 Answerer 输出

`predictions.jsonl` 每行对应一道 QA，必须包含：

```json
{
  "qa_id": "...",
  "qtype": "number|list_recall|open_end",
  "evidence_ids": ["..."],
  "answer": "...",
  "prompt_tokens": 0,
  "completion_tokens": 0,
  "reasoning_tokens": 0,
  "cached_tokens": 0,
  "total_tokens": 0,
  "latency_ms": 0,
  "requested_model": "...",
  "returned_model": "..."
}
```

MiMo 请求中不出现 `thinking` 字段。若 API 不返回某类 usage，则对应字段写 `null`，不得写成 0；同时在 manifest 中记录 token 估算方法或“不可获得”。

### 7.3 汇总输出

每个模型和实验条件生成 `run_stats.json`，分别汇总：

- annotation prompt、completion、total tokens；
- answerer prompt、completion、reasoning、cached、total tokens；
- annotation 与 answerer 的调用次数、平均延迟和总延迟；
- API retry、annotation parse failure 和 judge fallback 次数；
- ATM/QS、number EM、list_recall Jaccard 和 open_end judge score；
- 按题型分组的题数与得分。

Oracle 与 NIAH 分别报告 SGM baseline、SGM+VA 和绝对差值；NIAH 另按 $k$ 分列。只有取得逐题 baseline 输出时才做 paired transition 分析。
