### Date: 250829
### VlnPlot, DotPlot
### [使用ggplot2美化Dotplot结果](https://mp.weixin.qq.com/s/rXbm4SQO6tl5hjY_BTI3dQ)

library(Seurat)
library(grid) 
library(patchwork)
library(ggplot2)
library(dplyr)
library(optparse)

option_list <- list(
    make_option(
        c("--input_rds"),
        type = "character",
        default = "/data/work/Single-Cell-Pipeline/Anno-sctype/input/NipLSD10_anno_merged_data.rds",
        help = "Path to input RDS file [default: %default]"
    ),
    make_option(
        c("--markers_csv"),
        type = "character",
        default = "/data/work/Single-Cell-Pipeline/Anno-sctype/input/rice_leaf_marker.csv",
        help = "Path to markers CSV file [default: %default]"
    ),
    make_option(
        c("--cell_type"),
        type = "character",
        default = "leaf",
        help = "The value of tissue"
    ),
    make_option(
        c("--cluster_key"),
        type = "character",
        default = "seurat_clusters",
        help = "The clustering info key"
    )
)
opt <- parse_args(OptionParser(option_list = option_list))
input_rds <- opt$input_rds
markers_csv <- opt$markers_csv
cell_type <- opt$cell_type
cluster_key <- opt$cluster_key


seu <- readRDS(input_rds); print(seu)
prefix <- basename(input_rds); print(prefix)
print(colnames(seu@meta.data))


cell_markers <- read.csv(markers_csv)
cell_markers = cell_markers[cell_markers$tissueType == cell_type,] 
cell_markers$geneSymbolmore1 = gsub(" ","",cell_markers$geneSymbolmore1); cell_markers$geneSymbolmore2 = gsub(" ","",cell_markers$geneSymbolmore2)
cell_markers$geneSymbolmore1 = gsub("///",",",cell_markers$geneSymbolmore1);cell_markers$geneSymbolmore1 = gsub(" ","",cell_markers$geneSymbolmore1)
cell_markers$geneSymbolmore2 = gsub("///",",",cell_markers$geneSymbolmore2);cell_markers$geneSymbolmore2 = gsub(" ","",cell_markers$geneSymbolmore2)
cat("\n###Head markers of cell annotation \n")
print(head(cell_markers))


gene_df <- do.call(rbind, lapply(seq_len(nrow(cell_markers)), function(i) {
  celltype <- cell_markers$cellName[i]
  genes    <- unlist(strsplit(cell_markers$geneSymbolmore1[i], ","))
  genes    <- genes[genes %in% rownames(seu)]
  if (length(genes) == 0) return(NULL)
  data.frame(gene = genes, cluster = celltype, stringsAsFactors = FALSE)
}))
gene_df <- unique(gene_df) # Delate repeat rows
print(head(gene_df))

# --------- VlnPlot ---------
p1  <- VlnPlot(
    seu,
    features = gene_df$gene,
    group.by = cluster_key,
    fill.by = 'ident',
    flip = TRUE,
    stack = TRUE,
) +
ggtitle(paste0(cluster_key, " of ", prefix)) +
theme(plot.title = element_text(hjust = 0.5, size = 8))

p2 <- p1 + NoLegend()
ggsave(p2,
    file = paste0("VlnPlot_", prefix,".pdf"),
    height = 1 + length(gene_df$gene)/4,
    width = 1 + length(unique(seu@meta.data[[cluster_key]]))/2,
    dpi = 100
)
gene_df <- gene_df[!duplicated(gene_df$gene), ]
# ----------- DotPlot --------------- 
pdf(paste0("DotPlot_", prefix,".pdf"), width= 1 + 0.2*length(gene_df$gene), height= 2 + 0.3*length(unique(gene_df$cluster)))
# 1. 绘制 DotPlot：按 cluster 分组展示基因
#    - split(gene_df$gene, gene_df$cluster) 把基因按 cluster 分面
#    - cols 指定颜色梯度：白色(低表达) → 火砖红(高表达)
p <- DotPlot(
        seu,
        features = split(gene_df$gene, gene_df$cluster),
        cols     = c("#ffffff", "firebrick3"),
        group.by = cluster_key
) +
    RotatedAxis() +
    theme(
        strip.text.x = element_text(size = 8),
        axis.text.x  = element_text(
            color = "black",
            size  = 10,          # 字号
            family = "serif",    # 字体族（可选：serif/sans/mono/自定义）
            face   = "plain",     # 粗体/斜体/普通 bold//plain
            angle  = 70          # 旋转90°（与 RotatedAxis 二选一即可）
        ),
        panel.border  = element_rect(color = "black"),
        panel.spacing = unit(1, "mm"),
        axis.title    = element_blank()
    )
print(p)
dev.off()