# 输入一个h5ad文件，包含分群的key，可能包含batch_key，可能包含reduction的key

import scanpy as sc

int_h5ad="" 
cluster_key="CHOIR"
batch_key=
reduction_key=


adata = sc.read_h5ad(int_h5ad)
print(adata)

# 检查输入矩阵是否标准化

# check adata.obs and adata.obsm

# 检查

# 找cluster的marker基因保存为csv

