# J-lens 工具有效性诊断

## 范围

Qwen3-VL-2B，ATM Hard 31，C0/C1 paired。目标由冻结规则生成，只包含 `Unknown` 与 `known` 的单 token aliases；本报告是探索性工具审计，不是论文机制结论。

## 行为锚点

- `N->N`: 21
- `N->U`: 8
- `U->U`: 2

## 读出结果

在 C1 最后一个 evidence 位置、第 24 层，`Unknown-known` margin 对最终 `Unknown` 输出的 AUC：J-lens = 0.852，logit lens = 0.752。

对两种 lens 的 AUC 差做按题 paired bootstrap，点估计为 `+0.100`，95% 区间约为 `[-0.063, 0.273]`。区间跨过 0，当前样本不能证明 J-lens 稳定优于 logit lens。

在 `P_a0` 第 22 层，C1-C0 margin 增量区分新增 `Unknown` (`N->U`) 与稳定非 `Unknown` (`N->N`) 的 AUC：J-lens = 0.940，logit lens = 0.857。

## 当前判断

J-lens 工具链能够在生成前读出与最终弃答相关的内部状态，并且在证据末端的晚中层显示出比同位置 logit lens 更强的点估计。该优势尚不显著。到 `P_a0`，两种 lens 都能较强地区分输出，说明一部分信号已经成为普通输出准备状态，不能据此宣称 J-lens 独有地读出了推理过程。

## 边界

- ATM prompt 中 `P_q` 位于 evidence 之前，只作为负对照。
- C0/C1 总序列长度不同，BF16 attention kernel 在相同前缀上产生了小幅数值漂移；连续 margin 是主要指标，低概率 token 的 rank 跳动不能单独解释。
- `Unknown` 是输出邻近概念；该实验验证诊断可读性，不验证变量绑定或答案正确性。
- 样本仅 31 题，其中新增 `Unknown` 只有 8 题；区间见 `layerwise_auc.csv` 和 `paired_delta_auc.csv`。
- 下一步必须使用人工冻结的 gold、operand 与 intermediate targets，才能判断 J-lens 是否解释 evidence use，而不只是预测输出。
