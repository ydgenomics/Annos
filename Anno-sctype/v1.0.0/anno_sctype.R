# Date: 250903 anno_sctype.R
# Description: Using sctype to annotate single-cell RNA-seq data based on marker gene csv.
# Input: marker_csv file, query .rds file, cluster key in query .rds object, and UMAP reduction name
# Output: "_sctype.rds" and "_sctype_umap.pdf" files
# Image: Seurat-R--04 /software/miniconda/envs/Seurat/bin/R
# Reference: [单细胞全自动注释篇(四)——ScType](https://mp.weixin.qq.com/s/hKBiZCHwDdoJOk0YChbtMA)

lapply(c("ggraph","igraph","tidyverse", "data.tree"), library, character.only = T)
lapply(c("dplyr","Seurat","HGNChelper", "optparse"), library, character.only = T)
library(optparse)

option_list <- list(
    make_option(
        c("--input_marker_csv"), type = "character", default = "/data/work/script/sctype0614/rice_leaf_marker0614.csv", help = "Path to marker csv file"),
    make_option(
        c("--tissue"), type = "character", default = "leaf", help = "Tissue type"),
    make_option(
        c("--input_query_rds"), type = "character", default = "/data/work/script/sctype0614/output/day3/NipLSD3_anno_merged_data_obj_after_choir_sctype.rds", help = "Path to input Seurat RDS file"),
    make_option(
        c("--assay_key"), type = "character", default = "RNA", help = "Assay key in Seurat object"), # e.g. `RNA` or `SCT` 
    make_option(
        c("--cluster_key"), type = "character", default = "CHOIR_clusters_0.05", help = "Cluster key in Seurat object"), # e.g. `CHOIR_clusters_0.05`
    make_option(
        c("--umap_name"), type = "character", default = "CHOIR_P0_reduction_UMAP", help = "UMAP reduction name"), # `CHOIR_P0_reduction_UMAP`
    make_option(
        c("--n_circle"), type = "integer", default = 5, help = "Number of small circles to display per cluster (default: 5)")
)

opt <- parse_args(OptionParser(option_list = option_list))
input_marker_csv <- opt$input_marker_csv
tissue <- opt$tissue  # tissue type, e.g. leaf, root, etc.
input_query_rds <- opt$input_query_rds
assay_key <- opt$assay_key
cluster_key <- opt$cluster_key
umap_name <- opt$umap_name
n_circle <- opt$n_circle # 'n_circle' added by ydgenomics to adjust the display number of small circle in per cluster

########### load gene set preparation function ###################
gene_sets_prepare <- function(path_to_db_file, cell_type){
  #cell_markers = openxlsx::read.xlsx(path_to_db_file)
  cell_markers = read.csv(path_to_db_file) # 之前的读取xlsx文件有点不好编辑，改为读取csv文件
  cell_markers = cell_markers[cell_markers$tissueType == cell_type,] 
  cell_markers$geneSymbolmore1 = gsub(" ","",cell_markers$geneSymbolmore1); cell_markers$geneSymbolmore2 = gsub(" ","",cell_markers$geneSymbolmore2)
  cell_markers$geneSymbolmore1 = gsub("///",",",cell_markers$geneSymbolmore1);cell_markers$geneSymbolmore1 = gsub(" ","",cell_markers$geneSymbolmore1)
  cell_markers$geneSymbolmore2 = gsub("///",",",cell_markers$geneSymbolmore2);cell_markers$geneSymbolmore2 = gsub(" ","",cell_markers$geneSymbolmore2)
  gs = lapply(1:nrow(cell_markers), function(j) gsub(" ","",unlist(strsplit(toString(cell_markers$geneSymbolmore1[j]),",")))); names(gs) = cell_markers$cellName
  gs2 = lapply(1:nrow(cell_markers), function(j) gsub(" ","",unlist(strsplit(toString(cell_markers$geneSymbolmore2[j]),",")))); names(gs2) = cell_markers$cellName
  list(gs_positive = gs, gs_negative = gs2)
}

############ load cell type annotation function ################
sctype_score <- function(scRNAseqData, scaled = !0, gs, gs2 = NULL, gene_names_to_uppercase = !0, ...){
  
  # check input matrix
  if(!is.matrix(scRNAseqData)){
    warning("scRNAseqData doesn't seem to be a matrix")
  } else {
    if(sum(dim(scRNAseqData))==0){
       warning("The dimension of input scRNAseqData matrix equals to 0, is it an empty matrix?")
    }
  }
  
  # marker sensitivity
  marker_stat = sort(table(unlist(gs)), decreasing = T); 
  marker_sensitivity = data.frame(score_marker_sensitivity = scales::rescale(as.numeric(marker_stat), to = c(0,1), from = c(length(gs),1)),
                                      gene_ = names(marker_stat), stringsAsFactors = !1)

  # convert gene names to Uppercase
  #if(gene_names_to_uppercase){
  #  rownames(scRNAseqData) = toupper(rownames(scRNAseqData));
  #}
  
  # subselect genes only found in data
  names_gs_cp = names(gs); names_gs_2_cp = names(gs2);
  gs = lapply(1:length(gs), function(d_){ 
    GeneIndToKeep = rownames(scRNAseqData) %in% as.character(gs[[d_]]); rownames(scRNAseqData)[GeneIndToKeep]})
  gs2 = lapply(1:length(gs2), function(d_){ 
    GeneIndToKeep = rownames(scRNAseqData) %in% as.character(gs2[[d_]]); rownames(scRNAseqData)[GeneIndToKeep]})
  names(gs) = names_gs_cp; names(gs2) = names_gs_2_cp;
  cell_markers_genes_score = marker_sensitivity[marker_sensitivity$gene_ %in% unique(unlist(gs)),]
  
  # z-scale if not
  if(!scaled) Z <- t(scale(t(scRNAseqData))) else Z <- scRNAseqData
  
  # multiple by marker sensitivity
  for(jj in 1:nrow(cell_markers_genes_score)){
    Z[cell_markers_genes_score[jj,"gene_"], ] = Z[cell_markers_genes_score[jj,"gene_"], ] * cell_markers_genes_score[jj, "score_marker_sensitivity"]
  }
  
  # subselect only with marker genes
  Z = Z[unique(c(unlist(gs),unlist(gs2))), ]
  
  # combine scores
  es = do.call("rbind", lapply(names(gs), function(gss_){ 
    sapply(1:ncol(Z), function(j) {
      gs_z = Z[gs[[gss_]], j]; gz_2 = Z[gs2[[gss_]], j] * -1
      sum_t1 = (sum(gs_z) / sqrt(length(gs_z))); sum_t2 = sum(gz_2) / sqrt(length(gz_2));
      if(is.na(sum_t2)){
        sum_t2 = 0;
      }
      sum_t1 + sum_t2
    })
  })) 
  
  dimnames(es) = list(names(gs), colnames(Z))
  es.max <- es[!apply(is.na(es) | es == "", 1, all),] # remove na rows
 
  es.max
}

#' Run ScType for cell type annotation

seu <- readRDS(input_query_rds)
if ("sctype" %in% colnames(seu@meta.data)) {
  seu$sctype0 <- seu$sctype
}
gs_list <- gene_sets_prepare(input_marker_csv, tissue); str(gs_list)
gene_vector <- unlist(c(gs_list$gs_positive, gs_list$gs_negative))[unlist(c(gs_list$gs_positive, gs_list$gs_negative)) != "NA"]
gene_vector <- unique(as.character(gene_vector))

DefaultAssay(seu) <- assay_key; print(seu)
# message("Running NormalizeData, FindVariableFeatures, and ScaleData.")
# seu <- NormalizeData(seu, normalization.method = "LogNormalize", scale.factor = 10000)
# seu <- FindVariableFeatures(seu)
# seu <- ScaleData(seu)

# check Seurat object version (scRNA-seq matrix extracted differently in Seurat v4/v5)
seurat_package_v5 <- isFALSE('counts' %in% names(attributes(seu[["RNA"]])));
print(sprintf("Seurat object %s is used", ifelse(seurat_package_v5, "v5", "v4")))

# extract scaled scRNA-seq matrix
scRNAseqData_scaled <- if (seurat_package_v5) as.matrix(seu[[assay_key]]$scale.data) else as.matrix(seu[[assay_key]]@scale.data)
missing_genes <- setdiff(gene_vector, rownames(scRNAseqData_scaled))

# 放在脚本第一行即可
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
  cat("###These marker genes are not found in the input scale.data of scRNA-seq data:\n")
  print(missing_genes)
})

# run ScType
es.max <- sctype_score(scRNAseqData = scRNAseqData_scaled, scaled = TRUE, gs = gs_list$gs_positive, gs2 = gs_list$gs_negative)
str(es.max)

# NOTE: scRNAseqData parameter should correspond to your input scRNA-seq matrix. For raw (unscaled) count matrix set scaled = FALSE
# When using Seurat, we use "RNA" slot with 'scale.data' by default. Please change "RNA" to "SCT" for sctransform-normalized data,
# or to "integrated" for joint dataset analysis. To apply sctype with unscaled data, use e.g. pbmc[["RNA"]]$counts or pbmc[["RNA"]]@counts, with scaled set to FALSE.

# # merge by cluster
# cL_resutls <- do.call("rbind", lapply(unique(seu@meta.data[[cluster_key]]), function(cl){
#     es.max.cl = sort(rowSums(es.max[ ,rownames(seu@meta.data[seu@meta.data[[cluster_key]]==cl, ])]), decreasing = !0)
#     head(data.frame(cluster = cl, type = names(es.max.cl), scores = es.max.cl, ncells = sum(seu@meta.data[[cluster_key]]==cl)), 10)
# }))

# 'n_circle' added by ydgenomics to adjust the display number of small circle in per cluster 
cL_resutls <- do.call("rbind", lapply(unique(seu@meta.data[[cluster_key]]), function(cl){
  es.max.cl = sort(rowSums(es.max[ ,rownames(seu@meta.data[seu@meta.data[[cluster_key]]==cl, ])]), decreasing = !0)
  head(data.frame(cluster = cl, type = names(es.max.cl), scores = es.max.cl, ncells = sum(seu@meta.data[[cluster_key]]==cl)), n=n_circle)
}))

sctype_scores <- cL_resutls %>% group_by(cluster) %>% top_n(n = 1, wt = scores)  

# set low-confident (low ScType score) clusters to "unknown"
sctype_scores$type[as.numeric(as.character(sctype_scores$scores)) < sctype_scores$ncells/4] <- "Unknown"
print(sctype_scores[,1:3])
sctype_scores_sorted <- sctype_scores %>% arrange(type)
write.csv(sctype_scores_sorted, paste0(sub("\\.rds$", "", basename(input_query_rds)), "_sctype_scores_sorted.csv"), row.names = FALSE)

seu@meta.data$sctype = ""
for(j in unique(sctype_scores$cluster)){
  cl_type = sctype_scores[sctype_scores$cluster==j,]; 
  seu@meta.data$sctype[seu@meta.data[[cluster_key]] == j] = as.character(cl_type$type[1])
}

#p3 <- DimPlot(pbmc, reduction = "umap", label = TRUE, repel = TRUE, group.by = 'sctype_classification')        
#source("https://raw.githubusercontent.com/kris-nader/sc-type/master/R/sctype_wrapper.R"); 
#pbmc <- run_sctype(pbmc,known_tissue_type="Immune system",custom_marker_file="https://raw.githubusercontent.com/IanevskiAleksandr/sc-type/master/ScTypeDB_full.xlsx",name="sctype_classification",plot=TRUE)


# prepare edges
cL_resutls <- cL_resutls[order(cL_resutls$cluster),]; 
edges = cL_resutls; edges$type = paste0(edges$type,"_",edges$cluster); 
edges$cluster = paste0("cluster ", edges$cluster); edges = edges[,c("cluster", "type")]; 
colnames(edges) = c("from", "to"); rownames(edges) <- NULL

# prepare nodes
nodes_lvl1 <- sctype_scores[,c("cluster", "ncells")]; 
nodes_lvl1$cluster = paste0("cluster ", nodes_lvl1$cluster); 
nodes_lvl1$Colour = "#f1f1ef"; nodes_lvl1$ord = 1; 
nodes_lvl1$realname = nodes_lvl1$cluster; 
nodes_lvl1 = as.data.frame(nodes_lvl1); 
nodes_lvl2 = c(); 

# 获取 Idents 的唯一值数量
Idents(seu) <- cluster_key
num_idents <- length(unique(Idents(seu)))
# 预定义的颜色方案
predefined_colors <- c("#5f75ae", "#92bbb8", "#64a841", "#e5486e", "#de8e06", "#eccf5a", 
                    "#b5aa0f", "#e4b680", "#7ba39d", "#b15928", "#ffff99", 
                    "#6a3d9a", "#cab2d6", "#ff7f00", "#fdbf6f", "#e31a1c", 
                    "#fb9a99", "#33a02c", "#b2df8a", "#1f78b4", "#a6cee3")
# 如果唯一值数量大于 21，生成随机颜色
if (num_idents > 21) {
# 获取所有可用的颜色
all_colors <- colors()
# 从可用颜色中随机选择不重复的颜色
random_colors <- sample(all_colors, num_idents, replace = FALSE)
# 将随机颜色存储到 ccolss
ccolss <- random_colors
} else {
# 如果唯一值数量小于或等于 21，使用预定义的颜色方案
ccolss <- predefined_colors[1:num_idents]
}
# 查看生成的颜色方案
#print(ccolss)

####### Old nodes way: big circular is cell number and small circular is score number ###########
# for (i in 1:length(unique(cL_resutls$cluster))){
#   dt_tmp = cL_resutls[cL_resutls$cluster == unique(cL_resutls$cluster)[i], ]; 
#   nodes_lvl2 = rbind(nodes_lvl2, data.frame(cluster = paste0(dt_tmp$type,"_",dt_tmp$cluster), ncells = dt_tmp$scores, Colour = ccolss[i], ord = 2, realname = dt_tmp$type))
# }

########## added by ydgenomics ###########
for (i in seq_along(unique(cL_resutls$cluster))) {
  dt_tmp  <- cL_resutls[cL_resutls$cluster == unique(cL_resutls$cluster)[i], ]
  dt_tmp$scores[dt_tmp$scores<1] = 1
  total   <- sum(dt_tmp$scores)                     # 该 cluster 总分数
  ncells_cl <- unique(dt_tmp$ncells)                # 该 cluster 总细胞数（唯一值）
  # 计算百分比 × 总细胞数
  dt_tmp$ncells_new <- (dt_tmp$scores / total) * ncells_cl
  nodes_lvl2 <- rbind(
    nodes_lvl2,
    data.frame(
      cluster  = paste0(dt_tmp$type, "_", dt_tmp$cluster),
      ncells   = dt_tmp$ncells_new,               # 新的权重
      Colour   = ccolss[i],
      ord      = 2,
      realname = dt_tmp$type
    )
  )
}

nodes <- rbind(nodes_lvl1, nodes_lvl2); nodes$ncells[nodes$ncells<1] = 1;
files_db <- read.csv(input_marker_csv)[,c("cellName","shortName")]; 
files_db = unique(files_db); 
nodes = merge(nodes, files_db, all.x = T, all.y = F, by.x = "realname", by.y = "cellName", sort = F)
nodes$shortName[is.na(nodes$shortName)] = nodes$realname[is.na(nodes$shortName)]; nodes = nodes[,c("cluster", "ncells", "Colour", "ord", "shortName", "realname")]
write.csv(nodes, paste0(sub("\\.rds$", "", basename(input_query_rds)), "_nodes.csv"), row.names = FALSE)

mygraph <- graph_from_data_frame(edges, vertices=nodes)

# Make the graph
gggr <- ggraph(mygraph, layout = 'circlepack', weight=I(ncells)) + 
    geom_node_circle(aes(filter=ord==1,fill=I("#F5F5F5"), colour=I("#D3D3D3")), alpha=0.9) +
    geom_node_circle(aes(filter=ord==2,fill=I(Colour), colour=I("#D3D3D3")), alpha=0.9) +
    theme_void() + 
    geom_node_text(aes(filter=ord==2, label=shortName, colour=I("#ffffff"), fill="white", repel = !1, parse = T, size = I(log(ncells,25)*1.5)))+ 
    geom_node_label(aes(filter=ord==1,  label=shortName, colour=I("#000000"), size = I(3), fill="white", parse = T), repel = !0, segment.linetype="dotted")

# 1) 取出 Seurat 中真实的 cluster 顺序
cl_order <- sort(unique(seu@meta.data[[cluster_key]]))  # 1,2,3,...,56
# 2) 构造颜色映射表（以 cluster 为 key）
col_map <- setNames(unique(nodes_lvl2$Colour), unique(cL_resutls$cluster))

# # 3) 直接画图
# DimPlot(seu,
#         reduction = umap_name,
#         label      = TRUE,
#         repel      = TRUE,
#         cols       = col_map[cl_order])  # 保证顺序完全一致
p4 <- DimPlot(seu, reduction = umap_name, group.by = cluster_key, label = TRUE, repel = TRUE, cols = col_map[cl_order])+ gggr
p5 <- DimPlot(seu, reduction = umap_name, group.by = "sctype", label = TRUE, repel = TRUE)
output_query_rds <- paste0(sub("\\.rds$", "", basename(input_query_rds)), "_sctype.rds")
output_umap <- paste0(sub("\\.rds$", "", basename(input_query_rds)), "_sctype_umap.pdf")
plot_height=8
pdf(output_umap, width = 2.5 * plot_height, height = plot_height)
print(p4)
print(p5)
dev.off()

print(colnames(seu@meta.data))
saveRDS(seu, output_query_rds)