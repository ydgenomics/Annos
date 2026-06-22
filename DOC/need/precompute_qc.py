#!/usr/bin/env python3
"""
预计算 QC 统计量 — 服务器端一次性运行
输入: scanpy AnnData (.h5ad)
输出: qc_stats.csv (供 Quarto 前端使用)

用法:
    conda activate scanpy
    python precompute_qc.py -i /path/to/adata.h5ad -o ./qc_stats.csv
"""

import scanpy as sc
import pandas as pd
import numpy as np
import argparse
import os

# ─── 植物线粒体/叶绿体基因模式 ─────────────────────────────
# 不同物种前缀可能不同，可根据需要修改
MT_PREFIXES = ['MT-', 'mt-', 'Mt-', 'AtMp']       # 线粒体
CHLORO_PREFIXES = ['ChrM', 'ChrC', 'Pt-', 'cp-']   # 叶绿体


def compute_qc_stats(adata, mt_prefixes=None, chloro_prefixes=None,
                     mt_genes=None, chloro_genes=None):
    """
    计算 QC 统计量并返回 DataFrame

    Parameters
    ----------
    adata : AnnData
    mt_prefixes : list, optional
        线粒体基因前缀
    chloro_prefixes : list, optional
        叶绿体基因前缀
    mt_genes : list, optional
        自定义线粒体基因列表 (优先级高于前缀)
    chloro_genes : list, optional
        自定义叶绿体基因列表 (优先级高于前缀)

    Returns
    -------
    pd.DataFrame
    """
    mt_prefixes = mt_prefixes or MT_PREFIXES
    chloro_prefixes = chloro_prefixes or CHLORO_PREFIXES

    # 1. 基础 QC (scanpy 自带)
    sc.pp.calculate_qc_metrics(adata, percent_top=None, log1p=False,
                               inplace=True)

    # 2. 识别线粒体基因
    if mt_genes is not None:
        adata.var['mt'] = adata.var_names.isin(mt_genes)
    else:
        adata.var['mt'] = adata.var_names.str.startswith(tuple(mt_prefixes))

    # 3. 识别叶绿体基因 (植物特有)
    if chloro_genes is not None:
        adata.var['chloro'] = adata.var_names.isin(chloro_genes)
    else:
        adata.var['chloro'] = adata.var_names.str.startswith(tuple(chloro_prefixes))

    # 4. 计算线粒体/叶绿体占比
    mt_counts = adata[:, adata.var['mt']].X.sum(axis=1).A1 if adata.var['mt'].any() else np.zeros(adata.n_obs)
    chloro_counts = adata[:, adata.var['chloro']].X.sum(axis=1).A1 if adata.var['chloro'].any() else np.zeros(adata.n_obs)
    total_counts = adata.X.sum(axis=1).A1

    adata.obs['pct_counts_mt'] = (mt_counts / total_counts * 100).round(3)
    adata.obs['pct_counts_chloro'] = (chloro_counts / total_counts * 100).round(3)

    # 5. 组装输出 DataFrame
    cols = [
        'n_genes_by_counts',       # 每个细胞检测到的基因数
        'total_counts',            # 每个细胞的 UMI 总数
        'total_counts_mt',         # 线粒体 UMI 数
        'total_counts_chloro',     # 叶绿体 UMI 数
        'pct_counts_mt',           # 线粒体占比 (%)
        'pct_counts_chloro',       # 叶绿体占比 (%)
        'n_genes',                 # 基因数 (同 n_genes_by_counts)
    ]

    df = adata.obs[cols].copy()
    df.index.name = 'cell_barcode'

    # 6. 添加基因层面的统计 (用于基因过滤)
    gene_stats = pd.DataFrame({
        'gene_id': adata.var_names,
        'n_cells': np.array((adata.X > 0).sum(axis=0)).flatten(),
        'total_counts': np.array(adata.X.sum(axis=0)).flatten(),
        'pct_cells': np.array((adata.X > 0).sum(axis=0)).flatten() / adata.n_obs * 100,
    })
    gene_stats = gene_stats.set_index('gene_id')

    return df, gene_stats


def main():
    parser = argparse.ArgumentParser(description='预计算 QC 统计量')
    parser.add_argument('-i', '--input', required=True, help='输入 .h5ad 文件路径')
    parser.add_argument('-o', '--output', default='./qc_stats',
                        help='输出前缀 (默认: ./qc_stats)')
    parser.add_argument('--mt-prefixes', nargs='+', default=MT_PREFIXES,
                        help='线粒体基因前缀 (默认: MT- mt- Mt- AtMp)')
    parser.add_argument('--chloro-prefixes', nargs='+', default=CHLORO_PREFIXES,
                        help='叶绿体基因前缀 (默认: ChrM ChrC Pt- cp-)')
    parser.add_argument('--mt-genes', help='线粒体基因列表文件 (每行一个基因名)')
    parser.add_argument('--chloro-genes', help='叶绿体基因列表文件 (每行一个基因名)')
    args = parser.parse_args()

    # 读取数据
    print(f"[1/3] 读取 AnnData: {args.input}")
    adata = sc.read_h5ad(args.input)
    print(f"      {adata.n_obs} 细胞 × {adata.n_vars} 基因")

    # 加载自定义基因列表
    mt_genes = None
    chloro_genes = None
    if args.mt_genes:
        mt_genes = pd.read_csv(args.mt_genes, header=None)[0].tolist()
        print(f"      使用自定义线粒体基因列表: {len(mt_genes)} 个基因")
    if args.chloro_genes:
        chloro_genes = pd.read_csv(args.chloro_genes, header=None)[0].tolist()
        print(f"      使用自定义叶绿体基因列表: {len(chloro_genes)} 个基因")

    # 计算 QC 统计
    print(f"[2/3] 计算 QC 统计量...")
    cell_stats, gene_stats = compute_qc_stats(
        adata,
        mt_prefixes=args.mt_prefixes,
        chloro_prefixes=args.chloro_prefixes,
        mt_genes=mt_genes,
        chloro_genes=chloro_genes,
    )

    # 导出
    cell_file = f"{args.output}_cells.csv"
    gene_file = f"{args.output}_genes.csv"
    print(f"[3/3] 导出结果:")
    cell_stats.to_csv(cell_file)
    print(f"      → {cell_file}  ({len(cell_stats)} 细胞)")
    gene_stats.to_csv(gene_file)
    print(f"      → {gene_file}  ({len(gene_stats)} 基因)")
    print("完成!")


if __name__ == '__main__':
    main()
