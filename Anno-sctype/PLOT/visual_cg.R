# Date: 250719 # Visualize different plots(cell&gene)
# Image: metaNeighbor--07

library(Seurat)
library(scCustomize)
library(patchwork)
library(ggplot2)
library(paletteer)
library(dplyr)
library(ggsci)
library(ComplexHeatmap)
library(optparse)

option_list <- list(
    make_option(
        c("--input_rds"),
        type = "character",
        default = "/data/work/script/sctype0614/output/day3/NipLSD3_anno_merged_data_obj_after_choir_sctype.rds",
        help = "Path to input RDS file [default: %default]"
    ),
    make_option(
        c("--markers_csv"),
        type = "character",
        default = "/data/work/script/sctype0614/rice_leaf_marker0614.csv",
        help = "Path to markers CSV file [default: %default]"
    ),
    make_option(
        c("--cluster_color_csv"),
        type = "character",
        default = "/data/work/cluster_color.csv",
        help = "Path to cluster color CSV file [default: %default]"
    ),
    make_option(
        c("--cell_type"),
        type = "character",
        default = "leaf",
        help = "Tissue/cell type [default: %default]"
    ),
    make_option(
        c("--cluster_key"),
        type = "character",
        default = "resolution0.5",
        help = "Cluster key in Seurat object [default: %default]"
    ),
    make_option(
        c("--reduction_key"),
        type = "character",
        default = "CHOIR_P0_reduction_UMAP",
        help = "Reduction key for DimPlot [default: %default]"
    )
)

opt <- parse_args(OptionParser(option_list = option_list))
input_rds <- opt$input_rds
markers_csv <- opt$markers_csv
cluster_color_csv <- opt$cluster_color_csv
cell_type <- opt$cell_type
cluster_key <- opt$cluster_key
reduction_key <- opt$reduction_key

# 放在脚本第一行即可
write_report <- function(..., append = FALSE) {
  con <- file("report.txt", if (append) "at" else "wt")
  sink(con, type = "output")
  #sink(con, type = "message")
  eval.parent(substitute(...))
  sink(type = "output")
  #sink(type = "message")
  close(con)
}

write_report({

seu <- readRDS(input_rds);
cat("### Info of Seurat object \n")
print(seu)
cat("Columns of meta.data: \n")
print(colnames(seu@meta.data))
cat(paste0("Looked column: ", cluster_key, "\n"))
print(unique(seu@meta.data[[cluster_key]]))
    
cell_markers <- read.csv(markers_csv)
cell_markers = cell_markers[cell_markers$tissueType == cell_type,] 
cell_markers$geneSymbolmore1 = gsub(" ","",cell_markers$geneSymbolmore1); cell_markers$geneSymbolmore2 = gsub(" ","",cell_markers$geneSymbolmore2)
cell_markers$geneSymbolmore1 = gsub("///",",",cell_markers$geneSymbolmore1);cell_markers$geneSymbolmore1 = gsub(" ","",cell_markers$geneSymbolmore1)
cell_markers$geneSymbolmore2 = gsub("///",",",cell_markers$geneSymbolmore2);cell_markers$geneSymbolmore2 = gsub(" ","",cell_markers$geneSymbolmore2)
cat("\n###Head markers of cell annotation \n")
print(head(cell_markers))

# color <- c(paletteer_d("awtools::bpalette"),paletteer_d("awtools::a_palette"),paletteer_d("awtools::mpalette"))
cat("\n### Selecting colors of clusters \n")
cluster_color <- if (file.exists(cluster_color_csv)) {
                   read.csv(cluster_color_csv)
                 } else {
                   NULL
                 }
cl_seu <- sort(unique(as.character(seu@meta.data[[cluster_key]])))
if (is.null(cluster_color)) {
  cat("Cluster color CSV file not found. Generating random colors. \n")
  num_clusters <- length(cl_seu)
  set.seed(123) # 保证可复现
  color <- grDevices::colors()[sample(length(grDevices::colors()), num_clusters)]
} else {
  cat("Cluster color CSV file found. Using provided colors. \n")
  head(cluster_color)
  cl_tbl <- sort(unique(as.character(cluster_color$cluster)))
  if (identical(cl_seu, cl_tbl)) {
    cat("✓ Cluster colors match the Seurat object. \n")
    color <- cluster_color$color
    cl_seu <- unique(as.character(cluster_color$cluster))
    col_map <- setNames(cluster_color$color, cl_seu)
  } else {
    cat("✗ Cluster mismatch. \n")
    # 根据聚类数量生成不重复的随机颜色
    num_clusters <- length(cl_seu)
    set.seed(123) # 保证可复现
    color <- grDevices::colors()[sample(length(grDevices::colors()), num_clusters)]
  }
}
col_map <- setNames(color, cl_seu)
cat("View match relationship between cluster and color \n")
print(col_map)

p0 <- DimPlot(seu, reduction = reduction_key, group.by = cluster_key, label = TRUE, repel = TRUE, cols = col_map[cl_seu])
# 保存 UMAP 图
pdf("UMAP_plot.pdf", width = 10, height = 8)
print(p0)
dev.off()

all_genes <- c()
for (row in seq_len(nrow(cell_markers))) {
    celltype <- cell_markers$cellName[row]
    genes <- cell_markers$geneSymbolmore1[row]
    genes <- unlist(strsplit(genes, ","))
    genes_in_seu <- genes[genes %in% rownames(seu)]
    genes_not_in_seu <- genes[!genes %in% rownames(seu)]
    if (length(genes_not_in_seu) > 0) {
        message("The following genes are not in the Seurat object and will be skipped for cell type ", celltype, ": ", paste(genes_not_in_seu, collapse = ", "))
    }
    genes <- genes_in_seu
    all_genes <- c(all_genes, genes)
    if (length(genes) == 0) {
        message("No valid genes found for cell type ", celltype, ". Skipping.")
        next
    }
    
    ######### FeaturePlot #########
    plots <- list()
    for (i in seq_along(genes)) {
        plots[[i]] <- FeaturePlot_scCustom(
            seurat_object = seu,
            colors_use = colorRampPalette(c("#3288BD", "white", "#D53E4F"))(50),
            reduction = reduction_key,
            features = genes[i]
        ) + NoAxes()
    }
    # p <- wrap_plots(plots, ncol = 4)
    p <- wrap_plots(plots, ncol = 3) +
      plot_annotation(
        title = celltype,
        # subtitle = "可选副标题",
        theme = theme(plot.title = element_text(hjust = 0.5, size = 16))
      )
    
    side_length <- 4
    ggsave(
        p,
        file = paste0(celltype, "_FeaturePlot.pdf"),
        width = min(3 * side_length, 50),
        height = min(ceiling(length(genes)/3) * side_length, 50),
        dpi = 300
    )
}
######### Violin Plot #########
p1  <- VlnPlot(
    seu,
    features = unique(all_genes),
    group.by = cluster_key,
    fill.by = 'ident',
    flip = TRUE,
    stack = TRUE,
    cols = col_map[cl_seu],
) +
ggtitle("All genes") +
theme(plot.title = element_text(hjust = 0.5, size = 14))

p2 <- p1 + NoLegend()
ggsave(p2,
    file = "All_genes_VlnPlot.pdf",
    height = 1 + length(unique(all_genes))/4,
    width = 1 + length(unique(seu@meta.data[[cluster_key]]))/2,
    dpi = 300
)

######### DotPlot #########
p3 <- DoHeatmap(
    seu, # 绘制热图，附加自定义颜色和渐变色
    features = as.character(unique(all_genes)),
    group.by = cluster_key,
    assay = "RNA",
    slot = "data", # Default is 'scale.data'
    label = FALSE,
    group.colors = col_map[cl_seu],
) +
ggtitle("All genes") +
theme(plot.title = element_text(hjust = 0.5, size = 14)) + # 自定义群组颜色
scale_fill_gradientn(colors = c("white", "grey", "firebrick3")) # 颜色渐变

ggsave(p3,
    file = "All_genes_DoHeatmap.pdf",
    dpi = 300
)

############ Heatmap of AverageExpression ############
cat("\n###Average Expression in .data of Seurat object \n")
aver_dt <- AverageExpression(
    seu,
    features = unique(all_genes),
    group.by = cluster_key,
    layer = 'data'
)

aver_dt <- as.data.frame(aver_dt$RNA)
cat("View head geneXcluster \n")
print(aver_dt[1:6,1:6])


# 假设 mat 是你的数值矩阵
row_h  <- 5                    # 你想要的每行像素高度
n_row  <- nrow(aver_dt)
total_height <- row_h * n_row   # 整张图高度（像素）
# 经验换算：1 pt ≈ 1.333 像素 → 字号 = 像素 / 1.333
fontsize_row_value <- round(row_h / 1.333)

col_w  <- 3*row_h                    # 你想要的每列像素宽度
n_col  <- ncol(aver_dt)
total_width <- col_w * n_col    # 整张图宽度（像素）
# 经验换算：1 pt ≈ 1.333 像素
fontsize_col_value <- round(col_w / 1.333)/2

p4 <- pheatmap(
    as.matrix(aver_dt),
    scale = 'row',
    legend = TRUE,
    cellheight = row_h,            # 固定行高
    fontsize_row = fontsize_row_value,
    cellwidth = col_w,            # 固定列宽
    fontsize_col = fontsize_col_value,
    angle_col = "45",
    cluster_rows = TRUE,          # 如不想打乱行序
    cluster_cols = TRUE)
pdf("All_genes_pheatmap.pdf")
print(p4)
dev.off()
})