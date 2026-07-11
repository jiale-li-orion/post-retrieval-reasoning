# J-Space 研究笔记阅读指南

> 面向 `J-Space_终极研究笔记_2026-07-10.pdf` 的阅读导航。目标是帮助快速定位：想理解什么、该看哪里、按什么顺序阅读，以及哪些部分最值得反复精读。

---

## 目录

- [1. 想先弄懂 J-space 到底是什么](#1-想先弄懂-j-space-到底是什么)
- [2. 想真正理解 J-lens 的数学机制](#2-想真正理解-j-lens-的数学机制)
- [3. 想知道论文到底发现了什么](#3-想知道论文到底发现了什么)
- [4. 想看真正的 insight](#4-想看真正的-insight)
- [5. 想研究 small model reasoning failure](#5-想研究-small-model-reasoning-failure)
- [6. 想知道社区做到什么程度了](#6-想知道社区做到什么程度了)
- [7. 想在 Qwen3-8B 上真正开工](#7-想在-qwen3-8b-上真正开工)
- [推荐阅读路线](#推荐阅读路线)
- [最值得反复重读的四处](#最值得反复重读的四处)
- [真正需要记住的三件事](#真正需要记住的三件事)
- [文档的正确使用方式](#文档的正确使用方式)

---

## 1. 想先弄懂 J-space 到底是什么

**看第 1 章，P7–8。**

重点阅读：

- `1.1` 从自动计算到可访问公共接口
- `1.3` 会计算 vs 能把结果交给任意下游操作
- `1.4` 统一信息生命周期

这里是整份文档的地基。

核心框架：

```text
source
→ formation
→ workspace entry
→ binding
→ broadcast / routing
→ consumption
→ behavior
```

以后讨论 reasoning failure，基本都在这条链上定位。

---

## 2. 想真正理解 J-lens 的数学机制

**看第 2 章，P8–10。**

重点阅读：

- `2.2` 平均 Jacobian 与 J-lens
- `2.3` Pullback 视角
- `2.5` J-space 的稀疏 frame 定义
- `2.8` 三类基本干预

核心公式：

```math
J_\ell
=
\mathbb{E}
\left[
\frac{\partial h_{\mathrm{final},t'}}
{\partial h_{\ell,t}}
\right]
```

它做的事情，是把最终层词表方向通过后续网络的平均局部动力学“拉回”到中间层。

然后：

```math
\mathrm{lens}(h_\ell)
=
W_U J_\ell h_\ell
```

于是某个 token 对应的方向，可以理解为：

> 当前内部状态沿哪个方向变化，会让模型未来更倾向说出这个 token。

这一章理解透，后面大约 70% 的内容都会顺下来。

---

## 3. 想知道论文到底发现了什么

**看第 4、5 章，P12–16。**

### 第 4 章：为什么 J-space 像 workspace

重点：

- `4.1` 可报告性
- `4.3` 定向召唤
- `4.6` 内部推理
- `4.7` 灵活泛化
- `4.8` 选择性

### 第 5 章：workspace 的结构特征

重点：

- `5.1` sensory–workspace–motor 三段式
- `5.2` ignition-like transition
- `5.3` capacity
- `5.4` competition
- `5.8` depth 与 sequence 两条时间轴

这两章合起来，基本就是论文主结果。

---

## 4. 想看真正的 insight

**直接看第 9、10 章，P22–24。**

这是最值得精读的部分之一。

### 第 9 章：Discussion 精华

重点：

- `9.1` J-space 的解释力来自公共接口
- `9.2` 最深开放问题：内容如何进入 J-space
- `9.3` small-model scale 尚未解决
- `9.6` GWT 类比最强与最弱之处

### 第 10 章：证据边界

重点回答：

- 论文真正证明了什么
- 因果性的准确含义
- 哪些问题仍没有被证明
- 什么结果才算真正反证

只想抓研究灵魂，优先读这里。

---

## 5. 想研究 small model reasoning failure

**看第 11–14 章，P25–32。**

这是整份笔记里最贴近 small-model reasoning 研究主线的部分。

### 第 11 章：reasoning failure taxonomy

核心分类：

- A. 正确概念缺失
- B. 错误概念进入
- C. 出现太晚
- D. margin 太低
- E. 存在于 non-J-space
- F. binding failure
- G. present-but-unused
- H. CoT externalization dependence
- I. phase mismatch
- J. horizon mismatch

### 第 12 章：phase-conditioned / horizon-conditioned dynamics

这对 Qwen3 很关键。

reasoning mode 下，“当前阶段应该读到什么”，可能和 answer phase 完全不同。

### 第 13 章：representation source

核心问题：

```text
pretraining prior
vs
context-conditioned temporary state
vs
online composed intermediate
```

这是我们后续讨论中最重要的推进之一。

### 第 14 章：五组去伪实验

最值得反复看的两组：

- `14.2` 反训练分布 / alternate-world reasoning
- `14.3` 新概念、临时绑定与在线组合

这两组最可能真正区分：

- 分布恢复
- 上下文覆盖
- 在线推理

---

## 6. 想知道社区做到什么程度了

**看第 18 章，P37–39。**

这里包括：

- Qwen3.5-4B 实时 J-space readout
- Gemma 上 workspace noise 预测 hallucination
- J-Space Prompting 中的 binding / routing / consumption
- Qwen2.5-3B flexible-generalization swap
- Qwen3-8B 的重要负结果

尤其看 `18.7`。

核心实验纪律：

> 任何漂亮的 J-lens 现象，都应该和 plain logit lens 比较。

> 任何只在 late layers 或模型已经写出的文本位置上出现的信号，都可能是 artifact。

---

## 7. 想在 Qwen3-8B 上真正开工

**看第 20、21 章，P39–44。**

### 第 20 章：实验蓝图

包括：

- two-hop 最小闭环
- target J-lens
- J-lens vs logit lens
- thinking / non-thinking / CoT 对照
- prior–context conflict
- ablation / swap / steering
- binding / consumption
- 统计设计

### 第 21 章：硬控制

实验前必须读。

重点：

- 十条最低要求
- 因果控制族
- 强证伪门槛

很多低质量实验，就是死在没有过这一章的控制要求。

---

# 推荐阅读路线

## 路线 A：第一次阅读，建立认知框架

```text
1 → 2 → 4 → 5 → 9 → 10
```

大致覆盖 P7–24。

第 3、6、7、8 章可以暂时跳过。

---

## 路线 B：进入 small model reasoning failure

```text
11 → 12 → 13 → 14
```

大致覆盖 P25–32。

---

## 路线 C：准备实验

```text
18 → 19 → 20 → 21
```

大致覆盖 P37–44。

---

## 路线 D：按需查附录

- 忘了公式：附录 A，P46–48
- 想跑代码：附录 B，P48
- 想直接拿实验模板：附录 C，P49–51
- 想判断结果属于哪类：附录 D，P51–52
- 想查原论文是否做过：附录 E，P52–54
- 想真正开始跑实验：附录 H，P55

---

# 最推荐的一条路线

```text
1
→ 2
→ 9
→ 10
→ 11
→ 13
→ 14
→ 20
→ 21
```

这条路线最适合当前目标：

> 从理解 J-space，直接走到研究 small-model reasoning failure。

---

# 最值得反复重读的四处

## P7–8：公共接口 + 信息生命周期

这是总框架。

## P22–24：Discussion + 证据边界

这是理论灵魂。

## P27–32：representation source + 去伪实验

这是最可能长出新工作的地方。

## P39–44：Qwen3-8B 实验蓝图 + 硬控制

这是落地执行层。

---

# 真正需要记住的三件事

## 1. J-space 是公共接口

```text
J-space ≈ verbalizable, causally accessible public interface
```

它承载模型内部一部分可被报告、调控、广播和下游调用的中间状态。

## 2. reasoning failure 是信息生命周期中的局部失效

```text
source
→ formation
→ workspace entry
→ binding
→ routing
→ consumption
→ behavior
```

模型失败时，真正的问题是：到底在哪一环坏了。

## 3. 最强证据必须区分表示来源

```text
prior
vs
context-created state
vs
online composition
```

真正强的实验，要能区分：

- 预训练先验自然投影
- 当前上下文创建的临时状态
- 在线计算产生的新中间变量

---

# 文档的正确使用方式

这份文档更适合作为研究手册，不适合作为教材从头到尾线性硬读。

推荐使用方式：

1. 第一次：读主线，建立统一框架。
2. 第二次：带着具体问题回查。
3. 第三次：做实验时直接使用第 20、21 章和附录 H。

最终的核心研究问题是：

```text
small model 在什么条件下能够：

1. 压制 pretrained prior；
2. 建立 context-created temporary representation；
3. 将中间变量送入可广播工作区；
4. 维持正确 binding；
5. 让后续计算真正消费这些变量；
6. 在失败时定位 information lifecycle 中具体断裂的位置。
```

---

## 推荐文件

- `J-Space_终极研究笔记_2026-07-10.pdf`
- `J-Space_终极研究笔记_2026-07-10.tex`

