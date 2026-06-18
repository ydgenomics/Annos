## tools
- SAMap 抽样提速
- SATURN

## Db
- https://www.tobaccodb.org/pcmdb/download


> [!NOTE]
> - [P-scAnno](../../PROJECT-open/P-scAnno-20260310/README.md)
> - [WORKFLOW/Annos](../../WORKFLOW/Annos/)
> - [Annos#protocol-plant-single-cell-annotation](https://github.com/ydgenomics/Annos#protocol-plant-single-cell-annotation)

- 细胞状态与细胞类别
- 高表达基因不等于细胞类型特异基因

- 细胞壁、细胞质和细胞核
- ambient RNA
- 物种限制

- 模式植物和非模式植物
- 有单细胞数据和无单细胞数据
- 有bulk数据和无bulk数据
- 有marker基因和无marker基因



```
目前，植物单细胞的细胞身份识别主要依赖已知标记基因。然而，由于植物细胞壁及非模型作物的复杂性，手动注释存在主观性高、标准不一的问题。正如 PlantscRNAdb 4.0 (2025/2026) 和 scPlantDB 等植物专属数据库及 scPlantLLM 等深度学习注释框架的建立，正在推动植物单细胞细胞注释向标准化、自动化的方向迈进
```
 
# scAnno
**scAnno**: **s**ingle **c**ell **Anno**tation pipeline. sxRNA-seq data are increasing like flooding for plants and animals, and good annotation for clustered and labeled data is basic foundament of downstream analysis. Now I supposed a rubust, avaiable, and easy piepeline to solve annotation problem of plants' sc-cells, like a diverse toolkie.

- 为什么要做好细胞注释？这既是数据的优势又是下游分析的关键。开发一个python版本的单细胞注释工具的必要性，大数据集合在python生态分析的优势。
- 项目很多，做的很多的也是细胞类型的注释，而这个也是最基础最根本的部分，要做好、做的快不容易。

## workflow
> cell types, states, and other biologically relevant patterns with the goal of creating annotated cell maps.
- 无参注释，接入大语言模型。
- 有参注释，harmony和scvi方法整合后，基于KNN标签转移。singler?
- 基于marker，自动与手动。sctype （也可接入大语言模型）
- Mapping Cell Names to the Cell Ontology/Taxonomy。植物能不能map到plantscrna，细胞相似性，metaneighbor，cellwalker2
- MetaTiME [omicverse](https://omicverse.readthedocs.io/en/latest/Tutorials-single/t_metatime.html#celltype-auto-annotation-with-metatime)
- TOSICA [omicverse](https://omicverse.readthedocs.io/en/latest/Tutorials-single/t_tosica.html#celltype-annotation-migration-mapping-with-tosica)
- 大语言模型训练数据模型用于注释 scMulan
- Consensus annotation with CellVote


## References
- [Annotating cell clusters in single cell RNA-seq datasets](https://pluto.bio/resources/Learning%20Series/annotating-clusters-in-scrnaseq)
- [List of annotation tools and approaches](https://airtable.com/appMd0h4vP7gzQaeK/shrgmvY3ZvswENjkJ/tblgv3JRYlbD34DYD)
- [OMG Browser (Orthologous Marker Groups Browser)](https://www.omicsempower.com/blog/plant-single-cell-cell-type-annotation-omg-browser/)
- https://omicverse.readthedocs.io/en/latest/tutorials/index_single_annotation.html#annotation
- [Annos](https://github.com/ydgenomics/Annos)
- 2025 [Genome Biol｜汤富酬等利用大型语言模型进行全自动单细胞RNA-seq数据注释和集成](https://mp.weixin.qq.com/s/2dTNAjCdFk7DPrrzA_ZMCw)
- [2025 细胞类型映射到细胞本体论：让你的单细胞注释更专业！](https://mp.weixin.qq.com/s/2PqmjBJukaMvy5iGdN2MJw)
- 2024 [非模式生物单细胞亚群类型注释](https://mp.weixin.qq.com/s/7ga9awAM8jlfia7B8b_2Sw)

## 同源
- orthofinder
- blastp/diamond

### 分群
- 2026 NC | 专门找找稀有细胞亚群的R包RareQ，单细胞、空间均可，笔记本就能搞定，快去挖一挖咱们的数据，看看有没有新的发现 https://mp.weixin.qq.com/s/68GWGrMgccFfyIWFBtUdzg
- 2026 [亚群细分注释」为何与「大群注释」不一致？](https://mp.weixin.qq.com/s/STwGADcesf4yVBOfqks9Kg) [github](https://github.com/Lu7-ydd/gecco)
- 2023 [CellHint自动化协调与整合不同scRNA-seq数据集的细胞类型注释](https://mp.weixin.qq.com/s/0O7VCFI-2zgDmjiHXqNLsg)

### 整合
- 新方法Coralysis：让单细胞数据整合告别“削足适履” https://mp.weixin.qq.com/s/kiCGdeLnqy4GhCcu6pY_zQ
- 
### Tips
- 2026 掌握这条基础规则后，细胞注释再也不会成为单细胞分析的限速步骤 https://mp.weixin.qq.com/s/EySwQGrFWu4m5z42gqYV1w
- 细胞“名片”：5大工具+全流程代码，解锁细胞注释最优解！ [wechat](https://mp.weixin.qq.com/s/fz0txK_mYAP0jxZ40I0gkw)
- 细胞注释：单细胞分析中最考验"内功"的判断题 https://mp.weixin.qq.com/s/6PV1PixHUlLRV3rmUQw2dw

## 注释工具
- 2026 Transformer 进入植物单细胞时代：scPlantAnnotate 如何重塑植物细胞类型注释范式 https://mp.weixin.qq.com/s/_tJqUSaEj5oUmiAcQwYOog
- 2026|dl [跨物种注释](https://github.com/illuminate6060/CellBLASTer) 
- 2026 单细胞 & 空间组学新神器 CSFeatures：精准锁定细胞类型特异性特征 https://mp.weixin.qq.com/s/VYO3jfiWUsM1zLryYw0Gsg
- 2026 scMarkerGene：细胞类型特异性标记基因识别 https://mp.weixin.qq.com/s/Dmd5ngV_OK4IKs3Lpdim5A
- 2019 singleR [使用singleR基于自建数据库来自动化注释单细胞转录组亚群](https://mp.weixin.qq.com/s/GpOxe4WLIrBOjbdH5gfyOQ) [python单细胞学习笔记-day8(singler自动注释)](https://mp.weixin.qq.com/s/EofelV1LY8sqKDRBnRNj9A)
- 2023 sctype [单细胞全自动注释篇(四)——ScType](https://mp.weixin.qq.com/s/hKBiZCHwDdoJOk0YChbtMA)
- Online website for annotation
  - 2026 [scPlantAnnotate](https://scplantannotate.missouri.edu/)
  - 2025 [XSpeciesSpaner](https://shoot.plantcellatlas.com/#/annotate)
- iMetaOmics | 北京科技大学杜宏武组-细胞类型映射注释 [wechat]
- 2025 【NC】利用 AnnDictionary 对大语言模型在细胞类型和基因集注释方面的表现进行基准测试 https://mp.weixin.qq.com/s/F8JhMUKVs49XzpHhALHKKg
- 2025 [单细胞全自动注释篇(一)——clustifyr](https://mp.weixin.qq.com/s/f-kRhKHsS3zygTiz67FoOQ) 
- 2021|Nat.biot 大型单细胞图谱如何整合和注释：scArches深度学习工具介绍 https://mp.weixin.qq.com/s/qpB2sTwJSDE41vUtWJOBIQ
- 2024 [单细胞数据分析 | SingleR、SCINA、scPred三种不同原理的单细胞自动注释工具的使用及解读](https://mp.weixin.qq.com/s/t4WGqy5UfLtk0oaQIf_QMg)
- [Cell_BLAST: 通过深度生成模型像做基因BLAST一样检索和注释细胞类型](https://mp.weixin.qq.com/s/6BH1C4IdzH5Pf9gRtZQukQ)

### 数据库
- 2025|Molecular Plant | PlantscRNAdb 4.0上线：首次建立植物细胞“通用语言”，破解跨物种识别难题 [wechat](https://mp.weixin.qq.com/s/rC7RDZZpFDyaDa8BED7YNw) [PCmaster_anno](https://github.com/bioinplant/PCmaster) [HCMarker](https://github.com/daidai905/HCMarker)
- 2025|Plant & Cell Physiology 【植物marker基因数据库】整合了来自38项研究、9个物种、17种组织和199种细胞类PscOA发布 https://mp.weixin.qq.com/s/7Haxzp4teJfNWXFeZRu3XA http://sdaubiodb.com.cn/pscoa/
- [cell维管植物茎图谱](https://shoot.plantcellatlas.com/#/resources)

### 基因
- 2026 植物基因表达综合数据库--涵盖147种植物的最大规模注释基因表达资源库 https://mp.weixin.qq.com/s/4OAPqKsRMchryhlHup32_A https://publish.obsidian.md/mutwillab/Homepage/README

### 基因
- 2023 [细胞类群marker基因识别及可视化](https://mp.weixin.qq.com/s/XA0gP-uYJmgcSQ1VAAYxYA)
- [EggNOG功能注释数据库在线和本地使用](https://mp.weixin.qq.com/s/1p0oCtgM2HQkXGqfMiHsMQ)

### 绘图
- 2026 Nat Metab | 层级注释：让单细胞分群从混乱细胞到清晰分层 https://mp.weixin.qq.com/s/44Vsi-T2mHSE_WkkbpZumA
