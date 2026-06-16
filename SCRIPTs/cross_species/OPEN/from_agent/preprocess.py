#!/usr/bin/env python3
"""
数据预处理脚本
==============
对每个物种的 h5ad 数据进行预处理:
1. 添加物种标签
2. 亚采样 (可选，按细胞群比例)
3. 保存预处理后的 h5ad

用法:
    python preprocess.py --species sp1:data/sp1.h5ad --species sp2:data/sp2.h5ad \\
                         --cluster_key celltype --subsample 0.1 --out_dir ./processed

    # 只预处理，不亚采样
    python preprocess.py --species sp1:data/sp1.h5ad --species sp2:data/sp2.h5ad \\
                         --out_dir ./processed
"""

import argparse
import os
import random
import sys
from pathlib import Path

import scanpy as sc
import pandas as pd
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser(description="跨物种数据预处理")
    parser.add_argument(
        "--species", "-s",
        action="append",
        required=True,
        help="物种信息，格式: name:h5ad_path (可多次使用)",
    )
    parser.add_argument(
        "--cluster_key",
        default="celltype",
        help="细胞类型/群列名，用于亚采样 (默认: celltype)",
    )
    parser.add_argument(
        "--subsample",
        type=float,
        default=None,
        help="按细胞群亚采样比例，如 0.1 保留每个群10%% (默认: 不采样)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="随机种子 (默认: 42)",
    )
    parser.add_argument(
        "--out_dir",
        default="./processed",
        help="输出目录 (默认: ./processed)",
    )
    return parser.parse_args()


def subsample_by_cluster(adata, fraction, cluster_key, seed=42):
    """按细胞群亚采样"""
    if fraction is None or fraction >= 1.0:
        return adata

    if cluster_key not in adata.obs.columns:
        print(f"  [警告] 找不到列 '{cluster_key}'，跳过亚采样")
        return adata

    random.seed(seed)
    n_before = adata.n_obs
    clusters = adata.obs[cluster_key].unique()
    selected = []

    for cluster in clusters:
        mask = adata.obs[cluster_key] == cluster
        idx = np.where(mask)[0]
        n = max(1, int(len(idx) * fraction))
        selected.extend(random.sample(list(idx), n))

    adata = adata[selected].copy()
    print(f"  [亚采样] {n_before} -> {adata.n_obs} 细胞 (保留 {fraction:.0%})")
    return adata


def main():
    args = parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 50)
    print("数据预处理")
    print(f"  亚采样: {args.subsample or '无'}")
    print(f"  输出: {out_dir}")
    print("=" * 50)

    for s in args.species:
        try:
            name, h5ad_path = s.split(":", 1)
            name = name.strip()
            h5ad_path = h5ad_path.strip()
        except ValueError:
            print(f"[错误] 格式错误: '{s}'，应为 name:h5ad_path")
            sys.exit(1)

        if not os.path.exists(h5ad_path):
            print(f"[错误] 文件不存在: {h5ad_path}")
            sys.exit(1)

        print(f"\n--- {name} ---")
        adata = sc.read_h5ad(h5ad_path)
        print(f"  读取: {h5ad_path} ({adata.n_obs} 细胞, {adata.n_vars} 基因)")

        # 检查 layers 中是否存在原始 counts，存在则恢复为 .X
        if "counts" in adata.layers:
            print(f"  ✓ 检测到 layers['counts']，恢复原始 counts 到 .X")
            adata.X = adata.layers["counts"].copy()
            if adata.raw is not None:
                del adata.raw
        else:
            print(f"  - 未检测到 layers['counts']，直接使用 .X 中的现有数据")

        # 添加物种标签
        adata.obs["species"] = name

        # QC 指标
        sc.pp.calculate_qc_metrics(adata, inplace=True)

        # 亚采样
        adata = subsample_by_cluster(adata, args.subsample, args.cluster_key, args.seed)

        # 保存
        out_path = out_dir / f"{name}_preprocessed.h5ad"
        adata.write(out_path, compression="gzip")
        print(f"  保存: {out_path}")

    print("\n完成!")


if __name__ == "__main__":
    main()
