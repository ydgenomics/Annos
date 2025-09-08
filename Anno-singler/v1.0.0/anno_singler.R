# Date: 20250908 # Title: run_singler.R # Coder: ydgenomics
# Description: Using SingleR to annotate single-cell RNA-seq data based on a custom reference dataset.
# Input: reference .rds has RNA, query .rds files, and a metadata key for clustering in the reference dataset
# Image: Seurat-R-- /software/miniconda/envs/Seurat/bin/R
# Reference: [使用singleR基于自建数据库来自动化注释单细胞转录组亚群](https://mp.weixin.qq.com/s/GpOxe4WLIrBOjbdH5gfyOQ)

library(Seurat)
library(SingleCellExperiment)
library(scater)
library(SingleR)
library(optparse)

option_list <- list(
    make_option(
        c("-r", "--input_ref_rds"), type = "character", default = "/data/work/Single-Cell-Pipeline/Alignment/test/Os.hr_genes_changed.rds", help = "Path to the reference dataset"),
    make_option(
        c("-k", "--ref_cluster_key"), type = "character", default = "celltypes",help = "Metadata key for clustering in the reference dataset"),
    make_option(
        c("-q", "--input_query_rds"), type = "character", default = "/data/input/Files/yangdong/wdl/Anno-singler/Sv.hr.rds", help = "Path to the query dataset"),
    make_option(
        c("-d", "--query_cluster_key"), type = "character", default = "seurat_clusters",help = "Metadata key for clustering in the query dataset"),
    make_option(
        c("-u", "--umap_name"), type = "character", default = "Xumap_", help = "UMAP reduction name") # `CHOIR_P0_reduction_UMAP`
)
opt <- parse_args(OptionParser(option_list = option_list))
input_ref_rds <- opt$input_ref_rds
ref_cluster_key <- opt$ref_cluster_key
input_query_rds <- opt$input_query_rds
query_cluster_key <- opt$query_cluster_key
umap_name <- opt$umap_name

# Precheck genes 
write_report <- function(..., append = FALSE) {
  con <- file("report.txt", if (append) "at" else "wt")
  sink(con, type = "output")
  sink(con, type = "message")
  eval.parent(substitute(...))
  sink(type = "output")
  sink(type = "message")
  close(con)
}

write_report({
  ref_seu <- readRDS(input_ref_rds)
  cat("Reference dataset loaded successfully.\n")
  print(ref_seu)
  cat("First 10 genes in the reference dataset:\n")
  print(head(rownames(ref_seu), n=10))
  query_seu <- readRDS(input_query_rds)
  cat("\nQuery dataset loaded successfully.\n")
  print(query_seu)
  cat("First 10 genes in the Query dataset:\n")
  print(head(rownames(query_seu), n=10))
  common_genes <- intersect(rownames(ref_seu), rownames(query_seu))
  num_common_genes <- length(common_genes)
  print(paste0("The common gene number of Reference and Query data: ", num_common_genes))
})


# Step 1: Load the reference dataset and create a singleR reference Rdata object
create_ref_singler <- function(input_ref_rds, ref_cluster_key) {
    ref_seu <- readRDS(input_ref_rds);print(ref_seu); print(head(rownames(ref_seu), n=10))
    colnames(ref_seu@meta.data); Idents(ref_seu) <- ref_seu@meta.data[[ref_cluster_key]]
    av <- AggregateExpression(
        ref_seu, group.by = ref_cluster_key, assays = "RNA"
    )
    ref_mat <- av[[1]]
    ref_sce <- SingleCellExperiment(
        assays = list(counts = ref_mat)
    )
    ref_sce <- scater::logNormCounts(ref_sce)
    colData(ref_sce)$Type <- colnames(ref_mat)
    output_ref_rdata <- paste0(sub("\\.rds$", "", basename(input_ref_rds)), "_ref_singler.Rdata")
    save(ref_sce, file = output_ref_rdata)
    return(ref_sce)
}


# Step 2: Load the query dataset and run singleR for annotation
run_singler <- function(query_seu, ref_sce, prefix) {
    # query_seu <- readRDS(input_query_rds); DefaultAssay(query_seu) <- "RNA"
    DefaultAssay(query_seu) <- "RNA"
    # query_seu <- NormalizeData(query_seu, normalization.method = "LogNormalize", scale.factor = 10000)
    query_data <- GetAssayData(query_seu, slot = "data")
    common_genes <- intersect(rownames(query_data), rownames(ref_sce))
    num_common_genes <- length(common_genes)
    print(
        paste0(
            "The common gene number of Reference and Query data: ",
            num_common_genes
        )
    )
    pred <- SingleR(
        test = query_data, ref = ref_sce, labels = ref_sce$Type
    )
    # plot and save pred
    n_label <- length(unique(pred$labels))
    pdf(paste0(prefix, "_pred.pdf"), width = n_label, height = n_label/2)
    plotScoreHeatmap(pred)
    p <- plotDeltaDistribution(pred, ncol = 8, dots.on.top = FALSE); print(p)
    p <- plotScoreDistribution(pred, ncol = 8, dots.on.top = FALSE); print(p)
    dev.off()
    write.csv(pred, paste0(prefix, "_pred.csv"))
    # save to query_seu
    if ("singler" %in% colnames(query_seu@meta.data)) {
        query_seu$singler0 <- query_seu$singler
    }
    query_seu$singler <- pred$labels
    return(query_seu)
}

ref_sce <- create_ref_singler(input_ref_rds, ref_cluster_key)
prefix <- sub("\\.rds$", "", basename(input_query_rds))
seu <- run_singler(query_seu, ref_sce, prefix)
p <- DimPlot(seu, reduction = umap_name, group.by = 'singler', label = TRUE, repel = TRUE)
pdf(paste0(prefix, "_singler.pdf"), width = 10, height = 8)
print(p)
dev.off()
              
# The heatmap of component
df <- seu@meta.data[c(query_cluster_key, "singler")]
colnames(df) <- c("seurat_clusters", "singler")
              
library(dplyr)
library(tidyr)
library(tibble)

percentage_df <- df %>%
  dplyr::count(seurat_clusters, singler) %>%
  group_by(seurat_clusters) %>%
  mutate(pct = as.numeric(n / sum(n) * 100)) %>%  # 确保pct是数值型
  select(-n) %>%
  pivot_wider(
    names_from = singler,
    values_from = pct,
    values_fill = 0
  ) %>%
  column_to_rownames("seurat_clusters")

heatmap_matrix <- as.matrix(percentage_df)

library(pheatmap)
pdf(paste0(prefix, "_component.pdf"), width = length(unique(seu$singler))/2, height = length(unique(seu$singler))/2)
pheatmap(heatmap_matrix,
         cluster_rows = TRUE,
         cluster_cols = TRUE,
         display_numbers = TRUE,
         number_format = "%.1f",
         number_color = "black",
         color = colorRampPalette(c("white", "yellow", "red"))(100),
         main = "Cluster Component Heatmap")

dev.off()
              
# Save the annotated query dataset
output_query_rds <- paste0(prefix, "_singler.rds")
saveRDS(seu, file = output_query_rds)