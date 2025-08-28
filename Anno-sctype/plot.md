[2024·FeaturePlot可视化及常用参数浅析](https://mp.weixin.qq.com/s/y5OUrAa9F8SIuZY-QqOKIw)
[2023·Featureplot美化](https://mp.weixin.qq.com/s/SVnOLyTWUSr4ynG6ps1ZZQ)

[2023·Violin plot 美化](https://mp.weixin.qq.com/s/YXjK59_jkZtXrK4WqtpX9A)
```R
VlnPlot
function (object, features, cols = NULL, pt.size = NULL, alpha = 1, 
    idents = NULL, sort = FALSE, assay = NULL, group.by = NULL, 
    split.by = NULL, adjust = 1, y.max = NULL, same.y.lims = FALSE, 
    log = FALSE, ncol = NULL, slot = deprecated(), layer = NULL, 
    split.plot = FALSE, stack = FALSE, combine = TRUE, fill.by = "feature", 
    flip = FALSE, add.noise = TRUE, raster = NULL)
```
| 参数              | 类型 / 默认值            | 说明                                 |
| --------------- | ------------------- | ---------------------------------- |
| **object**      | Seurat 对象           | 必需。要绘图的单细胞对象。                      |
| **features**    | 字符向量                | 必需。要展示的基因（或特征）列表。                  |
| **cols**        | 颜色向量 / NULL         | 为不同分组指定颜色；NULL 时自动配色。              |
| **pt.size**     | 数值 / NULL           | 添加抖动点时，点的大小；NULL 按默认。              |
| **alpha**       | 数值 \[0,1] / 1       | 小提琴及点透明度；1 为不透明。                   |
| **idents**      | 字符向量 / NULL         | 仅在这些细胞身份（cell identity）里绘图。        |
| **sort**        | 逻辑 / FALSE          | TRUE 时按表达量均值排序分组。                  |
| **assay**       | 字符 / NULL           | 指定使用哪个 assay，如 "RNA"、"integrated"。 |
| **group.by**    | 字符 / NULL           | 按哪一列 meta.data 分组（如 "celltype"）。   |
| **split.by**    | 字符 / NULL           | 在图外再分面，如 "sample"。                 |
| **adjust**      | 数值 / 1              | 小提琴核密度带宽调节因子；>1 更平滑。               |
| **y.max**       | 数值 / NULL           | 强制设置 y 轴上限；NULL 自动。                |
| **same.y.lims** | 逻辑 / FALSE          | TRUE 时所有小图共用同一 y 轴范围。              |
| **log**         | 逻辑 / FALSE          | TRUE 时先对表达量取 log2 再绘图。             |
| **ncol**        | 整数 / NULL           | 多图组合时的列数；NULL 自动。                  |
| **slot**        | 已弃用                 | 老版本用 slot 指定矩阵位置，现用 assay。         |
| **layer**       | 字符 / NULL           | 指定使用哪一层数据（如 "counts", "data"）。     |
| **split.plot**  | 逻辑 / FALSE          | TRUE 时每个 identity 单独一图，不合并。        |
| **stack**       | 逻辑 / FALSE          | TRUE 时把多个特征纵向堆叠在一起。                |
| **combine**     | 逻辑 / TRUE           | FALSE 时返回 ggplot 列表而非合并图。          |
| **fill.by**     | "feature" / "ident" | "feature" 按基因配色；"ident" 按细胞身份配色。   |
| **flip**        | 逻辑 / FALSE          | TRUE 时把 x 轴、y 轴互换，常用于横向展示。         |
| **add.noise**   | 逻辑 / TRUE           | 在图中加入抖动点，防止过度重叠。                   |
| **raster**      | 逻辑 / NULL           | TRUE 时把点栅格化，加速大样本绘图；NULL 自动。       |


[ComplexHeatmap：终极热图绘制工具](https://mp.weixin.qq.com/s/yuGTP_HFCj5XGcb5aEqDhw)
[单细胞分析细胞marker基因热图展示，美化热图](https://mp.weixin.qq.com/s/r6b6qWrNBQhVqRJE4XaVaw)
[如何为热图添加行/列分类注释色块？](https://mp.weixin.qq.com/s/vgwMTx3L1l2_MGRupN62Yw)
```R
pheatmap
function (mat, color = colorRampPalette(rev(brewer.pal(n = 7, 
    name = "RdYlBu")))(100), kmeans_k = NA, breaks = NA, border_color = ifelse(nrow(mat) < 
    100 & ncol(mat) < 100, "grey60", NA), cellwidth = NA, cellheight = NA, 
    scale = "none", cluster_rows = TRUE, cluster_cols = TRUE, 
    clustering_distance_rows = "euclidean", clustering_distance_cols = "euclidean", 
    clustering_method = "complete", clustering_callback = NA, 
    cutree_rows = NA, cutree_cols = NA, treeheight_row = ifelse(class(cluster_rows) == 
        "hclust" || cluster_rows, 50, 0), treeheight_col = ifelse(class(cluster_cols) == 
        "hclust" || cluster_cols, 50, 0), legend = TRUE, legend_breaks = NA, 
    legend_labels = NA, annotation_row = NA, annotation_col = NA, 
    annotation = NA, annotation_colors = NA, annotation_legend = TRUE, 
    annotation_names_row = TRUE, annotation_names_col = TRUE, 
    drop_levels = TRUE, show_rownames = TRUE, show_colnames = TRUE, 
    main = NA, fontsize = 10, fontsize_row = fontsize, fontsize_col = fontsize, 
    angle_col = c("270", "0", "45", "90", "315"), display_numbers = FALSE, 
    number_format = "%.2f", number_color = "grey30", fontsize_number = 0.8 * 
        fontsize, gaps_row = NULL, gaps_col = NULL, labels_row = NULL, 
    labels_col = NULL, filename = NA, width = NA, height = NA, 
    silent = FALSE, na_col = "#DDDDDD", name = NULL, fontfamily = "", 
    fontfamily_row = fontfamily, fontfamily_col = fontfamily, 
    fontface = 1, fontface_row = fontface, fontface_col = fontface, 
    heatmap_legend_param = list(), ..., run_draw = FALSE) 
```
| 参数                                                    | 中文一句话说明                       |
| ----------------------------------------------------- | ----------------------------- |
| **mat**                                               | 必需，数值矩阵/数据框，热图主体。             |
| **color**                                             | 配色函数，默认 7 级 RdYlBu 渐变色。       |
| **kmeans\_k**                                         | 把行/列做 k-means 聚类，指定聚类数。       |
| **breaks**                                            | 自定义颜色断点。                      |
| **border\_color**                                     | 单元格边框颜色；小矩阵默认 "grey60"。       |
| **cellwidth / cellheight**                            | 手动指定单元格宽/高（像素）。               |
| **scale**                                             | 行或列标准化："none"、"row"、"column"。 |
| **cluster\_rows / cluster\_cols**                     | 是否对行/列做层次聚类。                  |
| **clustering\_distance\_rows / \_cols**               | 距离度量："euclidean" 等。           |
| **clustering\_method**                                | 聚类方法："complete"、"ward.D2" 等。  |
| **clustering\_callback**                              | 自定义聚类回调函数。                    |
| **cutree\_rows / cutree\_cols**                       | 在热图旁画多少条树状分隔线。                |
| **treeheight\_row / \_col**                           | 树状图高度（像素）。                    |
| **legend**                                            | 是否画颜色条图例。                     |
| **legend\_breaks / legend\_labels**                   | 自定义图例刻度/标签。                   |
| **annotation\_row / annotation\_col / annotation**    | 额外的行/列注释数据框。                  |
| **annotation\_colors**                                | 注释配色字典。                       |
| **annotation\_legend**                                | 是否显示注释图例。                     |
| **annotation\_names\_row / annotation\_names\_col**   | 是否显示注释名称。                     |
| **drop\_levels**                                      | 是否丢弃注释变量中的未用水平。               |
| **show\_rownames / show\_colnames**                   | 是否显示行/列名。                     |
| **main**                                              | 主标题。                          |
| **fontsize / fontsize\_row / fontsize\_col**          | 全局/行/列字体大小。                   |
| **angle\_col**                                        | 列名旋转角度。                       |
| **display\_numbers**                                  | TRUE 时在格子内显示数值。               |
| **number\_format / number\_color / fontsize\_number** | 数值格式、颜色、大小。                   |
| **gaps\_row / gaps\_col**                             | 手动插入行/列间隔位置。                  |
| **labels\_row / labels\_col**                         | 自定义行/列标签。                     |
| **filename / width / height**                         | 保存文件路径及尺寸（英寸）。                |
| **silent**                                            | TRUE 时不输出进度信息。                |
| **na\_col**                                           | 缺失值颜色。                        |
| **name**                                              | 热图对象名（返回用）。                   |
| **fontfamily / fontfamily\_row / fontfamily\_col**    | 字体族。                          |
| **fontface / fontface\_row / fontface\_col**          | 字形（粗体、斜体）。                    |
| **heatmap\_legend\_param**                            | 传给图例的额外参数列表。                  |
| **...**                                               | 传递给底层 `grid::draw` 的其他图形参数。   |
| **run\_draw**                                         | FALSE 时仅返回热图对象而不绘制。           |


# Heatmap
```R

#生成注释信息：



# 添加热图并设置背景注释色块，包含行和列注释信息
Heatmap(as.matrix(aver_dt),
    width = unit(w, "cm"), # 设置热图宽度
    height = unit(h, "cm"), # 设置热图高度
    name = "expression", # 图例名称
    col = mycol, # 热图颜色
    cluster_columns = FALSE, # 不聚类列
    cluster_rows = FALSE, # 不聚类行
    column_names_side = "top", # 列名显示在顶部
    column_names_rot = 60, # 列名旋转角度
    row_title = "Top 5 TFs", # 行标题
    rect_gp = gpar(col = "white", lwd = 1.5), # 热图边框设置
    heatmap_legend_param = list(
        legend_height = unit(2.8, "cm"), # 图例高度
        grid_width = unit(0.4, "cm"), # 图例色块宽度
        labels_gp = gpar(col = "gray20", fontsize = 10) # 图例标签样式
    ),
    top_annotation = col_anno # 添加列注释
) +
    row_anno # 添加行注释

col_anno <- HeatmapAnnotation(
  df = aver_dt,
  show_annotation_name = FALSE,
  gp = gpar(col = "white", lwd = 2),
  col = list(
    cell = c(
    "g0" = "#E41A1C", "g1" = "#377EB8", "g2" = "#4DAF4A", "g3" = "#984EA3", "g4" = "#FF7F00",
    "g5" = "#FFFF33", "g6" = "#A65628", "g7" = "#F781BF", "g8" = "#999999", "g9" = "#66C2A5",
    "g10" = "#FC8D62", "g11" = "#8DA0CB", "g12" = "#E78AC3", "g13" = "#A6D854", "g14" = "#FFD92F",
    "g15" = "#E5C494", "g16" = "#B3B3B3", "g17" = "#B15928", "g18" = "#1F78B4"
    )
  )
)

# 根据 cluster 分类给 gene 添加颜色注释
# 假设 result_df 有 cluster 和 gene 两列
cluster_colors <- c(
    "dividing cells" = "#E41A1C",
    "Meristem" = "#377EB8",
    "procambium" = "#4DAF4A",
    "Phloem" = "#984EA3",
    "Xylem" = "#FF7F00",
    "Xylem parenchyma" = "#FFFF33",
    "Sclerenchyma" = "#A65628",
    "Epidermis" = "#F781BF",
    "Large parenchyma" = "#999999",
    "Bundle sheath" = "#66C2A5"
)
row_cols <- setNames(cluster_colors[result_df$cluster], result_df$gene)
row_cols
head(result_df, n = 8)
# cluster	gene
# <chr>	<chr>
# 1	dividing cells	LOC-Os04g40940
# 2	dividing cells	LOC-Os01g16650
# 3	dividing cells	LOC-Os04g47580
# 4	dividing cells	LOC-Os08g40170
# 5	Meristem	LOC-Os07g03770
# 6	Meristem	LOC-Os03g51690
# 7	Meristem	LOC-Os01g19694
# 8	Meristem	LOC-Os10g26340

#生成注释信息：
row_anno <- rowAnnotation(foo = anno_text(rownames(aver_dt),
								location = 0,
								just = "left",
								gp = gpar(fill = row_cols,
										  col = "black",
										  fontface = 'italic'),
								width = max_text_width(rownames(dt))*1.25))


# 添加热图并设置背景注释色块，包含行和列注释信息
Heatmap(as.matrix(aver_dt),
    width = unit(w, "cm"), # 设置热图宽度
    height = unit(h, "cm"), # 设置热图高度
    name = "expression", # 图例名称
    #col = mycol, # 热图颜色
    cluster_columns = FALSE, # 不聚类列
    cluster_rows = FALSE, # 不聚类行
    column_names_side = "top", # 列名显示在顶部
    column_names_rot = 60, # 列名旋转角度
    row_title = "Top 5 TFs", # 行标题
    rect_gp = gpar(col = "white", lwd = 1.5), # 热图边框设置
    heatmap_legend_param = list(
        legend_height = unit(2.8, "cm"), # 图例高度
        grid_width = unit(0.4, "cm"), # 图例色块宽度
        labels_gp = gpar(col = "gray20", fontsize = 10) # 图例标签样式
    ),
    top_annotation = col_anno, # 添加列注释
    left_annotation = row_anno, # 添加行注释
    cell_fun = function(j, i, x, y, width, height, fill) {
        grid.rect(x = x, y = y, width = unit(0.8, "cm"), height = unit(0.3, "cm"), gp = gpar(col = NA, fill = fill))
    }
)
# 添加热图并设置背景注释色块，包含行和列注释信息
pdf('test.pdf',width=12, height=24)
Heatmap(as.matrix(aver_dt),
    # width = unit(w, "cm"), # 设置热图宽度
    # height = unit(h, "cm"), # 设置热图高度
    name = "expression", # 图例名称
    #col = mycol, # 热图颜色
    cluster_columns = FALSE, # 不聚类列
    cluster_rows = FALSE, # 不聚类行
    column_names_side = "top", # 列名显示在顶部
    column_names_rot = 60, # 列名旋转角度
    row_title = "Top 5 TFs", # 行标题
    rect_gp = gpar(col = "white", lwd = 1.5), # 热图边框设置
    heatmap_legend_param = list(
        legend_height = unit(2.8, "cm"), # 图例高度
        grid_width = unit(0.4, "cm"), # 图例色块宽度
        labels_gp = gpar(col = "gray20", fontsize = 10) # 图例标签样式
    ),
    top_annotation = col_anno, # 添加列注释
    # right_annotation = row_anno, # 添加行注释
    # cell_fun = function(j, i, x, y, width, height, fill) {
    #     grid.rect(x = x, y = y, width = unit(0.8, "cm"), height = unit(0.3, "cm"), gp = gpar(col = NA, fill = fill))
    # }
)
dev.off()
```