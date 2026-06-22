#!/bin/bash
# ============================================================
# PhytoScope 环境配置脚本
# 目标系统: CentOS Linux
# 包管理器: conda / mamba
# 创建日期: 2025-06-22
#
# 使用方式:
#   chmod +x env_setup.sh
#   bash env_setup.sh
#
# 或分步执行各章节 (推荐首次逐段运行以排查网络问题)
# ============================================================

set -euo pipefail

# ─── 0. 基础配置 ───────────────────────────────────────────
MINICONDA_DIR="/opt/software/miniconda3"  # 根据实际路径修改
CONDA_SOURCE="source ${MINICONDA_DIR}/bin/activate"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ─── 1. 检查基础依赖 ───────────────────────────────────────
log_info "=== 1. 检查基础依赖 ==="

if ! command -v conda &> /dev/null; then
    log_error "conda 未安装！请先安装 Miniconda3"
    log_info "下载: https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    exit 1
fi
log_info "conda 已安装: $(conda --version)"

log_info "安装/更新 mamba..."
conda install -y -c conda-forge mamba

log_info "配置 conda 频道..."
conda config --remove-key channels 2>/dev/null || true
conda config --add channels conda-forge
conda config --add channels bioconda
conda config --add channels defaults
conda config --set channel_priority strict

# ─── 2. Python 环境 ────────────────────────────────────────
log_info "=== 2. 创建 Python 环境: phytoscope-py ==="

mamba create -y -n phytoscope-py python=3.11
source ${MINICONDA_DIR}/bin/activate phytoscope-py

# 基础科学计算
log_info "安装基础科学计算包..."
mamba install -y -c conda-forge \
    numpy pandas scipy scikit-learn \
    matplotlib seaborn plotly \
    ipykernel jupyter \
    pyyaml tqdm \
    h5py click

# scanpy 生态
log_info "安装 scanpy 生态..."
mamba install -y -c conda-forge \
    scanpy leidenalg louvain scikit-misc

# 双细胞检测
log_info "安装 scrublet..."
mamba install -y -c bioconda scrublet

# 整合工具
log_info "安装整合工具..."
mamba install -y -c conda-forge scvi-tools
mamba install -y -c bioconda harmonypy
pip install --use-pep517 bbknn

# 注释工具
log_info "安装注释工具..."
pip install pysctype
mamba install -y -c conda-forge rpy2

# 跨物种映射
log_info "安装跨物种映射工具..."
pip install samap saturn

# 富集分析 (Python 端)
pip install gseapy

# 报告生成
log_info "安装 Quarto..."
mamba install -y -c conda-forge quarto

# 注册 Jupyter kernel
python -m ipykernel install --user --name phytoscope-py \
    --display-name "Python (phytoscope-py)"

conda deactivate

# ─── 3. R 环境 ─────────────────────────────────────────────
log_info "=== 3. 创建 R 环境: phytoscope-r ==="

mamba create -y -n phytoscope-r r-base=4.4
source ${MINICONDA_DIR}/bin/activate phytoscope-r

log_info "安装 R 基础工具..."
mamba install -y -c conda-forge \
    r-optparse r-devtools r-remotes \
    r-biocmanager r-reticulate

log_info "安装 Seurat 生态..."
mamba install -y -c conda-forge r-seurat r-seuratdata r-tidyverse

log_info "安装 SingleR..."
mamba install -y -c bioconda bioconductor-singler

log_info "安装 presto..."
Rscript -e 'devtools::install_github("immunogenomics/presto")'

log_info "安装富集分析工具..."
mamba install -y -c bioconda \
    bioconductor-clusterprofiler \
    bioconductor-keggrest \
    bioconductor-annotationforge

log_info "安装可视化工具..."
mamba install -y -c conda-forge r-ggraph r-circlize
mamba install -y -c bioconda bioconductor-complexheatmap

log_info "安装格式转换工具..."
mamba install -y -c bioconda r-sceasy

conda deactivate

# ─── 4. 系统工具 ───────────────────────────────────────────
log_info "=== 4. 安装系统工具: phytoscope-sys ==="

mamba create -y -n phytoscope-sys
source ${MINICONDA_DIR}/bin/activate phytoscope-sys

mamba install -y -c bioconda blast orthofinder mafft diamond

conda deactivate

# ─── 5. 验证安装 ───────────────────────────────────────────
log_info "=== 5. 验证安装 ==="

verify_python() {
    source ${MINICONDA_DIR}/bin/activate phytoscope-py
    echo "--- Python 环境验证 ---"
    python -c "
import scanpy as sc; print(f'  scanpy: {sc.__version__}')
import numpy as np; print(f'  numpy: {np.__version__}')
import pandas as pd; print(f'  pandas: {pd.__version__}')
import pysctype; print(f'  pysctype: OK')
import rpy2; print(f'  rpy2: OK')
import samap; print(f'  samap: OK')
import gseapy; print(f'  gseapy: OK')
print('  Python 环境验证通过!')
"
    conda deactivate
}

verify_r() {
    source ${MINICONDA_DIR}/bin/activate phytoscope-r
    echo "--- R 环境验证 ---"
    Rscript -e '
library(Seurat); cat("  Seurat:", as.character(packageVersion("Seurat")), "\n")
library(SingleR); cat("  SingleR:", as.character(packageVersion("SingleR")), "\n")
library(clusterProfiler); cat("  clusterProfiler:", as.character(packageVersion("clusterProfiler")), "\n")
library(sceasy); cat("  sceasy:", as.character(packageVersion("sceasy")), "\n")
cat("  R 环境验证通过!\n")
'
    conda deactivate
}

verify_sys() {
    source ${MINICONDA_DIR}/bin/activate phytoscope-sys
    echo "--- 系统工具验证 ---"
    blastn -version 2>&1 | head -1
    orthofinder --help 2>&1 | head -2
    diamond --version 2>&1
    conda deactivate
}

verify_python || log_warn "Python 环境验证有误，请检查"
verify_r      || log_warn "R 环境验证有误，请检查"
verify_sys    || log_warn "系统工具验证有误，请检查"

# ─── 6. 总结 ───────────────────────────────────────────────
log_info "=== 6. 环境配置完成 ==="
cat << 'EOF'

┌─────────────────────────────────────────────────────────────┐
│  PhytoScope 环境配置完成!                                    │
├─────────────────────────────────────────────────────────────┤
│  环境名称        │  用途                    │  激活命令      │
├─────────────────────────────────────────────────────────────┤
│  phytoscope-py   │  Python 注释引擎          │ conda activate│
│  phytoscope-r    │  R 注释引擎               │ conda activate│
│  phytoscope-sys  │  系统工具 (blast/ortho)   │ conda activate│
├─────────────────────────────────────────────────────────────┤
│  使用提示:                                                 │
│  - PhytoScope.py 主控脚本会自动管理环境切换                 │
│  - 也可手动: conda activate phytoscope-py                   │
│  - R 脚本通过 rpy2 或子进程调用                             │
│  - Quarto 已安装在 phytoscope-py 环境中                     │
└─────────────────────────────────────────────────────────────┘
EOF