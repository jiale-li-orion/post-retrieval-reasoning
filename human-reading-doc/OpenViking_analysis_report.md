# OpenViking 源码分析报告：基于类型化访问模型的长时程智能体记忆系统


---

## 一、概述

OpenViking 是字节跳动开源的一个"面向 AI Agent 的上下文数据库"（Context Database），其核心设计理念是将 Agent 所需的记忆（memory）、资源（resource）和技能（skill）统一管理在一个虚拟文件系统中。本文按我们论文的分析框架，将其定位为长时程智能体记忆系统的一个实例，重点分析其运行时访问层（runtime access layer）的实现。

| 论文概念 | OpenViking 实现位置 | 核心文件 |
|---------|-------------------|---------|
| 工件存储（$\mathcal{A}$） | `viking://` 虚拟文件系统 | `storage/viking_fs.py` (2896行) |
| 工件类型（artifact types） | ContextType (memory/resource/skill) + 11种YAML结构化记忆 schema | `openviking_cli/retrieve/types.py:14-19` |
| 访问原语（P） | retrieve, read, browse, commit, add, remove, grep, glob | `hierarchical_retriever.py`, `viking_fs.py`, `sync_client.py` |
| 原语轨迹（primitive trace） | IntentAnalyzer → QueryPlan → HierarchicalRetriever.retrieve | `retrieve/intent_analyzer.py:176行` |
| 决策视图（v） | L0/L1/L2 分层上下文 + MatchedContext 聚合 | `viking_fs.py:1543-1562` |
| 解码器使用 | OpenCode 插件 autoRecall + chat.message hook | `examples/opencode-plugin/lib/memory-recall.mjs` |
| 诊断追溯 | ThinkingTrace + observer queue | `retrieve/types.py:130-233` |

---

## 二、工件存储层（Artifact Store）：类型化工件与虚拟文件系统

### 2.1 `viking://` 虚拟文件系统

OpenViking 用 RAGFS（Rust 实现的虚拟文件系统）将记忆、资源、技能映射为 `viking://` URI 下的目录树。核心实现在：

**Rust 层：** `crates/ragfs/src/core/mountable.rs` — `MountableFS` 使用 radix-trie 进行 URI 路由，支持 7 个 plugin 注册（localfs, vikingdb, memfs, logfs, configfs, redis, tempfs）。

**Python 层：** `storage/viking_fs.py:2896` — `VikingFS` 是核心抽象层，负责：
- URI 到向量存储的映射（`viking://user/{id}/memories/` → vector collection）
- L0（abstract）/ L1（overview）文本的生成与维护
- 关系链接（link/relate）管理
- 权限控制（`_ensure_access`）

**URI 路由机制：** RAGFS 的 `MountableFS`（`crates/ragfs/src/core/mountable.rs:591-627`）使用 radix-trie 进行最长前缀匹配来路由 URI：

```rust
// mountable.rs:591-627 — find_mount 核心路由算法
async fn find_mount(&self, path: &str) -> Result<(MountInfo, String)> {
    // 1. 精确匹配
    if let Some(mount_info) = mounts.get(&normalized_path) {
        return Ok((mount_info.clone(), "/".to_string()));
    }
    // 2. 最长前缀匹配：逐级回溯直到 /
    loop {
        if let Some(mount_info) = mounts.get(current) {
            let relative_path = normalized_path[current.len()..].to_string();
            return Ok((mount_info.clone(), relative_path));
        }
        if current == "/" { break; }
        current = &current[..current.rfind('/').unwrap_or(0)];  // 回溯
    }
    Err(Error::MountPointNotFound(normalized_path))
}
```

`read_dir`（即 `ls`）的实现直接委托给底层文件系统（`localfs/mod.rs:688-727`），每项返回 `FileInfo { name, size, mode, mod_time, is_dir }`。`grep` 有双路径：有 `rg` 则调用 ripgrep（`localfs/mod.rs:828-849`），否则使用 Rust `grep` crate 内存 grep。

```python
# viking_fs.py:63-72 — VikingFS 类定义
class VikingFS:
    def __init__(self, workspace: str, ...):
        self._workspace = workspace      # 物理存储路径
        self._embedder = embedder         # 向量嵌入器
        self._vector_store = vector_store # 向量数据库
        self._obs = obs                   # 观察者队列
```

### 2.2 三类工件：memory / resource / skill

OpenViking 定义了三种抽象工件类型（`openviking_cli/retrieve/types.py:14-19`）：

```python
class ContextType(str, Enum):
    MEMORY = "memory"     # 用户/Agent 记忆
    RESOURCE = "resource" # 知识资源（文档、代码、网页）
    SKILL = "skill"       # 可执行技能/工具
```

对应的目录结构：
```
viking://
├── user/{user_id}/
│   ├── memories/         # → ContextType.MEMORY
│   │   ├── identity.md   # Agent 身份
│   │   ├── preferences/  # 用户偏好
│   │   ├── events/       # 事件记忆
│   │   ├── experiences/  # Agent 经验记忆
│   │   ├── tools/        # 工具使用模式
│   │   └── ...
│   ├── resources/        # 用户私有资源
│   └── skills/           # 用户私有技能
├── resources/            # → ContextType.RESOURCE（共享知识）
└── skills/               # → ContextType.SKILL（共享技能）
```

**关键设计：** 每种工件类型有不同的使用语义，这直接影响了后续的访问策略。Memory 按会话提取，Resource 按文档建立索引，Skill 按可执行能力建模。

### 2.3 结构化记忆类型系统：11 种 YAML 驱动的记忆 Schema

OpenViking 实现了 Schema-Guided Memory，每种记忆类型有明确的结构化 schema，定义在 YAML 中。11 种记忆类型包括：

| 记忆类型 | YAML 文件 | 存放位置 | 用途 |
|---------|----------|---------|------|
| identity | `identity.yaml` | `memories/identity.md` | Agent 身份、名称、性格 |
| soul | `soul.yaml` | `memories/soul.md` | Agent 核心信条、边界 |
| profile | `profile.yaml` | `memories/profile.md` | 用户画像 |
| preferences | `preferences.yaml` | `memories/preferences/` | 用户偏好设置 |
| entities | `entities.yaml` | `memories/entities/` | 实体关系记忆 |
| events | `events.yaml` | `memories/events/` | 事件记忆（结构化） |
| experiences | `experiences.yaml` | `memories/experiences/` | Agent 任务执行经验 |
| tools | `tools.yaml` | `memories/tools/` | 工具使用模式与成功率 |
| skills | `skills.yaml` | `memories/skills/` | 技能学习记录 |
| trajectories | `trajectories.yaml` | — | 结构化操作轨迹 |
| experimental_memory | 目录 | — | 实验性记忆类型 |

每种 schema 定义了：
- **字段**（fields）：含 `name`, `type`, `description`, `merge_op`, `init_value`
- **合并策略**（merge_op）：`immutable`（不可变）、`patch`（文本追加/覆盖）、`sum`（数值累加）、`replace`（替换）
- **内容模板**（content_template）：Jinja2 模板生成的 Markdown 文件

例如 `tools.yaml` 的 schema 片段（`prompts/templates/memory/tools.yaml`）：

```yaml
fields:
  - name: tool_name
    type: string
    merge_op: immutable     # 工具名称不可修改

  - name: call_count
    type: int64
    merge_op: sum           # 调用次数累加

  - name: when_to_use
    type: string
    merge_op: patch         # 使用提示可增量更新

  - name: success_time
    type: int64
    merge_op: sum           # 成功次数累加
```

这相对于 Descriptive Memory（DM，即纯自由文本记忆）的最大区别是：DM 将记忆视为自由文本，OpenViking 将记忆视为**可合并的结构化记录**，每个字段有指定的类型和合并策略，允许字段级别的更新、累加和补丁。

### 2.4 记忆生命周期（Memory Lifecycle）

记忆的热度管理在 `retrieve/memory_lifecycle.py:64`：

```python
def hotness_score(active_count, updated_at, half_life_days=7.0):
    freq = sigmoid(log1p(active_count))        # 频率：访问越多越热
    recency = exp(-decay_rate * age_days)       # 新鲜度：越新越热
    return freq * recency                        # [0, 1]
```

在 `_convert_to_matched_contexts`（`hierarchical_retriever.py:565`）中混合：

```python
final_score = (1 - alpha) * semantic_score + alpha * hotness_score
```

---

## 三、访问原语层（Access Primitives）：超越单一检索接口

OpenViking 的关键设计贡献是**没有将所有内存访问简化为 top-k 检索**。它通过三种渠道暴露了多种访问原语：

### 3.1 核心访问原语

**A. `retrieve` — 语义检索（层次化递归检索）**

实现在 `hierarchical_retriever.py:92-239`。核心步骤：

1. **全局向量搜索**（`_global_vector_search:241-264`）→ 定位高分目录
2. **合并起始点**（`_merge_starting_points:298-339`）→ 目录路径 + 全局 top-k
3. **递归搜索**（`_recursive_search:367-543`）→ 优先队列驱动的目录遍历
4. **分数传播**：`final_score = α × child_score + (1-α) × parent_score`
5. **收敛检查**：连续 3 轮 top-k 不变则停止

```python
# hierarchical_retriever.py:484-488 — 分数传播
for r, score in zip(results, query_scores, strict=True):
    uri = r.get("uri", "")
    final_score = (
        alpha * score + (1 - alpha) * current_score
        if current_score else score
    )
```

**B. `read` — 分层读取（L0/L1/L2）**

打开 `viking://` URI 时，按需加载不同层次的内容：

- **L0 (abstract)**：约 100 tokens 的一句话摘要
- **L1 (overview)**：约 2k tokens 的结构化概览
- **L2 (details)**：完整原始数据

URI 后缀：`.abstract.md` (L0)、`.overview.md` (L1)。由 `_append_level_suffix`（`hierarchical_retriever.py:608-620`）自动附加。

**C. `browse` — 目录浏览与遍历**

类似于文件系统的 `ls` / `tree` 操作，在 OpenViking CLI 中：
```bash
ov ls viking://resources/           # 列出资源目录
ov tree viking://resources/ -L 2    # 树状展示
```

**D. `commit` — 会话提交与记忆提取**

将当前会话的消息、工具调用、结果异步提交到 OpenViking，触发背景记忆提取。`session/session.py:1067-1631`。

**E. `add` / `remove` — 资源管理**

添加 URL 或本地文件到 `viking://resources/`，或删除指定 URI。在 `sync_client.py` 和 OpenCode 插件中暴露。

**F. `grep` / `glob` — 模式匹配**

在 OpenViking 索引内容中进行正则/glob 模式搜索，对应 Rust 层 `ragfs` 的 grep 能力。

### 3.2 OpenCode 插件中的工具暴露

在 OpenCode 插件中，这些原语被暴露为显式工具。**11 个工具** 由 `index.mjs:47` 的 `tool` hook 注册（`lib/memory-tools.mjs:16-289`），每个工具精确映射到一个 HTTP API 端点：

| 工具 | 参数 | HTTP API | 代码位置 |
|------|------|----------|---------|
| `memsearch` | query, target_uri, mode, limit, score_threshold | `POST /api/v1/search/find` 或 `/search/search` (mode="deep") | `memory-tools.mjs:16-55` |
| `memread` | uri, level (auto/abstract/overview/read) | `GET /api/v1/content/{level}` | `memory-tools.mjs:57-86` |
| `membrowse` | uri, view (list/tree/stat), recursive | `GET /api/v1/fs/{ls\|tree\|stat}` | `memory-tools.mjs:88-124` |
| `memcommit` | session_id | `POST /api/v1/sessions/{id}/commit` | `memory-tools.mjs:126-149` |
| `memgrep` | pattern, uri, case_insensitive | `POST /api/v1/search/grep` | `memory-tools.mjs:151-184` |
| `memglob` | pattern, uri, node_limit | `POST /api/v1/search/glob` | `memory-tools.mjs:186-215` |
| `memadd` | path, to/parent, reason, wait | `POST /api/v1/resources` (+ temp_upload for local files) | `memory-tools.mjs:217-245` |
| `memremove` | uri, recursive, confirm=true | `DELETE /api/v1/fs` | `memory-tools.mjs:247-275` |
| `memqueue` | (none) | `GET /api/v1/observer/queue` | `memory-tools.mjs:277-289` |
| `codesearch` | query, uri | `POST /api/v1/code/search` | `code-tools.mjs:29` |
| `codeoutline` | uri | `POST /api/v1/code/outline` | `code-tools.mjs:65` |

**会话生命周期同步**（`lib/memory-session.mjs:651`）：插件在 `event` hook（`index.mjs:40-45`）中捕获 OpenCode 的 `session.created`、`session.deleted`、`session.error` 事件，自动映射 OpenCode session → `POST /api/v1/sessions` 创建 OpenViking session。消息通过 `message.part.updated` hook 增量捕获到 `pendingMessages` Map，最终调用 `POST /api/v1/sessions/{id}/messages` 批量发送。插件关闭时通过 `stop` hook 触发 `flushAll({ commit: true })`。

### 3.3 与单一检索接口的对比

论文主张记忆访问不应被简化为单一 top-k 检索原语。下表展示了 OpenViking 如何实例化论文的论点：

| 工件类型 | 使用语义 | OpenViking 访问方式 | 对应的原语 |
|---------|---------|-------------------|----------|
| memory | 查询当前约束/偏好/经验 | `memsearch(target_uri="viking://user/memories/")` + `memread` | retrieve + read |
| resource | 理解知识/概念 | `memsearch(target_uri="viking://resources/")` + `memread(level="auto")` | retrieve + read |
| skill | 调用/执行 | `membrowse` 定位 → `memread` 读取 | browse + read |
| workspace state | 编辑/验证 | `memadd` 写入 → `memsearch` 验证 | add + retrieve |
| session | 提交/压缩 | `memcommit` + 背景压缩 | commit |

---

## 四、意图解析与 Query 构造管道

这是 OpenViking 运行时访问的核心引擎，实现了论文中的「意图 → 访问程序」映射（$q = \mathcal{C}(u, c, \mathcal{A})$）。

### 4.1 整体管道

```
用户查询 u (viking_fs.py:1434-1562 search())
  │
  ├─ 有会话上下文？
  │   YES → IntentAnalyzer.analyze()
  │   │    ├─ 输入: compression_summary + recent_messages + current_message + target_abstract
  │   │    ├─ 调用 LLM (query_planner)
  │   │    └─ 输出: QueryPlan (多个 TypedQuery)
  │   │
  │   NO  → 直接创建单一 TypedQuery
  │
  └─ asyncio.gather() 并发执行所有 TypedQuery
       └─ HierarchicalRetriever.retrieve() × N
            └─ 聚合为 FindResult
```

### 4.2 IntentAnalyzer 实现

**文件位置：** `retrieve/intent_analyzer.py:38-176`

```python
class IntentAnalyzer:
    MAX_COMPRESSION_SUMMARY_CHARS = 30000  # 压缩摘要上限
    
    def __init__(self, max_recent_messages: int = 5):
        self.max_recent_messages = max_recent_messages
    
    async def analyze(
        self,
        compression_summary: str,   # 会话压缩摘要
        messages: List[Message],    # 最近 N 条消息
        current_message: str,       # 当前用户消息
        target_abstract: str = "",  # 目标目录摘要
    ) -> QueryPlan:
```

**分析方法（来自 `intent_analysis.yaml:97-167` prompt 模板）：**

1. **Step 1: 识别任务类型**
   - 操作性任务（含动词：create, build, analyze）→ 需要 skill + resource + memory
   - 信息性任务（what is, how to）→ 需要 resource + memory
   - 对话性任务（闲聊）→ 通常不需要查询

2. **Step 2: 检查上下文覆盖**
   - 已完全覆盖 → 跳过
   - 部分覆盖 → 生成补充查询
   - 未覆盖 → 生成完整查询

3. **Step 3: 生成查询**
   - 最多 5 个 TypedQuery
   - 使用陈述句（非疑问句）以优化向量检索嵌入匹配
   - 去除检索元词（"find", "search", "records" 等）
   - 保留具体实体（名称、日期、地点）

**关键 prompt 指令（`intent_analysis.yaml:148-153`）：**

```yaml
# Query Style (optimize for vector / semantic retrieval):
# - Declarative, not interrogative
# - One information need per query
# - Self-contained: resolve pronouns using session context
# - Concept-dense and natural
# - No retrieval-meta words
# - Keep discriminative specifics
```

### 4.3 QueryPlan 输出格式

```python
# openviking_cli/retrieve/types.py:237-269
@dataclass
class TypedQuery:
    query: str                       # "Carter Stewart conference presentation September 2026"
    context_type: Optional[ContextType]  # ContextType.MEMORY
    intent: str                      # "Find Carter Stewart's conference presentations"
    priority: int = 3               # 1-5, 1=最高
    target_directories: List[str]    # ["viking://user/default/memories/"]

@dataclass
class QueryPlan:
    queries: List[TypedQuery]
    session_context: str             # 会话上下文摘要
    reasoning: str                   # LLM 推理过程
```

### 4.4 Query Planner 模型选择

支持两种模型后端（`intent_analyzer.py:24-35`）：

```python
# 轻量 SFT 模型（更快更省）：通过 model name 匹配
QUERY_PLANNER_PROMPT_BY_MODEL = {
    "ollama/guoxuter/ov_intent_analysis_sft:v7_q8": "retrieval.ov_intent_analysis_sft_v7",
    "ollama/guoxuter/ov_intent_analysis_sft:v4_q8": "retrieval.ov_intent_analysis_sft_v4",
}

# 默认：使用通用 VLM + 标准 prompt
DEFAULT_INTENT_ANALYSIS_PROMPT = "retrieval.intent_analysis"
```

---

## 五、层次化检索（Hierarchical Retrieval）

### 5.1 递归搜索算法

**文件位置：** `retrieve/hierarchical_retriever.py:367-543`

核心是一个**优先队列驱动的递归目录遍历**：

```python
# 伪代码
def recursive_search(starting_points):
    dir_queue = PriorityQueue()         # (-score, uri) 最大堆
    collected_by_uri = {}               # URI → 最佳候选（去重）
    
    for uri, score in starting_points:
        heapq.heappush(dir_queue, (-score, uri))
    
    while dir_queue and not_converged():
        batch = pop_top_k(dir_queue, MAX_PARALLEL=4)
        
        for uri, score in batch:
            children = search_children(uri)    # 向量检索子节点
            reranked = rerank(children)        # 重排序
            
            for child, child_score in zip(children, reranked):
                final_score = α*child_score + (1-α)*parent_score
                
                if final_score > threshold:
                    # 按 URI 去重，保留最高分
                    if child.uri not in collected or final_score > collected[child.uri]:
                        collected[child.uri] = child
                    
                    # L0/L1 目录递归进入，L2 文件作为终止命中
                    if child.level != 2:
                        heapq.heappush(dir_queue, (-final_score, child.uri))
        
        # 收敛检查
        if top_k_unchanged_for_3_rounds:
            break
```

**关键参数：**

| 参数 | 默认值 | 作用 |
|------|--------|------|
| `MAX_CONVERGENCE_ROUNDS` | 3 | 连续收敛轮数后停止 |
| `MAX_PARALLEL_CHILD_SEARCHES` | 4 | 每轮并行搜索的子目录数 |
| `GLOBAL_SEARCH_TOPK` | 10 | 全局检索的候选数 |
| `score_propagation_alpha` | 1.0 | 父→子分数传播权重 |
| `hotness_alpha` | 0.0（默认关闭） | 热度分数混合权重 |

### 5.2 分数传播机制

```python
# hierarchical_retriever.py:484-488
final_score = alpha * child_rerank_score + (1 - alpha) * parent_score
```

这使得子节点的排名受其所在目录的分数影响，当 `alpha=0` 时完全由父目录分数决定（广度优先），当 `alpha=1` 时完全由子节点自身分数决定（扁平向量检索）。

---

## 六、决策视图构造（Decision-facing View）

### 6.1 结果聚合为 FindResult

**文件位置：** `viking_fs.py:1541-1562`

多 TypedQuery 并发执行后，按 context_type 分类聚合：

```python
# VikingFS.search() — 聚合逻辑
query_results = await asyncio.gather(
    *[_execute(tq) for tq in typed_queries]
)

memories, resources, skills = [], [], []
for result in query_results:
    for ctx in result.matched_contexts:
        if ctx.context_type == ContextType.MEMORY:
            memories.append(ctx)
        elif ctx.context_type == ContextType.RESOURCE:
            resources.append(ctx)
        elif ctx.context_type == ContextType.SKILL:
            skills.append(ctx)

find_result = FindResult(
    memories=memories,
    resources=resources,
    skills=skills,
    query_plan=query_plan,         # 包含原始意图和推理过程
    query_results=query_results,   # 保留每个查询的详细结果
)
```

### 6.2 视图暴露的三种格式

**A. 完整 API 响应**（REST/MCP endpoint）

每个 `MatchedContext` 序列化为：
```json
{
    "context_type": "memory",
    "uri": "viking://user/default/memories/events/carter_stewart_presentation.md",
    "level": 2,
    "score": 0.85,
    "abstract": "Carter Stewart presented about statistical analysis at...",
    "overview": null,
    "category": "events",
    "match_reason": "",
    "relations": [{"uri": "...", "abstract": "..."}]
}
```

**B. MCP 格式化文本**（`mcp_endpoint.py:265-290`）：

```python
def _format_search_result(result):
    """格式化为 markdown 列表"""
    # 输出格式：
    # - [resource 85%] viking://resources/...
    #     abstract text
```

**C. OpenCode 插件 `<relevant-memories>` XML 块**（`examples/opencode-plugin/lib/memory-recall.mjs`）：

```xml
<relevant-memories>
  <memory uri="viking://user/default/memories/preferences/coding_style.md" 
          score="0.92" type="memory">
    User prefers tabs over spaces, 2-space indent for Python
  </memory>
</relevant-memories>
```

### 6.3 视图角色分析（View Roles）

对照论文的视图角色框架，OpenViking 的视图构造覆盖情况：

| 视图角色 | 是否暴露 | 实现位置 |
|---------|---------|---------|
| 证据可见性（evidence visibility） | ✅ | L0/L1/L2 分层 |
| 来源身份（source identity） | ✅ | `uri` 字段指向 `viking://` |
| 时间定位（temporal grounding） | ⚠️ 部分 | `updated_at` 参与 hotness 排序，但不在视图中显式展示 |
| 引用绑定（referential binding） | ❌ 不充分 | `relations` 字段存在但当前实现为空列表 |
| 聚合结构（aggregation） | ✅ | `memories/resources/skills` 分类，`query_plan` 保留原始意图 |
| 冲突权威（conflict authority） | ❌ 缺失 | 没有标记哪个记忆是最新的权威版本 |
| 时效性（freshness/recency） | ⚠️ 间接 | 通过 `hotness_alpha` 影响排序，不在视图中显式标注 |

**关键缺陷：** OpenViking 的视图构造大量依赖隐式排序（score + hotness）来表达信息优先级，但缺少显式的权威标记。模型收到排序后的列表，但不被告知哪个记忆是"当前有效的"还是"已过时的"。

---

## 七、会话记忆提取管道

### 7.1 会话生命周期

**文件位置：** `session/session.py:3419`

```python
class Session:
    def __init__(self, session_id, storage):
        self.id = session_id
        self._messages: List[Message] = []
        self._meta: Dict = {}          # 内存中的元数据
        self._archives: List[Dict] = [] # 压缩归档

    async def add_messages(self, messages):
        """添加消息（用户/助手/工具调用）"""
    
    async def commit(self, ...):
        """Phase 1: 序列化消息到文件存储"""
    
    async def _run_memory_extraction(self, ...):
        """Phase 2: LLM 驱动的记忆提取"""
```

会话的生命周期：`create → add_messages → commit → _run_memory_extraction → archive`

### 7.2 CompressorV2：记忆提取引擎

**文件位置：** `session/compressor_v2.py:1193`

**`SessionCompressorV2` 类**（`line 123`）仅保存两个字段：`vikingdb` 和 `skill_processor`。所有状态（providers, extract loops, updaters）每次提取调用新创建。

**主入口 `extract_long_term_memories()`**（`lines 222-476`）的精确流程：

```
1. Line 266: 创建 MemoryTypeRegistry（加载所有 YAML schema）
2. Line 269: 初始化默认记忆文件（soul.md, identity.md）
3. Line 304: 创建 SessionExtractContextProvider
4. Line 312: prepare_extraction_messages() — 图片→VLM描述
5. Line 313: get_extract_context() — 创建ExtractContext + PageIdMap
6. Line 325: 创建 ExtractLoop (ReAct编排器, max_iterations=3)
7. Line 380: orchestrator.run() — LLM驱动的提取循环
8. Line 386: MemoryUpdater.apply_operations() — 写回文件系统
```

**`extract_execution_memories()`**（`lines 478-662`）分两阶段：

```python
# Phase 1: 轨迹提取
AgentTrajectoryContextProvider → ExtractLoop.run() → 写入 trajectories/
# Phase 2: 经验整合（对每个新轨迹）
AgentExperienceContextProvider → ExtractLoop.run() → 写入 experiences/
```

**`_run_extract_phase()`**（`line 694`）是阶段提取的共享方法：创建 ExtractLoop → 获取锁 → orchestrator.run() → 拆分 memory/skill ops → updater.apply_operations() → supersedes 处理 → 释放锁。

### 7.3 ExtractLoop：ReAct 编排器

**文件位置：** `session/memory/extract_loop.py:41-303`

核心循环（`run()` method, `lines 99-303`）：

```
1. Line 116: 获取 memory schemas
2. Line 120: 构建 SchemaModelGenerator → JSON Schema（LLM输出格式约束）
3. Line 162: 构建 system message（instructions + JSON Schema + page_id规则）
4. Line 199: prefetch() — 搜索已有记忆 + 读取单文件 schema + 可选 eager-read
5. Line 205-290: 主 ReAct 循环（最多 max_iterations=3 轮）
   ├── _call_llm() → 返回 (tool_calls, operations)
   ├── 如果有 tool_calls → 并行执行 → 结果追加到 messages → 继续
   ├── 如果有 operations → 验证 URIs/page_ids → 检查未读文件 → 验证 SEARCH/REPLACE → break
   └── 如果两者都无 → 格式重试(1次) → 失败抛 RuntimeError
6. Line 301: finalize_operations() — 注册page_ids + 解析 WikiLinks
```

**`AgentExperienceContextProvider`** 的 prefetch（`agent_experience_context_provider.py:157-266`）特别精细：
1. 搜索候选经验（top-5）
2. 读取每个候选经验（`context_role="candidate_experience"`）
3. 对 top-3 候选，加载其 `derived_from` 轨迹（`context_role="candidate_source_trajectory"`）
4. 注入新轨迹（`context_role="new_trajectory"`）
5. **不给工具调用**（`get_tools()` 返回 `[]`），所有上下文预加载

### 7.4 合并策略（Merge Ops）与 MemoryUpdater

**MemoryUpdater.apply_operations()**（`memory_updater.py:698`）：

```
1. Line 726: 验证所有操作的 URIs 已解析
2. Line 739: 将 resolved links 分配给 upsert 操作
3. Line 742-762: 遍历 upsert → _apply_upsert(每个操作)
4. Line 768-781: 应用删除操作（跳过同一批次中已 upsert 的 URI）
5. Line 783: _sync_resource_refs_for_result() — 同步资源引用
6. Line 786: _vectorize_memories() — 入队向量嵌入
7. Line 808-825: 为每个被修改的目录生成 .overview.md
```

**`_apply_upsert()`**（`lines 855-959`）：读取磁盘上现有文件 → 按 schema 字段应用 `MergeOp` → 保留系统元数据 → 合并 links/backlinks → 通过 `viking_fs.write_file()` 写回。
  - name: recommendation
    merge_op: replace      # 完全替换
```

四种合并操作的具体实现：

| merge_op | 行为 | 适用场景 |
|----------|------|---------|
| `immutable` | 创建后不可修改 | 工具名称、事件ID |
| `sum` | 新旧值相加 | 调用次数、成功次数 |
| `patch` | 增量文本追加 | 使用提示、推荐 |
| `replace` | 完全覆盖 | 最新推荐、当前状态 |

---

## 八、OpenCode 集成：运行时访问的终端实现

### 8.1 两种集成模式

OpenViking 提供两种 OpenCode 插件：

**模式一：Tool 暴露模式**（`examples/opencode-memory-plugin/openviking-memory.ts`）
- 将 OpenViking 能力暴露为 4 个显式工具（memsearch, memread, membrowse, memcommit）
- 模型自行决定何时调用哪个工具
- 数据按需获取，不预注入

**模式二：上下文注入 + Tool 模式（推荐）**（`examples/opencode-plugin/`）
- 同时支持上下文注入（将 `viking://resources/` 仓库索引注入系统 prompt）
- 暴露 9 个工具（额外包含 memgrep, memglob, memadd, memremove, memqueue）
- 自动会话同步 + 自动记忆召回

### 8.2 自动记忆召回（Auto Recall）

这是 OpenViking 运行时访问最关键的终端实现，由 `lib/memory-recall.mjs:14-214` 实现：

**`injectRelevantMemories()` 的 6 步流水线**（`line 14-41`）：

```
Step 1: extractCurrentUserText (line 63-72)
  ├─ 遍历 output.parts[] 非 synthetic 文本 part
  ├─ **防回环**: 如果任何 part 包含 <relevant-memories> → 跳过
  └─ 返回文本或 null

Step 2: performRecallSearch (line 43-58)
  ├─ POST /api/v1/search/find { query: text.slice(0,4000), limit: 20 }
  ├─ timeout: 5000ms (AUTO_RECALL_TIMEOUT_MS)
  └─ 返回 memories[] 或 []

Step 3: pickMemoriesForInjection (line 139-163)
  ├─ rankForInjection() 复合评分 (line 112-119):
  │   baseScore = clamp(score)                     // [0,1]
  │   leafBoost = isLeafLikeMemory ? +0.12         // L2 或 is_leaf=true
  │   eventBoost = wantsTemporal && isEvent ? +0.1
  │   preferenceBoost = wantsPreference ? +0.08
  │   overlapBoost = lexicalOverlap (max +0.2)     // token 重叠
  ├─ 去重: getMemoryDedupeKey() (line 132-137)
  │   events/cases → "uri:{uri}"
  │   普通记忆 → "abstract:{category}:{normalizedAbstract}"
  └─ 优先选择 leaf 项，余位填非 leaf 项

Step 4: postProcessMemories (line 166-177)
  ├─ 截断 content → maxContentChars (默认500)
  └─ preferAbstract → 优先使用 abstract 字段

Step 5: formatMemoryBlock (line 179-198)
  ├─ 预算: tokenBudget*4 字符 (默认8000)
  └─ 输出格式:
    <relevant-memories>
    <memory uri="viking://..."> Title\nContent </memory>
    </relevant-memories>
    Use `memread` with a memory URI and level="overview" or level="read" for more details.

Step 6: prependSyntheticRecallPart (line 200-214)
  ├─ 创建 synthetic text part (ID: prt-ov-recall-{ts}-{rand6})
  ├─ synthetic: true ← 防止被自身重新索引
  └─ unshift 到 output.parts[0]
```

### 8.3 会话到记忆的同步

OpenCode 插件在每个生命周期边界自动提交：

```
Session 生命周期事件:
  - session.create  → 创建 OpenViking session
  - chat.message    → 实时同步消息到 session（非阻塞）
  - session.delete  → 触发 commit + memory extraction
  - compaction      → 触发 commit
  - plugin.shutdown → 触发 commit
```

---

## 九、可追溯性与诊断

### 9.1 ThinkingTrace：检索决策过程的完整记录

**文件位置：** `openviking_cli/retrieve/types.py:130-233`

```python
@dataclass
class ThinkingTrace:
    start_time: float
    _events: queue.Queue  # 线程安全的分布式追踪
    
    def add_event(self, event_type, message, data, query_id):
        """添加追踪事件"""
        
# 事件类型
class TraceEventType(str, Enum):
    SEARCH_DIRECTORY_START    # 进入目录
    SEARCH_DIRECTORY_RESULT   # 目录搜索结果
    EMBEDDING_SCORES          # 向量相似度分数
    RERANK_SCORES             # 重排序分数
    CANDIDATE_SELECTED         # 候选入选及原因
    CANDIDATE_EXCLUDED         # 候选排除及原因
    DIRECTORY_QUEUED           # 目录入队
    CONVERGENCE_CHECK          # 收敛检查
    SEARCH_CONVERGED           # 搜索收敛
    SEARCH_SUMMARY             # 总结
```

每个 ThinkingTrace 可在 API 响应中通过 `include_provenance=true` 获取，作为 `provenance` 字段返回。

### 9.2 Observer Queue：异步处理状态

`storage/queuefs/semantic_queue.py` — 观察者队列管理嵌入和语义处理的异步任务，包括去重合并（60 秒窗口）。

### 9.3 Telemetry：运行时遥测

`telemetry/operation.py` — 性能度量（检索耗时、嵌入调用数、向量搜索次数），通过 OpenTelemetry 导出。

---

## 十、按论文框架的故障模式分析（含源码证据）

### 10.1 故障模式一：存储缺失（Artifact Construction Failure）

**论文定义**：所需工件在存储中不存在，或压缩格式错误使信息不可检索。

**OpenViking 防护：**

| 防护机制 | 实现位置 | 验证细节 |
|---------|---------|---------|
| Observer Queue 异步处理 | `storage/queuefs/semantic_queue.py:55-59` | 60秒去重窗口，防止同一文件被重复处理 |
| EmbeddingTracker | `storage/queuefs/embedding_tracker.py` | 追踪每个文件的嵌入状态 |
| SemanticProcessor | `storage/queuefs/semantic_processor.py` | 自动生成 L0 abstract + L1 overview |
| SemanticDAG | `storage/queuefs/semantic_dag.py:884` | DAG 执行器确保文件+子文件的处理顺序 |
| 会话 commit 完整性 | `memory-session.mjs:301-326` | `pendingMessages` Map + `capturedMessages` Set 双重追踪；sendingMessages Set 防止并发重复 |

**残余风险**：Observer Queue 是异步的——`memadd` 调用后资源不会立即可检索（需要通过 `memqueue` 轮询状态）。如果在处理完成前发起搜索，会出现"存储已写入但尚未索引"的中间状态。

### 10.2 故障模式二：访问不可达（Access Failure）

**论文定义**：工件存在但可用原语和预算无法暴露它。

**OpenViking 防护：**

| 访问原语 | 代码位置 | 预算控制 |
|---------|---------|---------|
| 向量语义检索 | `hierarchical_retriever.py:367-543` | `MAX_CONVERGENCE_ROUNDS=3`, `MAX_PARALLEL_CHILD_SEARCHES=4` |
| 精确 grep | `localfs/mod.rs:804-866` (Rust) + `memory-tools.mjs:151-184` | `node_limit` 限制遍历节点数 |
| glob 模式匹配 | `memory-tools.mjs:186-215` | `node_limit` |
| 目录浏览 | `memory-tools.mjs:88-124` | `recursive` + 深度限制 |
| 分层读取 | `memory-tools.mjs:57-86` | `level` 参数控制返回精度 |

**特定残余风险：**

1. **grep 不跨 mount**：`MountableFS.grep()`（`mountable.rs:779`）的 `exclude_path` 仅在同一 mount 内有效，跨 mount 文件不会被排除。
2. **LocalFS.read() 全量读取**（`localfs/mod.rs:617-645`）：即使只需要小范围（offset/size），底层 `fs::read()` 读取整个文件到内存再切片——大文件有内存风险。
3. **递归搜索预算硬编码**：`MAX_CONVERGENCE_ROUNDS=3`（`hierarchical_retriever.py:47`）对某些深度嵌套目录可能不充分。

### 10.3 故障模式三：视图不充分（View-Use Failure）

**论文定义**：证据可访问但暴露的视图遗漏关键角色信息。

**OpenViking 的视图构造链**（论文框架映射）：

```
检索原语 → MatchedContext → FindResult.to_dict() → API JSON
                                                    → MCP markdown
                                                    → autoRecall XML
```

**逐层分析**：

| 视图角色 | L0 (abstract) | L1 (overview) | L2 (full content) | FindResult JSON | autoRecall XML |
|---------|:---:|:---:|:---:|:---:|:---:|
| 证据可见性 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 来源身份 (uri) | ✅ | ✅ | ✅ | ✅ | ✅ |
| 时间定位 | ❌ | ⚠️ | ⚠️ | ❌ | ❌ |
| 冲突权威 | ❌ | ❌ | ❌ | ❌ | ❌ |
| 多证据聚合 | ❌ | ❌ | ❌ | ⚠️ (分类但不去重) | ❌ |
| 引用绑定 | ❌ | ❌ | ❌ | ❌ | ❌ |
| 时效性 | ❌ | ❌ | ❌ | ⚠️ (hotness隐性排序) | ❌ |

**具体代码证据：**

- **跨查询不去重**（`viking_fs.py:1543-1562`）：`memories/resources/skills` 三个列表直接 `append`，不同 `TypedQuery` 返回的同一 URI 会重复出现。
- **无时间戳序列化**（`retrieve/types.py:373-385`）：`MatchedContext._context_to_dict()` 的字段只有 `uri`, `level`, `score`, `category`, `match_reason`, `abstract`, `overview`——无 `created_at`, `updated_at`, `valid_until` 等时间字段。
- **无权威标记**：`FindResult` 中所有 memory 平等排序，无"当前有效"vs"已被覆盖"的区分。`supersedes` 链接在 compressor_v2 中存在但不暴露给检索结果。
- **关系字段空置**（`hierarchical_retriever.py:558`）：`_convert_to_matched_contexts` 中 `relations = []` 始终空列表，`MatchedContext.relations` 从未被填充。

### 10.4 故障模式四：解码器使用故障（Decoder-Use Failure）

**论文定义**：视图充分但解码器未正确使用证据。

**OpenViking 防护：**

| 机制 | 实现位置 | 效果 |
|------|---------|------|
| autoRecall synthetic text 注入 | `memory-recall.mjs:200-214` | `synthetic: true` 防止记忆污染后续消息的 user input |
| 防回环检查 | `memory-recall.mjs:67` | 如果 text 已含 `<relevant-memories>` 则跳过 |
| token_budget 控制 | `memory-recall.mjs:181` | 默认 8000 字符上限，防止记忆挤占推理空间 |
| preferAbstract 优先 | `memory-recall.mjs:171` | L0 摘要（~100 tokens）优先，减少噪声 |

**残余风险**：

1. **无解码器使用反馈**：系统不测量模型是否实际使用了注入的记忆（无 attention weight 或 logit probability 探针）。
2. **hotness 排序的隐式性**：模型看到的只是排序后的列表，不知道"排序靠前=最近/最热"的隐含语义。
3. **去重策略不完整**：`getMemoryDedupeKey()`（`memory-recall.mjs:132-137`）对事件类使用 URI 去重，对普通记忆使用 abstract 去重——语义相似但 abstract 不同的重复记忆不会被去重。

---

## 十一、源码追溯索引表

| 分析维度 | 核心文件 | 关键行/函数 |
|---------|---------|-----------|
| **工件存储** | `storage/viking_fs.py` | L63 - `VikingFS` 类定义 |
| ContextType 枚举 | `openviking_cli/retrieve/types.py` | L14-19 |
| 结构化记忆 schema | `prompts/templates/memory/*.yaml` | 11 种 schema（tools, events, identity, soul, profile, preferences, entities, experiences, skills, trajectories） |
| 合并策略 | `session/memory/merge_op/base.py` | merge_op 实现（immutable/sum/patch/replace） |
| MemoryUpdater | `session/memory/memory_updater.py` | L698 - `apply_operations()`, L855 - `_apply_upsert()` |
| **RAGFS Rust 层** | | |
| FileSystem trait | `crates/ragfs/src/core/filesystem.rs` | L97-557 - 14个核心方法 |
| MountableFS 路由 | `crates/ragfs/src/core/mountable.rs` | L591-627 - `find_mount()` 最长前缀匹配 |
| Plugin 注册 | `crates/ragfs/src/core/mountable.rs` | L229-233 - `register_plugin()` |
| 插件列表 | `crates/ragfs/src/plugins/mod.rs` | L5-21 - 7个插件 |
| LocalFS read/read_dir/grep | `crates/ragfs/src/plugins/localfs/mod.rs` | L617-645 (read), L688-727 (read_dir), L804-866 (grep) |
| 核心类型 | `crates/ragfs/src/core/types.rs` | FileInfo, TreeEntry, GrepResult, WriteFlag |
| **意图分析** | `retrieve/intent_analyzer.py` | L38-176 - `IntentAnalyzer` 类 |
| 意图分析 prompt | `prompts/templates/retrieval/intent_analysis.yaml` | L38-174 - 3步骤分析方法 |
| TypedQuery/QueryPlan | `openviking_cli/retrieve/types.py` | L237-269 |
| **层次化检索** | `retrieve/hierarchical_retriever.py` | L44-620 - `HierarchicalRetriever` 类 |
| 递归搜索核心 | `retrieve/hierarchical_retriever.py` | L367-543 - `_recursive_search()` |
| 全局向量搜索 | `retrieve/hierarchical_retriever.py` | L241-264 - `_global_vector_search()` |
| 分数传播 | `retrieve/hierarchical_retriever.py` | L484-488 - `alpha * score + (1-alpha) * parent_score` |
| Rerank 混合 | `retrieve/hierarchical_retriever.py` | L565 - hotness α 混合 |
| **记忆生命周期** | `retrieve/memory_lifecycle.py` | L19-64 - `hotness_score()` |
| **结果聚合** | `storage/viking_fs.py` | L1541-1562 - `search()` 中的聚合 |
| 序列化 | `openviking_cli/retrieve/types.py` | L348-412 - `FindResult.to_dict()` |
| **向量存储** | `storage/vectordb_adapters/base.py` | L56-555 - `CollectionAdapter` ABC |
| 租户搜索 | `storage/viking_vector_index_backend.py` | L801-859 - `search_in_tenant/search_children` |
| VikingDBManagerProxy | `storage/vikingdb_manager.py` | L172-519 |
| **重排序** | `models/rerank/` | 4 种 provider（volcengine, cohere, openai, litellm） |
| **会话管理** | `session/session.py` | L1067-1631 - `commit()` + 记忆提取 |
| **压缩器 V2** | `session/compressor_v2.py` | L123 - `SessionCompressorV2`, L222-476 - `extract_long_term_memories()`, L478-662 - `extract_execution_memories()`, L694 - `_run_extract_phase()` |
| ExtractLoop（ReAct） | `session/memory/extract_loop.py` | L41-303 - ReAct 编排器 |
| SessionExtractContextProvider | `session/memory/session_extract_context_provider.py` | L57, L473-589 - `prefetch()` |
| AgentExperienceContextProvider | `session/memory/agent_experience_context_provider.py` | L36, L157-266 - `prefetch()` |
| **Semantic Queue** | `storage/queuefs/semantic_queue.py` | L55-59 - 去重窗口 |
| `storage/queuefs/semantic_dag.py` | 884行 - DAG 执行器 |
| `storage/queuefs/semantic_processor.py` | L0/L1 生成 |
| **OpenCode 插件** | | |
| 入口 + hooks 注册 | `examples/opencode-plugin/index.mjs` | L16 - `OpenVikingPlugin`, L39-77 - hooks 注册 |
| 记忆工具 (11个) | `examples/opencode-plugin/lib/memory-tools.mjs` | L16-289 - 全部 API 端点映射 |
| autoRecall 流水线 | `examples/opencode-plugin/lib/memory-recall.mjs` | L14-214 - 6步注入流水线 |
| 会话同步 | `examples/opencode-plugin/lib/memory-session.mjs` | 651行 - session mapping + 生命周期 |
| 运行状态 | `examples/opencode-plugin/lib/runtime.mjs` | L3-21 - `checkServiceHealth()` |
| 配置管理 | `examples/opencode-plugin/lib/utils.mjs` | L5-28 - 默认配置, L99-106 - 配置优先级 |
| **REST API** | `server/routers/search.py` | L175-263 - search/find 端点 |
| MCP 端点 | `server/mcp_endpoint.py` | L216-290 - find/search 工具 |
| **追踪与遥测** | `retrieve/types.py` | L130-229 - `ThinkingTrace` |
| 遥测 | `telemetry/operation.py` | L67 - intent_analysis 计时 |

---

## 十二、与论文框架的对齐总结

OpenViking 是论文"类型化访问模型"的一个可追溯实例系统。

### 验证论文核心论点的证据：

1. **压缩侧 ≠ 访问侧**：OpenViking 的结构化记忆系统（YAML 驱动的字段级 schema + merge_op）解决了"记忆怎么写"的问题（压缩侧）。但其运行时创新在于"记忆怎么用"（访问侧）——IntentAnalyzer + HierarchicalRetriever + autoRecall 构成了完整的运行时访问机制。

2. **原语多样性**：经源码验证，OpenViking 同时暴露了 **11 个工具**（memory-tools.mjs:16-289），每个都精确映射到一个 REST API 端点——不是单一 top-k 检索。

3. **视图分层**：经源码验证，L0/L1/L2 三级上下文存在于三层消费端：API JSON (`FindResult.to_dict()`)、MCP markdown (`_format_search_result()`)、autoRecall XML (`formatMemoryBlock()`)。

4. **故障可诊断**：经源码验证，ThinkingTrace 捕获 10 种事件类型（`TraceEventType` enum），Observer Queue 提供异步处理可见性，Telemetry 记录检索性能。

### 不足（与论文框架的差距）：

1. **视图角色不全**：`_context_to_dict()` 输出的 7 个字段中，缺少 created_at、updated_at、valid_until 等时间标记，无权威性标记。
2. **跨查询不去重**：`viking_fs.py:1543-1562` 的聚合逻辑仅按 context_type 分类，不检查 URI 重复。
3. **关系字段空置**：`hierarchical_retriever.py:558` 的 `relations = []` 始终空列表。
4. **无解码器使用反馈**：系统不测量模型是否实际使用了注入的证据（无 attention/logit probe）。
5. **LocalFS 读性能**：`localfs/mod.rs:617` 的 `read()` 全量读取再切片——对大文件造成内存浪费。

### 论文贡献的实证强度

OpenViking 源码验证表明：即使设计良好的工业级记忆系统，仍然在运行时访问层存在系统性的设计空白。这些空白（视图角色缺失、去重不完整、解码器使用不可观测）恰好是论文诊断框架试图识别和分类的问题——从而证实了论文分析框架的有效性和实用价值。
