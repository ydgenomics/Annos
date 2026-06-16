# 植物单细胞全自动智能注释平台（Plant Cell Annotator）

## 项目详细设计文档

---

**文档版本**：v1.0  
**最后更新**：2026年6月15日  
**项目代号**：PlantAnnotator-Agent

---

## 目录

1. [项目背景与立项依据](#1-项目背景与立项依据)
2. [平台总体架构](#2-平台总体架构)
3. [Skill能力组件详细设计](#3-skill能力组件详细设计)
4. [资源数据库层详细设计](#4-资源数据库层详细设计)
5. [自动化注释方法集成规范](#5-自动化注释方法集成规范)
6. [用户输出与交互设计](#6-用户输出与交互设计)
7. [API接口规范](#7-api接口规范)
8. [项目实施路线图](#8-项目实施路线图)
9. [风险评估与应对策略](#9-风险评估与应对策略)
10. [附录](#10-附录)

---

## 1. 项目背景与立项依据

### 1.1 植物单细胞注释的核心困境

单细胞转录组学正从模式植物向非模式植物迅速扩展，但"细胞注释"始终是整个分析流程中最为关键、最为耗时的瓶颈环节。当前的困境主要体现在三个层面：

#### 1.1.1 通用困境

| 困境类型 | 具体表现 | 影响 |
|:---|:---|:---|
| **标记基因匮乏** | 与动物研究拥有的CellMarker、PanglaoDB等成熟数据库相比，植物界缺乏系统性的细胞标记基因知识库，许多细胞类型缺乏保守、特异的标记基因 | 导致注释高度依赖个人经验，结果不可复现 |
| **发育连续性** | 植物细胞分化常呈现连续谱系（如根尖从干细胞到分化细胞的渐变过程），细胞边界模糊 | "全或无"的离散标记策略失效，注释分辨率受限 |
| **原生质体胁迫** | 植物单细胞测序需要去除细胞壁制备原生质体，此过程引入的胁迫基因表达会模糊真实的生物学信号 | 聚类和注释结果中混入技术噪音 |
| **功能注释不全** | 大量植物基因功能尚未被实验验证，基因组功能注释不完整 | 仅靠同源比对常导致错误的功能推断 |

#### 1.1.2 模式植物的特有难点

以拟南芥（*Arabidopsis thaliana*）和水稻（*Oryza sativa*）为代表的模式植物，虽然研究基础深厚，但面临的是更高层次的挑战：

- **分辨率需求升级**：研究已不满足于将细胞注释为"叶肉细胞"，而需要精确到"远轴端海绵组织叶肉细胞第3亚群"的精细程度。现有知识边界被持续挑战。
- **新细胞状态的定义困境**：如何在注释逻辑上区分"已知细胞类型的新状态"与"全新的细胞类型"，是方法学与认识论上的双重挑战。
- **数据整合复杂性**：多个实验室、多个发育阶段、多种处理条件的数据需要统一注释框架，批次效应与生物学差异的区分成为难题。

#### 1.1.3 非模式植物的更大挑战

对于大多数经济作物、药用植物、林木等非模式物种，困境更加严峻：

| 挑战维度 | 具体表现 |
|:---|:---|
| **基因组资源缺失** | 参考基因组常为草图水平，基因模型不完整，注释质量低 |
| **先验知识近乎空白** | 可能完全不知道某一物种的根尖除了皮层、内皮层，是否还有特化的通气组织或其他未知结构 |
| **标记基因跨物种失效** | 拟南芥中被验证的标记基因，在此物种中可能完全不表达，或表达模式已因进化而改变 |
| **个体间异质性高** | 野生材料、多年生木本植物个体间的遗传和生理差异远大于实验室纯合系，增加了注释噪音 |

### 1.2 细胞注释的重要性：单细胞研究的"翻译中枢"

细胞注释不是简单的分类学练习，而是**将无意义的聚类ID转化为生物学洞察的关键翻译步骤**。其重要性体现在：

1. **比较分析的基石**：不同物种、不同处理、不同发育时期的单细胞图谱比较，全部建立在同源细胞类型被正确识别的前提之上。

2. **新发现的前提条件**：只有明确界定了哪些细胞类型是已知的，才能从逻辑上定义和验证什么是"真正的新细胞类型"。

3. **基因功能的组织锚定**：将特定基因的表达模式"锚定"到特定的细胞类型，才能阐明基因在组织层面的生物学功能。

4. **计算模型的基础标注**：基因调控网络推断、细胞间通讯分析、发育轨迹重建等所有高阶分析，都依赖于准确的细胞身份信息。

### 1.3 项目目标

构建一个从**数据输入到可解释报告输出**的全自动、智能化植物单细胞注释平台。该平台具有以下核心特征：

- **智能体（Agent）驱动**：由大语言模型驱动的智能体自动执行知识检索、工具选择、结果解读等任务
- **多算法集成**：同时运行多种注释算法，进行共识决策
- **知识库支撑**：构建标准化的植物细胞标记基因库、同源基因库、解剖本体库等资源数据库
- **可解释输出**：生成包含细胞身份自然语言描述的交互式HTML报告
- **API化能力**：所有功能通过标准化API暴露，可整合进现有分析管线

---

## 2. 平台总体架构

### 2.1 架构概览

平台采用**四层微服务架构**，将原先的单体流程重构为两大基础设施——**可独立调用的Skill能力组件**和**标准化的资源数据库**。

```
┌─────────────────────────────────────────────────────────┐
│                    用户交互层                            │
│   · Web界面：上传h5ad + 填写元信息 → 在线查看HTML报告    │
│   · API接口：标准化RESTful API，支持管线集成              │
│   · 支持格式：h5ad, h5seurat, loom                      │
└───────────────────────────┬─────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
    ┌─────────▼──────────┐     ┌──────────▼────────────┐
    │   Skill 能力组件层  │     │    资源数据库层        │
    │   (微服务集群)      │◄────│    (标准化数据仓库)    │
    └─────────┬──────────┘     └──────────┬────────────┘
              │                           │
    ┌─────────▼──────────┐     ┌──────────▼────────────┐
    │  计算引擎层         │     │   LLM推理层            │
    │   · 容器化算法运行   │     │   · 知识检索Agent      │
    │   · GPU/CPU资源调度  │     │   · 共识解读Agent      │
    │   · 并行任务管理     │     │   · 报告生成Agent      │
    └────────────────────┘     └───────────────────────┘
```

### 2.2 核心设计原则

| 原则 | 说明 |
|:---|:---|
| **组件松耦合** | 每个Skill和数据库独立部署、独立版本控制、独立扩展 |
| **知识资产化** | 文献挖掘和专家知识以结构化数据库形式沉淀，避免重复劳动 |
| **算法可插拔** | 新注释算法可通过标准接口快速集成，不影响已有流程 |
| **结果可复现** | 全程记录软件版本、数据库版本、参数设置、随机种子 |
| **植物优先** | 所有设计和优化均以植物单细胞数据的特殊性为出发点 |

### 2.3 系统数据流

```
用户输入: {h5ad文件, 物种学名, 组织部位, [可选参数]}
    │
    ▼
┌──────────────────────────────────────────────┐
│  步骤1：知识检索 Skill                        │
│  ┌──────────────────────────────────────┐    │
│  │ · 查询标记基因库 → 获取候选标记基因集  │    │
│  │ · 查询解剖本体库 → 获取组织细胞组成     │    │
│  │ · 查询图谱索引库 → 定位可用参考图谱     │    │
│  │ · 查询同源基因库 → 跨物种标记基因映射   │    │
│  │ · 可选：PubMed实时检索 → 补充最新文献   │    │
│  └──────────────────────────────────────┘    │
│  输出：标准化 knowledge_json                   │
└─────────────────────┬────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────┐
│  步骤2：多算法注释 Skill（并行执行）            │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌───────┐ │
│  │SingleR │ │ SCType │ │ SAMap  │ │SATURN │ │
│  └────┬───┘ └───┬────┘ └───┬────┘ └───┬───┘ │
│       │         │          │          │      │
│  ┌────▼─────────▼──────────▼──────────▼───┐  │
│  │         GO/KEGG 富集分析（始终运行）     │  │
│  └────────────────────────────────────────┘  │
│  输出：annotation_matrix.json                 │
└─────────────────────┬────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────┐
│  步骤3：共识与解读 Skill                       │
│  ┌──────────────────────────────────────┐    │
│  │ · 加权投票算法                         │    │
│  │ · 冲突检测与语义消歧                   │    │
│  │ · 新细胞类型判定                       │    │
│  │ · LLM生成细胞身份摘要                  │    │
│  └──────────────────────────────────────┘    │
│  输出：consensus_result.json                  │
└─────────────────────┬────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────┐
│  步骤4：报告生成 Skill                         │
│  ┌──────────────────────────────────────┐    │
│  │ · 交互式UMAP/t-SNE可视化              │    │
│  │ · 注释详情表格（可排序、可筛选）        │    │
│  │ · 细胞群故事卡片                       │    │
│  │ · 证据浏览器（小提琴图、富集图）        │    │
│  └──────────────────────────────────────┘    │
│  输出：HTML报告（单页应用）                    │
└──────────────────────────────────────────────┘
```

---

## 3. Skill能力组件详细设计

### 3.1 概述

Skill层是平台的核心计算单元，每个Skill封装为一个独立的微服务，通过标准化的RESTful API对外暴露。所有Skill遵循统一的输入输出规范，可独立开发、测试、部署和扩展。

### 3.2 Skill 1：知识检索（Knowledge Retrieval Skill）

#### 3.2.1 基本信息

| 属性 | 描述 |
|:---|:---|
| **服务名称** | `knowledge-retrieval-skill` |
| **API端点** | `POST /api/v1/skills/knowledge` |
| **核心功能** | 基于物种和组织信息，自动检索并返回结构化的先验知识 |
| **驱动方式** | LLM Agent自主决策检索策略 |

#### 3.2.2 输入参数

```json
{
  "species": "Oryza sativa",          // 必填：物种学名
  "tissue": "root tip",               // 必填：组织/器官名称
  "options": {
    "include_live_search": true,      // 可选：是否包含实时文献检索
    "max_markers_per_type": 20,       // 可选：每类细胞最多返回的标记基因数
    "ortholog_species": ["Arabidopsis thaliana"], // 可选：优先使用的参考物种
    "evidence_threshold": "experimental" // 可选：证据级别筛选
  }
}
```

#### 3.2.3 检索流程

```
输入: {species: "玉米", tissue: "发育中的胚乳"}
    │
    ▼
步骤1: 并行查询所有本地资源数据库
    ├── 查询标记基因库
    │   → 找到3篇玉米胚乳scRNA-seq文献
    │   → 提取标记基因列表：传递细胞标记、淀粉胚乳标记、糊粉层标记...
    │
    ├── 查询解剖本体库
    │   → 获取胚乳标准细胞类型组成：
    │       ["传递细胞", "淀粉胚乳", "糊粉层", "胚乳基底传递细胞", "中央淀粉胚乳"]
    │   → 获取细胞类型空间关系信息
    │
    ├── 查询图谱索引库
    │   → 找到匹配项：PRJNA123456 (玉米胚乳, 12,000细胞, 已精细注释)
    │   → 评分：quality_score=0.92, 推荐作为参考图谱
    │
    └── 查询同源基因库
        → 将拟南芥胚乳标记基因映射为玉米直系同源基因
        → 返回映射结果，附带置信度评分
    │
    ▼
步骤2: （可选）实时文献检索
    └── PubMed API → 检索 "Zea mays endosperm single cell 2024-2026"
    └── LLM提取摘要中的新细胞类型/标记基因信息
    │
    ▼
步骤3: LLM整合与格式化
    └── 去重、冲突解决、证据链整理
    └── 生成标准化 knowledge_json
```

#### 3.2.4 输出格式

```json
{
  "query": {
    "species": "Zea mays",
    "tissue": "developing endosperm",
    "timestamp": "2026-06-15T10:30:00Z"
  },
  "cell_types": [
    {
      "name": "transfer cells",
      "anatomical_description": "位于胚乳基底部的特化细胞，具有细胞壁内突结构，负责母体-胚乳间的营养转运",
      "marker_genes": [
        {
          "gene_id": "Zm00001d012345",
          "gene_symbol": "ZmSWEET4c",
          "specificity_score": 0.95,
          "evidence": "in_situ_hybridization",
          "source": "DOI:10.1038/s41477-021-00912-3"
        }
      ],
      "parent_tissue": "endosperm",
      "developmental_origin": "受精极核"
    },
    {
      "name": "starchy endosperm",
      "anatomical_description": "占据胚乳主体的薄壁细胞，主要积累淀粉和储藏蛋白",
      "marker_genes": [
        {
          "gene_id": "Zm00001d098765",
          "gene_symbol": "O2",
          "specificity_score": 0.98,
          "evidence": "reporter_gene",
          "source": "DOI:10.1105/tpc.15.00877"
        }
      ],
      "parent_tissue": "endosperm",
      "developmental_origin": "淀粉胚乳前体细胞分化"
    }
  ],
  "reference_atlas": {
    "available": true,
    "accession": "PRJNA123456",
    "title": "A single-cell atlas of developing maize endosperm",
    "cell_count": 12000,
    "quality_score": 0.92,
    "compatibility": "high",
    "local_cache_path": "/data/atlases/PRJNA123456_processed.h5ad"
  },
  "anatomy_ontology": {
    "plant_ontology_id": "PO:0009089",
    "term": "endosperm",
    "substructures": ["basal transfer cell", "starchy endosperm", "aleurone layer"]
  },
  "knowledge_confidence": "high",
  "warnings": []
}
```

### 3.3 Skill 2：多算法注释（Annotation Ensemble Skill）

#### 3.3.1 基本信息

| 属性 | 描述 |
|:---|:---|
| **服务名称** | `annotation-ensemble-skill` |
| **API端点** | `POST /api/v1/skills/annotate` |
| **核心功能** | 并行运行多种注释算法，返回原始注释矩阵 |
| **执行策略** | 根据知识检索结果动态决定运行哪些算法 |

#### 3.3.2 输入参数

```json
{
  "expression_data": "base64编码的h5ad文件或S3路径",
  "knowledge_json": {},              // Skill 1的输出
  "algorithms": {
    "singler": {"run": true, "params": {}},
    "sctype": {"run": true, "params": {}},
    "samap": {"run": true, "params": {"ref_species": "Arabidopsis thaliana"}},
    "saturn": {"run": false},
    "seurat_transfer": {"run": true, "params": {"ref_atlas_id": "PRJNA123456"}},
    "go_enrichment": {"run": true, "params": {"p_cutoff": 0.05}}
  },
  "clustering": "leiden_res0.8"      // 使用的聚类方案
}
```

#### 3.3.3 集成算法详细规范

##### 算法1：SingleR

| 属性 | 规范 |
|:---|:---|
| **调用条件** | `knowledge_json`中marker_genes非空 |
| **参考构建** | 使用knowledge_json中的`cell_type → marker_genes`映射构建自定义参考表达矩阵 |
| **植物适配** | 不使用默认的人类/小鼠参考，完全基于检索到的植物标记基因 |
| **参数** | 默认使用`de.method="classic"`，相关性方法 |
| **输出** | 每个细胞的类型标签 + 置信度打分 + delta值 |

##### 算法2：SCType

| 属性 | 规范 |
|:---|:---|
| **调用条件** | `knowledge_json`中marker_genes非空 |
| **标记基因集** | 使用与SingleR相同的标记基因集，形成方法间可比较的基础 |
| **植物适配** | 禁用其内置的动物组织标记基因集 |
| **参数** | 使用默认打分阈值，开放用户调整 |
| **输出** | 每个聚类的类型标签 + 打分矩阵 |

##### 算法3：SAMap

| 属性 | 规范 |
|:---|:---|
| **调用条件** | `knowledge_json`中`reference_atlas.available==true` 且参考物种与查询物种不同 |
| **功能** | 利用同源基因信息进行跨物种单细胞图谱映射 |
| **植物适配** | 使用平台自有的同源基因库，优先于SAMap内置的同源推断 |
| **触发逻辑** | 非模式植物 + 存在可用跨物种参考图谱时自动触发 |
| **输出** | 跨物种映射的细胞类型对应关系 + 映射置信度 |

##### 算法4：SATURN

| 属性 | 规范 |
|:---|:---|
| **调用条件** | 查询物种为非模式植物，且无任何近缘物种参考图谱 |
| **功能** | 使用蛋白质语言模型（ProtLM）编码基因，实现不依赖同源推断的跨物种细胞类型匹配 |
| **植物适配** | 使用预训练的植物蛋白质语言模型（如PlantProtLM） |
| **触发逻辑** | 当SAMap不适用时的兜底方案 |
| **输出** | 基于蛋白质序列相似性的细胞类型对应关系 |

##### 算法5：Seurat标签转移

| 属性 | 规范 |
|:---|:---|
| **调用条件** | `knowledge_json`中`reference_atlas.available==true` 且为同物种或近缘物种 |
| **方法** | 使用`FindTransferAnchors` + `TransferData`流程 |
| **植物适配** | 使用SCTransform归一化以适应植物数据特性 |
| **参考图谱** | 直接加载平台图谱索引库中缓存的预处理后参考数据 |
| **输出** | 预测标签 + 预测打分 + 每个细胞的锚定信息 |

##### 算法6：GO/KEGG富集分析（无监督兜底）

| 属性 | 规范 |
|:---|:---|
| **调用条件** | 始终运行 |
| **方法** | 对每个聚类进行差异基因分析（vs. 其余所有细胞），对top100差异基因进行富集分析 |
| **工具** | clusterProfiler + 平台通路库 |
| **植物适配** | 使用物种对应的OrgDb（如有）或同源推断的功能注释 |
| **输出** | 每个聚类的显著富集GO BP/MF/CC条目和KEGG通路，附带p值和基因列表 |

#### 3.3.4 输出格式

```json
{
  "annotation_matrix": {
    "cluster_0": {
      "cell_count": 345,
      "algorithms": {
        "singler": {
          "label": "transfer_cells",
          "score": 0.89,
          "delta": 0.23,
          "status": "success"
        },
        "sctype": {
          "label": "transfer_cells",
          "score": 0.91,
          "status": "success"
        },
        "samap": {
          "label": "basal_endosperm_transfer_cell",
          "score": 0.85,
          "ref_species": "Arabidopsis_thaliana",
          "status": "success"
        },
        "seurat_transfer": {
          "label": "transfer_cells",
          "prediction_score_max": 0.94,
          "status": "success"
        },
        "saturn": {
          "status": "not_executed",
          "reason": "higher_priority_algorithm_available"
        },
        "go_enrichment": {
          "top_terms": [
            {"term": "GO:0015770", "description": "sucrose transport", "p.adjust": 1.2e-8},
            {"term": "GO:0071705", "description": "nitrogen compound transport", "p.adjust": 3.4e-6}
          ],
          "status": "success"
        }
      }
    },
    "cluster_1": {
      "cell_count": 1203,
      "algorithms": { /* ... */ }
    }
  },
  "execution_summary": {
    "total_clusters": 15,
    "algorithms_executed": ["singler", "sctype", "samap", "seurat_transfer", "go_enrichment"],
    "algorithms_skipped": {"saturn": "higher_priority_algorithm_available"},
    "execution_time_seconds": 1245
  }
}
```

### 3.4 Skill 3：共识与解读（Consensus & Interpretation Skill）

#### 3.4.1 基本信息

| 属性 | 描述 |
|:---|:---|
| **服务名称** | `consensus-interpretation-skill` |
| **API端点** | `POST /api/v1/skills/consensus` |
| **核心功能** | 多算法结果整合、冲突消解、LLM生成细胞身份自然语言描述 |

#### 3.4.2 共识决策算法

```
输入: annotation_matrix (来自Skill 2)
      knowledge_json (来自Skill 1)

步骤1: 标签标准化
    └── 使用Plant Ontology标准化不同算法的标签名称
    └── 例："transfer_cells", "basal_endosperm_transfer_cell", "transfer cell" 
        → 统一为 "basal transfer cell (PO:0009018)"

步骤2: 加权投票
    └── 权重预设（基于在基准测试集上的历史准确率）:
        · Seurat标签转移（同物种参考）: weight=0.30
        · SAMap（跨物种）: weight=0.25
        · SingleR（标记基因）: weight=0.20
        · SCType（标记基因打分）: weight=0.15
        · SATURN: weight=0.10
    └── 计算公式: weighted_score(label) = Σ(weight_i × I(algorithm_i==label))

步骤3: 置信度分级
    └── 高置信度: 加权分数 ≥ 0.7 或 3个以上算法一致
    └── 中置信度: 0.4 ≤ 加权分数 < 0.7
    └── 低置信度: 加权分数 < 0.4
    └── 候选新类型: 所有算法均低分 + GO富集结果显著且特异

步骤4: 冲突检测与语义消歧（LLM介入）
    └── 检测场景：多个算法给出不同但语义相关的标签
    └── LLM推理示例:
        输入: "SingleR标注为'皮层', SCType标注为'内皮层', SAMap标注为'皮层'"
        LLM输出: 结合GO富集("凯氏带形成"显著), 建议标注为"内皮层"
        推理: 内皮层与皮层的空间位置和功能相关，且凯氏带是内皮层特征

步骤5: LLM细胞身份摘要生成
    └── 为每个细胞群生成自然语言描述
    └── 融合信息:
        · 解剖学描述 (来自knowledge_json)
        · 共识注释标签
        · 关键标记基因及其功能
        · GO/KEGG显著通路
        · 发育轨迹位置（如有拟时序分析结果）
```

#### 3.4.3 细胞身份摘要模板

```
【细胞群 3】共识注释：内皮层（Endodermis）
置信度：高 | 细胞数：1,245

📝 细胞身份描述：
该细胞群被高置信度注释为根尖内皮层细胞。内皮层是根系皮层内侧的单层细胞，
构成根内与维管系统间的关键屏障。在解剖学上，内皮层细胞的标志性特征是在径向
细胞壁上形成凯氏带（Casparian strip），这一木质化结构可阻断质外体途径的
水分和溶质运输，迫使所有物质必须经过原生质体的选择性跨膜转运。

🔬 关键分子证据：
· CASP1/CASP2：凯氏带形成的关键支架蛋白，本群中特异性高表达（logFC=3.2）
· MYB36：内皮层命运决定转录因子，表达量排全群前5%
· CIF1/CIF2：凯氏带形成所需的肽信号

📊 功能富集：
· 次生细胞壁生物合成（GO:0009834, p=2.3e-12）
· 水分运输（GO:0006833, p=5.7e-8）
· 脱落酸响应（GO:0009737, p=1.2e-5）

🧬 算法共识：
SingleR: 内皮层 (0.89) | SCType: 内皮层 (0.92) | 
Seurat转移: 内皮层 (0.94) | GO富集: 支持
```

#### 3.4.4 输出格式

```json
{
  "consensus_annotations": [
    {
      "cluster_id": "cluster_3",
      "cell_count": 1245,
      "consensus_label": "endodermis",
      "confidence": "high",
      "consensus_score": 0.89,
      "is_novel": false,
      "vote_details": {
        "singler": {"label": "endodermis", "score": 0.89},
        "sctype": {"label": "endodermis", "score": 0.92},
        "seurat_transfer": {"label": "endodermis", "score": 0.94}
      },
      "llm_summary": "该细胞群被高置信度注释为根尖内皮层细胞...（完整文本见上）",
      "key_markers": ["CASP1", "CASP2", "MYB36", "CIF1"],
      "top_go_terms": ["次生细胞壁生物合成", "水分运输", "脱落酸响应"]
    }
  ],
  "novel_candidates": [
    {
      "cluster_id": "cluster_12",
      "cell_count": 89,
      "reason": "所有算法打分<0.3，GO富集显示独特的光合相关通路，但所在组织为根尖",
      "suggested_investigation": "可能为胁迫诱导的异位表达群体或技术噪音"
    }
  ],
  "summary_statistics": {
    "total_clusters": 15,
    "high_confidence": 10,
    "medium_confidence": 3,
    "low_confidence": 1,
    "novel_candidates": 1
  }
}
```

### 3.5 Skill 4：报告生成（Report Generation Skill）

#### 3.5.1 基本信息

| 属性 | 描述 |
|:---|:---|
| **服务名称** | `report-generation-skill` |
| **API端点** | `POST /api/v1/skills/report` |
| **核心功能** | 整合所有分析结果，生成交互式HTML报告 |
| **技术选型** | Plotly.js交互可视化 + Bootstrap响应式布局 |

#### 3.5.2 HTML报告页面结构

```
┌─────────────────────────────────────────┐
│  Plant Cell Annotator - 分析报告         │
│  项目ID: PCA-20260615-001                │
│  生成时间: 2026-06-15 14:30:00 UTC       │
├─────────────────────────────────────────┤
│  📊 项目概览卡片                          │
│  物种: 水稻 | 组织: 根尖 | 细胞数: 8,234  │
│  聚类数: 15 | 注释细胞类型: 12            │
│  高置信度: 10 | 中置信度: 3               │
├─────────────────────────────────────────┤
│  🗺️ 细胞图谱（可交互UMAP）                │
│  ┌───────────────────────────────────┐  │
│  │                                   │  │
│  │    [UMAP散点图，按共识注释着色]      │  │
│  │    - 点击细胞群高亮                  │  │
│  │    - 悬停显示细胞身份                │  │
│  │    - 图例可筛选显示/隐藏              │  │
│  │                                   │  │
│  └───────────────────────────────────┘  │
├─────────────────────────────────────────┤
│  📋 注释详情表（可排序、搜索、筛选）       │
│  ┌───────────────────────────────────┐  │
│  │ 聚类 │ 细胞数 │ 共识注释 │ 置信度 │..│  │
│  │ C0  │ 345  │ 传递细胞 │ 高    │..│  │
│  │ C1  │ 1203 │ 皮层    │ 高    │..│  │
│  │ ...                               │  │
│  └───────────────────────────────────┘  │
├─────────────────────────────────────────┤
│  📖 细胞群故事（为每个类型生成摘要卡片）    │
│  ┌───────────────────────────────────┐  │
│  │ 内皮层 (Endodermis)  置信度: 高    │  │
│  │                                   │  │
│  │ [LLM生成的细胞身份描述文本]          │  │
│  │                                   │  │
│  │ 🔑 标记基因: [小提琴图面板]          │  │
│  │ 📊 GO富集: [柱状图]                 │  │
│  │ 🗳️ 算法共识: [投票详情]             │  │
│  └───────────────────────────────────┘  │
├─────────────────────────────────────────┤
│  🔍 证据浏览器                           │
│  - 自定义基因表达查询                     │
│  - 聚类间差异基因对比                     │
│  - 多算法结果原始矩阵查看                  │
├─────────────────────────────────────────┤
│  ⚙️ 分析参数与复现信息                    │
│  软件版本 | 数据库版本 | 参数设置          │
└─────────────────────────────────────────┘
```

#### 3.5.3 交互功能说明

| 功能 | 说明 |
|:---|:---|
| **图谱交互** | 支持缩放、平移、框选；点击细胞群联动更新其他面板 |
| **基因查询** | 输入基因ID或符号，在UMAP上展示表达分布，并生成小提琴图 |
| **注释反馈** | 每个细胞类型旁有"👍确认/👎修正"按钮，收集用户反馈用于持续优化 |
| **报告导出** | 支持导出为独立HTML文件（自包含，无需服务器），或PDF快照 |
| **数据下载** | 提供注释结果CSV、标记基因列表、富集分析结果的下载链接 |

---

## 4. 资源数据库层详细设计

### 4.1 概述

资源数据库层是平台的"知识大脑"，将分散的植物单细胞知识以结构化、可查询、带版本控制的方式进行管理。共有五个核心数据库。

### 4.2 数据库1：植物标记基因库（Plant Marker Gene Database）

#### 4.2.1 数据库基本信息

| 属性 | 描述 |
|:---|:---|
| **数据库名称** | `plant_marker_db` |
| **数据库类型** | PostgreSQL + Elasticsearch（全文检索） |
| **更新频率** | 每季度增量更新；重大文献发布后即时更新 |
| **版本策略** | 语义化版本（如v2.1.0），每次更新附带变更日志 |

#### 4.2.2 表结构设计

```sql
-- 主表：标记基因记录
CREATE TABLE marker_genes (
    id              SERIAL PRIMARY KEY,
    species         VARCHAR(100) NOT NULL,          -- 物种学名
    strain          VARCHAR(100),                   -- 品种/品系
    tissue          VARCHAR(100) NOT NULL,          -- 组织/器官
    cell_type       VARCHAR(200) NOT NULL,          -- 细胞类型
    sub_type        VARCHAR(200),                   -- 细胞亚型（如适用）
    
    gene_id         VARCHAR(50) NOT NULL,           -- 基因ID（物种特异性）
    gene_symbol     VARCHAR(50),                    -- 基因符号
    gene_family     VARCHAR(100),                   -- 所属基因家族
    
    specificity_score DECIMAL(3,2),                 -- 特异性评分（0-1）
    expression_pattern VARCHAR(500),                -- 表达模式描述
    
    evidence_type   VARCHAR(50) NOT NULL,           -- 证据类型
    -- 可选值: in_situ_hybridization, reporter_gene, 
    --        immunolocalization, scRNA_seq, bulk_RNA_seq, 
    --        literature_mining
    
    evidence_strength VARCHAR(20),                  -- 证据强度: gold_standard, strong, moderate, weak
    
    source_doi      VARCHAR(100),                   -- 来源文献DOI
    source_pmid     VARCHAR(20),                    -- PubMed ID
    source_title    TEXT,                           -- 文献标题
    
    cross_ref_ath   VARCHAR(50),                    -- 拟南芥直系同源基因ID
    cross_ref_osa   VARCHAR(50),                    -- 水稻直系同源基因ID
    cross_ref_other JSONB,                          -- 其他物种同源基因（JSON格式）
    
    curator_notes   TEXT,                           -- 审编注释
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW(),
    
    -- 索引
    UNIQUE(species, tissue, cell_type, gene_id, evidence_type)
);

-- 全文检索索引
CREATE INDEX idx_marker_species_tissue ON marker_genes(species, tissue);
CREATE INDEX idx_marker_cell_type ON marker_genes(cell_type);
CREATE INDEX idx_marker_gene_id ON marker_genes(gene_id);
```

#### 4.2.3 数据来源优先级

| 优先级 | 来源 | 预期记录数 | 说明 |
|:---|:---|:---|:---|
| **P0（核心）** | 已发表高质量植物单细胞图谱 | ~2000条 | 拟南芥10+篇、水稻5+篇、玉米3+篇、番茄2+篇、杨树2+篇等 |
| **P1** | 经典原位杂交/报告基因实验 | ~1000条 | 来自传统发育生物学和分子遗传学文献 |
| **P2** | 大规模转录组数据分析推断 | ~3000条 | 来自Genevestigator、Expression Atlas等数据库 |
| **P3** | 文献挖掘自动提取 | ~2000条 | 使用NLP技术从PubMed摘要中自动提取 |

#### 4.2.4 数据质量控制流程

```
原始文献
    │
    ▼
步骤1: 自动提取
    └── NLP解析摘要/全文，提取物种-组织-基因-细胞类型关系
    │
    ▼
步骤2: 人工审编（P0/P1数据）
    └── 领域专家验证证据充分性
    └── 标准化细胞类型名称（映射到Plant Ontology）
    └── 评估特异性评分
    │
    ▼
步骤3: 证据分级
    └── Gold Standard: 原位杂交 + 报告基因 + 功能验证
    └── Strong: 单细胞数据 + 正交验证（如免疫组化）
    └── Moderate: 单细胞数据 + 文献支持
    └── Weak: 仅基于同源推断或计算预测
    │
    ▼
步骤4: 入库
    └── 写入PostgreSQL，同步更新Elasticsearch索引
```

### 4.3 数据库2：跨物种同源基因库（Plant Ortholog Database）

#### 4.3.1 数据库基本信息

| 属性 | 描述 |
|:---|:---|
| **数据库名称** | `plant_ortholog_db` |
| **数据库类型** | PostgreSQL + 预计算相似度矩阵文件 |
| **更新频率** | 跟随主要植物基因组版本更新 |
| **核心方法** | OrthoFinder + InParanoid + BLAST互惠最佳匹配 |

#### 4.3.2 表结构设计

```sql
CREATE TABLE ortholog_pairs (
    id                  SERIAL PRIMARY KEY,
    ref_species         VARCHAR(100) NOT NULL,       -- 参考物种（锚定物种）
    ref_gene_id         VARCHAR(50) NOT NULL,        -- 参考物种基因ID
    ref_gene_symbol     VARCHAR(50),
    ref_genome_version  VARCHAR(50),                 -- 参考基因组版本
    
    target_species      VARCHAR(100) NOT NULL,       -- 目标物种
    target_gene_id      VARCHAR(50) NOT NULL,        -- 目标物种基因ID
    target_gene_symbol  VARCHAR(50),
    target_genome_version VARCHAR(50),
    
    orthology_type      VARCHAR(20),                 -- 直系同源类型
    -- 可选值: one2one, one2many, many2many
    
    method              VARCHAR(50),                 -- 推断方法
    -- 可选值: OrthoFinder, InParanoid, RBH_BLAST, Ensembl_Compara
    
    confidence          VARCHAR(20),                 -- 置信度: high, medium, low
    similarity_score    DECIMAL(5,4),                -- 序列相似度
    
    created_at          TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(ref_species, ref_gene_id, target_species, target_gene_id, method)
);

CREATE INDEX idx_ortholog_ref ON ortholog_pairs(ref_species, ref_gene_id);
CREATE INDEX idx_ortholog_target ON ortholog_pairs(target_species, target_gene_id);
```

#### 4.3.3 预计算物种矩阵

| 参考物种（锚定） | 目标物种 | 基因对数 | 直系同源方法 | 状态 |
|:---|:---|:---|:---|:---|
| *Arabidopsis thaliana* | *Oryza sativa* | ~18,000 | OrthoFinder | 已完成 |
| *Arabidopsis thaliana* | *Zea mays* | ~16,000 | OrthoFinder | 已完成 |
| *Arabidopsis thaliana* | *Solanum lycopersicum* | ~17,000 | OrthoFinder | 已完成 |
| *Arabidopsis thaliana* | *Glycine max* | ~20,000 | OrthoFinder | 规划中 |
| *Oryza sativa* | *Zea mays* | ~19,000 | OrthoFinder | 已完成 |
| *Arabidopsis thaliana* | *Triticum aestivum* | ~15,000 | OrthoFinder | 规划中 |

### 4.4 数据库3：组织解剖本体库（Plant Anatomy Ontology Database）

#### 4.4.1 数据库基本信息

| 属性 | 描述 |
|:---|:---|
| **数据库名称** | `plant_anatomy_ontology_db` |
| **数据来源** | Plant Ontology (PO)、各物种特异性解剖本体 |
| **更新频率** | 跟随PO发布周期（约每年一次） |

#### 4.4.2 表结构设计

```sql
CREATE TABLE anatomy_terms (
    id                  SERIAL PRIMARY KEY,
    po_id               VARCHAR(20) UNIQUE,          -- Plant Ontology ID
    term_name           VARCHAR(200) NOT NULL,       -- 术语名称
    term_definition     TEXT,                        -- 术语定义
    category            VARCHAR(50),                 -- 分类: tissue, cell_type, developmental_stage
    
    parent_po_id        VARCHAR(20),                 -- 父术语PO ID
    children_po_ids     TEXT[],                      -- 子术语PO ID数组
    
    species_applicability TEXT[],                    -- 适用的物种列表
    -- ['Arabidopsis thaliana', 'Oryza sativa', ...]
    
    species_specific_notes JSONB,                    -- 物种特异性说明
    -- {
    --   "Oryza sativa": {"note": "水稻根尖内皮层与拟南芥有差异...",
    --                     "ref": "DOI:..."}
    -- }
    
    spatial_relationships JSONB,                     -- 空间关系
    -- {
    --   "adjacent_to": ["cortex", "pericycle"],
    --   "contains": [],
    --   "part_of": ["root"]
    -- }
    
    developmental_origin VARCHAR(200),               -- 发育起源
    
    created_at          TIMESTAMP DEFAULT NOW()
);

-- 物种-组织-细胞类型快速查询表
CREATE TABLE tissue_cell_type_index (
    id              SERIAL PRIMARY KEY,
    species         VARCHAR(100) NOT NULL,
    tissue          VARCHAR(100) NOT NULL,
    cell_type       VARCHAR(200) NOT NULL,
    po_id           VARCHAR(20),
    evidence_level  VARCHAR(20),  -- confirmed, predicted, uncertain
    
    UNIQUE(species, tissue, cell_type)
);

CREATE INDEX idx_tissue_species ON tissue_cell_type_index(species, tissue);
```

#### 4.4.3 核心数据内容

```
根尖 (root tip) PO:0000025
├── 根冠 (root cap) PO:0020123
│   ├── 小柱根冠 (columella root cap) PO:0020056
│   └── 侧生根冠 (lateral root cap) PO:0020132
├── 顶端分生组织 (root apical meristem) PO:0020147
│   ├── 静止中心 (quiescent center) PO:0020148
│   └── 干细胞 (stem cells) PO:0020149
├── 伸长区 (elongation zone) PO:0020125
└── 分化区 (differentiation zone) PO:0020135
    ├── 表皮 (epidermis) PO:0005679
    │   ├── 根毛细胞 (root hair cell) PO:0000256
    │   └── 非根毛细胞 (non-hair cell) PO:0000263
    ├── 皮层 (cortex) PO:0000258
    ├── 内皮层 (endodermis) PO:0000252
    ├── 中柱鞘 (pericycle) PO:0000260
    └── 维管组织 (vascular tissue) PO:0009015
        ├── 木质部 (xylem) PO:0005352
        └── 韧皮部 (phloem) PO:0005417
```

### 4.5 数据库4：公共单细胞图谱索引库（Plant scAtlas Catalog）

#### 4.5.1 数据库基本信息

| 属性 | 描述 |
|:---|:---|
| **数据库名称** | `plant_scatlas_catalog` |
| **数据库类型** | PostgreSQL（元数据） + 对象存储（数据文件） |
| **数据来源** | GEO, SRA, Figshare, Zenodo, 期刊附属数据 |

#### 4.5.2 表结构设计

```sql
CREATE TABLE scatlas_records (
    id                  SERIAL PRIMARY KEY,
    accession           VARCHAR(50) UNIQUE NOT NULL,  -- GEO/SRA编号
    title               TEXT NOT NULL,
    species             VARCHAR(100) NOT NULL,
    tissue              VARCHAR(100) NOT NULL,
    developmental_stage VARCHAR(200),
    condition           VARCHAR(200),                 -- 处理条件
    
    sequencing_platform VARCHAR(50),                  -- 10x Genomics, Drop-seq, etc.
    cell_count          INTEGER,
    gene_count          INTEGER,
    
    cell_types_annotated TEXT[],                      -- 已注释的细胞类型列表
    annotation_method   VARCHAR(100),                 -- 原始注释方法
    annotation_quality  VARCHAR(20),                  -- 注释质量评估: high, medium, low
    
    data_url            TEXT,                         -- 原始数据URL
    data_format         VARCHAR(50),                  -- h5ad, rds, loom, mtx
    local_cache_path    VARCHAR(500),                 -- 本地缓存路径
    preprocessed        BOOLEAN DEFAULT FALSE,        -- 是否已预处理
    
    reference_paper     TEXT,                         -- 参考文献信息
    doi                 VARCHAR(100),
    
    quality_score       DECIMAL(2,2),                 -- 内部质量评分 (0-1)
    quality_notes       TEXT,                         -- 质量评估说明
    
    recommended_as_ref  BOOLEAN DEFAULT FALSE,        -- 是否推荐作为注释参考
    
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_atlas_species_tissue ON scatlas_records(species, tissue);
CREATE INDEX idx_atlas_quality ON scatlas_records(quality_score DESC);
```

#### 4.5.3 收录优先级与计划

| 优先级 | 物种 | 组织 | 数据集数量（规划） |
|:---|:---|:---|:---|
| **P0** | 拟南芥 | 根尖、叶片、花分生组织 | 15 |
| **P0** | 水稻 | 根尖、叶片、花序 | 8 |
| **P1** | 玉米 | 根尖、胚乳、花序 | 6 |
| **P1** | 番茄 | 果实、根尖 | 4 |
| **P2** | 杨树 | 木质部、形成层 | 3 |
| **P2** | 大豆 | 根瘤、根尖 | 3 |
| **P3** | 其他物种 | 各类组织 | 15+ |

### 4.6 数据库5：植物通路与功能注释库（Plant Pathway Database）

#### 4.6.1 数据库基本信息

| 属性 | 描述 |
|:---|:---|
| **数据库名称** | `plant_pathway_db` |
| **数据来源** | GO, KEGG, PlantCyc, MapMan, TAIR, RAP-DB, MaizeGDB |
| **更新频率** | 跟随上游数据库更新 |

#### 4.6.2 表结构设计

```sql
CREATE TABLE gene_annotations (
    id              SERIAL PRIMARY KEY,
    species         VARCHAR(100) NOT NULL,
    gene_id         VARCHAR(50) NOT NULL,
    gene_symbol     VARCHAR(50),
    
    go_id           VARCHAR(20),
    go_term         VARCHAR(300),
    go_category     VARCHAR(10),  -- BP, MF, CC
    go_evidence     VARCHAR(10),  -- EXP, ISS, IEA, etc.
    
    kegg_pathway_id VARCHAR(20),
    kegg_pathway_name VARCHAR(300),
    
    plantcyc_pathway VARCHAR(300),
    mapman_bin      VARCHAR(100),
    
    annotation_source VARCHAR(100),
    annotation_date TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(species, gene_id, go_id)
);

CREATE INDEX idx_gene_annotation_species ON gene_annotations(species, gene_id);
```

---

## 5. 自动化注释方法集成规范

### 5.1 算法选择决策树

```
用户输入: {物种, 组织, 是否有本地参考图谱}

┌─ 同物种有高质量参考图谱？
│   ├── 是 → 运行 Seurat标签转移 + SingleR + SCType + GO富集
│   │        SAMap/SATURN: 不触发
│   │
│   └── 否 →
│       │
│       ┌─ 近缘物种有高质量参考图谱？
│       │   ├── 是 → 运行 SAMap + SingleR + SCType + GO富集
│       │   │        SATURN: 不触发（SAMap优先级更高）
│       │   │
│       │   └── 否 →
│       │       │
│       │       ┌─ 知识库中有标记基因信息？
│       │       │   ├── 是 → 运行 SingleR + SCType + SATURN + GO富集
│       │       │   │
│       │       │   └── 否 → 运行 SATURN + GO富集（仅无监督）
│       │       │
│       │       └── GO富集分析始终运行（无监督兜底）
```

### 5.2 算法权重配置（可调优）

```yaml
algorithm_weights:
  default:
    seurat_transfer_same_species: 0.30
    samap_cross_species: 0.25
    singler: 0.20
    sctype: 0.15
    saturn: 0.10
    
  mode: # 模式植物场景
    model_plant:
      seurat_transfer_same_species: 0.35
      singler: 0.25
      sctype: 0.20
      go_enrichment_consistency: 0.20  # 额外：与GO富集的一致性加分
    
  non_model_plant:
    samap_cross_species: 0.30
    singler: 0.20
    saturn: 0.20
    sctype: 0.15
    go_enrichment_consistency: 0.15
```

### 5.3 置信度计算与分级

```
对每个聚类:
  consensus_score = Σ(weight_i × 1[algorithm_i == consensus_label])
  
  # 额外加分项
  if GO富集结果与共识标签功能一致: consensus_score += 0.05
  
  # 分级
  if consensus_score >= 0.70: confidence = "高"
  elif consensus_score >= 0.40: confidence = "中"
  else: 
      if GO富集有≥3个特异显著条目: confidence = "低（候选新类型）"
      else: confidence = "低（待验证）"
```

---

## 6. 用户输出与交互设计

### 6.1 HTML报告详细设计

参见第3.5节Skill 4的完整设计。

### 6.2 API接口规范概览

| 端点 | 方法 | 功能 | 输入 | 输出 |
|:---|:---|:---|:---|:---|
| `/api/v1/skills/knowledge` | POST | 知识检索 | species, tissue | knowledge_json |
| `/api/v1/skills/annotate` | POST | 多算法注释 | h5ad, knowledge_json | annotation_matrix |
| `/api/v1/skills/consensus` | POST | 共识与解读 | annotation_matrix, knowledge_json | consensus_result |
| `/api/v1/skills/report` | POST | 报告生成 | consensus_result, h5ad | report_url |
| `/api/v1/annotate/full` | POST | 一键全流程 | h5ad, species, tissue | report_url |
| `/api/v1/databases/query` | GET | 数据库查询 | db_name, query_params | query_results |
| `/api/v1/feedback` | POST | 用户反馈 | cluster_id, feedback_type | status |

### 6.3 一键式调用示例

```bash
# 全流程一键调用
curl -X POST https://api.plant-annotator.org/v1/annotate/full \
  -H "Content-Type: multipart/form-data" \
  -F "file=@rice_root_tip.h5ad" \
  -F "species=Oryza sativa" \
  -F "tissue=root tip" \
  -F "email=user@example.com" \
  -o annotation_report.html
```

---

## 7. 项目实施路线图

### 7.1 总体时间线

```
总工期：18个月（分为三个阶段）

阶段一（M1-M6）：基础设施与核心流程
阶段二（M7-M12）：智能增强与生态扩展
阶段三（M13-M18）：生产化与社区建设
```

### 7.2 阶段一：MVP（最小可行产品）— M1至M6

| 月份 | 里程碑 | 交付物 |
|:---|:---|:---|
| **M1** | 项目启动与架构设计 | 详细技术设计文档、API规范文档 |
| **M2** | 标记基因库v1.0构建 | 拟南芥根尖、叶片标记基因库（~200条P0级记录） |
| **M3** | Knowledge Skill开发 | 知识检索API（针对拟南芥根尖的硬编码版） |
| **M4** | Annotation Skill开发 | 集成SingleR + SCType + GO富集，支持拟南芥根尖 |
| **M5** | Consensus + Report Skill开发 | 共识投票算法 + 基础HTML报告 |
| **M6** | MVP集成测试与发布 | 端到端流程可运行，开放内测 |

**MVP能力边界**：
- 支持物种：拟南芥（Arabidopsis thaliana）
- 支持组织：根尖、叶片
- 集成算法：SingleR, SCType, GO富集
- 输出：基础HTML报告

### 7.3 阶段二：智能增强与跨物种 — M7至M12

| 月份 | 里程碑 | 交付物 |
|:---|:---|:---|
| **M7** | 标记基因库扩展 | 扩展至水稻、玉米、番茄（~800条记录） |
| **M8** | 同源基因库构建 | 预计算5个主要物种的直系同源关系 |
| **M9** | SAMap/SATURN集成 | 跨物种注释能力上线 |
| **M10** | LLM Agent完全体 | 实时文献检索 + 自动工具选择 + 语义解读 |
| **M11** | 图谱索引库建设 | 收录30+公共图谱，预处理并缓存 |
| **M12** | 阶段二发布 | 支持5个主要物种，完整多算法注释 |

### 7.4 阶段三：生产化与生态 — M13至M18

| 月份 | 里程碑 | 交付物 |
|:---|:---|:---|
| **M13-M14** | 性能优化与压力测试 | 支持1000+并发请求，单次注释<30分钟 |
| **M15** | 开放API与文档 | 完善的API文档、SDK（Python/R） |
| **M16** | 社区贡献接口 | 用户可提交验证过的标记基因、报告反馈 |
| **M17** | 多模态支持 | 开始整合scATAC-seq注释能力 |
| **M18** | 正式版v1.0发布 | 论文投稿，社区推广，文档完善 |

---

## 8. 风险评估与应对策略

| 风险类别 | 风险描述 | 严重程度 | 应对策略 |
|:---|:---|:---|:---|
| **数据质量风险** | 标记基因库中部分记录可能不可靠 | 高 | 严格的证据分级体系；金标准数据独立审核；提供每项记录的来源引用 |
| **算法可靠性** | 自动化注释可能在某些场景下失效 | 高 | 多算法共识机制降低单一算法偏差；对低置信度结果明确标注；提供置信度分级 |
| **非模式植物困难** | 基因功能注释严重不足 | 中 | 基于基因集功能富集替代单基因推断；SATURN等不依赖同源的方法作为兜底 |
| **LLM幻觉** | LLM可能生成看似合理但错误的解读 | 中 | LLM仅用于"整合已有分析结果"而非"创造新知识"；所有LLM输出明确标注为"AI生成，需人工审核" |
| **计算资源** | SAMap/SATURN等算法计算开销大 | 中 | 使用云端弹性计算资源；对大型数据集建议用户本地运行部分步骤 |
| **数据库维护** | 数据库内容过时 | 低 | 设定定期更新周期；追踪主要期刊新发表文献；社区贡献机制 |
| **用户接受度** | 研究者可能不信任自动化注释结果 | 中 | 提供完整的证据链和原始结果；允许用户交互式验证和修正；发表基准测试论文证明准确性 |

---

## 9. 附录

### 9.1 术语表

| 术语 | 定义 |
|:---|:---|
| **Skill** | 平台中可独立调用的能力组件，每个Skill封装一个完整的分析功能 |
| **Agent** | 由LLM驱动的智能体，能够自主决策工具选择和信息检索策略 |
| **知识JSON** | 标准化的结构化先验知识输出格式，包含细胞类型、标记基因、解剖信息等 |
| **共识注释** | 综合多种算法结果，通过加权投票等机制得出的最终注释结果 |
| **植物本体（Plant Ontology, PO）** | 标准化的植物解剖结构和发育阶段术语体系 |
| **原生质体胁迫** | 制备原生质体过程中引入的人为基因表达变化 |

### 9.2 参考文献（选列）

1. Denyer, T., et al. (2019). Spatiotemporal developmental trajectories in the Arabidopsis root revealed using high-throughput single-cell RNA sequencing. *Developmental Cell*, 48(6), 840-852.
2. Zhang, T. Q., et al. (2019). A single-cell RNA sequencing profiles the developmental landscape of Arabidopsis root. *Molecular Plant*, 12(5), 648-660.
3. Liu, Q., et al. (2021). Single-cell RNA sequencing of developing maize ears facilitates functional analysis and trait candidate gene discovery. *Developmental Cell*, 56(4), 557-568.
4. Xu, X., et al. (2021). Single-cell RNA sequencing of developing sorghum seeds elucidates mechanisms of endosperm development. *Nature Communications*, 12, 6544.
5. Plant Ontology Consortium. (2023). The Plant Ontology: a tool for plant genomics. *Nucleic Acids Research*, 51(D1), D1467-D1473.

### 9.3 技术栈参考

| 层级 | 技术选型 |
|:---|:---|
| **后端框架** | FastAPI (Python) |
| **LLM推理** | LangChain + OpenAI API / 开源模型（Llama, Qwen等） |
| **单细胞分析** | Scanpy, Seurat (via rpy2), scvi-tools |
| **数据库** | PostgreSQL + Elasticsearch + MinIO（对象存储） |
| **容器化** | Docker + Kubernetes |
| **前端可视化** | Plotly.js + D3.js + Bootstrap 5 |
| **消息队列** | RabbitMQ / Redis（任务调度） |
| **CI/CD** | GitHub Actions + ArgoCD |
| **监控** | Prometheus + Grafana |

---

**文档编制**：项目组  
**文档状态**：草案  
**下次评审日期**：根据项目启动时间确定

---

*本文件为Plant Cell Annotator项目的全面设计文档，涵盖背景分析、架构设计、Skill与数据库详细规范、实施路线及风险应对。如有疑问或建议，请联系项目负责人。*