[scPlantDB下载拟南芥的全组织marker基因](https://biobigdata.nju.edu.cn/scplantdb/marker)
```R
> unique(at$tissue)
# [1] "Leaf"             "Shoot axis apex"  "Unknow"           "Root"
# [5] "Hypocotyl callus" "Inflorescence"    "Pollen"
> unique(at$clusterName)
#  [1] "Mesophyll"
#  [2] "Leaf pavement cell"
#  [3] "Companion cell"
#  [4] "Xylem"
#  [5] "Leaf guard cell"
#  [6] "Phloem parenchyma"
#  [7] "S phase"
#  [8] "Vascular tissue"
#  [9] "Shoot apical meristem"
# [10] "Shoot system epidermis"
# [11] "Guard cell"
# [12] "Unknow"
# [13] "G2/M phase"
# [14] "Sieve element"
# [15] "Hydathodes"
# [16] "Phloem"
# [17] "Lateral root cap"
# [18] "Root cortex"
# [19] "Root endodermis"
# [20] "Root cap"
# [21] "Non-hair"
# [22] "Root hair"
# [23] "G1/G0 phase"
# [24] "Columella root cap"
# [25] "Root procambium"
# [26] "Xylem pole pericycle"
# [27] "Phloem pole pericycle"
# [28] "Protoxylem"
# [29] "Metaxylem"
# [30] "Root stele"
# [31] "Pericycle"
# [32] "Meristematic cell"
# [33] "Stem cell niche"
# [34] "Root epidermis"
# [35] "Phloem/Pericycle"
# [36] "Spongy mesophyll"
# [37] "Palisade mesophyll"
# [38] "Stress response"
# [39] "Bundle sheath"
# [40] "Leaf epidermis"
# [41] "Explant vasculature and callus founder cell"
# [42] "Outer cell layer"
# [43] "Inner cell layer"
# [44] "Middle cell layer"
# [45] "Lateral root primordia"
# [46] "Vascular cambium"
# [47] "Flower meristem"
# [48] "Cortex"
# [49] "Vegetative nuclei"
# [50] "Generative nuclei"
# [51] "Microspore nuclei"
# [52] "Contaminating nuclei"
# [53] "Sperm nuclei"
# [54] "Transitory"
> unique(at$dataset)    
#  [1] "CRA002977_1" "CRA002977_2" "DRP009643"   "ERP132245"   "SRP148288"  
#  [6] "SRP166333"   "SRP169576"   "SRP171040"   "SRP173393"   "SRP182008"
# [11] "SRP235541"   "SRP247828_1" "SRP247828_2" "SRP247828_3" "SRP253497"
# [16] "SRP267870"   "SRP273996"   "SRP279055"   "SRP280069"   "SRP285040"
# [21] "SRP285817"   "SRP292306"   "SRP307169"   "SRP320285"   "SRP330542"  
# [26] "SRP332285"   "SRP338044"   "SRP374045"   "SRP394711"   "SRP398011"
> colnames(at)
#  [1] "gene"        "name"        "p_val"       "p_val_adj"   "pct_1"      
#  [6] "pct_2"       "pct_diff"    "avg_log2FC"  "clusterName" "celltype_id"
# [11] "species"     "tissue"      "dataset"
```

```R
at <- read.csv()
# 提取关键字段
at$tissueType <- at$tissue
at$cellName <- at$clusterName
at$geneSymbolmore1 <- at$gene  # 假设 gene 是需要的基因字段

# 分组和聚合
library(dplyr)
grouped <- at %>%
  group_by(tissueType, cellName) %>%
  summarise(
    geneSymbolmore1 = paste(geneSymbolmore1, collapse = ","),
    geneSymbolmore2 = "",  # 假设没有第二个基因字段
    shortName = first(cellName),  # 假设 shortName 和 cellName 相同
    .groups = "drop"
  )

# 输出结果
head(grouped)
write.csv(grouped, "at_marker_sctype.csv",row.names = FALSE)
```