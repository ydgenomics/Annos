# PhytoScope：植物单细胞可解释注释框架 — 项目设计书

## 一、项目概述与核心理念

PhytoScope 是一个专为植物单细胞转录组数据设计的**可解释、多专家证据整合的注释框架**。其核心哲学是：**注释是一个可审计的论证过程，而非一个黑箱输出的标签。**

框架整合了：
- 大语言模型（LLM）策划的先验知识库
- 多种主流及前沿的自动注释算法
- 一个创新的多专家 AI 审查系统

最终交付一个**交互式 HTML 报告**，其中每个细胞类型的决策都通过"解剖学背景 → 标记基因验证 → 跨算法共识"的透明证据链进行解释。

---

## 二、系统架构与数据流

系统分为五个核心层次，以 `PhytoScope.py` 为主控脚本，通过 `config.yaml` 统一配置。

### 1. 输入层
- 接受已分群的 **h5ad** 文件（scanpy AnnData 格式）
- 用户提供分群键（`cluster_key`）和可选的降维键（`reduction_key`）

### 2. 预处理与特征工程层
- **数据重标准化**：确保下游分析的数据一致性
- **差异基因分析**：调用 scanpy 的 `sc.tl.rank_genes_groups()`，根据设定的 `p_val_adj` 和 `log2FC` 阈值筛选标记基因
- **同源基因映射**：对非模式物种，通过同源比对（如 BLASTx, OrthoFinder）获取 `orth_gene` 列，映射到拟南芥等模式物种

### 3. 核心注释引擎层（多算法并行）

#### 基于标记基因
- 过滤后的标记基因通过点图、小提琴图进行可视化验证
- 通过 `sc.tl.score_genes()` 计算功能富集分数
- **scType**：重写或封装核心逻辑，基于细胞类型特异性标记基因集评分

#### 基于参考映射（两种互补方案）

| 维度 | `pip install singler` | `scArches` |
|------|----------------------|------------|
| **维护方** | SingleR 官方团队（C++ 实现，Python 绑定） | scverse 社区 |
| **版本** | v0.5.0（2026-01 发布） | 活跃更新 |
| **核心原理** | 基于**表达谱相关性**——计算 query 与参考细胞/类别的 Spearman 相关性，迭代筛选标记基因 | 基于**条件变分自编码器 (cVAE)**——学习参考数据的潜空间，映射后分类 |
| **输入格式** | `SingleCellExperiment`（需 `singlecellexperiment` 包） | `AnnData`（与 scanpy 原生集成） |
| **参考数据** | 需要带标签的参考，可通过 `celldex` 获取内置参考 | 需要带标签的参考，需训练 cVAE 模型 |
| **速度** | **快**——C++ 底层，无需训练 | **较慢**——需要训练，GPU 推荐 |
| **Batch 校正** | ❌ 不支持 | ✅ **核心优势** |
| **跨物种** | ❌ 弱——依赖基因交集 | ✅ 强——潜空间对齐 |
| **多参考整合** | ✅ 支持 `annotate_integrated()` 整合多个参考 | ✅ 支持多参考 |
| **与 scanpy 集成** | ⚠️ 需通过 `singlecellexperiment` 转换 | ✅ 原生 AnnData |
| **植物适用性** | 需自行准备植物参考数据集 | 需自行准备植物参考数据集 |
| **定位** | **默认**——快速、同物种、有高质量参考时首选 | **进阶**——跨物种/跨 batch、需要模型复用时选用 |

#### 跨物种映射（进阶）
- 部署离线的 XSpeciesSpaner
- 集成 SAMap 或 SATURN，利用同源基因网络进行跨物种细胞映射

#### 基于大语言模型
- 集成 scPlantLLM 或 scPlantAnnotate，利用 LLM 的文本知识进行注释

### 4. 分析与审查层
- **基因集富集分析**（基于 GSEApy）：
  - 方案一：内置拟南芥功能注释背景库，直接对 `orth_gene` 进行富集
  - 方案二：支持用户导入自定义 `db.gz` 文件建库进行富集
  - 支持接入 **eggnog-mapper** 输出：`*.emapper.annotations` 中的 GOs / KEGG_ko 列可直接构建 GSEApy 基因集字典
- **元细胞（Metacell）策略**：为提升参考映射算法的信噪比和效率，需评估并集成 Metacell 构建流程

### 5. 报告生成与交互层（Quarto）
- 将背景知识、算法参数、中间结果、可视化图表整理进 Quarto 文档
- 渲染为**交互式 HTML 报告**

---

## 三、多专家 AI 审查系统与交互设计

这是 PhytoScope 区别于其他工具的核心创新点，旨在模拟同行评议过程，提供深度解读。

### 1. 前端交互设计（嵌入 Quarto HTML）

**选项卡布局：**
- **总结面板**：提供最终结论、可编辑的综合报告区域
- **中间结果面板**：展示各注释算法的原始输出、图表、富集分析结果
- **AI 审查面板**：展示多个 LLM "专家"的实时审查意见

**用户输入区**：允许用户在审查面板中修改提示词，重新提问

**结果管理：**
- API 结果同时显示在 AI 审查面板和总结面板
- 总结面板内容可由用户手动自由编辑，且此编辑操作独立，不会回溯修改 AI 审查面板的原始记录

### 2. 豆包 API 调用框架（JS 代码设计）

---

## 四、项目目录结构与工程化

### 目录结构

```
phytoscope/
├── PhytoScope.py                  # 主控脚本（入口）
├── config.yaml                    # 统一配置文件
├── env_setup.sh                   # Conda 环境配置脚本
├── requirements.txt               # Python 依赖清单
├── README.md                      # 项目说明
│
├── phytoscope/                    # 核心 Python 包
│   ├── __init__.py
│   │
│   ├── core/                      # 核心流程编排
│   │   ├── __init__.py
│   │   ├── pipeline.py            # 主流程控制（按 config 调度各模块）
│   │   ├── config_loader.py       # config.yaml 解析与校验
│   │   └── exceptions.py          # 自定义异常
│   │
│   ├── input/                     # 输入层
│   │   ├── __init__.py
│   │   ├── reader.py              # 读取 h5ad，校验 AnnData 结构
│   │   └── validator.py           # 验证 cluster_key / reduction_key 等
│   │
│   ├── preprocessing/             # 预处理与特征工程层
│   │   ├── __init__.py
│   │   ├── normalize.py           # 数据重标准化
│   │   ├── markers.py             # 差异基因分析（rank_genes_groups）
│   │   └── orthology.py           # 同源基因映射（BLASTx / OrthoFinder 调用）
│   │
│   ├── annotation/                # 核心注释引擎层
│   │   ├── __init__.py
│   │   ├── base.py                # 注释器基类（统一接口）
│   │   ├── sctype.py              # scType 注释
│   │   ├── singler_annotator.py   # singler (pip) 注释
│   │   ├── scarches_annotator.py  # scArches 注释
│   │   ├── xspecies.py            # XSpeciesSpaner 跨物种映射
│   │   ├── samap_annotator.py     # SAMap 跨物种映射
│   │   ├── llm_annotator.py       # LLM 注释（scPlantLLM / scPlantAnnotate）
│   │   └── ensemble.py            # 多算法结果整合与共识打分
│   │
│   ├── analysis/                  # 分析与审查层
│   │   ├── __init__.py
│   │   ├── enrichment.py          # GSEApy 富集分析
│   │   ├── metacell.py            # Metacell 构建
│   │   └── score_genes.py         # 基因集评分（sc.tl.score_genes）
│   │
│   ├── report/                    # 报告生成层
│   │   ├── __init__.py
│   │   ├── report.qmd             # Quarto 主模板
│   │   ├── _quarto.yml            # Quarto 配置
│   │   ├── report_utils.py        # Python → Quarto 数据导出工具
│   │   └── templates/             # Quarto 子模板
│   │       ├── summary.qmd        # 总结面板
│   │       ├── results.qmd        # 中间结果面板
│   │       └── ai_review.qmd      # AI 审查面板
│   │
│   └── utils/                     # 工具函数
│       ├── __init__.py
│       ├── logger.py              # 日志配置
│       ├── io_utils.py            # 文件读写工具
│       └── plot_utils.py          # 可视化工具（点图、小提琴图等）
│
├── scripts/                       # 独立脚本
│   ├── run_pipeline.sh            # 一键运行脚本
│   ├── precompute_qc.py           # QC 预计算（可选前置步骤）
│   └── download_ref.py            # 参考数据集下载工具
│
├── data/                          # 数据目录（用户放置）
│   ├── input/                     # 输入 h5ad
│   ├── reference/                 # 参考数据集
│   └── orthology/                 # 同源基因映射结果
│
├── configs/                       # 预设配置文件
│   ├── config.default.yaml        # 默认配置
│   └── config.plant.yaml          # 植物专用预设
│
├── tests/                         # 单元测试
│   ├── __init__.py
│   ├── test_input.py
│   ├── test_preprocessing.py
│   ├── test_annotation.py
│   └── test_analysis.py
│
├── docs/                          # 文档
│   ├── usage.md                   # 使用说明
│   └── algorithm.md               # 算法说明
│
└── output/                        # 输出目录（自动生成）
    ├── markers/                   # 差异基因结果
    ├── annotation/                # 各算法注释结果
    ├── enrichment/                # 富集分析结果
    ├── figures/                   # 可视化图表
    └── report/                    # 最终 HTML 报告
```

### 环境管理

统一 Conda 环境（纯 Python，无需 R）：

| 环境名称 | 用途 | 关键包 |
| --- | --- | --- |
| `phytoscope-py` | Python 注释引擎 | scanpy, pysctype, singler, scarches, samap, gseapy, quarto |
| `phytoscope-sys` | 系统工具 | blast, orthofinder, diamond, mafft |

**核心依赖安装：**
```bash
# Python 注释引擎
pip install singlecellexperiment
pip install singler
pip install scarches
pip install pysctype
pip install samap
pip install gseapy

# 系统工具 (conda)
conda install -c bioconda blast orthofinder diamond mafft
```

### 数据流与目录对应关系

```text
输入层                   预处理层                  注释引擎层                分析层              报告层
data/input/     →   preprocessing/       →   annotation/           →   analysis/       →   report/
  adata.h5ad          normalize.py            sctype.py               enrichment.py       report.qmd
                      markers.py              singler_annotator.py    metacell.py         → output/report/
                      orthology.py            scarches_annotator.py                       index.html
                                              ensemble.py
```