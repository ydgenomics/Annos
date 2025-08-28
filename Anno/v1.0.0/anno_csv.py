### 2500828 anno_csv.py
### 为h5ad的细胞添加新的注释，input_csv的第一列为h5ad原来的列和值，第二列为新建的列和值
### 确保输入的h5ad的.obsm是X_umap=umap

import pandas as pd
import scanpy as sc
import os
import argparse

parser = argparse.ArgumentParser(description="Process input file paths.")
parser.add_argument(
    "--input_h5ad",
    type=str,
    default="/data/work/Single-Cell-Pipeline/output/dataget/H1314/H1314.h5ad",
    help="Path to the input h5ad file. (default: %(default)s)"
)
parser.add_argument(
    "--input_csv",
    type=str,
    default="/data/work/Single-Cell-Pipeline/Anno/input/anno_H1314.csv",
    help="Path to the input CSV file. (default: %(default)s)"
)
parser.add_argument(
    "--reduction_key",
    type=str,
    default="umap",
    help="The reduction key of single cell data"
)
args = parser.parse_args()
input_h5ad = args.input_h5ad
input_csv = args.input_csv
reduction_key = args.reduction_key

# load anndata object
adata = sc.read_h5ad(input_h5ad)
print(adata)
# read mapping csv
mapping_df = pd.read_csv(input_csv)
mapping_df = mapping_df.astype(str)
# construct dictionary between new name and old name
rename_dict = dict(zip(mapping_df[mapping_df.columns[0]].astype(str),
                       mapping_df[mapping_df.columns[1]].astype(str)))
# check the new name wethere repeat
if mapping_df.columns[1] in adata.obs.columns:
    print(f"Warning: {mapping_df.columns[1]} already exists in adata.obs, it will be overwritten.")
# check all valuse of old column
print("--- old column included unique values ---")
print(adata.obs[mapping_df.columns[0]].unique())
# adata.obs[mapping_df.columns[1]] = adata.obs[mapping_df.columns[0]].cat.rename_categories(rename_dict)
adata.obs[mapping_df.columns[1]] = (adata.obs[mapping_df.columns[0]].map(mapping_df.set_index(mapping_df.columns[0])[mapping_df.columns[1]]))
file_name = os.path.basename(input_h5ad)
base_name = os.path.splitext(file_name)[0] # 提取文件名（不包括扩展名）
output_h5ad = base_name + "_anno.h5ad" # 构造输出文件名
output_umap = base_name + "_anno.pdf"
print(f"Output h5ad file: {output_h5ad}")
adata.write_h5ad(output_h5ad, compression='gzip')

from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
with PdfPages(output_umap) as pdf:
    # sc.pl.umap默认的.obsm是X_umap
    sc.pl.scatter(adata, basis=reduction_key, color=[mapping_df.columns[0],mapping_df.columns[1]], legend_loc="on data") #sc.pl.embedding(adata, basis='umap_test') 
    plt.savefig(pdf, format='pdf', dpi=100, bbox_inches='tight')
    plt.close()