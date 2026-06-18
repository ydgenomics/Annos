# 使用jupyter转换为html，可以添加其它模块吗？比如提供接入api模块，可选择子图片的保存，在html里面查找群特异基因

- 使用 Plotly 替代静态绘图
- 在 HTML 中交互式查找群特异基因（无需后台服务器）
- 纯前端 JavaScript 接入（推荐，不需要服务器）

在单细胞分析（如使用 Seurat、Scanpy 等）完成后，通常会产生大量的图片（如 UMAP 降维图、Marker 基因小提琴图、细胞比例条形图）和表格（如差异表达基因列表、细胞数量统计）。

将这些离散的结果整合成一个交互式、可读性高的 **HTML 报告**，是生信下游分析的常规需求。以下是目前生信领域最主流的 **4 种落地方案**，从代码级定制到工具箱自动化，你可以根据团队的技术栈进行选择。

---

## 方案一：R Markdown / Quarto（最推荐，R 语言生态）

如果你的单细胞分析是用 R (Seurat) 做的，**R Markdown (`.Rmd`)** 或其升级版 **Quarto (`.qmd`)** 是官方且最优雅的解决方案。它们支持直接运行 R 代码，捕获 GGplot 图像，并将其与 Markdown 文本完美融合成一个 HTML 文件。

### 1. 编写 `.Rmd` 文件示例

创建一个名为 `sc_report.Rmd` 的文件：

```markdown
---
title: "单细胞 RNA-Seq 质控与聚类报告"
author: "Bioinformatics Team"
date: "`r Sys.Date()`"
output: 
  html_document:
    toc: true
    toc_float: true
    theme: cosmo
    code_folding: hide
---

## 1. 细胞降维与聚类 (UMAP)
以下是基于 Seurat 聚类后生成的 UMAP 降维图：

```{r umap_plot, warning=FALSE, message=FALSE, fig.width=8, fig.height=6}
library(Seurat)
library(ggplot2)

# 假设 pbmc 是你分析好的 Seurat 对象
# DimPlot(pbmc, reduction = "umap", group.by = "celltype") + theme_minimal()

# 示例：用内置绘图模拟
DimPlot(pbmc, reduction = "umap")

```

## 2. 差异表达基因 (DEGs) 列表

使用 `DT` 包可以把普通的表格变成支持前端搜索、分页、排序的交互式 HTML 表格：

```{r deg_table}
library(DT)
# 假设 deg_df 是 FindAllMarkers 算出来的表格
# datatable(deg_df, filter = 'top', options = list(pageLength = 10))

# 示例数据
datatable(head(iris, 20), options = list(pageLength = 5))

```

```

### 2. 编译生成 HTML
在 R 终端或 RStudio 中运行以下命令，即可在本地生成一个自包含（Self-contained）的 `sc_report.html`：

```R
library(rmarkdown)
render("sc_report.Rmd")

```

---

## 2. 方案二：Jupyter Notebook 导出（Python 生态）

如果你的单细胞分析是用 Python (Scanpy / MuData) 做的，日常分析多半在 Jupyter Notebook 中完成。你可以直接通过 `nbconvert` 将其转化为美观的 HTML。

### 1. 丰富你的 Notebook

* 使用 `scanpy.pl.umap(adata)` 绘制的图片会直接内嵌在 Cell 的输出中。
* 使用 `import pandas as pd` 显示的表格默认在 Notebook 中就是 HTML 格式。

### 2. 一键转换为 HTML

在终端执行以下命令，可以将 `.ipynb` 文件静态化输出为网页：

```bash
jupyter nbconvert --to html sc_analysis.ipynb

```

> **进阶提示：隐藏代码块**
> 如果报告是给无代码背景的导师或合作方看，可以加上 `--no-input` 参数，这样生成的 HTML 网页里就只有文字、图片和表格，没有任何代码。
> ```bash
> jupyter nbconvert --to html sc_analysis.ipynb --no-input
> 
> ```
> 
> 

---

## 方案三：MultiQC 自定义模块（多样本自动化汇报）

如果你有多个单细胞样本，或者想把单细胞分析的质控（QC）指标与上游的比对（CellRanger）指标整合在一起，**MultiQC** 是标准解法。虽然它主要用于上游，但它支持通过 **Custom Content（自定义内容）** 读入你导出的图片和表格。

### 1. 准备数据结构

你需要把单细胞分析里的表格存为 `.txt` 或 `.tsv`，图片存为 `.png`。
例如，将细胞比例存在 `cell_counts_mqc.txt` 中，内容必须带有 MultiQC 的文件头（Header）：

```text
# id: sc_cell_counts
# plot_type: table
# section_name: '单细胞各样本细胞类型统计'
# description: '展示了每个样本通过质控后的不同细胞亚群数量。'
CellType    Sample_A    Sample_B
T_cells     1200        1450
B_cells     450         380
Macrophage  800         920

```

### 2. 运行 MultiQC

将包含上述文件以及 UMAP 图片的文件夹传给 MultiQC：

```bash
multiqc . --title "单细胞分析综合报告"

```

MultiQC 会自动识别带有 `# plot_type: table` 的文件，并将其转换为 HTML 报告中的交互式表格，同时也可以把图片挂载到报告的特定位置。

---

## 方案四：Python / R 脚本手动组装（适合做自动化 Pipeline）

如果你正在开发一套单细胞自动化分析流程（Nextflow / Snakemake），希望流程结束时自动拼装网页，不想依赖 Rmd 或 Notebook 的渲染环境，可以使用 **Python 的 Jinja2 模板引擎** 动态组装。

### 1. 准备一个 HTML 模板 (`template.html`)

```html
<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>单细胞分析结果</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .chart { margin-bottom: 30px; text-align: center; }
        img { max-width: 80%; height: auto; box-shadow: 0 0 10px #ccc; }
        table { border-collapse: collapse; width: 100%; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>单细胞分析自动化报告</h1>
    <hr>
    
    <h2>1. 细胞聚类图 (UMAP)</h2>
    <div class="chart">
        <img src="{{ umap_img_path }}" alt="UMAP Plot">
    </div>

    <h2>2. 高表达 Marker 基因列表</h2>
    <div>
        {{ table_html | safe }}
    </div>
</body>
</html>

```

### 2. 使用 Python 脚本填充数据并输出

```python
import pandas as pd
from jinja2 import Template

# 1. 读入你的单细胞分析表格，转为标准 HTML 字符串
df = pd.read_csv("deg_markers.csv")
table_html = df.head(10).to_html(classes='dataframe', index=False)

# 2. 读取模板
with open("template.html", "r", encoding="utf-8") as f:
    template_str = f.read()

template = Template(template_str)

# 3. 渲染并保存
rendered_html = template.render(
    umap_img_path="plots/umap.png",  # 这里可以用相对路径，也可以用 base64
    table_html=table_html
)

with open("sc_final_report.html", "w", encoding="utf-8") as f:
    f.write(rendered_html)

```

---

## 💡 总结与选型建议

* **如果你平时用 R (Seurat)**：毫不犹豫选择 **R Markdown / Quarto**，可以用 `DT` 包做表格，用 `plotly` 包把 UMAP 图变成可以鼠标悬停看细胞标签的动态图。
* **如果你平时用 Python (Scanpy)**：直接用 **Jupyter Notebook** 分析，最后用 `nbconvert --no-input` 导出一式两份（一份留底，一份给合作者）。
* **如果你在写标准化生信流程 (Pipeline)**：建议使用 **方案四（Jinja2 组装）** 或 **MultiQC 自定义内容**，方便在服务器后端脱离图形界面批量生成。