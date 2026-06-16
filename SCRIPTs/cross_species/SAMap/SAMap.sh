set -euo pipefail

# 记录开始时间
start_time=$(date +%s)

# 准备蛋白质文件
mkdir -p ./SAMap/tmp/pep
mkdir -p ./SAMap/tmp/maps
mkdir -p ./SAMap/SAMap_result

#!/bin/bash

h5ad_list=${1:-"/data/work/anndata/At_stem.h5ad,/data/work/anndata/Sp_stem.h5ad"}
pep_list=${2:-"/data/work/processed/At.pep,/data/work/processed/Sp.pep"}
species_list=${3:-"At,Sp"}
cluster_list=${4:-"celltype,metaneighbor"}
do_rename_list=${5:-"no,no"}
do_process_list=${6:-"yes,yes"}
do_harmonization_list=${7:-"no,biosample"}

# 将逗号分隔的字符串转换为数组
IFS=',' read -ra pep_arr <<< "$pep_list"
IFS=',' read -ra species_arr <<< "$species_list"

# 循环创建软链接
for i in "${!species_arr[@]}"; do
    ln -sf "${pep_arr[$i]}" "./SAMap/tmp/pep/${species_arr[$i]}.pep"
done

sh ./SAMap/tmp/pairwise_blastp.sh

python ./SAMap/tmp/SAMap_prepare.py $h5ad_list $species_list \
$do_rename_list $do_process_list $do_harmonization_list

python ./SAMap/SAMap_result/SAMap_integration.py $species_list $cluster_list

python ./SAMap/tmp/sanky_plot.py \
--path ./SAMap/SAMap_result/MappingTable.csv \
--seq $species_list --slimit 0.7

# 计算运行时间（小时）
end_time=$(date +%s)
elapsed=$((end_time - start_time))
hours=$(echo "scale=2; $elapsed / 3600" | bc)
echo "运行时间: ${hours} 小时"