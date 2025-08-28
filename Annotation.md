# Annotation for single-cell
- **Brief:** 单细胞注释是一个不断优化的过程，没有绝对的正确答案(毕竟细胞类型也是人分出来的🐶)。我们需要做的就是尽可能利用当下的所有资源(实验取样信息，单细胞数据库资源，已发表文章等)，在尽力的科学的对细胞进行注释。这里我将整理可以利用的数据库，个人认为的分析流程，给出个人学习资源的出处。
- **Fature:** 数据库资源不断更新，文章发表也很快，尽快整理出最新的资源很有必要
- **Log:** 
  - 20250806 1.0.0 第一次撰写
- **Tradition:** anno_sctype; anno_singler

---
# Input
- input_h5ad: 待注释的.h5ad文件，`.obs`有期望注释的column，**Dataget**输出的.h5ad文件可以直接作为输入
- input_csv: 提前编辑好的注释对应关系，第一列列名为参考分群，例如注释`leiden_res_0.50`，则第一列名为"leiden_res_0.50"，第二列列名为新产生的列名，例如注释的细胞信息存储在`.obs['cell_type']`，则第二列列名为"cell_type" [download template .csv file]()
- mem_csv: 流程所用的内存，默认8G完全够了，非报错不用修改

---
# Output
- h5ad: 在`.obs`带有第二列名注释信息的.h5ad文件
- pdf: 基于第一个列名和第二个列名画的umap图，注意输入的.h5ad对象在`.obsm`要有"X_umap"

---
# Opinion in annotation
*尽人事！任重道远*
**Brief** 
  - [What is cell/cluster Annotation in scRNA-data?](https://pluto.bio/resources/Learning%20Series/annotating-clusters-in-scrnaseq)
  - Single cell RNA sequencing (scRNA-seq) has revolutionized the way we study gene expression at the individual cell level. However, once you’ve performed clustering to group similar cells together, you’re faced with one of the most challenging tasks in scRNA-seq analysis: annotating your clusters. Cluster annotation is the process of assigning biological meaning to these groups, essentially identifying the cell types or states that each cluster represents.[List of annotation tools and approaches](https://airtable.com/appMd0h4vP7gzQaeK/shrgmvY3ZvswENjkJ/tblgv3JRYlbD34DYD)

**Methods**
  - 第一种策略：利用现有的基因集和参考数据库
  - 第二种策略：借助人工智能（AI）工具 scGPT scPlantLLM
  - 第三种策略：应用机器学习方法
  - 第四种策略：使用算法方法或专用软件
  - 第五种策略：结合领域知识进行手动注释

**Opinion**: 
  - **细胞注释是什么？** 首先是细胞分群，那什么也是分群呢，这应该是回答为什么做scRNAseq而不做bulkRNA，生物体不同细胞间分子机制差异很大，我们关注某一类细胞时，bulkRNA是没办法提供这种分辨率的，而scRNA解决了这个问题，并且提供了潜在的对比信息，跟其它细胞类型对比，不同处理下同一细胞类群的对比。[细胞注释小技巧1：【单细胞专题】单细胞测序中细胞鉴定的技巧-联川生物 学习笔记](https://mp.weixin.qq.com/s/zvsvRapJCZe0z6VxTNzSEA)
  - **分群分多少合适呢？** 分群多少以及最终注释出多少细胞类型，应该依赖于取样，取样后基于显微镜观察等大致知道有那些细胞类型，那么后面的分群和注释应该要围绕这个信息，这样才有生物学意义，而不是从数据上的分群。这个数不能过多也不能过少，这样来看又是一个比较主观的过程🐶，当然也有一些工具在尝试从计算上解决分群数的问题，例如**CHOIR**。但是仍然有很多挑战，目前大家一般以`resolution`为0.50为基础做注释
  - **什么是手动注释？** 手动注释就是查看各个群的marker基因/特异高表达基因，这些基因在以往的研究中已经被发表作为某些细胞注释的标记基因，需要文献支撑，耗时耗力。**什么是marker基因？** [试谈单细胞的marker gene 是什么（一）](https://mp.weixin.qq.com/s/4EzWkWTY_dw_ipXmpldk2g)。**什么才是高质量的marker基因或者梦中情marker基因呢？** 我的观点：1.有实验支持；2.有文献支持；3.在自己的数据中有很好的特异性(感觉因数据质量原因很难如意)
  - **当下细胞注释的解决方案** 一般对于批次小(同一次实验的多个生物学重复)的数据做整合后一起分群注释，**Dataget**产出`dotplot.pdf`看看有没有明显特异的marker基因(大概率很少🐶);`leiden_res_0.50`的`marker.csv`做基因富集(运行**Enrich**)，看各个群的特异基因主要功能是什么，特异的细胞类型有特异的功能; **eplant**对拟南芥数据整理的很好，可以利用其中转录组模块做一定参考 [ePlant-web版可视化功能基因组学工具](https://mp.weixin.qq.com/s/DHLZQWFRniOrlf935MOuqA)；自动注释方面，如果该物种有整理的*细胞类型-marker基因列表*可以运行一下**anno_sctype**，如果该物种有较好的参考数据集可以运行一下**anno_singler**，如果是基因名不统一也可以通过蛋白质比对后做基因名对应，非模式生物的注释挑战更大 [非模式生物单细胞亚群类型注释](https://mp.weixin.qq.com/s/7ga9awAM8jlfia7B8b_2Sw)，[65款单细胞亚群注释工具你用过几款？](https://mp.weixin.qq.com/s/gy9UbSID733BhDPSnjk_jA)，软件虽层出不穷，但可靠性堪忧，只能作为最基础的参考；考虑到批次信息，最终注释要有很好的一致性，可以运行**Similarity**查看在不同批次下相近的群，可能要将其注释为相同细胞类型

# Pipeline
  1. 分群(resolution=0.5)后找各个群的特异基因(FindAllMarkers)
  2. 基于各个群的特异基因做基因富集，揭示对应群的特异生物学功能
  3. 整理先验知识
---
# Database of plants
- Reference:
  - [*小杜的生信笔记*·植物学中常用的数据库 | 通用数据库](https://mp.weixin.qq.com/s/eWRKpZbVN8iY1qmu5mue2g)
  - [*基迪奥生物*·研究植物转录调控，你不能不知道的数据库](https://mp.weixin.qq.com/s/yee680uNUmQQUOXISr479A) [PlantTFDB](http://planttfdb.cbi.pku.edu.cn/)
  - 植物单细胞marker系列
    - [*联川生物*·植物细胞marker数据库总览，植物单细胞分析的最佳伴侣！| 植物单细胞专题](https://mp.weixin.qq.com/s/CXGkNuBDQin5MrPWMgt8ng)
    - [scPlantDB](https://biobigdata.nju.edu.cn/scplantdb/home) [*基迪奥生物*·分享一个好用的植物单细胞数据库](https://mp.weixin.qq.com/s/1dTCDc5U3dvCy15GfLRY4A)
    - [PlantCellMarker](https://www.tobaccodb.org/pcmdb/homePage) [*生信益站*·单细胞专题25| 植物细胞类型注释数据库: PlantCellMarker](https://mp.weixin.qq.com/s/Y1AyXa8jkQBV4yWo_HihTw)
    - [PsctH](http://jinlab.hzau.edu.cn/PsctH/) [*植物科学最前言*·PBJ | 华中农大开发出植物单细胞转录组综合数据库，提供综合全面的单细胞Marker基因资源和单细胞研究的workflow](https://mp.weixin.qq.com/s/5dMORWQeX4eTFgH0e1YkTg)
    - [PlantscRNAdb](http://ibi.zju.edu.cn/plantscrnadb/index.php)
    - [XSpeciesSpanner](https://shoot.plantcellatlas.com/#/annotate)

---
# Coder
- **Editor:** yangdong (yangdong@genomics.cn)
- **GitHub:** [ydgenomics](https://github.com/ydgenomics)
- **Prospect:** Focused on innovative, competitive, open-source projects. 
- **Repository:** [Scripts/multi_annotation_scRNAseq](https://github.com/ydgenomics/Scripts/tree/main/multi_annotation_scRNAseq)
