# https://github.com/ydgenomics/scLine/tree/main/env

source /opt/software/miniconda3/bin/activate
# # nextflow
# conda install bioconda::nextflow -y
conda create -n sc r-base=4.3 -y
conda activate sc
conda install conda-forge::r-optparse -y
conda install conda-forge::r-biocmanager -y
conda install conda-forge::r-devtools -y
conda install conda-forge::r-remotes -y

conda install conda-forge::r-seurat -y
conda install bioconda::bioconductor-dropletutils -y
conda install conda-forge::r-rcppplanc -y
conda install pwwang::r-seuratwrappers -y
conda install bioconda::bioconductor-glmgampoi -y

Rscript -e "BiocManager::install('multtest')"
Rscript -e "install.packages('metap')"
Rscript -e "install.packages('presto')"


conda install conda-forge::scanpy -y
conda install bioconda::scrublet -y
conda install conda-forge::leidenalg -y

pip install singlecellexperiment
pip install singler


# quarto
conda install conda-forge::r-quarto -y


# docker run -it --name sc continuumio/miniconda3:latest /bin/bash
source /opt/software/miniconda3/bin/activate
conda config --remove channels defaults
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/bioconda/
conda config --set show_channel_urls yes
conda clean --all -y

cat << 'EOF' > ~/.condarc
channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/bioconda/
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
show_channel_urls: true
default_channels: []
EOF

conda create -n sc python=3.11 -y
conda activate sc
conda install -c conda-forge -c bioconda blast orthofinder -y
conda install -c conda-forge scanpy anndata pandas scipy scikit-learn matplotlib seaborn plotly python-igraph louvain biopython tqdm ipython ipdb ipykernel -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install gseapy singlecellexperiment singler scarches scvi-tools ensembl-rest -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install einops
pip install local-attention
pip install plotly
pip install Jinja2

# conda install -c conda-forge r-quarto -y
# quarto check
# conda remove dart-sass -y
# conda install -c conda-forge nodejs -y
# node --version
# npm --version
# npm install -g sass
# sass --version

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install gseapy singlecellexperiment singler scarches scvi-tools ensembl-rest -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install einops
pip install local-attention

# install singler
# ../meson.build:25:4: ERROR: Problem encountered: NumPy requires GCC >= 9.3

# python3.11使用pip安装samap会报错 # Cannot install on Python version 3.11.15; only versions >=3.7,<3.11 are supported.
conda create -n samap python=3.10 -y
conda activate samap
# 1. 更新 apt 软件源并安装 C++ 编译工具链（build-essential）
apt-get update && apt-get install -y build-essential
# 2. 重新单独安装刚才失败的 hnswlib
pip install hnswlib -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install samap -i https://pypi.tuna.tsinghua.edu.cn/simple


conda clean --all -y
pip cache purge
