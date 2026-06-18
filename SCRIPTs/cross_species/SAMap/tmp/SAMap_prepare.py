# 260617

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
keys = sys.argv[3]
subset = sys.argv[4]
do_rename_list = sys.argv[5]
do_process_list = sys.argv[6]
do_harmonization_list = sys.argv[7]

fn_list=fn_list.split(',')
s_list=s_list.split(',')
keys=keys.split(',')
subset=subset.split(',')
do_rename_list=do_rename_list.split(',')
do_process_list=do_process_list.split(',')
do_harmonization_list=do_harmonization_list.split(',')


def getRandomAnndata(adata, ratio=0.2, seed=123, 
                              by_group=None, stratify=None,
                              return_indices=False, verbose=True):
    """
    高级版随机取细胞函数，支持分层抽样和多种功能
    
    Parameters
    ----------
    adata : AnnData
        输入的 AnnData 对象
    ratio : float or int, optional (default: 0.2)
        如果为float: 抽取细胞的比例 (0, 1]
        如果为int: 抽取细胞的绝对数量
    seed : int, optional (default: 123)
        随机种子
    by_group : str, optional (default: None)
        按照 obs 中的某一列进行分层抽样
    stratify : array-like, optional (default: None)
        用于分层抽样的标签
    return_indices : bool, optional (default: False)
        是否返回选择的索引
    verbose : bool, optional (default: True)
        是否打印详细信息
    
    Returns
    -------
    adata_subset : AnnData
        包含随机抽取细胞的 AnnData 对象
    indices : ndarray (optional)
        如果 return_indices=True，返回选择的索引
    """
    import numpy as np
    import scanpy as sc
    from sklearn.model_selection import train_test_split
    # 设置随机种子
    np.random.seed(seed)
    # 计算要抽取的细胞数量
    if isinstance(ratio, float):
        if ratio <= 0 or ratio > 1:
            raise ValueError("当 ratio 为 float 时，必须在 (0, 1] 范围内")
        n_cells = int(adata.n_obs * ratio)
        n_cells = max(1, n_cells)
        ratio_type = '比例'
    elif isinstance(ratio, int):
        if ratio <= 0 or ratio > adata.n_obs:
            raise ValueError(f"当 ratio 为 int 时，必须在 1 到 {adata.n_obs} 范围内")
        n_cells = ratio
        ratio_type = '数量'
    else:
        raise ValueError("ratio 必须是 float 或 int")
    # 选择抽样方法
    if by_group is not None:
        # 按组分层抽样
        if by_group not in adata.obs.columns:
            raise ValueError(f"by_group '{by_group}' 不在 adata.obs 中")
        # 计算每组的抽样数量
        group_counts = adata.obs[by_group].value_counts()
        group_ratios = group_counts / adata.n_obs
        group_samples = (group_ratios * n_cells).astype(int)
        # 确保每组至少抽1个
        group_samples = group_samples.clip(lower=1)
        # 调整总抽样数量
        total_samples = group_samples.sum()
        if total_samples > adata.n_obs:
            # 如果超出，按比例减少
            group_samples = (group_samples * (n_cells / total_samples)).astype(int)
            group_samples = group_samples.clip(lower=1)
        # 从每组中随机抽取
        indices = []
        for group, count in group_samples.items():
            group_indices = np.where(adata.obs[by_group] == group)[0]
            if count > len(group_indices):
                count = len(group_indices)
            group_selected = np.random.choice(group_indices, size=count, replace=False)
            indices.extend(group_selected)
        indices = np.array(indices) 
    elif stratify is not None:
        # 使用 sklearn 的分层抽样
        from sklearn.model_selection import train_test_split
        # 创建临时索引
        temp_indices = np.arange(adata.n_obs)
        # 分层抽样
        _, indices = train_test_split(temp_indices, 
                                      train_size=n_cells/adata.n_obs,
                                      random_state=seed,
                                      stratify=stratify)  
    else:
        # 简单随机抽样
        indices = np.random.choice(adata.n_obs, size=n_cells, replace=False)
    # 排序索引以保持原始顺序（可选）
    indices = np.sort(indices)
    # 创建新的 AnnData 对象
    adata_subset = adata[indices].copy()
    # 打印统计信息
    if verbose:
        print(f"原始细胞数: {adata.n_obs}")
        print(f"抽取{ratio_type}: {ratio}")
        print(f"抽取细胞数: {n_cells}")
        print(f"实际抽取数: {len(indices)}")
        print(f"新对象形状: {adata_subset.shape}")
        if by_group is not None:
            print(f"\n按 '{by_group}' 分层抽样结果:")
            original_dist = adata.obs[by_group].value_counts(normalize=True)
            sampled_dist = adata_subset.obs[by_group].value_counts(normalize=True)
            for group in original_dist.index:
                print(f"  {group}: 原始 {original_dist[group]:.2%} -> 抽样 {sampled_dist[group]:.2%}")
    if return_indices:
        return adata_subset, indices
    else:
        return adata_subset


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
    
    if int(subset[i]) == 0:
        ratio = float(subset[i])
    else:
        ratio = int(subset[i])
    adata = getRandomAnndata(adata, ratio=ratio, seed=123, 
                              by_group=keys[i], stratify=None,
                              return_indices=False, verbose=True)
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