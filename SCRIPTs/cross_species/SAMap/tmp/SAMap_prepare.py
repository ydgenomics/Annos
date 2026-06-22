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
    高级版随机取细胞函数，支持分层抽样和按组指定细胞数

    Parameters
    ----------
    adata : AnnData
        输入的 AnnData 对象
    ratio : float, int, or dict, optional (default: 0.2)
        抽样策略:
        - float (0, 1]: 抽取细胞的比例
        - int (>0): 与 by_group 配合时, 每组最多取 N 个 (不足则全保留);
                    无 by_group 时, 全局取 N 个
        - dict: 按组指定细胞数, e.g. {'T cell': 500, 'B cell': 300}
                此时必须设置 by_group, 未指定的组不抽取
    seed : int, optional (default: 123)
        随机种子
    by_group : str, optional (default: None)
        按照 obs 中的某一列进行分层抽样
        当 ratio 为 dict 时, by_group 必须指定
    stratify : array-like, optional (default: None)
        用于分层抽样的标签 (仅当 ratio 非 dict 时有效)
    return_indices : bool, optional (default: False)
        是否返回选择的索引
    verbose : bool, optional (default: True)
        是否打印详细信息

    Returns
    -------
    adata_subset : AnnData
        包含随机抽取细胞的 AnnData 对象
    indices : ndarray (optional)
        如果 return_indices=True, 返回选择的索引
    """
    np.random.seed(seed)

    # ── 模式1: ratio 为 dict → 按组指定细胞数 ──
    if isinstance(ratio, dict):
        if by_group is None:
            raise ValueError("ratio 为 dict 时, by_group 必须指定")
        if by_group not in adata.obs.columns:
            raise ValueError(f"by_group '{by_group}' 不在 adata.obs 中")

        indices = []
        sample_plan = {}
        for group, n_requested in ratio.items():
            group_mask = adata.obs[by_group] == group
            n_avail = group_mask.sum()
            if n_avail == 0:
                print(f"  ⚠ 组 '{group}' 在数据中不存在, 跳过")
                continue
            n_take = min(int(n_requested), n_avail)
            sample_plan[group] = (n_take, n_avail)
            group_idx = np.where(group_mask)[0]
            selected = np.random.choice(group_idx, size=n_take, replace=False)
            indices.extend(selected)
        indices = np.sort(np.array(indices))

        if verbose:
            print(f"原始细胞数: {adata.n_obs}")
            print(f"按组指定细胞数抽样:")
            for g, (n_take, n_avail) in sample_plan.items():
                print(f"  {g}: 抽取 {n_take}/{n_avail}")
            print(f"实际抽取总数: {len(indices)}")

        adata_subset = adata[indices].copy()
        if return_indices:
            return adata_subset, indices
        return adata_subset

    # ── 模式2: ratio 为 float/int → 按类型处理 ──
    if isinstance(ratio, float):
        if ratio <= 0 or ratio > 1:
            raise ValueError("当 ratio 为 float 时, 必须在 (0, 1] 范围内")
        n_cells = max(1, int(adata.n_obs * ratio))
        ratio_desc = f'比例 {ratio}'
    elif isinstance(ratio, int):
        if ratio <= 0:
            raise ValueError("当 ratio 为 int 时, 必须 > 0")
        n_cells = ratio
        ratio_desc = f'每至多 {ratio}'
    else:
        raise ValueError("ratio 必须是 float, int 或 dict")

    # 选择抽样方法
    if by_group is not None:
        # ── 按组 cap 抽样: 每组最多取 n_cells 个, 不足则全保留 ──
        if by_group not in adata.obs.columns:
            raise ValueError(f"by_group '{by_group}' 不在 adata.obs 中")

        indices = []
        sample_detail = {}
        for group in adata.obs[by_group].unique():
            group_idx = np.where(adata.obs[by_group] == group)[0]
            n_avail = len(group_idx)
            n_take = min(n_cells, n_avail)
            sample_detail[group] = (n_take, n_avail)
            selected = np.random.choice(group_idx, size=n_take, replace=False)
            indices.extend(selected)
        indices = np.sort(np.array(indices))

    elif stratify is not None:
        # ── sklearn 分层抽样 ──
        from sklearn.model_selection import train_test_split
        temp_indices = np.arange(adata.n_obs)
        # train_size 是保留为训练集的比例, 这里保留的是要抽取的细胞
        train_ratio = n_cells / adata.n_obs
        _, indices = train_test_split(temp_indices,
                                      train_size=train_ratio,
                                      random_state=seed,
                                      stratify=stratify)
        indices = np.sort(indices)

    else:
        # ── 简单随机抽样 ──
        indices = np.sort(np.random.choice(adata.n_obs, size=n_cells, replace=False))

    # 创建子集
    adata_subset = adata[indices].copy()

    # 打印统计信息
    if verbose:
        print(f"原始细胞数: {adata.n_obs}")
        print(f"抽样策略: {ratio_desc}")
        print(f"实际抽取数: {len(indices)}")
        print(f"新对象形状: {adata_subset.shape}")
        if by_group is not None:
            print(f"\n按 '{by_group}' 分层抽样结果:")
            original_dist = adata.obs[by_group].value_counts(normalize=True)
            sampled_dist = adata_subset.obs[by_group].value_counts(normalize=True)
            for group in original_dist.index:
                n_orig = (adata.obs[by_group] == group).sum()
                n_samp = (adata_subset.obs[by_group] == group).sum()
                print(f"  {group}: {n_orig} ({original_dist[group]:.1%})"
                      f" → {n_samp} ({sampled_dist[group]:.1%})")

    if return_indices:
        return adata_subset, indices
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