# ATM Hard-31 模型回答对照复查

> 本报告不运行新模型，只读取三份冻结产物：Qwen3-VL-2B SGM、MiMo V2.5 SGM、MiMo V2.5 Raw。
> 模型回答只用于检验审计判断，不以答对/答错反推题目是否可解。

## 修订结论

- 第 3 题由 B 改为 D：三种回答都纳入 gold 排除的 transit/airport cities，暴露未声明的 visit/city ontology。
- 第 21 题由 B 改为 D：模型识别两次访问后将 `last visit` 解释为最近一次，gold 却要求返回两次日期。
- 修订后 A=10、B=9、C=3、D=3、E=6，C+D+E=12/31。
- 第 10、26 题的满分不能证明语义可恢复：Oracle list-recall 允许直接复制全部 evidence IDs。
- 第 16、25、30 题暴露 answer prompt 的输出合同干扰：qtype 是 `open_end`，模型却可能受 `recall/list items -> IDs` 指令影响输出 IDs；第 16 题在 Qwen SGM 与 MiMo SGM 中都出现。
- 第 29 题 judge 理由有误：它把 evidence 中的酒店正式名称称为错误；但模型没有明确给出 timelapse 与酒店的关系，因此本轮不据此改类。

## 按类别的实际 ATM 均分

| 类别 | 题数 | Qwen3-VL-2B SGM | MiMo SGM | MiMo Raw |
|:---:|---:|---:|---:|---:|
| A | 10 | 0.6000 | 0.8424 | 0.9757 |
| B | 9 | 0.3111 | 0.4444 | 0.6667 |
| C | 3 | 0.3333 | 0.2051 | 0.3077 |
| D | 3 | 0.0000 | 0.0000 | 0.0000 |
| E | 6 | 0.1667 | 0.1042 | 0.2222 |

这些均分仅作 sanity check。尤其是 list-recall Oracle 条件存在全量 ID 复制捷径，
因此 C/E 类得到高分并不构成可解性证据。

## 31 题回答总表

| # | 类 | qtype | Qwen SGM | MiMo SGM | MiMo Raw | 复查标记 |
|---:|:---:|---|---|---|---|---|
| 1 | A | list_recall | 20250223_130249, 20250223_132602, 20250225_141559, 20250225_141720, 20250225_142539, 20250225_150659, 20250225_173637, 20250225_184511<br>**score=1.0000** | 20250223_130249, 20250223_132602, 20250225_141720, 20250225_142539, 20250225_150659, 20250225_173637, 20250225_184511<br>**score=0.8750** | 20250223_130249, 20250223_132602, 20250225_141720, 20250225_142539, 20250225_150659, 20250225_173637, 20250225_184511<br>**score=0.8750** | - |
| 2 | E | number | 202502200013<br>**score=0.0000** | 445.26 EUR<br>**score=0.0000** | Unknown<br>**score=0.0000** | - |
| 3 | D | open_end | London, United Kingdom, 2023-12-09 New Orleans, Louisiana, 2023-12-09 Kenner, Louisiana, 2023-12-15 Houston, Texas, 2023-12-15 Boston, Massachusetts, 2023-12-15 Toronto, Ontario...<br>**score=0.0000** | London: 2023-12-09, New Orleans: 2023-12-09, Houston: 2023-12-15, Boston: 2023-12-15, Cambridge: 2023-12-15, Toronto: 2023-12-19, Mississauga: 2023-12-31. Total cities: 7.<br>**score=0.0000** | London, 2023-12-09; New Orleans, 2023-12-09; Houston, 2023-12-15; Boston, 2023-12-15; Cambridge, 2023-12-15; Toronto, 2023-12-19; Mississauga, 2023-12-31; 8<br>**score=0.0000** | `reclassify_B_to_D`<br>三种回答都纳入 gold 排除的 transit/airport cities；输入没有一致的 visited-city ontology。 |
| 4 | C | number | Unknown<br>**score=0.0000** | Unknown<br>**score=0.0000** | Unknown<br>**score=0.0000** | - |
| 5 | E | number | 20250310_202208,202502110008,202502200013<br>**score=0.0000** | 445.26 EUR<br>**score=0.0000** | 408.00 EUR and 445.26 EUR<br>**score=0.0000** | - |
| 6 | A | list_recall | 20230401_115135, 20230403_114911, 20230403_114939<br>**score=1.0000** | 20230401_115135, 20230403_114911<br>**score=0.6667** | 20230401_115135, 20230403_114911, 20230403_114939<br>**score=1.0000** | - |
| 7 | A | list_recall | 20231210_123349, 20231210_124112, 20231210_124201, 20231210_124255, 20231210_124635, 20231210_124834, 20231210_125002, 20231210_125339, 20231210_125556, 20231210_125641, 2023121...<br>**score=1.0000** | 20231210_123349, 20231210_124112, 20231210_124201, 20231210_124255, 20231210_124635, 20231210_124834, 20231210_125002, 20231210_125339, 20231210_125556, 20231210_125641, 2023121...<br>**score=1.0000** | 20231210_123349, 20231210_124112, 20231210_124201, 20231210_124255, 20231210_124635, 20231210_124834, 20231210_125002, 20231210_125339, 20231210_125556, 20231210_125641, 2023121...<br>**score=1.0000** | - |
| 8 | B | open_end | 2, 2022, 2024, 2024, 2024, 2024<br>**score=0.0000** | 3 nights in 2022, 4 nights in 2024<br>**score=0.0000** | 2 nights in 2022, 1 night in 2024.<br>**score=0.0000** | - |
| 9 | A | open_end | 2023-12-09, 2024-01-01, 31 days<br>**score=0.0000** | Start date: 2023-12-09, End date: 2024-01-01, Total duration: 24 days.<br>**score=1.0000** | December 9, 2023 to January 1, 2024, 24 days<br>**score=1.0000** | - |
| 10 | C | list_recall | 20240715_125140, 20240715_125144, 20241004_213143, 20241117_115411, 20241117_115422, 20250119_000631, 20250221_002514, 20250221_002518, 20250509_232737, 20250509_232753, 2025050...<br>**score=1.0000** | 20240715_125140, 20240715_125144, 20241117_115411, 20250119_000631, 20250221_002514, 20250221_002518, 20250509_232737, 20250509_232802<br>**score=0.6154** | 20240715_125140, 20240715_125144, 20241117_115411, 20241117_115422, 20250119_000631, 20250221_002514, 20250221_002518, 20250509_232737, 20250509_232753, 20250509_232802, 2025051...<br>**score=0.9231** | `supports_C_but_exposes_oracle_id_shortcut`<br>Qwen 直接输出全部 13 个 Oracle evidence IDs 获得 1.0；这不要求解析 Grace 与 cat 的身份映射。 |
| 11 | E | list_recall | Unknown<br>**score=0.0000** | Unknown<br>**score=0.0000** | 20230307_161006, 20230307_161017, 20230307_161038<br>**score=0.3333** | - |
| 12 | B | open_end | evidence1,evidence2,evidence3,evidence5<br>**score=0.0000** | The Z Hotel Glasgow (June 23-24, 2022), Hilton Glasgow (November 24-27, 2024), DoubleTree by Hilton Glasgow Central (November 23-24, 2024)<br>**score=0.0000** | The Z Hotel Glasgow (June 23-24, 2022), Hilton Glasgow (November 24-28, 2024), DoubleTree by Hilton Glasgow Central (November 23-24, 2024).<br>**score=1.0000** | - |
| 13 | B | number | 20220906_134413,20220916_154434,20220924_194144<br>**score=0.0000** | £190.00<br>**score=1.0000** | £190.00<br>**score=1.0000** | - |
| 14 | B | list_recall | 20250221_133131, 20250221_135227, 20250221_142725<br>**score=1.0000** | 20250221_133131, 20250221_135227, 20250221_142725<br>**score=1.0000** | 20250221_133131, 20250221_135227, 20250221_142725<br>**score=1.0000** | - |
| 15 | B | list_recall | 20230327_205909, 20230327_210005, 20240819_205823, 20240819_205827, 20240819_210159<br>**score=1.0000** | 20230327_205909, 20230327_210005, 20240819_205823, 20240819_205827, 20240819_210159<br>**score=1.0000** | 20230327_205909, 20230327_210005, 20240819_205823, 20240819_205827, 20240819_210159<br>**score=1.0000** | - |
| 16 | A | open_end | 20231210_111815, 20240701_120945, 20240811_150248, 20240930_132654, 20241021_153837, 20241127_193516, 20250223_100830, 20250428_114056<br>**score=0.0000** | 20231210_111815, 20240701_120945, 20240811_150248, 20240930_132654, 20241021_153837, 20241127_193516, 20250223_100830, 20250428_114056<br>**score=0.0000** | NeurIPS 2023, UKIS 2024, ACL 2024, ECCV 2024, ECAI 2024, BMVC 2024, ROBOVIS 2025, WWW 2025<br>**score=1.0000** | `official_prompt_output_contract_interference`<br>Qwen 与 MiMo SGM 对 open_end 的会议名称问题输出 evidence IDs，而 MiMo Raw 输出会议名并答对；官方 prompt 的 recall/list-items 规则与 qtype 所需自然语言答案冲突，SGM 中显著的 ID 字段进一步放大了这一干扰。 |
| 17 | D | open_end | 2<br>**score=0.0000** | 2<br>**score=0.0000** | Unknown<br>**score=0.0000** | - |
| 18 | B | open_end | Evidence 1, 2, and 3 all refer to the same location, Abadia do Porto in Porto, Portugal, and describe different meals. Evidence 1 shows a charcuterie board, bread, wine, and ora...<br>**score=0.0000** | Abadia do Porto, for its warm, intimate atmosphere and traditional Portuguese cuisine.<br>**score=1.0000** | Abadia do Porto. The evidence shows multiple visits (Feb 22 and Feb 27) with a variety of traditional Portuguese dishes, including cured meats, rice, stews, and seafood, indicat...<br>**score=1.0000** | - |
| 19 | C | number | 23,00 EUR<br>**score=0.0000** | Unknown<br>**score=0.0000** | Unknown<br>**score=0.0000** | - |
| 20 | B | open_end | 20240730_024914, 20240730_203024, 20240731_102216<br>**score=0.0000** | Novotel Cairo Airport, Sofitel Cairo<br>**score=0.0000** | Novotel Cairo Airport, Sofitel Cairo<br>**score=0.0000** | - |
| 21 | D | open_end | 2024-08-19, Baihua Traditional Dessert Shop<br>**score=0.0000** | Unknown<br>**score=0.0000** | Based on the evidence provided: 1. **Shop Name**: Evidence 3 shows the storefront with the sign "BAIHUA TRADITIONAL DESSERT SHOP" (百花传统甜品店). 2. **Last Visit Date**: The evidence...<br>**score=0.0000** | `reclassify_B_to_D`<br>模型识别两次访问后仍将 last visit 解释为最近一次；gold 却要求两次日期。 |
| 22 | A | list_recall | 20230416_114842, 20230416_191938, 20230416_191943, 20230417_133726, 20230418_121232, 20230418_184523, 20230419_130151, 20230419_130159, 20230419_134456, 20230419_194245, 2023041...<br>**score=1.0000** | 20230416_114842, 20230416_191938, 20230416_191943, 20230417_133726, 20230418_121232, 20230418_184523, 20230419_130151, 20230419_130159, 20230419_134456, 20230419_200149, 2023041...<br>**score=0.8824** | 20230416_114842, 20230416_191938, 20230416_191943, 20230417_133726, 20230418_121232, 20230418_184523, 20230419_130151, 20230419_130159, 20230419_134456, 20230419_194245, 2023041...<br>**score=0.8824** | - |
| 23 | E | number | 23.00, 9.10, 35.00, 10.80, 9.50<br>**score=0.0000** | 23.00 EUR, 9.50 EUR<br>**score=0.0000** | 62.75 EUR<br>**score=0.0000** | - |
| 24 | A | list_recall | 20230418_135743, 20230418_135752, 20230418_135850, 20230418_135852, 20230418_195315, 20230418_195319, 20230418_195350<br>**score=1.0000** | 20230418_135743, 20230418_135752, 20230418_135850, 20230418_135852, 20230418_195315, 20230418_195319, 20230418_195350<br>**score=1.0000** | 20230418_135743, 20230418_135752, 20230418_135850, 20230418_135852, 20230418_195315, 20230418_195319, 20230418_195350<br>**score=1.0000** | - |
| 25 | A | open_end | 20220917_134113, 20240930_180605, 20241021_134620, 20250208_123453, 20250223_132602, 20250407_201317<br>**score=0.0000** | England, Italy, Spain, France, Portugal, Hungary<br>**score=1.0000** | United Kingdom, Italy, Spain, France, Portugal, Hungary<br>**score=1.0000** | `official_prompt_output_contract_interference`<br>Qwen 对 open_end 的国家问题输出 evidence IDs，MiMo 则输出国家并答对。 |
| 26 | E | list_recall | 20230905_144627, 20230905_152531, 20230905_152605, 20230905_153314, 20230905_153627, 20230906_121206, 20230906_121455, 20230906_155344<br>**score=1.0000** | 20230905_144627, 20230905_152531, 20230905_152605, 20230906_121206, 20230906_155344<br>**score=0.6250** | 20230905_144627, 20230905_152531, 20230905_152605, 20230905_153314, 20230905_153627, 20230906_121206, 20230906_121455, 20230906_155344<br>**score=1.0000** | `supports_E_but_exposes_oracle_id_shortcut`<br>Qwen SGM 和 MiMo Raw 复制全部 8 个 Oracle IDs 获得 1.0，但若干 SGM 项并未暴露 sheep 语义。 |
| 27 | A | list_recall | 20231210_111815, 20240701_120945, 20240811_150248, 20240930_132654, 20241003_184216, 20250428_114056, 20250428_114126<br>**score=1.0000** | 20231210_111815, 20240701_120945, 20240811_150248, 20240930_132654, 20241003_184216, 20250428_114056, 20250428_114126<br>**score=1.0000** | 20231210_111815, 20240701_120945, 20240811_150248, 20240930_132654, 20241003_184216, 20250428_114056, 20250428_114126<br>**score=1.0000** | - |
| 28 | E | open_end | 20240708_170032, 20240711_121848, 20240711_125806, 20240712_101712, 20240712_142629, 20240713_144451, 20240713_192657, 20240713_193044, 20240713_224255, 20250208_125156<br>**score=0.0000** | Marignane, Puyvert, Pertuis, La Seyne-sur-Mer, Cassis, Aubagne, Paris<br>**score=0.0000** | Marignane, Apt, Pertuis, La Seyne-sur-Mer, Cassis, Aubagne, Paris<br>**score=0.0000** | - |
| 29 | B | open_end | Sofitel Legend Winter Palace Hotel, 0, Kornish Al Nile Street, Luxor City, Luxor, 85951, Egypt Sofitel Legend Old Cataract Aswan Hotel, 81511, Al Fanadq Street, Taqouk Mountain,...<br>**score=0.0000** | Sofitel Legend Winter Palace Hotel, Sofitel Legend Old Cataract Aswan Hotel; 20240801_201540<br>**score=0.0000** | Sofitel Legend Winter Palace Hotel, Sofitel Legend Old Cataract Aswan Hotel; 20240801_201540<br>**score=0.0000** | `judge_explanation_anomaly_not_reclassified`<br>MiMo 使用证据中的 Sofitel Legend Winter Palace Hotel 名称并给出正确 ID；judge 将该证据内名称称为错误。不过回答没有显式说明 timelapse 属于哪家酒店，因此 false verdict 仍有独立依据。 |
| 30 | A | open_end | 20241001_171053, 20241001_173039, 20241001_174058, 20241001_175310, 20241001_180247, 20241001_181259, 20241001_182544, 20241001_183401, 20241001_184112, 20241001_184155, 2024100...<br>**score=0.0000** | Safe-CLIP: Removing NSFW Concepts from Vision-and-Language Models, Learning Anomalies with Normality Prior for Unsupervised Video Anomaly Detection, Towards Surprising Video Com...<br>**score=1.0000** | Safe-CLIP: Removing NSFW Concepts from Vision-and-Language Models, Learning Anomalies with Normality Prior for Unsupervised Video Anomaly Detection, Towards Surprising Video Com...<br>**score=1.0000** | `official_prompt_output_contract_interference`<br>Qwen 对 open_end 的论文标题问题输出 evidence IDs，MiMo 输出标题并答对。 |
| 31 | B | list_recall | 20240628_105911, 20241017_140703, 20241116_174018, 20241116_174026<br>**score=0.8000** | Unknown<br>**score=0.0000** | 20240628_105911, 20240926_131909, 20241017_140703, 20241116_174018, 20241116_174026<br>**score=1.0000** | - |

## 关键病例完整对照

### 03. `de07dd6e-ac2f-4517-a084-e193a3d93601` — D

- **Question:** During my NeurIPS 2023 North America trip (prior to returning home), list all cities I visited along with the specific dates associated with each location, and provide the total number of cities visited.
- **Gold:** During your NeurIPS 2023 North America trip (before returning home on 2024-01-01), you visited 5 cities in total: Houston (layovers on 2023-12-09 and 2023-12-15), New Orleans (2023-12-09 to 2023-12-15), Boston (2023-12-15 to 2023-12-19), Cambridge, MA (2023-12-15 to 2023-12-19), and Toronto (2023-12-19 to 2023-12-31).
- **复查结论:** 三种回答都纳入 gold 排除的 transit/airport cities；输入没有一致的 visited-city ontology。
- **qwen3vl2b_sgm (0.0000):** London, United Kingdom, 2023-12-09<br>
New Orleans, Louisiana, 2023-12-09<br>
Kenner, Louisiana, 2023-12-15<br>
Houston, Texas, 2023-12-15<br>
Boston, Massachusetts, 2023-12-15<br>
Toronto, Ontario, 2023-12-19<br>
Mississauga, Ontario, 2023-12-31<br>
Petersfield, Cambridgeshire, England, 2024-01-31<br>
<br>
Total number of cities visited: 7
  - Judge: The prediction does not match the ground truth. The ground truth lists 5 cities with specific date ranges; the prediction lists different cities (including London, Kenner, Mississauga, Petersfield), different dates (and an extra 2024-01-31), and a different total (7 vs 5). Multiple dates and locations conflict, so accuracy is false.
- **mimo_v25_sgm (0.0000):** London: 2023-12-09, New Orleans: 2023-12-09, Houston: 2023-12-15, Boston: 2023-12-15, Cambridge: 2023-12-15, Toronto: 2023-12-19, Mississauga: 2023-12-31. Total cities: 7.
  - Judge: The prediction does list cities and dates but conflicts with the ground truth: it adds London and Mississauga (not in ground truth), changes Houston and New Orleans dates (swapped layover vs stay), and reports 7 cities instead of 5. Because the prediction does not match the ground truth details, accuracy is false.
- **mimo_v25_raw (0.0000):** London, 2023-12-09; New Orleans, 2023-12-09; Houston, 2023-12-15; Boston, 2023-12-15; Cambridge, 2023-12-15; Toronto, 2023-12-19; Mississauga, 2023-12-31; 8
  - Judge: The prediction does list cities and dates but conflicts with the ground truth: it adds London and Mississauga (not in ground truth), has wrong Houston dates (should be layovers on 2023-12-09 and 2023-12-15 but prediction lists only 2023-12-15), and reports 8 cities instead of the ground-truth 5. Because of these mismatches and extra items, accuracy is false.

### 10. `afa4bf6a-c459-4173-9de9-2aac6183a4a7` — C

- **Question:** I remember several moments when Grace was hiding in strange places, or being sneaky and peeking at me with her body partially hidden. I’d like to make a collection of those moments. Which photos or videos captured that?
- **Gold:** 20250509_232753, 20250509_232802, 20250509_232737, 20250221_002518, 20250221_002514, 20250119_000631, 20241117_115411, 20241117_115422, 20241004_213143, 20240715_125140, 20240715_125144, 20250511_120224, 20250606_231452
- **复查结论:** Qwen 直接输出全部 13 个 Oracle evidence IDs 获得 1.0；这不要求解析 Grace 与 cat 的身份映射。
- **qwen3vl2b_sgm (1.0000):** 20240715_125140, 20240715_125144, 20241004_213143, 20241117_115411, 20241117_115422, 20250119_000631, 20250221_002514, 20250221_002518, 20250509_232737, 20250509_232753, 20250509_232802, 20250511_120224, 20250606_231452
- **mimo_v25_sgm (0.6154):** 20240715_125140, 20240715_125144, 20241117_115411, 20250119_000631, 20250221_002514, 20250221_002518, 20250509_232737, 20250509_232802
- **mimo_v25_raw (0.9231):** 20240715_125140, 20240715_125144, 20241117_115411, 20241117_115422, 20250119_000631, 20250221_002514, 20250221_002518, 20250509_232737, 20250509_232753, 20250509_232802, 20250511_120224, 20250606_231452

### 16. `30ad0a48-89ef-46c4-a388-a3c872bd16b8` — A

- **Question:** Today is July, 1 2025, Help me recall all the acadamic conference I went to in the past two years. (Leave out one-day seminars/workshops)
- **Gold:** NeurIPS 2023, UKIS 2024, ACL 2024, ECCV 2024, ECAI 2024, BMVC 2024, ROBOVIS 2025, WWW 2025
- **复查结论:** Qwen 与 MiMo SGM 对 open_end 的会议名称问题输出 evidence IDs，而 MiMo Raw 输出会议名并答对；官方 prompt 的 recall/list-items 规则与 qtype 所需自然语言答案冲突，SGM 中显著的 ID 字段进一步放大了这一干扰。
- **qwen3vl2b_sgm (0.0000):** 20231210_111815, 20240701_120945, 20240811_150248, 20240930_132654, 20241021_153837, 20241127_193516, 20250223_100830, 20250428_114056
  - Judge: The prediction provides only timestamps, not conference names. It does not map to the ground-truth conference list, so it fails to answer the question. Therefore accuracy is false.
- **mimo_v25_sgm (0.0000):** 20231210_111815, 20240701_120945, 20240811_150248, 20240930_132654, 20241021_153837, 20241127_193516, 20250223_100830, 20250428_114056
  - Judge: Prediction lists timestamps rather than conference names, so it does not answer the question. It fails to match the ground-truth list of conference names and thus does not cover the required information.
- **mimo_v25_raw (1.0000):** NeurIPS 2023, UKIS 2024, ACL 2024, ECCV 2024, ECAI 2024, BMVC 2024, ROBOVIS 2025, WWW 2025
  - Judge: The prediction exactly lists the same conferences as the ground truth in the same order. It directly answers the request to recall conferences (excluding one-day events). Therefore it matches the ground truth.

### 21. `7665e37d-29a0-4450-8d03-6539122a6b3f` — D

- **Question:** I recall visiting a dessert shop in Guangzhou on multiple occasions. The shop had an extensive menu, with several hundred items available. On what exact dates did I last visit this dessert shop? What is the name of the shop?
- **Gold:** The dessert shop is 百花传统甜品店.
The most recent visit dates were 27 March 2023 and 19 August 2024.
- **复查结论:** 模型识别两次访问后仍将 last visit 解释为最近一次；gold 却要求两次日期。
- **qwen3vl2b_sgm (0.0000):** 2024-08-19, Baihua Traditional Dessert Shop
  - Judge: The prediction gives one of the two ground-truth visit dates (2024-08-19) and an English name for the shop but omits the earlier date (27 March 2023) and the exact Chinese shop name. Because it does not fully match the ground truth, accuracy is false.
- **mimo_v25_sgm (0.0000):** Unknown
  - Judge: The prediction 'Unknown' does not answer the question asking for the shop name and exact last visit dates. Ground truth gives a specific name and two dates, so the model output conflicts with that (fails to provide the required information).
- **mimo_v25_raw (0.0000):** Based on the evidence provided:<br>
<br>
1.  **Shop Name**: Evidence 3 shows the storefront with the sign "BAIHUA TRADITIONAL DESSERT SHOP" (百花传统甜品店).<br>
2.  **Last Visit Date**: The evidence contains timestamps for visits on 2023-03-27 (Evidence 1 and 2) and 2024-08-19 (Evidence 3). The latest date is 2024-08-19.<br>
<br>
**Answer**: 2024-08-19, Baihua Traditional Dessert Shop
  - Judge: The prediction names the shop correctly (百花传统甜品店) but gives only one of the two most recent visit dates (returned 2024-08-19 but omitted 2023-03-27). Ground truth lists both 27 March 2023 and 19 August 2024, so the prediction does not fully match.

### 25. `7b24dbf3-dbe0-4382-9e9c-996cf614657e` — A

- **Question:** Which European countries have I visted?
- **Gold:** United Kingdom, Spain, Portugal, Hungary, France, Italy.
- **复查结论:** Qwen 对 open_end 的国家问题输出 evidence IDs，MiMo 则输出国家并答对。
- **qwen3vl2b_sgm (0.0000):** 20220917_134113, 20240930_180605, 20241021_134620, 20250208_123453, 20250223_132602, 20250407_201317
  - Judge: The prediction lists filenames/timestamps, not country names. It does not answer which European countries were visited, so it fails to match the ground truth list of countries. Therefore accuracy is false.
- **mimo_v25_sgm (1.0000):** England, Italy, Spain, France, Portugal, Hungary
  - Judge: The prediction lists England, Italy, Spain, France, Portugal, Hungary. Ground truth lists United Kingdom, Spain, Portugal, Hungary, France, Italy. England is part of the United Kingdom, so the sets match semantically. Order differs but that's allowed. Therefore the prediction matches the ground truth.
- **mimo_v25_raw (1.0000):** United Kingdom, Italy, Spain, France, Portugal, Hungary
  - Judge: The prediction lists the same six countries as the ground truth, just in a different order. All ground-truth items are present and there are no extras or omissions, so it matches exactly.

### 26. `716095fa-6f76-4f19-95e4-3c8bf079fbdd` — E

- **Question:** Help me recall all of my sheep related photo ids in Newcastle.
- **Gold:** 20230905_144627, 20230905_152531, 20230906_155344, 20230906_121455, 20230906_121206, 20230905_153627, 20230905_153314, 20230905_152605
- **复查结论:** Qwen SGM 和 MiMo Raw 复制全部 8 个 Oracle IDs 获得 1.0，但若干 SGM 项并未暴露 sheep 语义。
- **qwen3vl2b_sgm (1.0000):** 20230905_144627, 20230905_152531, 20230905_152605, 20230905_153314, 20230905_153627, 20230906_121206, 20230906_121455, 20230906_155344
- **mimo_v25_sgm (0.6250):** 20230905_144627, 20230905_152531, 20230905_152605, 20230906_121206, 20230906_155344
- **mimo_v25_raw (1.0000):** 20230905_144627, 20230905_152531, 20230905_152605, 20230905_153314, 20230905_153627, 20230906_121206, 20230906_121455, 20230906_155344

### 29. `17b8b612-213a-4ab3-87f9-356b8cf0d7e5` — B

- **Question:** During my recent trip to Egypt, I remember staying at some Sofitel-branded hotels and having a very good experience. Could you remind me which hotels these were?
I also recall taking a nice timelapse at one of the hotels, could you help me identify which hotel it was taken at and the ID of that timelapse?
- **Gold:** The Sofitel hotels you stayed at were Sofitel Winter Palace Luxor and Sofitel Legend Old Cataract Aswan.
The timelapse was taken at Sofitel Winter Palace Luxor, and the ID of the timelapse is 20240801_201540.
- **复查结论:** MiMo 使用证据中的 Sofitel Legend Winter Palace Hotel 名称并给出正确 ID；judge 将该证据内名称称为错误。不过回答没有显式说明 timelapse 属于哪家酒店，因此 false verdict 仍有独立依据。
- **qwen3vl2b_sgm (0.0000):** Sofitel Legend Winter Palace Hotel, 0, Kornish Al Nile Street, Luxor City, Luxor, 85951, Egypt<br>
Sofitel Legend Old Cataract Aswan Hotel, 81511, Al Fanadq Street, Taqouk Mountain, Aswan, 81529, Egypt<br>
<br>
20240731_155548, 20240801_201540
  - Judge: The prediction lists two Sofitel properties: one is named incorrectly as 'Sofitel Legend Winter Palace Hotel' instead of 'Sofitel Winter Palace Luxor' (name mismatch) but includes Old Cataract Aswan correctly. It also provides three timelapse IDs; only one of them (20240801_201540) matches the ground truth. Because of the incorrect hotel name and extra/unverified timelapse IDs, the prediction does not fully match the ground truth.
- **mimo_v25_sgm (0.0000):** Sofitel Legend Winter Palace Hotel, Sofitel Legend Old Cataract Aswan Hotel; 20240801_201540
  - Judge: The prediction misnames one hotel: it lists "Sofitel Legend Winter Palace" instead of the correct "Sofitel Winter Palace Luxor" (adding "Legend" and altering name). It correctly includes Sofitel Legend Old Cataract Aswan and the timelapse ID matches. Because one hotel name is incorrect, accuracy is false.
- **mimo_v25_raw (0.0000):** Sofitel Legend Winter Palace Hotel, Sofitel Legend Old Cataract Aswan Hotel; 20240801_201540
  - Judge: The prediction lists 'Sofitel Legend Winter Palace Hotel' which conflicts with the ground truth 'Sofitel Winter Palace Luxor' (name mismatch). It correctly includes 'Sofitel Legend Old Cataract Aswan' and the timelapse ID matches. Because one hotel name does not match exactly, accuracy is false.

### 30. `361fef09-dbcc-4a68-aed2-187f9728b792` — A

- **Question:** I just returned from the first day of ECCV 2024. Help me gather all the interesting papers I discovered today and list their titles.
- **Gold:** Safe-CLIP removing NSFW Concepts from VLM,  Towards Surprising Video Comprehension, Learning Anomalies with Normality Prior for Unsupervised Video Anomaly Detection, 3x2: 3D Object Part Segmentation by 2D Semantic Correspondences, Camera Calibration using a Collimator System, DSMix: Distortion-Induced Sensitivity Map Based Pre-training for No-Reference Image Quality Assessment, EA-VTR: Event-Aware Video-Text Retrieval, PosterLlama: Bridging Design Ability of Language Model to Contents-Aware Layout Generation, CTRLorALTer: Conditional LoRAdapter for Efficient 0-Shot Control & Altering of T2I Models, PreciseControl: Enhancing Text-To-Image Diffusion Models with Fine-Grained Attribute Control, Efficient Pre-Training for Localized Instruction Generation of Videos, Commonly Interesting Images
- **复查结论:** Qwen 对 open_end 的论文标题问题输出 evidence IDs，MiMo 输出标题并答对。
- **qwen3vl2b_sgm (0.0000):** 20241001_171053, 20241001_173039, 20241001_174058, 20241001_175310, 20241001_180247, 20241001_181259, 20241001_182544, 20241001_183401, 20241001_184112, 20241001_184155, 20241001_184633, 20241001_184746
  - Judge: The prediction lists timestamps/IDs, not paper titles, so it fails to answer the request. It does not match any of the given ground-truth paper titles, therefore accuracy is false.
- **mimo_v25_sgm (1.0000):** Safe-CLIP: Removing NSFW Concepts from Vision-and-Language Models, Learning Anomalies with Normality Prior for Unsupervised Video Anomaly Detection, Towards Surprising Video Comprehension, 3x2: 3D Object Part Segmentation by 2D Semantic Correspondences, Camera Calibration using a Collimator System, DSMix: Distortion-Induced Sensitivity Map Based Pre-training for No-Reference Image Quality Assessment, EA-VTR: Event-Aware Video-Text Retrieval, PosterLlama: Bridging Design Ability of Language Model to Contents-Aware Layout Generation, CTRLorAltEr: Conditional LoRA Adapter for Efficient 0-Shot Control & Altering of T2I Models, PreciseControl: Enhancing Text-To-Image Diffusion Models with Fine-Grained Attribute Control, Efficient Pre-Training For Localized Instruction Generation Of Videos, Commonly Interesting Images
  - Judge: The prediction lists titles matching the user's request. Comparing to ground truth, all titles appear present and correspond closely. Minor differences are capitalization and small naming variants (e.g., 'Safe-CLIP: Removing NSFW Concepts from Vision-and-Language Models' vs 'Safe-CLIP removing NSFW Concepts from VLM', and 'CTRLorAltEr' vs 'CTRLorALTer'), but these do not change content. Therefore the prediction matches the ground truth.
- **mimo_v25_raw (1.0000):** Safe-CLIP: Removing NSFW Concepts from Vision-and-Language Models, Learning Anomalies with Normality Prior for Unsupervised Video Anomaly Detection, Towards Surprising Video Comprehension, 3x2: 3D Object Part Segmentation by 2D Semantic Correspondences, Camera Calibration using a Collimator System, DSMix: Distortion-Induced Sensitivity Map Based Pre-training for No-Reference Image Quality Assessment, EA-VTR: Event-Aware Video-Text Retrieval, PosterLlama: Bridging Design Ability of Language Model to Contents-Aware Layout Generation, CTRLorALTer: Conditional LoRAAdapter for Efficient 0-Shot Control & Altering of T2I Models, PreciseControl: Enhancing Text-To-Image Diffusion Models with Fine-Grained Attribute Control, Efficient Pre-Training For Localized Instruction Generation Of Videos, Commonly Interesting Images
  - Judge: The prediction lists the same papers as the ground truth with matching titles (minor punctuation/capitalization differences only). All ground-truth items are present and no extra items were added, so it matches.

## Provenance

- `qwen3vl2b_sgm` predictions: `/home/orion/research_artifacts/frozen_behavior/qwen3vl2b-hard-c0-c1-v1/C0/predictions.jsonl`
  - SHA256: `5904069c9c245b1ff24247c0cfcedebbb2b9c4555634c581c0adfab687ae0a7c`
- `qwen3vl2b_sgm` evaluation: `/home/orion/research_artifacts/frozen_behavior/qwen3vl2b-hard-c0-c1-v1/C0/evaluations/atm-primary-gpt5mini-stable-v1/atm_gpt-5-mini_stable.json`
  - SHA256: `d4e93fcae242926ee2fefe31d4a5936f77507ce3075cb503b25049bb2ab26a5a`
- `mimo_v25_sgm` predictions: `/home/orion/research_artifacts/frozen_behavior/mimo-v25-legacy-oracle-v1/sgm/predictions.jsonl`
  - SHA256: `eb6be94d8eaa92a90fd2d17ceeba0ecb4e8d6f1644ebfbe78410eda00a153f9b`
- `mimo_v25_sgm` evaluation: `/home/orion/research_artifacts/frozen_behavior/mimo-v25-legacy-oracle-v1/sgm/evaluations/atm-primary-gpt5mini-stable-v1/atm_gpt-5-mini_stable.json`
  - SHA256: `d44a232d8759c71102e16bef7e106eb7a42d5f6a39fe827df774ead8550fa746`
- `mimo_v25_raw` predictions: `/home/orion/research_artifacts/frozen_behavior/mimo-v25-legacy-oracle-v1/raw/predictions.jsonl`
  - SHA256: `4db3f2603b333fb441a20766028c28fce73c62ea894055078ede4bdbca30db8f`
- `mimo_v25_raw` evaluation: `/home/orion/research_artifacts/frozen_behavior/mimo-v25-legacy-oracle-v1/raw/evaluations/atm-primary-gpt5mini-stable-v1/atm_gpt-5-mini_stable.json`
  - SHA256: `e7a2bcf51fdab3c8157d1ae1a8996bf1a5104c740f39ffcc968beaf12a153943`
