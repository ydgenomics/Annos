# from_agent — 跨物种单细胞整合 (SAMap)

基于 `from_zly` 方案改进，简化参数传递，增加灵活配置。

## 设计思路

| 改进点 | from_zly | from_agent |
| :----- | :------- | :--------- |
| 参数传递 | 需准备 meta 表格文件 | 命令行直接传参 `--species name:h5ad,pep` |
| 比对工具 | 仅 BLASTp | 可选 **BLASTp / DIAMOND** |
| 基因ID替换 | 硬编码 | 外部传参 `--replace_id yes/no` |
| 亚采样 | 无 | 可选按细胞群比例采样 `--subsample 0.1` |
| counts 恢复 | 需手动指定 | **自动检测** `layers['counts']` |
| 代码组织 | 3个独立脚本 | 1个主脚本整合全流程 |

## 关于 counts 自动恢复

SAMap 内部 `preprocess_data()` 会对 `.X` 做 **sum_norm + log 变换**。如果 `.X` 已经是 log-normalize 后的数据，会导致二次归一化错误。

脚本会自动检测：

- **`layers['counts']` 存在** → 自动复制到 `.X`，并清理 `.raw`
- **`layers['counts']` 不存在** → 直接使用 `.X` 现有数据

无需手动干预，运行时会打印判断信息。

## 文件说明

```text
from_agent/
├── run_samap.py      # 主流程脚本 (一键运行)
├── run_align.sh      # 独立比对脚本 (BLASTp / DIAMOND)
├── preprocess.py     # 独立预处理脚本 (含亚采样)
└── README.md         # 本文件
```

## 快速开始

### 安装依赖

```bash
# Python 包
pip install samap samalg scanpy anndata pandas matplotlib

# 比对工具 (二选一)
conda install -c bioconda blast      # BLAST+
conda install -c bioconda diamond    # DIAMOND (更快)
```

### 方式一：一键运行 (推荐)

```bash
python run_samap.py \
    --species sp1:data/sp1.h5ad,data/sp1.pep \
    --species sp2:data/sp2.h5ad,data/sp2.pep \
    --aligner diamond \
    --threads 20 \
    --replace_id yes \
    --subsample 0.1
```

### 方式二：分步运行

```bash
# 1. 预处理 + 亚采样
python preprocess.py \
    --species sp1:data/sp1.h5ad \
    --species sp2:data/sp2.h5ad \
    --subsample 0.1 \
    --out_dir ./processed

# 2. 同源基因比对
bash run_align.sh ./pep_files ./maps diamond 40 1e-6 yes

# 3. 运行 SAMap 整合
python run_samap.py \
    --species sp1:processed/sp1_preprocessed.h5ad,data/sp1.pep \
    --species sp2:processed/sp2_preprocessed.h5ad,data/sp2.pep \
    --maps_dir ./maps \
    --skip_align
```

## 参数说明

### run_samap.py

| 参数 | 简写 | 说明 | 默认值 |
| :--- | :--- | :--- | :----- |
| `--species` | `-s` | 物种信息 `name:h5ad,pep` (可多次) | **必填** |
| `--aligner` | `-a` | 比对工具: `blastp` / `diamond` | `diamond` |
| `--threads` | `-t` | 比对线程数 | `40` |
| `--evalue` | | BLAST/DIAMOND E-value 阈值 | `1e-6` |
| `--maps_dir` | | 同源映射表目录 | `./maps` |
| `--skip_align` | | 跳过比对，使用已有 maps | `False` |
| `--replace_id` | | 替换基因ID: `yes` / `no` | `no` |
| `--subsample` | | 按细胞群亚采样比例 (如 0.1) | 不采样 |
| `--subsample_seed` | | 亚采样随机种子 | `42` |
| `--batch_key` | | Harmony 批次 key | `None` |
| `--cluster_key` | | 细胞类型列名 | `celltype` |
| `--raw_layer` | | (已废弃) 自动检测 `layers['counts']` | 自动 |
| `--out_dir` | | 输出目录 | `./samap_result` |
| `--prefix` | | 输出文件前缀 | `samap` |

### run_align.sh

```bash
bash run_align.sh <pep_dir> <maps_dir> [aligner] [threads] [evalue] [replace_id]
```

| 参数 | 说明 | 默认值 |
| :--- | :--- | :----- |
| `pep_dir` | 存放 .pep 蛋白文件的目录 | **必填** |
| `maps_dir` | 输出映射表目录 | **必填** |
| `aligner` | 比对工具: `blastp` / `diamond` | `diamond` |
| `threads` | 线程数 | `40` |
| `evalue` | E-value 阈值 | `1e-6` |
| `replace_id` | 替换基因ID: `yes` / `no` | `no` |

### preprocess.py

```bash
python preprocess.py --species name:h5ad_path [--subsample 0.1] [--out_dir ./processed]
```

## 输出文件

```text
samap_result/
├── samap_celltype_relationship.csv   # 细胞类型映射分数
├── samap_MappingTable.csv            # 细胞类型映射表
├── samap_sankey.pdf                  # Sankey 图
├── samap_umap.pdf                    # 整合 UMAP
├── samap_gene_pairs.csv              # 跨物种基因对
├── samap_integrated.h5ad             # 整合后的 AnnData
└── samap_samap.pkl                   # 完整 SAMap 对象 (可 reload)
```

## 与 from_zly 的对比

| 特性 | from_zly | from_agent |
| :--- | :------- | :--------- |
| 参数传递 | meta 表格文件 | 命令行直接传参 |
| 比对工具 | 仅 BLASTp | BLASTp / DIAMOND 可选 |
| 基因ID替换 | 硬编码 | `--replace_id yes/no` |
| 亚采样 | 无 | `--subsample 0.1` |
| 代码量 | 3个文件 ~150行 | 3个文件 ~400行 |
| 易用性 | 需准备额外文件 | 一行命令搞定 |
