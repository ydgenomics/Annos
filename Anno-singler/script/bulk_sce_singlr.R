# Date: 0616
# 用bulk数据作为参考数据去分割scRNA数据(注释)，并做一定的可视化

# 加载必要的包
library(SingleCellExperiment)
library(SummarizedExperiment)

# # 读取文件
# file_path <- "/data/work/test/E1_exp.txt"
# data <- read.table(file_path, header = TRUE, sep = "\t", check.names = FALSE)

file_path <- "/data/work/test/E1_exp.txt"  # 替换为你的文件路径
data <- read.delim(file_path, header = TRUE, stringsAsFactors = FALSE)

# 提取基因表达矩阵
counts <- as.matrix(data[, -1])
rownames(counts) <- data$Geneid
ref_sce <- SingleCellExperiment(
    assays = list(counts = counts)
)
rownames(ref_sce) <- rownames(counts)
ref_sce <- scater::logNormCounts(ref_sce)
colData(ref_sce)$Type <- colnames(counts)
save(ref_sce, file = "/data/work/test/E1_exp_refsingler.Rdata")


library(Seurat)
library(SingleCellExperiment)
library(scater)
library(SingleR)
library(dplyr)
library(optparse)

input_query_rds <- "/data/users/yangdong/yangdong_faff775391984da0a355d4bd70217714/online/SCPipelines/pp_scRNA/cotton_dataget.hr.rds"
seu <- readRDS(input_query_rds); DefaultAssay(seu) <- "RNA"

seu <- seu
seu <- NormalizeData(seu)
seu <- FindVariableFeatures(seu, selection.method = "vst", nfeatures = 2000)
seu <- ScaleData(seu)

# seu <- RunPCA(seu, verbose = FALSE)
# seu <- RunUMAP(seu, reduction = "pca", dims = 1:30, verbose = FALSE)

# Step 2: Load the query dataset and run singleR for annotation
run_singler <- function(query_seu, ref_sce) {
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
    query_seu$singler <- pred$labels
    #output_query_rds <- paste0(sub("\\.rds$", "", basename(input_query_rds)), "_singler.rds")
    #saveRDS(query_seu, file = output_query_rds)
    return(query_seu)
}

seu <- run_singler(seu, ref_sce)
seu$time <- seu$singler

seu@meta.data$time <- case_when(
  seu@meta.data$time %in% c("E1_.1day_rep1", "E1_.1day_rep2") ~ "day-1",
  seu@meta.data$time %in% c("E1_0day_rep1", "E1_0day_rep2") ~ "day0",
  seu@meta.data$time %in% c("E1_.2day_rep1", "E1_.2day_rep2") ~ "day-2",
  seu@meta.data$time %in% c("E1_1day_rep1", "E1_1day_rep2") ~ "day1",
  TRUE ~ seu@meta.data$time
)

# 查看 Seurat 对象的元数据
head(seu@meta.data)

pdf("/data/work/test/bulk_anno.pdf")
DimPlot(seu, reduction = "Xumap_", label = TRUE, pt.size = 0.5, group.by = "leiden_res_0.50")
DimPlot(seu, reduction = "Xumap_", label = TRUE, pt.size = 0.5, group.by = "singler")
DimPlot(seu, reduction = "Xumap_", label = TRUE, pt.size = 0.5, group.by = "time")
dev.off()

pdf("/data/work/test/bulk_anno2.pdf", width=20, height=5)
DimPlot(seu, reduction = "Xumap_", label = TRUE, pt.size = 0.5, split.by = "time", group.by = "leiden_res_0.50")
dev.off()
saveRDS(seu, "/data/work/test/bulk_anno_seu.rds")


library(Seurat)
seu <- readRDS("/data/work/test/bulk_anno_seu.rds")

pdf("/data/work/test/Ga12g00054.pdf",width=12, height=6)
DotPlot(seu, features = "Ga12g00054", group.by = "leiden_res_0.50")
FeaturePlot(seu, features = "Ga12g00054", split.by = "time")
DoHeatmap(seu, features = "Ga12g00054", group.by = "leiden_res_0.50")
VlnPlot(seu, features = "Ga12g00054", group.by = "leiden_res_0.50")
dev.off()