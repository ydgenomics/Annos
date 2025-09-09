```shell
cd /
wget https://genentech.github.io/scimilarity/_downloads/862f33e11cc6529e534bbf5808474218/environment.yaml
source /opt/software/miniconda3/bin/activate
conda env create -f environment.yaml -y
conda activate scimilarity
pip install scimilarity
```