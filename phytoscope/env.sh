#!/bin/bash

# 确保脚本在遇到错误时立即停止执行
set -e

# 1. 清理所有未下载完的包缓存和索引
conda clean --all -y

# 2. 添加清华大学的 Conda 镜像源（覆盖 main, conda-forge 和 bioconda）
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/bioconda/

# 3. 设置搜索时显示通道来源（方便排查问题）
conda config --set show_channel_urls yes
source /opt/software/miniconda3/bin/activate
echo "========= 1. 创建基础 Conda 环境 ========="
# 合并基础包、quarto、blast 和 orthofinder，减少环境解算冲突
conda create -n sc python=3.11 \
    scanpy \
    matplotlib \
    seaborn \
    scikit-learn \
    pandas \
    scipy \
    biopython \
    tqdm \
    plotly \
    igraph \
    louvain \
    notebook \
    ipython \
    ipdb \
    conda-forge::r-quarto \
    bioconda::blast \
    bioconda::orthofinder \
    -y

echo "========= 2. 激活 Conda 环境 ========="
# 激活环境以进行后续的 pip 安装
source $(conda info --base)/etc/profile.d/conda.sh
conda activate sc

echo "========= 3. 安装特定版本的 PyTorch & 显卡加速相关 (SATURN 依赖) ========="
# 1. 激活新环境
conda activate sc

# 2. 使用清华源安装特定 CUDA 12.1 的 PyTorch 2.x
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3. 继续安装你需要的其他高级单细胞包
pip install gseapy singlecellexperiment singler scarches samap scvi-tools ensembl-rest -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装 FAISS GPU 版本及英特尔加速组件（如果不需要 GPU 加速，可调整为 cpu 版本）
conda install -c pytorch faiss-gpu -y
conda install -c intel scikit-learn-intelex -y

echo "========= 4. 安装基础单细胞/基础工具 Pip 包 ========="
pip install gseapy
pip install scikit-misc  # scanpy 高级功能常用依赖
pip install typed-argument-parser record-keeper

echo "========= 5. 安装高级单细胞分析工具 (SingleR, scArches, SAMap, SATURN) ========="
# SingleR 相关的 Python 实现
pip install singlecellexperiment singler

# 映射与集成工具
pip install scarches
pip install samap

# SATURN 的核心依赖：scvi-tools 及 ensembl 接口
pip install scvi-tools
pip install ensembl-rest

echo "=================================================="
echo " 检查完毕！环境 'sc' 已成功创建并配置完成。 "
echo " 请使用 'conda activate sc' 激活环境。 "
echo "=================================================="