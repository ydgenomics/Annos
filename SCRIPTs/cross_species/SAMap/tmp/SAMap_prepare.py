# 260614

# Set in advance to prevent Python from crashing due to large data
# Reduce the value appropriately if the data is larger
import os
# Set this before importing other libraries that depend on OpenBLAS
os.environ["OPENBLAS_NUM_THREADS"] = "4"

from samap.mapping import SAMAP
from samap.analysis import (get_mapping_scores, GenePairFinder,
                            sankey_plot, chord_plot, CellTypeTriangles, 
                            ParalogSubstitutions, FunctionalEnrichment,
                            convert_eggnog_to_homologs, GeneTriangles)
from samalg import SAM
import pandas as pd
import scanpy as sc
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scanpy.external as sce
import scipy.sparse
from samalg import SAM #import SAM

# 判断是否需要做sam.preprocess_data，判断是否需要做去批次，判断是否要做基因名替换-为_

import sys
fn_list = sys.argv[1]
s_list = sys.argv[2]
do_rename_list = sys.argv[3]
do_process_list = sys.argv[4]
do_harmonization_list = sys.argv[5]

fn_list=fn_list.split(',')
s_list=s_list.split(',')
do_rename_list=do_rename_list.split(',')
do_process_list=do_process_list.split(',')
do_harmonization_list=do_harmonization_list.split(',')


for i in range(len(fn_list)):
    print(f'process: {s_list[i]}')
    adata = sc.read_h5ad(fn_list[i])
    adata.obs['species'] = s_list[i]
    if do_rename_list[i] == 'yes':
        adata.var_names = adata.var_names.str.replace('-', '_')
    print(adata)
    if 'counts' in adata.layers.keys():
        adata.X = adata.layers['counts'].copy()
    # 检查数据是否为稠密矩阵（即 numpy.ndarray）
    if not scipy.sparse.issparse(adata.X):
        print(f"正在将 {s_list[i]} 的数据转换为稀疏矩阵...")
        # 强制转换为 CSR 格式
        adata.X = scipy.sparse.csr_matrix(adata.X)
    else:
        # 如果已经是稀疏矩阵，确保它是 CSR 格式
        adata.X = adata.X.tocsr()
    if adata.raw is not None:
        del adata.raw
    sam = SAM()
    # sam.load_data(fn)
    sam.adata = adata.copy()
    sam.adata_raw = adata.copy()
    if do_process_list[i] == 'yes':
        sam.preprocess_data() # log transforms and filters the data
    if do_harmonization_list[i] == 'no':
        # don't remove batch
        sam.run() # run SAM with harmonization
    else:
        sam.run(batch_key = do_harmonization_list[i])
    sam.save(f"./SAMap/tmp/{s_list[i]}")