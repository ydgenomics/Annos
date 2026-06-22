#!/usr/bin/env python3
"""
scType 单细胞注释封装脚本
================================
基于 https://github.com/kris-nader/sc-type-py

功能:
  1. 读取已分群的 AnnData (.h5ad)
  2. 加载 scType marker 数据库 (XLSX)
  3. 计算每个 cluster 的 scType 得分
  4. 将注释结果写回 adata.obs
  5. 输出注释后的 h5ad + 结果 CSV

输入:
  - h5ad: 已分群的 AnnData (需包含 adata.X, adata.obs[cluster_key])
  - marker_db: scType 格式的 XLSX 数据库 (URL 或本地路径)
  - tissue_type: 组织类型 (对应 XLSX 中的 tissueType 列)

输出:
  - adata.obs['sctype_classification']: 每个细胞的注释结果
  - adata.uns['sctype_scores']: 每个 cluster 的得分详情
  - 结果 CSV: cluster 级别的注释汇总

依赖:
  pip install scanpy pandas numpy openpyxl requests

使用:
  python run_pysctype.py \\
      --adata input.h5ad \\
      --marker_db ScTypeDB_full.xlsx \\
      --tissue_type "Immune system" \\
      --cluster_key leiden \\
      --output annotated.h5ad

作者: ydgenomics
日期: 260623
"""

import argparse
import sys
import warnings
from pathlib import Path
from typing import Optional, Dict, Tuple

import numpy as np
import pandas as pd
import scanpy as sc

warnings.filterwarnings('ignore')

# ────────────────────────────────────────────────────────────
# 1. 核心函数: 从 sc-type-py 移植 (跳过 HGNC 查询)
# ────────────────────────────────────────────────────────────

def gene_sets_prepare(path_to_db_file: str, cell_type: str,
                      skip_hgnc: bool = True) -> Dict[str, Dict[str, list]]:
    """
    从 scType 数据库文件准备基因集

    Parameters
    ----------
    path_to_db_file : str
        XLSX 文件路径或 URL
    cell_type : str
        组织类型 (对应 tissueType 列)
    skip_hgnc : bool
        是否跳过 HGNC 查询 (植物数据建议 True)

    Returns
    -------
    dict: {'gs_positive': {cellType: [genes]}, 'gs_negative': {cellType: [genes]}}
    """
    # 读取数据库
    db = pd.read_excel(path_to_db_file, engine='openpyxl')

    # 按组织类型过滤
    db_filtered = db[db['tissueType'] == cell_type].copy()

    if db_filtered.empty:
        raise ValueError(f"未找到组织类型 '{cell_type}'，可用类型: {db['tissueType'].unique()}")

    # 解析基因列表
    gs_positive = {}
    gs_negative = {}

    for _, row in db_filtered.iterrows():
        cell_name = str(row['cellName']).strip()

        # 阳性基因
        pos_genes = str(row['geneSymbolmore1']).split(',')
        pos_genes = [g.strip() for g in pos_genes if g.strip() and g.strip() != 'nan']
        if pos_genes:
            gs_positive[cell_name] = pos_genes

        # 阴性基因
        neg_genes = str(row['geneSymbolmore2']).split(',')
        neg_genes = [g.strip() for g in neg_genes if g.strip() and g.strip() != 'nan']
        if neg_genes:
            gs_negative[cell_name] = neg_genes

    return {'gs_positive': gs_positive, 'gs_negative': gs_negative}


def sctype_score(scRNAseqData: pd.DataFrame,
                 gs: Dict[str, list],
                 gs2: Optional[Dict[str, list]] = None,
                 scaled: bool = True,
                 gene_names_to_uppercase: bool = True) -> pd.DataFrame:
    """
    计算 scType 富集得分

    Parameters
    ----------
    scRNAseqData : pd.DataFrame
        行=基因, 列=细胞, 已 scale 的表达矩阵
    gs : dict
        {cellType: [marker_genes]} 阳性基因集
    gs2 : dict, optional
        {cellType: [marker_genes]} 阴性基因集
    scaled : bool
        是否已 scale
    gene_names_to_uppercase : bool
        是否转大写

    Returns
    -------
    pd.DataFrame: 行=细胞类型, 列=细胞, 值为得分
    """
    if gene_names_to_uppercase:
        scRNAseqData.index = scRNAseqData.index.str.upper()
        gs = {k: [g.upper() for g in v] for k, v in gs.items()}
        if gs2:
            gs2 = {k: [g.upper() for g in v] for k, v in gs2.items()}

    # Z-score 标准化 (如果未 scale)
    if not scaled:
        scRNAseqData = scRNAseqData.apply(lambda x: (x - x.mean()) / x.std(), axis=1)
        scRNAseqData = scRNAseqData.fillna(0)

    # Marker 敏感度计算
    all_markers = set()
    for genes in gs.values():
        all_markers.update(genes)
    n_types = len(gs)

    marker_sensitivity = {}
    for gene in all_markers:
        count = sum(1 for genes in gs.values() if gene in genes)
        marker_sensitivity[gene] = 1 - (count - 1) / (n_types - 1) if n_types > 1 else 1.0

    # 计算每个细胞-细胞类型对的得分
    cell_types = list(gs.keys())
    cells = scRNAseqData.columns
    score_matrix = pd.DataFrame(0.0, index=cell_types, columns=cells)

    for ct in cell_types:
        pos_genes = [g for g in gs[ct] if g in scRNAseqData.index]
        if not pos_genes:
            continue

        # 提取表达值 × marker 敏感度
        expr = scRNAseqData.loc[pos_genes].copy()
        sens = np.array([marker_sensitivity[g] for g in pos_genes])
        weighted = expr.multiply(sens, axis=0)

        # 阳性得分
        pos_score = weighted.sum(axis=0) / np.sqrt(len(pos_genes))

        # 阴性得分 (取负值)
        if gs2 and ct in gs2:
            neg_genes = [g for g in gs2[ct] if g in scRNAseqData.index]
            if neg_genes:
                neg_expr = scRNAseqData.loc[neg_genes].copy()
                neg_score = neg_expr.sum(axis=0) / np.sqrt(len(neg_genes))
                pos_score -= neg_score

        score_matrix.loc[ct] = pos_score.values

    return score_matrix


def process_cluster(cluster, adata, es_max, clustering, top_n=10):
    """
    处理单个 cluster 的 scType 结果

    Parameters
    ----------
    cluster : str
        cluster 名称
    adata : AnnData
    es_max : pd.DataFrame
        行=细胞类型, 列=细胞, 值为得分
    clustering : str
        adata.obs 中的聚类列名
    top_n : int
        返回 top N 候选

    Returns
    -------
    pd.DataFrame
    """
    cells_in_cluster = adata.obs_names[adata.obs[clustering] == cluster]
    if len(cells_in_cluster) == 0:
        return pd.DataFrame()

    cluster_scores = es_max[cells_in_cluster]
    # 按行求和排序
    score_sum = cluster_scores.sum(axis=1).sort_values(ascending=False)
    top = score_sum.head(top_n)

    results = []
    for ct, score in top.items():
        results.append({
            'cluster': cluster,
            'type': ct,
            'scores': round(score, 2),
            'ncells': len(cells_in_cluster)
        })

    return pd.DataFrame(results)


# ────────────────────────────────────────────────────────────
# 2. 主封装函数
# ────────────────────────────────────────────────────────────

def run_sctype(adata: sc.AnnData,
               marker_db: str,
               tissue_type: str,
               cluster_key: str = 'leiden',
               skip_hgnc: bool = True,
               min_score_ratio: float = 0.25,
               inplace: bool = True) -> Tuple[sc.AnnData, pd.DataFrame]:
    """
    对 AnnData 运行 scType 注释

    Parameters
    ----------
    adata : AnnData
        已分群的 AnnData 对象
    marker_db : str
        scType 数据库 XLSX 路径或 URL
    tissue_type : str
        组织类型 (对应 XLSX 中的 tissueType 列)
    cluster_key : str
        adata.obs 中的聚类列名, 默认 'leiden'
    skip_hgnc : bool
        跳过 HGNC 基因名查询 (植物数据建议 True)
    min_score_ratio : float
        最低得分比例, 低于此值设为 Unknown, 默认 0.25
    inplace : bool
        是否直接修改 adata

    Returns
    -------
    tuple: (adata, sctype_scores)
        - adata.obs['sctype_classification'] 已更新
        - adata.uns['sctype_scores'] 已更新
        - sctype_scores: cluster 级别注释汇总 DataFrame
    """
    if not inplace:
        adata = adata.copy()

    # ── Step 1: 校验 ──
    if cluster_key not in adata.obs:
        raise KeyError(f"adata.obs 中未找到聚类列 '{cluster_key}'，可用列: {list(adata.obs.columns)}")

    print(f"[scType] 数据: {adata.n_obs} 细胞 × {adata.n_vars} 基因, "
          f"{adata.obs[cluster_key].nunique()} 个 cluster")

    # ── Step 2: Scale 数据 ──
    print(f"[scType] 标准化表达矩阵...")
    adata_tmp = adata.copy()
    sc.pp.scale(adata_tmp, max_value=10)

    # 转为 genes × cells DataFrame
    scRNAseqData = pd.DataFrame(
        adata_tmp.X,
        columns=adata_tmp.var_names,
        index=adata_tmp.obs_names
    ).T

    # ── Step 3: 准备基因集 ──
    print(f"[scType] 加载 marker 数据库: {marker_db}")
    print(f"[scType] 组织类型: {tissue_type}")
    gs_list = gene_sets_prepare(marker_db, tissue_type, skip_hgnc=skip_hgnc)

    n_pos = sum(len(v) for v in gs_list['gs_positive'].values())
    n_neg = sum(len(v) for v in gs_list['gs_negative'].values())
    n_types = len(gs_list['gs_positive'])
    print(f"[scType] 基因集: {n_types} 种细胞类型, {n_pos} 个阳性 marker, {n_neg} 个阴性 marker")

    # ── Step 4: 计算得分 ──
    print(f"[scType] 计算富集得分...")
    es_max = sctype_score(
        scRNAseqData=scRNAseqData,
        scaled=True,
        gs=gs_list['gs_positive'],
        gs2=gs_list['gs_negative']
    )

    # ── Step 5: 按 cluster 聚合 ──
    print(f"[scType] 按 cluster 聚合得分...")
    clusters = adata.obs[cluster_key].unique()
    cL_results = pd.concat([
        process_cluster(cl, adata, es_max, cluster_key)
        for cl in clusters
    ], ignore_index=True)

    # ── Step 6: 每个 cluster 取最佳 ──
    sctype_scores = cL_results.groupby('cluster').apply(
        lambda x: x.nlargest(1, 'scores')
    ).reset_index(drop=True)

    # ── Step 7: 低置信度过滤 ──
    sctype_scores.loc[
        sctype_scores['scores'] < sctype_scores['ncells'] * min_score_ratio,
        'type'
    ] = 'Unknown'

    # ── Step 8: 写回 adata ──
    adata.obs['sctype_classification'] = ''

    for _, row in sctype_scores.iterrows():
        mask = adata.obs[cluster_key] == row['cluster']
        adata.obs.loc[mask, 'sctype_classification'] = row['type']

    # 保存得分详情到 uns
    adata.uns['sctype_scores'] = {
        'cluster_scores': sctype_scores.to_dict('records'),
        'tissue_type': tissue_type,
        'marker_db': marker_db,
        'min_score_ratio': min_score_ratio,
    }

    # 统计
    n_annotated = (adata.obs['sctype_classification'] != '').sum()
    n_unknown = (adata.obs['sctype_classification'] == 'Unknown').sum()
    print(f"[scType] 完成! 注释 {n_annotated} 细胞, "
          f"其中 {n_unknown} 为 Unknown")

    return adata, sctype_scores


# ────────────────────────────────────────────────────────────
# 3. CLI 入口
# ────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description='scType 单细胞注释 — 基于 marker 基因集的细胞类型注释',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本用法
  python run_pysctype.py -i adata.h5ad -o annotated.h5ad \\
      --marker_db ScTypeDB_full.xlsx --tissue_type "Immune system"

  # 植物数据 (跳过 HGNC 查询)
  python run_pysctype.py -i adata.h5ad -o annotated.h5ad \\
      --marker_db plant_markers.xlsx --tissue_type "Root" --skip_hgnc

  # 自定义 cluster 列名
  python run_pysctype.py -i adata.h5ad -o annotated.h5ad \\
      --marker_db ScTypeDB_full.xlsx --tissue_type "Brain" \\
      --cluster_key louvain
        """)

    parser.add_argument('-i', '--adata', required=True,
                        help='输入 h5ad 文件路径')
    parser.add_argument('-o', '--output', default='annotated.h5ad',
                        help='输出 h5ad 文件路径 (默认: annotated.h5ad)')
    parser.add_argument('--marker_db', required=True,
                        help='scType marker 数据库 XLSX 文件路径或 URL')
    parser.add_argument('--tissue_type', required=True,
                        help='组织类型 (对应 XLSX 中的 tissueType 列)')
    parser.add_argument('--cluster_key', default='leiden',
                        help='adata.obs 中的聚类列名 (默认: leiden)')
    parser.add_argument('--skip_hgnc', action='store_true', default=True,
                        help='跳过 HGNC 基因名查询 (植物数据推荐)')
    parser.add_argument('--min_score_ratio', type=float, default=0.25,
                        help='最低得分比例, 低于此值设为 Unknown (默认: 0.25)')
    parser.add_argument('--csv', default=None,
                        help='额外输出 cluster 级别注释 CSV (可选)')
    parser.add_argument('--inplace', action='store_true', default=True,
                        help='直接修改输入文件 (默认: True)')

    return parser.parse_args()


def main():
    args = parse_args()

    # 读取数据
    print(f"[scType] 读取 AnnData: {args.adata}")
    adata = sc.read_h5ad(args.adata)
    print(f"          {adata.n_obs} 细胞 × {adata.n_vars} 基因")

    # 运行 scType
    adata, scores = run_sctype(
        adata=adata,
        marker_db=args.marker_db,
        tissue_type=args.tissue_type,
        cluster_key=args.cluster_key,
        skip_hgnc=args.skip_hgnc,
        min_score_ratio=args.min_score_ratio,
        inplace=args.inplace,
    )

    # 保存
    print(f"[scType] 保存结果: {args.output}")
    adata.write_h5ad(args.output)

    # 可选: 输出 CSV
    if args.csv:
        scores.to_csv(args.csv, index=False)
        print(f"[scType] 保存 CSV: {args.csv}")

    # 打印结果摘要
    print("\n=== scType 注释结果 ===")
    for _, row in scores.iterrows():
        print(f"  Cluster {row['cluster']:>4s}: {row['type']:<20s} "
              f"(得分: {row['scores']:.1f}, 细胞: {row['ncells']})")

    print(f"\n[scType] 完成!")


if __name__ == '__main__':
    main()
