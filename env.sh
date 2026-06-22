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