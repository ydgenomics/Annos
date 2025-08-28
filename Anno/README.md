# Anno
- **Brief:** 用csv中对应关系注释单细胞数据新建一列细胞注释信息
- **Fature** 
- **Log:** 
  - v1.0.0
    - 250828 完善Description, 支持rds和h5ad的注释


# Input
- **Variable**
  - `input_file` Array[File] 待注释的文件(.rds/.h5ad)且包含分群的键(与`input_csv`第一列列名一致)
  - `input_csv` Array[File] 分群和细胞类型对应关系，第一列列名为分群的键名，第二列列名为即将添加到meta.data的键
  - `reduction_key` Array[String] 可视化umap的键名，其中Seurat方法可视化键要强一致，scanpy的umap对应.obsm['X_umap']
- **Example** [download]()

| EntityID | input_file | input_csv | reduction_key |
|-|-|-|-|
| test_peanut | /Files/yangdong/wdl/SCP/Dataget/W202508040017201/01_dataget/H1314_dataget/H1314.h5ad | /Files/yangdong/wdl/SCP/Annotation/anno_H1314.csv | umap |
| test_peanut | /Files/yangdong/wdl/SCP/Dataget/W202508040017201/01_dataget/H2014_dataget/H2014.h5ad | /Files/yangdong/wdl/SCP/Annotation/anno_H2014.csv | umap |

---
# Output
- **Frame**
```shell
tree /data/input/Files/yangdong/wdl/SCP/Annotation/W202508090004764
/data/input/Files/yangdong/wdl/SCP/Annotation/W202508090004764
├── H1314_anno.h5ad
├── H1314_anno.pdf
├── H2014_anno.h5ad
├── H2014_anno.pdf
└── input.json

1 directory, 5 files
```
- **Interpretation**
  - `anno.rds/anno.h5ad` 添加注释信息后输出的rds/h5ad
  - `anno.pdf` 可视化分群键和新添加注释键的umap
- **Next**
  - Integration_scIB
  - Similarity

---
# Detail
- **Pipeline** 读取文件，新建列，可视化并保存更新的文件
- **Software**
  - Seurat
  - scanpy
- **Script**
  - anno_csv.py
  - anno_csv.R
- **Image**
  - Integration-R--05

---
# Reference & Citation


---
# Coder
- **Editor:** yangdong (yangdong@genomics.cn)
- **GitHub:** [ydgenomics](https://github.com/ydgenomics)
- **Prospect:** Focused on innovative, competitive, open-source projects and collaboration
- **Repository:** [Annos/Anno](https://github.com/ydgenomics/Annos/tree/main/Anno)