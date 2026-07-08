# Related Work Citation 原文

依据：`references.md` 当前 32 个 reference。

标注规则：

- **作者自标**：来自论文/项目官方 README、项目页或论文页给出的 citation block。
- **arXiv fallback**：未找到作者自标 citation，暂用 arXiv 官方 BibTeX；正式写 references 前还应再查论文 PDF、OpenReview、PMLR/ACL/ACM 页面。
- **无论文 citation**：当前只找到工程项目或产品页，没有可引用论文条目。

## 覆盖统计

| 状态 | 数量 |
| --- | ---: |
| 作者/官方自标 citation 已找到 | 11 |
| 未找到作者自标，暂用 arXiv fallback | 20 |
| 无论文 citation | 1 |
| **合计** | **32** |

## 作者/官方自标 Citation 已找到

### AdaMEM

来源：`https://github.com/yunx-z/AdaMEM` README Citation。

```bibtex
@inproceedings{zhang2026adamem,
  title     = {{AdaMEM}: Test-Time Adaptive Memory for Language Agents},
  author    = {Zhang, Yunxiang and Li, Yiheng and Payani, Ali and Wang, Lu},
  booktitle = {Proceedings of the 43rd International Conference on Machine Learning},
  series    = {Proceedings of Machine Learning Research},
  year      = {2026},
}
```

### A-Mem

来源：`https://github.com/WujiangXu/A-mem` README Citation。

```bibtex
@inproceedings{xu2025amem,
  title={A-Mem: Agentic memory for llm agents},
  author={Xu, Wujiang and Liang, Zujie and Mei, Kai and Gao, Hang and Tan, Juntao and Zhang, Yongfeng},
  booktitle={Advances in Neural Information Processing Systems},
  year={2025}
}
```

### mem0

来源：`https://github.com/mem0ai/mem0` README Citation。

```bibtex
@article{mem0,
  title={Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory},
  author={Chhikara, Prateek and Khant, Dev and Aryan, Saket and Singh, Taranjeet and Yadav, Deshraj},
  journal={arXiv preprint arXiv:2504.19413},
  year={2025}
}
```

### MemoryOS

来源：`https://github.com/BAI-LAB/MemoryOS` README Citation。

```bibtex
@misc{kang2025memoryosaiagent,
      title={Memory OS of AI Agent}, 
      author={Jiazheng Kang and Mingming Ji and Zhe Zhao and Ting Bai},
      year={2025},
      eprint={2506.06326},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2506.06326}, 
}
```

### HippoRAG

来源：`https://github.com/OSU-NLP-Group/HippoRAG` README Citation。

```bibtex
@inproceedings{gutiérrez2024hipporag,
      title={HippoRAG: Neurobiologically Inspired Long-Term Memory for Large Language Models}, 
      author={Bernal Jiménez Gutiérrez and Yiheng Shu and Yu Gu and Michihiro Yasunaga and Yu Su},
      booktitle={The Thirty-eighth Annual Conference on Neural Information Processing Systems},
      year={2024},
      url={https://openreview.net/forum?id=hkujvAPVsg}
}
```

### HippoRAG 2 / From RAG to Memory

来源：`https://github.com/OSU-NLP-Group/HippoRAG` README Citation。

```bibtex
@misc{gutiérrez2025ragmemorynonparametriccontinual,
      title={From RAG to Memory: Non-Parametric Continual Learning for Large Language Models}, 
      author={Bernal Jiménez Gutiérrez and Yiheng Shu and Weijian Qi and Sizhe Zhou and Yu Su},
      year={2025},
      eprint={2502.14802},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2502.14802}, 
}
```

### SimpleMem

来源：`https://github.com/aiming-lab/SimpleMem` README Citation。

```bibtex
@article{simplemem2026,
  title={SimpleMem: Efficient Lifelong Memory for LLM Agents},
  author={Liu, Jiaqi and Su, Yaofeng and Xia, Peng and Zhou, Yiyang and Han, Siwei and  Zheng, Zeyu and Xie, Cihang and Ding, Mingyu and Yao, Huaxiu},
  journal={arXiv preprint arXiv:2601.02553},
  year={2026},
  url={https://arxiv.org/abs/2601.02553}
}
```

### Mnemis

来源：本地 `Mnemis/README.md` Citation。

```bibtex
@inproceedings{tang2026mnemis,
  title     = {Mnemis: Dual-Route Retrieval on Hierarchical Graphs for Long-Term LLM Memory},
  author    = {Tang, Zihao and Yu, Xin and Xiao, Ziyu and Wen, Zengxuan and Li, Zelin and Zhou, Jiaxi and Wang, Hualei and Wang, Haohua and Huang, Haizhen and Deng, Weiwei and Sun, Feng and Zhang, Qi},
  booktitle = {Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (ACL 2026)},
  year      = {2026},
  address   = {San Diego, California, USA},
  publisher = {Association for Computational Linguistics},
  note      = {Accepted to ACL 2026 Main Conference},
  url       = {https://arxiv.org/abs/2602.15313}
}
```

### Entity Collision

来源：`https://github.com/youwangd/engram` README Citation。

```bibtex
@misc{deng2026entity,
  title={Entity-Collision: A Stratified Protocol for Attributing Retrieval Lift in Agent Memory},
  author={Deng, Youwang},
  year={2026},
  eprint={2605.29630},
  archivePrefix={arXiv},
  primaryClass={cs.CL},
  url={https://arxiv.org/abs/2605.29630}
}
```

### MemTrace

来源：`https://github.com/zjunlp/MemTrace` README Citation。

```bibtex
@misc{deng2026memtracetracingattributingerrors,
      title={MemTrace: Tracing and Attributing Errors in Large Language Model Memory Systems}, 
      author={Xinle Deng and Ruobin Zhong and Hujin Peng and Xiaoben Lu and Yanzhe Wu and Guang Li and Buqiang Xu and Yunzhi Yao and Jizhan Fang and Haoliang Cao and Junjie Guo and Yuan Yuan and Ziqing Ma and Yuanqiang Yu and Rui Hu and Baohua Dong and Hangcheng Zhu and Ningyu Zhang},
      year={2026},
      eprint={2605.28732},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2605.28732}, 
}
```

### ATM-Bench / According to Me

来源：本地 `ATM-Bench/README.md` Citation。

```bibtex
@article{mei2026atm,
  title={According to Me: Long-Term Personalized Referential Memory QA},
  author={Mei, Jingbiao and Chen, Jinghong and Yang, Guangyu and Hou, Xinyu and Li, Margaret and Byrne, Bill},
  journal={arXiv preprint arXiv:2603.01990},
  year={2026},
  url={https://arxiv.org/abs/2603.01990},
  doi={10.48550/arXiv.2603.01990}
}
```

## 未找到作者自标，暂用 arXiv Fallback

### Experience Compression Spectrum

```bibtex
@misc{zhang2026experiencecompressionspectrumunifying,
      title={Experience Compression Spectrum: Unifying Memory, Skills, and Rules in LLM Agents}, 
      author={Xing Zhang and Guanghui Wang and Yanwei Cui and Wei Qiu and Ziyuan Li and Bing Zhu and Peiyang He},
      year={2026},
      eprint={2604.15877},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2604.15877}, 
}
```

### Externalization in LLM Agents

```bibtex
@misc{zhou2026externalizationllmagentsunified,
      title={Externalization in LLM Agents: A Unified Review of Memory, Skills, Protocols and Harness Engineering}, 
      author={Chenyu Zhou and Huacan Chai and Wenteng Chen and Zihan Guo and Rong Shan and Yuanyi Song and Tianyi Xu and Yingxuan Yang and Aofan Yu and Weiming Zhang and Congming Zheng and Jiachen Zhu and Zeyu Zheng and Zhuosheng Zhang and Xingyu Lou and Changwang Zhang and Zhihui Fu and Jun Wang and Weiwen Liu and Jianghao Lin and Weinan Zhang},
      year={2026},
      eprint={2604.08224},
      archivePrefix={arXiv},
      primaryClass={cs.SE},
      url={https://arxiv.org/abs/2604.08224}, 
}
```

### Overcoming the Impedance Mismatch

```bibtex
@misc{dhayalkar2026overcomingimpedancemismatchtheoretical,
      title={Overcoming the Impedance Mismatch: A Theoretical Roadmap for Fusing Foundation Models and Knowledge Graphs}, 
      author={Sahil Rajesh Dhayalkar},
      year={2026},
      eprint={2606.15656},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2606.15656}, 
}
```

### GSW / Beyond Fact Retrieval

```bibtex
@misc{rajesh2026factretrievalepisodicmemory,
      title={Beyond Fact Retrieval: Episodic Memory for RAG with Generative Semantic Workspaces}, 
      author={Shreyas Rajesh and Pavan Holur and Chenda Duan and David Chong and Vwani Roychowdhury},
      year={2026},
      eprint={2511.07587},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2511.07587}, 
}
```

### StructMem

```bibtex
@misc{xu2026structmemstructuredmemorylonghorizon,
      title={StructMem: Structured Memory for Long-Horizon Behavior in LLMs}, 
      author={Buqiang Xu and Yijun Chen and Jizhan Fang and Ruobin Zhong and Yunzhi Yao and Yuqi Zhu and Lun Du and Shumin Deng},
      year={2026},
      eprint={2604.21748},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2604.21748}, 
}
```

### LinkedIn Hierarchical Long-Term Semantic Memory

```bibtex
@misc{xu2026hierarchicallongtermsemanticmemory,
      title={Hierarchical Long-Term Semantic Memory for LinkedIn's Hiring Agent}, 
      author={Zhentao Xu and Shangjin Zhang and Emir Poyraz and Yvonne Li and Ye Jin and Xie Lu and Xiaoyang Gu and Karthik Ramgopal and Praveen Kumar Bodigutla and Xiaofeng Wang},
      year={2026},
      eprint={2604.26197},
      archivePrefix={arXiv},
      primaryClass={cs.IR},
      doi={https://doi.org/10.1145/3770855.3818432},
      url={https://arxiv.org/abs/2604.26197}, 
}
```

### HiGMem

```bibtex
@misc{cao2026higmemhierarchicalllmguidedmemory,
      title={HiGMem: A Hierarchical and LLM-Guided Memory System for Long-Term Conversational Agents}, 
      author={Shuqi Cao and Jingyi He and Fei Tan},
      year={2026},
      eprint={2604.18349},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2604.18349}, 
}
```

### APEX-MEM

```bibtex
@misc{banerjee2026apexmemagenticsemistructuredmemory,
      title={APEX-MEM: Agentic Semi-Structured Memory with Temporal Reasoning for Long-Term Conversational AI}, 
      author={Pratyay Banerjee and Masud Moshtaghi and Shivashankar Subramanian and Amita Misra and Ankit Chadha},
      year={2026},
      eprint={2604.14362},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2604.14362}, 
}
```

### HyperMem

```bibtex
@misc{yue2026hypermemhypergraphmemorylongterm,
      title={HyperMem: Hypergraph Memory for Long-Term Conversations}, 
      author={Juwei Yue and Chuanrui Hu and Jiawei Sheng and Zuyi Zhou and Wenyuan Zhang and Tingwen Liu and Li Guo and Yafeng Deng},
      year={2026},
      eprint={2604.08256},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2604.08256}, 
}
```

### VikingMem

```bibtex
@misc{fu2026vikingmemmemorybasemanagement,
      title={VikingMem: A Memory Base Management System for Stateful LLM-based Applications}, 
      author={Jiajie Fu and Junwen Chen and Mengzhao Wang and Aoxiang He and Maojia Sheng and Xiangyu Ke and Yifan Zhu and Yunjun Gao},
      year={2026},
      eprint={2605.29640},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2605.29640}, 
}
```

### Memory is Reconstructed, Not Retrieved / MRAgent

```bibtex
@misc{ji2026memoryreconstructedretrievedgraph,
      title={Memory is Reconstructed, Not Retrieved: Graph Memory for LLM Agents}, 
      author={Shuo Ji and Yibo Li and Bryan Hooi},
      year={2026},
      eprint={2606.06036},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2606.06036}, 
}
```

### GrepSeek

```bibtex
@misc{salemi2026grepseektrainingsearchagents,
      title={GrepSeek: Training Search Agents for Direct Corpus Interaction}, 
      author={Alireza Salemi and Chang Zeng and Atharva Nijasure and Jui-Hui Chung and Razieh Rahimi and Fernando Diaz and Hamed Zamani},
      year={2026},
      eprint={2605.29307},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2605.29307}, 
}
```

### TruthfulRAG

```bibtex
@misc{liu2025truthfulragresolvingfactuallevelconflicts,
      title={TruthfulRAG: Resolving Factual-level Conflicts in Retrieval-Augmented Generation with Knowledge Graphs}, 
      author={Shuyi Liu and Yuming Shang and Xi Zhang},
      year={2025},
      eprint={2511.10375},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2511.10375}, 
}
```

### STALE

说明：本地 `STALE/README.md`、`STALE/STALE/README.md`、`STALE/cup_mem/README.md` 未找到 citation block。

```bibtex
@misc{chao2026stalellmagentsknow,
      title={STALE: Can LLM Agents Know When Their Memories Are No Longer Valid?}, 
      author={Hanxiang Chao and Yihan Bai and Rui Sheng and Tianle Li and Yushi Sun},
      year={2026},
      eprint={2605.06527},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2605.06527}, 
}
```

### MemConflict

```bibtex
@misc{tao2026memconflictevaluatinglongtermmemory,
      title={MemConflict: Evaluating Long-Term Memory Systems Under Memory Conflicts}, 
      author={Zhen Tao and Jinxiang Zhao and Peng Liu and Dinghao Xi and Yanfang Chen and Wei Xu and Zhiyu Li},
      year={2026},
      eprint={2605.20926},
      archivePrefix={arXiv},
      primaryClass={cs.IR},
      url={https://arxiv.org/abs/2605.20926}, 
}
```

### MedMemoryBench

```bibtex
@misc{wang2026medmemorybenchbenchmarkingagentmemory,
      title={MedMemoryBench: Benchmarking Agent Memory in Personalized Healthcare}, 
      author={Yihao Wang and Haoran Xu and Renjie Gu and Yixuan Ye and Xinyi Chen and Xinyu Mu and Yuan Gao and Chunxiao Guo and Peng Wei and Jinjie Gu and Huan Li and Ke Chen and Lidan Shou},
      year={2026},
      eprint={2605.11814},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2605.11814}, 
}
```

### Are LLMs Really Not Knowledgeable?

```bibtex
@misc{tao2026llmsreallyknowledgeablemining,
      title={Are LLMs Really Not Knowledgeable? Mining the Submerged Knowledge in LLMs' Memory}, 
      author={Xingjian Tao and Yiwei Wang and Yujun Cai and Zhicheng Yang and Jing Tang},
      year={2026},
      eprint={2412.20846},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2412.20846}, 
}
```

### SURE-RAG

```bibtex
@misc{qiu2026sureragsufficiencyuncertaintyawareevidence,
      title={SURE-RAG: Sufficiency and Uncertainty-Aware Evidence Verification for Selective Retrieval-Augmented Generation}, 
      author={Jingxi Qiu and Zeyu Han and Cheng Huang},
      year={2026},
      eprint={2605.03534},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2605.03534}, 
}
```

### Substrate Asymmetry in User-Side Memory

说明：`https://github.com/EpistemicaLab/substrate-asymmetry-memory` README 未找到 citation block。

```bibtex
@misc{deng2026substrateasymmetryusersidememory,
      title={Substrate Asymmetry in User-Side Memory: A Diagnostic Framework}, 
      author={Youwang Deng},
      year={2026},
      eprint={2606.11712},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2606.11712}, 
}
```

### SuperMemory-VQA

```bibtex
@misc{alam2026supermemoryvqaegocentricvisualquestionanswering,
      title={SuperMemory-VQA: An Egocentric Visual Question-Answering Benchmark for Long-Horizon Memory}, 
      author={Samiul Alam and Shakhrul Iman Siam and Michael J. Proulx and James Fort and Richard Newcombe and Hyo Jin Kim and Mi Zhang},
      year={2026},
      eprint={2606.00825},
      archivePrefix={arXiv},
      primaryClass={cs.CV},
      url={https://arxiv.org/abs/2606.00825}, 
}
```

## 无论文 Citation

### MemPalace

当前 `references.md` 标注为“无论文，纯工程产品”。未找到论文 citation。后续如果正文引用，建议只在脚注或系统例子中引用 GitHub URL，不放作正式论文 reference，除非找到论文/技术报告。
