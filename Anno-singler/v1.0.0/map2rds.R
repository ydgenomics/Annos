# Date: 250722
# /software/miniconda/envs/Seurat/bin/R

library(Seurat)
library(optparse)

option_list <- list(
  make_option(c("-r", "--input_ref_rds"), type = "character", default = "/data/work/SingleR/convert/Sv.hr.rds",
              help = "Reference Seurat RDS file [default: %default]"),
  make_option(c("-b", "--reciprocal_best_txt"), type = "character", default = "/data/work/SingleR/output/reciprocal_best.txt",
              help = "Reciprocal best txt file [default: %default]")
)
opt <- parse_args(OptionParser(option_list = option_list))
input_ref_rds <- opt$input_ref_rds
reciprocal_best_txt <- opt$reciprocal_best_txt

seu <- readRDS(input_ref_rds); print(seu)
blast <- read.csv(reciprocal_best_txt,sep='\t',header = FALSE)
head(blast)


# 1. Seurat 基因集合
seu_genes <- rownames(seu)

# 2. 计算两列的命中数
n_v1 <- sum(blast$V1 %in% seu_genes);print(paste0("Common number in V1: ", n_v1))
n_v2 <- sum(blast$V2 %in% seu_genes);print(paste0("Common number in V2: ", n_v2))

# 3. 决定用哪一列做 key
if (n_v1 >= n_v2) {
  key_col   <- "V1"
  value_col <- "V2"
} else {
  key_col   <- "V2"
  value_col <- "V1"
}

# 4. 只保留 key 列存在于 Seurat 的行
blast_sub <- blast[blast[[key_col]] %in% seu_genes, ]

# 5. 建立映射表（key → value）
gene_map <- setNames(blast_sub[[value_col]], blast_sub[[key_col]])

# 6. 提取 counts 矩阵
mat <- GetAssayData(seu, slot = "counts")  # 稀疏矩阵 (dgCMatrix)
# 7. 只保留 gene_map 中有的基因
genes_to_keep <- intersect(rownames(mat), names(gene_map))
mat <- mat[genes_to_keep, , drop = FALSE]
# 8. 按映射改名
rownames(mat) <- gene_map[genes_to_keep]
# 9. 强制把行名变成普通字符向量
new_rownames <- as.character(unname(rownames(mat)))
# 10. 直接赋值给矩阵
rownames(mat) <- new_rownames
# 11. 再创建 Seurat 对象
seu_new <- CreateSeuratObject(counts = mat,meta.data = seu@meta.data)
# seu_new$celltypes <- ifelse(seu_new$celltypes %in% mapping$old, mapping$new[match(seu_new$celltypes, mapping$old)], seu_new$celltypes)
saveRDS(seu_new, paste0(sub("\\.rds$", "", basename(input_ref_rds)), "_genes_changed.rds"))