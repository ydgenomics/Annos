# Using [singleR](https://github.com/dviraran/SingleR) do annotation of cells/clusters
- **Brief:** 用csv中对应关系注释单细胞数据新建一列细胞注释信息
- **Fature** 
- **Log:** 
  - v1.0.0
    - 250828 提交Description

---
# Input
- **Variable**
  - `input_query_rds` 待注释的.rds文件包含RNA@data即标准化处理后的矩阵
  - `input_query_fa` 非必须文件，待注释数据对应蛋白质文件，如果要做基因名一致性处理需要做蛋白质序列比对
  - `input_ref_rds` 参考rds文件包含RNA@counts和已经注释细胞类型的键`ref_cluster_key`
  - `input_ref_fa` 非必须文件，参考数据矩阵基因对应蛋白质文件，如果要做基因名一致性处理需要做蛋白质序列比对 
  - `ref_cluster_key` 参考数据储存细胞类型的键名见`colnames(seu@meta.data)`
  - `umap_name` 降维可视化umap的键名例如"umap"
  - `whether_protein` 是否是做蛋白质序列比对，"yes" or "no"
  - `mem_alignment` 任务运行内存GB
  - `mem_singler` 任务运行内存GB
- **Example** [download](https://github.com/ydgenomics/Annos/blob/main/Anno-singler/v1.0.0/Anno-singler_v1.0.0.csv)

| EntityID | input_query_rds | input_query_fa | input_ref_rds | input_ref_fa | ref_cluster_key | umap_name | whether_protein | mem_alignment | mem_singler |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| yd_test | Os.hr.rds | Osativa_323_v7.0.protein1.fa | Sv.hr.rds | Sviridis_500_v2.1.protein1.fa | celltypes | Xumap_ | yes | 8 | 16 |

---
# Output
- **Frame**
```sehll
tree /data/input/Files/ResultData/Workflow/W202507220030347
/data/input/Files/ResultData/Workflow/W202507220030347
├── anno_singler
│   ├── report.txt
│   ├── Os.hr_singler.pdf
│   ├── Os.hr_singler.rds
│   └── Sv.hr_genes_changed_ref_singler.Rdata
└── input.json

1 directories, 5 files
```
- **Interpretation**



---
# Detail
- **Pipeline**
singleR: 对每个细胞做注释，而非对cluster做注释！拿到参考数据集的RNA@counts矩阵后，计算每种细胞的平均表达量后做log处理。而查询数据集的data矩阵按每个细胞去拟合参考数据集的细胞类型表达模式，所有两个数据集共同所有的基因数很重要。参考数据集获取可以来自于scRNA，也可以bulkRNA，因为最终是对数据集bulk化，参考数据集最终是**细胞类型×基因**的矩阵。`logcounts()`：对原始计数数据进行对数转换，减少数据的偏态分布。输出对数转换后的矩阵，值的范围通常在0到10之间。`Normalization()`：对原始计数数据进行归一化处理，调整每个细胞的总读数。输出归一化后的矩阵，值的范围通常在0到1之间。
  - ref和query对象的基因名一致性较好√
  - ref和query对象的基因名注释体系完全不一样: 拿到ref.protein.fa和query.protein.fa做blastp比对拿到一对一关系，根据一对一关系对ref.rds取子集后对基因重命名; 只拿到cds.fa文件，做核酸的比对
- **Software**
  - singleR
- **Script**
  - anno_singler.R

---
# Reference & Citation
> [使用singleR基于自建数据库来自动化注释单细胞转录组亚群](https://mp.weixin.qq.com/s/GpOxe4WLIrBOjbdH5gfyOQ)

---
# Coder
- **Editor:** yangdong (yangdong@genomics.cn)
- **GitHub:** [ydgenomics](https://github.com/ydgenomics)
- **Prospect:** Focused on innovative, competitive, open-source projects and collaboration
- **Repository:** [Annos/Anno-singler](https://github.com/ydgenomics/Annos/tree/main/Anno-singler)