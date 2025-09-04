# Using [sctype](https://github.com/IanevskiAleksandr/sc-type) do annotation of cells/clusters
- **Brief:** 用csv中对应关系注释单细胞数据新建一列细胞注释信息
- **Fature** 
- **Log:** 
  - v1.0.0
    - 250903 Assay通过`assay_key`传参，默认Assay为'RNA'，Assay下必须具有scale.data
    - 250828 简化marker基因可视化方案，dotplot和vlnplot

---
# Input
- **Variable**

|变量名|类型|必需|参数说明|
|-|-|-|-|
|input_query_rds|File|是|待注释的已做过标准化处理的Seurat对象(`.rds`),包含`scale.data``和HVGs`|
|assay_key|String|否|指定Assay且该Assay必须具有scale.data，如若不指定则默认为RNA|
|marker_csv|File|是|对应细胞表达的marker基因(`.csv`)|
|tissue|String|是|`"leaf"`|组织类型见`.csv`里面的第一列名`tissueType`|
|cluster_key|String|是|待注释的Seurat对象分群列名见`colnames(seu@meta.data)`|
|reduction_key|String|是|降维可视化的umap键名(如`"umap"`)|
|save_rds|String|是|保存文件名(需以`.rds`结尾)|
|n_circle|Int|是|每个cluster/circle包含最多数量|
|mem|Int|是|资源|
|cluster_color_csv|File|否|`cluster_key`唯一值与颜色的对应关系|

**marker_csv**: Four columns(`tissueType`,`cellName`,`geneSymbolmore1`,`geneSymbolmore2`,`shortName`), `geneSymbolmore1` stores high expression genes(positive) and `geneSymbolmore2` stores low expression genes(negative)
| tissueType | cellName | geneSymbolmore1 | geneSymbolmore2 | shortName |
|-|-|-|-|-|
| leaf | dividing cells | LOC-Os04g40940,LOC-Os01g16650,LOC-Os04g47580,LOC-Os08g40170 |  | dividing cells |
| leaf | Meristem | LOC-Os07g03770,LOC-Os03g51690,LOC-Os01g19694,LOC-Os10g26340,LOC-Os06g12610,LOC-Os03g14080,LOC-Os01g67410,LOC-Os05g45460 |  | Meristem |
| leaf | Procambium | LOC-Os06g44750,LOC-Os04g04330,LOC-Os11g25920,LOC-Os06g12610,LOC-Os03g14080,LOC-Os10g05690,LOC-Os04g56850,LOC-Os08g44750,LOC-Os03g43930,LOC-Os05g01810 |  | Procambium |

- **Note**
  - 检查输入的rds文件和csv文件
  - 查看单细胞矩阵的基因与细胞类型的marker基因格式一致
  - 查看rds文件当前assay是否有`scale.data`和`variable features`

```R
> seu <- readRDS('/data/work/Single-Cell-Pipeline/Anno-sctype/input/NipLSD10_anno_merged_data.rds')
> head(rownames(seu))
[1] "LOC-Os01g01010" "LOC-Os01g01150" "LOC-Os01g01120" "LOC-Os01g01312"
[5] "LOC-Os01g01060" "LOC-Os01g01390"
> seu
An object of class Seurat 
29773 features across 22566 samples within 1 assay 
Active assay: RNA (29773 features, 3000 variable features)
3 layers present: counts, data, scale.data
2 dimensional reductions calculated: pca, umap
```
- **Example** [download](https://github.com/ydgenomics/Annos/blob/main/Anno-sctype/v1.0.0/Anno-sctype_v1.0.0.csv)

| EntityID | input_query_rds | input_marker_csv | prefix | tissue | cluster_key | reduction_key | mem_sctype |
| --- | --- | --- | --- | --- | --- | --- | --- |
| yd_test | NipLSD10_anno_merged_data_obj_after_choir.rds | rice_leaf_marker0614.csv | rice | leaf | CHOIR_clusters_0.05 | CHOIR_P0_reduction_UMAP | 8 |

---
# Output
- **Frame**
```shell
tree /data/users/yangdong/yangdong_db936836d4034b638f5c86db02932db1/online/Single-Cell-Pipeline/Anno-sctype/test
/data/users/yangdong/yangdong_db936836d4034b638f5c86db02932db1/online/Single-Cell-Pipeline/Anno-sctype/test
├── DotPlot_NipLSD10_anno_merged_data.rds.pdf
├── NipLSD10_anno_merged_data_nodes.csv
├── NipLSD10_anno_merged_data_sctype.pdf
├── NipLSD10_anno_merged_data_sctype.rds
├── NipLSD10_anno_merged_data_sctype_scores_sorted.csv
├── report.txt
└── VlnPlot_NipLSD10_anno_merged_data.rds.pdf

1 directory, 7 files
```
- **Interpretation**
  - VlnPlot_*.pdf DotPlot_*pdf 查看选取的marker基因在待注释分组中的特异性
  - _nodes.csv 绘制大小圈图的输入文件
  - _scores_sorted.csv 待注释群和sctype注释结果的得分
  - report.txt 打印有多少基因在scale.data矩阵中(为hvgs),是被考虑作为自动注释的marker基因
  - _sctype.rds sctype注释后会新建一列sctype保存注释信息
  - _sctype.pdf 可视化注释后结果，sctype的umap图和sctype给每个群注释细胞类型打分的大小圈图

---
# Detail
- **Pipeline**
sctype：*Fully-automated and ultra-fast cell-type identification using specific marker combinations from single-cell transcriptomic data*。输入csv格式的marker基因列表，关注查询数据集的scale.data的矩阵，按查询分群来做注释，一个群可能会被分到多个细胞类型，取最优，同时如果太差会被认定为Unknown。前期marker基因的准备很重要，要选取高质量的marker基因，csv的marker基因要尽可能多的存在于查询数据的scale.data的基因中。
  1. 提取seurat对象scale.data矩阵数据，所以marker是hvg很重要！；
  2. 根据细胞类型对应的marker基因得到**细胞类型×细胞名**的表格，值为基因表达值(scale.data)计算得到的`sctype_score`，所以marker基因一定要为hvg，或者就没法在scale.data找到。实现了将几千的维度降低到二位数以内，而且维度与细胞类型直接关联
  3. 关注每个细胞在各个细胞类型的得分，基于得分高低可以把每个细胞注释为得分最高的细胞，对于我们关注的cluster而言，一个cluster的每个细胞都是单独注释的，这样就可以得到这个cluster里面有多少个细胞注释为该细胞类型，对应的得分应该是累计的，最后将该cluster注释到的细胞类型得分进行排序，只展示前10得分
  4. 取每个cluster得分最高的细胞类型就可以将该cluster注释为该细胞类型
  5. 对于低代表性的群注释为"Unknown"，即该cluster的所有细胞类型得分差距都不大，未表现出特异性
  6. 源代码：可视化大小圈意义，大圈是cluster细胞数，小圈是score大小，但是存在score大于细胞数的情况，导致大圈被迫变大而非真实的细胞数
  7. 修改后的可视化解决了三个问题，umap分群颜色和圆圈图颜色对应、大圈大小与细胞数正相关、小圈大小为得分占比乘以细胞数大小(保证小圈永远小于大圈大小)
- **Software**
  - sctype
- **Script**
  - plot.R
  - anno_sctype.R
- **Image**
  - Seurat-R--10, Seurat-R--09

# Reference & Citation
> [单细胞全自动注释篇(四)——ScType](https://mp.weixin.qq.com/s/hKBiZCHwDdoJOk0YChbtMA)

# Coder
- [yangdong/yangdong@genomics.cn](https://github.com/ydgenomics)
- [Anno-sctype](https://github.com/ydgenomics/Annos/tree/main/Anno-sctype)