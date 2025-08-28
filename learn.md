# [What is cell/cluster Annotation in scRNA-data?](https://pluto.bio/resources/Learning%20Series/annotating-clusters-in-scrnaseq)
**Brief**: Single cell RNA sequencing (scRNA-seq) has revolutionized the way we study gene expression at the individual cell level. However, once you’ve performed clustering to group similar cells together, you’re faced with one of the most challenging tasks in scRNA-seq analysis: annotating your clusters. Cluster annotation is the process of assigning biological meaning to these groups, essentially identifying the cell types or states that each cluster represents.[List of annotation tools and approaches](https://airtable.com/appMd0h4vP7gzQaeK/shrgmvY3ZvswENjkJ/tblgv3JRYlbD34DYD)

**Methods**
  - 第一种策略：利用现有的基因集和参考数据库
  - 第二种策略：借助人工智能（AI）工具 scGPT scPlantLLM
  - 第三种策略：应用机器学习方法
  - 第四种策略：使用算法方法或专用软件
  - 第五种策略：结合领域知识进行手动注释

**Database of Markers**
  - [*联川生物*·植物细胞marker数据库总览，植物单细胞分析的最佳伴侣！| 植物单细胞专题](https://mp.weixin.qq.com/s/CXGkNuBDQin5MrPWMgt8ng)
  - [scPlantDB](https://biobigdata.nju.edu.cn/scplantdb/home) [*基迪奥生物*·分享一个好用的植物单细胞数据库](https://mp.weixin.qq.com/s/1dTCDc5U3dvCy15GfLRY4A)
  - [PlantCellMarker](https://www.tobaccodb.org/pcmdb/homePage) [*生信益站*·单细胞专题25| 植物细胞类型注释数据库: PlantCellMarker](https://mp.weixin.qq.com/s/Y1AyXa8jkQBV4yWo_HihTw)
  - [PsctH](http://jinlab.hzau.edu.cn/PsctH/) [*植物科学最前言*·PBJ | 华中农大开发出植物单细胞转录组综合数据库，提供综合全面的单细胞Marker基因资源和单细胞研究的workflow](https://mp.weixin.qq.com/s/5dMORWQeX4eTFgH0e1YkTg)
  - [PlantscRNAdb](http://ibi.zju.edu.cn/plantscrnadb/index.php)

---



---

# Using [singleR](https://github.com/dviraran/SingleR) do annotation of cells/clusters
**Overview**
singleR: 对每个细胞做注释，而非对cluster做注释！拿到参考数据集的RNA@counts矩阵后，计算每种细胞的平均表达量后做log处理。而查询数据集的data矩阵按每个细胞去拟合参考数据集的细胞类型表达模式，所有两个数据集共同所有的基因数很重要。参考数据集获取可以来自于scRNA，也可以bulkRNA，因为最终是对数据集bulk化，参考数据集最终是**细胞类型×基因**的矩阵。
我有一个疑问,构建reference对counts做的logcounts处理和查询数据做了Normalization的data，在计算方式上不一样，这样会影响singleR注释。假设不考虑两次数据实验误差。我想到了，如果singleR设计的时候查看的是不同基因的波动而非专注于某个值的话，就不会在意这个问题
logcounts()：对原始计数数据进行对数转换，减少数据的偏态分布。输出对数转换后的矩阵，值的范围通常在0到10之间。
Normalization()：对原始计数数据进行归一化处理，调整每个细胞的总读数。输出归一化后的矩阵，值的范围通常在0到1之间。

**Input**
ref_data需要有RNA的counts层
query_data需要有RNA的data层

**Script**
ref和query对象的基因名一致性较好√
ref和query对象的基因名注释体系完全不一样
  - 拿到ref.protein.fa和query.protein.fa做blastp比对拿到一对一关系，根据一对一关系对ref.rds取子集后对基因重命名
  - 只拿到cds.fa文件，做DNA的blastn

**Output**

**Reference**
> [使用singleR基于自建数据库来自动化注释单细胞转录组亚群](https://mp.weixin.qq.com/s/GpOxe4WLIrBOjbdH5gfyOQ)

---
