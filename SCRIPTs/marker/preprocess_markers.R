# 预处理植物单细胞marker基因文件，统一成6列格式
# date: 260609

library(data.table)

smart_read_file <- function(file_path) {
  # 尝试用逗号分隔符读取
  tryCatch({
    df <- read.csv(file_path, sep = ",", header = TRUE)
    # 检查是否只有一列
    if (length(colnames(df)) == 1) {
      stop("Only one column detected, trying tab separator")
    }
    cat("成功用逗号分隔符读取\n")
    return(df)
  }, error = function(e) {
    cat("逗号分隔符读取失败，尝试其他方法...\n")
    
    # 如果是gz文件，先解压再读
    if (grepl("\\.gz$", file_path)) {
      cat("检测到gz压缩文件，正在解压...\n")
      temp_file <- tempfile()
      gunzip(file_path, destname = temp_file, remove = FALSE)
      
      # 尝试用制表符读取解压后的文件
      df <- tryCatch({
        read.csv(temp_file, sep = "\t", header = TRUE)
      }, error = function(e2) {
        # 如果制表符也失败，尝试自动检测
        read.csv(temp_file, header = TRUE)
      })
      
      unlink(temp_file)  # 删除临时文件
      cat("成功从gz文件读取\n")
      return(df)
    } else {
      # 非gz文件，直接用制表符读取
      df <- tryCatch({
        read.csv(file_path, sep = "\t", header = TRUE)
      }, error = function(e2) {
        # 如果制表符也失败，尝试自动检测
        read.csv(file_path, header = TRUE)
      })
      cat("成功用制表符分隔符读取\n")
      return(df)
    }
  })
}
    
#' 加载植物单细胞marker基因文件
#' @param file_path 文件路径
#' @return 返回6列的data.table: species, tissue, celltype, power, from, description
load_marker_file <- function(file_path) {
  # 检查是否已经包含所需的7列
  required_cols <- c("species", "tissue", "celltype", "gene", "power", "from", "description")
  df <- smart_read_file(file_path)
  
  # 根据列名判断数据源并处理
  if ("Celltypes" %in% colnames(df) && "Marker.genes" %in% colnames(df)) {
    # scPlantDB
    result <- data.table(
      species = gsub(" ", "_", df$Species),
      tissue = gsub(" ", "_", df$Tissue),
      celltype = gsub(" ", "_", df$Celltypes),
      gene = df$Marker.genes,
      power = ifelse(df$experiment == "Yes", "yes", "no"),
      from = "scPlantDB",
      description = paste("Source:", df$Source)
    )
    
  } else if ("Cell_type" %in% colnames(df) && "Gene_id" %in% colnames(df)) {
    # PCMDB https://www.tobaccodb.org/pcmdb/download
    result <- data.table(
      species = gsub(" ", "_", df$Species_type),
      tissue = gsub(" ", "_", df$Tissus_type),
      celltype = gsub(" ", "_", df$Cell_type),
      gene = df$Gene_id,
      power = ifelse(df$Marker_resource == "Experimental", "yes", "no"),
      from = "PCMDB",
      description = df$Description
    )
    
  } else if ("clusterName" %in% colnames(df) && "gene" %in% colnames(df)) {
    # PlantSCRNAdb http://ibi.zju.edu.cn/plantscrnadb/#/gene_marker
    result <- data.table(
      species = gsub(" ", "_", df$species),
      tissue = gsub(" ", "_", df$tissue),
      celltype = gsub(" ", "_", df$clusterName),
      gene = df$gene,
      power = ifelse(df$avg_log2FC == Inf, "yes", "no"),
      from = "PlantSCRNAdb",
      description = paste("Celltype:", df$celltype_id)
    )
  } else if (all(required_cols %in% colnames(df))) {
    cat("检测到文件已包含所需7列，直接使用\n")
    result <- df[, ..required_cols]  # 只保留这6列
    result <- unique(result)
  } else {
    stop("无法识别的文件格式")
  }
  
  # 清理空格
  result[, `:=`(
    species = gsub(" ", "_", species),
    tissue = gsub(" ", "_", tissue),
    celltype = gsub(" ", "_", celltype)
  )]
  
  # 去重
  result <- unique(result)
  
  cat(sprintf("加载完成: %d 条记录\n", nrow(result)))
  cat("species: ")
  cat(table(result$species), "\n")
  cat("tissue: ")
  cat(table(result$tissue), "\n")
  cat("celltype: ")
  cat(table(result$celltype), "\n")
  cat("power: ")
  cat(table(result$power), "\n")

  return(result)
}


# 使用示例
# markers <- load_marker_file("/data/work/Annos/MARKER/Gene_marker.txt")
# markers <- load_marker_file("/data/work/Annos/PCMDB_Download_20260609130536.csv")
# markers <- load_marker_file("/data/work/Annos/MARKER/arabidopsis_thaliana.marker_fd.csv")


s2s <- function(df, reciprocal_txt){
  # 读取BLAST结果文件
  df2 <- read.csv(reciprocal_txt, sep='\t', header=FALSE)
  
  # 合并数据框
  df <- tryCatch({
    # 尝试用 V2 列匹配
    result <- merge(df, df2, by.x = "gene", by.y = "V2", all.x = FALSE)
    # 重命名 V1 列为 new
    colnames(result)[colnames(result) == "V1"] <- "new"
    return(result)
  }, error = function(e) {
    # 如果失败，尝试用 V1 列匹配
    result <- merge(df, df2, by.x = "gene", by.y = "V1", all.x = FALSE)
    colnames(result)[colnames(result) == "V2"] <- "new"
    return(result)
  })
  
  # 查看结果
  head(df)
  
  return(df)
}

df_reconstructed <- df %>%
  group_by(species, tissue, celltype) %>%
  summarise(
    geneSymbolmore1 = paste(gene, collapse = ","),
    .groups = "drop"
  )

df_reconstructed <- df %>%
  group_by(species, tissue, celltype) %>%
  summarise(
    geneSymbolmore1 = paste(new, collapse = ","),
    .groups = "drop"
  )

df_reconstructed <- df_reconstructed %>%
  rename(
    tissueType = tissue,
    cellName = celltype
  )
df_reconstructed$geneSymbolmore2 <- NA

df_reconstructed$shortName <- df_reconstructed$cellName

write.csv(df_reconstructed, '/data/work/at_sp_stem_plantscrnaddb2.csv', row.names=FALSE)