我是一位植物单细胞数据生信分析专家，我拿到scanpy的anndata对象，现在想确定过滤低质量的细胞和基因的指标，想做一个类似cellxgene的拖动指标看那些细胞/基因被去除，基于quarto实现，对我的想法进行评价

---

# 单细胞 QC 交互过滤工具

## 设计思路

**服务端预计算 + 轻量前端交互**，避免每次拖动都重算 anndata。

```
服务器 (Python)                   浏览器 (Quarto + Observable JS)
┌──────────────────┐             ┌──────────────────────────────┐
│ anndata (.h5ad)  │             │  滑块拖动 → 实时筛选         │
│       ↓          │    CSV      │  ┌─ n_genes 范围 ───┐        │
│ 计算 QC 统计量   │ ─────────→  │  └─ total_counts ───┘        │
│ - n_genes        │             │  ┌─ pct_mito 上限 ──┐        │
│ - total_counts   │             │  └─ pct_chloro ─────┘        │
│ - pct_mito       │             │  ┌─ min_cells ──────┐        │
│ - pct_chloro     │             │  └───────────────────┘        │
│       ↓          │             │       ↓                       │
│ qc_stats.csv     │             │  实时可视化 + 统计概览        │
└──────────────────┘             └──────────────────────────────┘
```

## 文件说明

| 文件 | 作用 | 运行位置 |
| --- | --- | --- |
| `precompute_qc.py` | Python 预计算脚本 | **服务器** (一次性) |
| `qc_interactive.qmd` | Quarto 交互式 QC 文档 | **本地** (Quarto render) |
| `qc_stats_cells.csv` | 预计算输出的细胞统计 | 中间文件 |
| `qc_stats_genes.csv` | 预计算输出的基因统计 | 中间文件 |

## 使用流程

### 1️⃣ 服务器端：预计算 QC 统计量

```bash
conda activate scanpy
python precompute_qc.py -i /path/to/adata.h5ad -o ./qc_stats
```

参数说明:
- `-i` : 输入 `.h5ad` 文件
- `-o` : 输出前缀 (默认 `./qc_stats`，生成 `qc_stats_cells.csv` + `qc_stats_genes.csv`)
- `--mt-prefixes` : 自定义线粒体基因前缀 (默认: MT- mt- Mt- AtMp)
- `--chloro-prefixes` : 自定义叶绿体基因前缀 (默认: ChrM ChrC Pt- cp-)
- `--mt-genes` : 线粒体基因列表文件 (每行一个，优先级高于前缀)
- `--chloro-genes` : 叶绿体基因列表文件 (每行一个，优先级高于前缀)

### 2️⃣ 本地：Quarto 交互式探索

将生成的 `qc_stats_cells.csv` 和 `qc_stats_genes.csv` 放到本目录下，然后:

```bash
# 安装 Quarto (如未安装): https://quarto.org/docs/get-started/
quarto render qc_interactive.qmd
# 或实时预览
quarto preview qc_interactive.qmd
```

生成的 `qc_interactive.html` 是**自包含文件**，可直接分享。

### 3️⃣ 在浏览器中交互

打开 HTML 后，你可以:

- 🧬 拖动 **n_genes** 范围滑块 — 过滤检测基因数过少/过多的细胞
- 📊 拖动 **total_counts** 范围滑块 — 过滤 UMI 过低/过高的细胞
- 🧪 拖动 **pct_mito** 滑块 — 设置线粒体占比上限
- 🌿 拖动 **pct_chloro** 滑块 — 设置叶绿体占比上限 (植物特有)
- 🎯 拖动 **min_cells** 滑块 — 过滤在少数细胞中表达的基因
- 👀 实时查看过滤概览卡片 (保留/去除的细胞和基因数)
- 📉 查看过滤前后的分布对比直方图
- 📋 展开查看被去除的细胞 barcode 列表

## 技术栈

- **预计算**: Python + scanpy + pandas
- **交互前端**: Quarto + Observable JS + Plotly
- **部署**: 纯静态 HTML (零后端依赖)