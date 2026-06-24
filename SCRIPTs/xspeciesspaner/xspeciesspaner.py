#!/usr/bin/env python3
"""
XSpeciesSpanner — 跨物种细胞类型注释工具
=========================================
基于超几何分布检验的跨物种细胞类型注释算法。

算法流程:
  1. 构建评分基因集: 读取 foundation genes CSV，构建 {cell_type: [genes]} 字典
  2. 同源蛋白质预测: 使用 BLASTP 将 query 物种蛋白质与 foundation 蛋白质序列比对
  3. 运行评分算法: 对每个 cluster 的 DEGs，使用超几何分布检验评估富集程度
  4. 定义细胞类型: 基于 p-value 应用顺序决策规则确定细胞类型

用法:
    python XSpeciesSpanner.py \\
        --foundation_csv foundation_genes.csv \\
        --foundation_pep foundation_species.pep \\
        --query_pep query_species.pep \\
        --marker_csv find_all_markers.csv \\
        --output ./xspeciesspanner_result

依赖:
    pip install pandas numpy scipy biopython
    conda install -c bioconda blast
"""

import argparse
import os
import sys
import subprocess
import warnings
from pathlib import Path
from collections import defaultdict

import numpy as np
import pandas as pd
from scipy.stats import hypergeom

warnings.filterwarnings("ignore")

# ============================================================
# 参数解析
# ============================================================
def parse_args():
    parser = argparse.ArgumentParser(
        description="XSpeciesSpanner — 跨物种细胞类型注释工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 完整流程
  python XSpeciesSpanner.py \\
    --foundation_csv ./foundation_genes/epidermis.csv \\
    --foundation_pep ./proteome/athaliana.pep \\
    --query_pep ./proteome/query_species.pep \\
    --marker_csv ./markers/find_all_markers.csv \\
    --output ./result

  # 跳过 BLASTP（使用已有同源映射）
  python XSpeciesSpanner.py \\
    --foundation_csv ./foundation_genes/epidermis.csv \\
    --marker_csv ./markers/find_all_markers.csv \\
    --homology_map ./result/blast_results/query_to_foundation.txt \\
    --output ./result
        """,
    )

    # --- 必需参数 ---
    parser.add_argument(
        "--foundation_csv", type=str, required=True,
        help="Foundation genes CSV 文件路径 (两列: gene, cell_type)",
    )
    parser.add_argument(
        "--marker_csv", type=str, required=True,
        help="FindAllMarkers 结果 CSV 文件路径 (scanpy 输出格式)",
    )

    # --- BLASTP 相关参数 ---
    parser.add_argument(
        "--foundation_pep", type=str, default=None,
        help="Foundation 物种的蛋白质 FASTA 文件 (用于 BLASTP 建库)",
    )
    parser.add_argument(
        "--query_pep", type=str, default=None,
        help="Query 物种的蛋白质 FASTA 文件",
    )
    parser.add_argument(
        "--homology_map", type=str, default=None,
        help="已有的同源映射文件 (BLASTP outfmt 6 格式)，跳过 BLASTP 步骤",
    )

    # --- BLASTP 参数 ---
    parser.add_argument(
        "--blast_evalue", type=float, default=1e-6,
        help="BLASTP E-value 阈值 (默认: 1e-6)",
    )
    parser.add_argument(
        "--blast_threads", type=int, default=8,
        help="BLASTP 线程数 (默认: 8)",
    )
    parser.add_argument(
        "--blast_max_targets", type=int, default=5,
        help="BLASTP 每个 query 保留的最大目标序列数 (默认: 5)",
    )

    # --- SATURN 基因过滤 ---
    parser.add_argument(
        "--saturn_genes", type=str, default=None,
        help="SATURN 识别的基因列表文件 (每行一个基因)，用于过滤 foundation genes",
    )

    # --- 评分参数 ---
    parser.add_argument(
        "--pval_threshold", type=float, default=0.05,
        help="显著性阈值 (默认: 0.05)",
    )
    parser.add_argument(
        "--mixed_ratio", type=float, default=0.1,
        help="混合细胞类型判断的 p-value 比值阈值 (默认: 0.1)",
    )
    parser.add_argument(
        "--min_deg_genes", type=int, default=5,
        help="每个 cluster 最少 DEG 数量 (默认: 5)",
    )

    # --- 输出参数 ---
    parser.add_argument(
        "--output", type=str, default="./xspeciesspanner_result",
        help="输出目录 (默认: ./xspeciesspanner_result)",
    )
    parser.add_argument(
        "--prefix", type=str, default="XSpeciesSpanner",
        help="输出文件前缀 (默认: XSpeciesSpanner)",
    )

    return parser.parse_args()


# ============================================================
# Step 1: 构建评分基因集
# ============================================================
def build_scoring_gene_sets(foundation_csv, saturn_genes=None):
    """
    读取 foundation genes CSV，构建评分基因集字典。

    CSV 格式: 两列 [gene, cell_type]
    每行表示一个基因属于某个细胞类型的 foundation gene set。

    可选: 与 SATURN 识别的基因取交集过滤。
    """
    print("\n" + "=" * 60)
    print("Step 1: 构建评分基因集 (Scoring Gene Set Construction)")
    print("=" * 60)

    df = pd.read_csv(foundation_csv)
    required_cols = {"gene", "cell_type"}
    if not required_cols.issubset(df.columns):
        print(f"[错误] foundation_csv 必须包含列: {required_cols}")
        print(f"  当前列: {list(df.columns)}")
        sys.exit(1)

    # 构建 {cell_type: set(genes)} 字典
    gene_sets = {}
    for cell_type, group in df.groupby("cell_type"):
        genes = set(group["gene"].dropna().str.strip())
        gene_sets[cell_type] = genes

    print(f"  读取 foundation genes: {len(df)} 行, {len(gene_sets)} 个细胞类型")
    for ct, genes in gene_sets.items():
        print(f"    - {ct}: {len(genes)} 个基因")

    # 可选: 与 SATURN 识别的基因取交集
    if saturn_genes:
        saturn_set = set()
        with open(saturn_genes) as f:
            for line in f:
                gene = line.strip()
                if gene:
                    saturn_set.add(gene)
        print(f"\n  SATURN 基因列表: {len(saturn_set)} 个基因")

        filtered_sets = {}
        for ct, genes in gene_sets.items():
            overlap = genes & saturn_set
            filtered_sets[ct] = overlap
            print(f"    - {ct}: {len(genes)} -> {len(overlap)} (交集后)")
        gene_sets = filtered_sets

    # 统计所有 foundation genes 的并集
    all_foundation_genes = set()
    for genes in gene_sets.values():
        all_foundation_genes.update(genes)

    print(f"\n  所有 foundation genes 并集: {len(all_foundation_genes)} 个基因")
    print(f"  Step 1 完成!")
    return gene_sets, all_foundation_genes


# ============================================================
# Step 2: 同源蛋白质预测 (BLASTP)
# ============================================================
def run_blastp(query_pep, foundation_pep, output_dir, args):
    """
    使用 BLASTP 建立 query 物种与 foundation 物种之间的同源关系。

    流程:
    1. 为 foundation 蛋白质 FASTA 创建 BLAST 数据库
    2. 使用 query 蛋白质 FASTA 进行 BLASTP 查询
    3. 解析 outfmt 6 结果，建立 query_gene → foundation_gene 映射
    """
    print("\n" + "=" * 60)
    print("Step 2: 同源蛋白质预测 (Homologous Protein Prediction)")
    print("=" * 60)

    blast_dir = Path(output_dir) / "blast_results"
    blast_dir.mkdir(parents=True, exist_ok=True)

    # --- 2.1 创建 BLAST 数据库 ---
    print("\n--- 2.1 创建 BLAST 数据库 ---")
    db_name = str(blast_dir / "foundation_db")
    makeblastdb_cmd = [
        "makeblastdb",
        "-in", foundation_pep,
        "-dbtype", "prot",
        "-out", db_name,
    ]
    print(f"  $ {' '.join(makeblastdb_cmd)}")
    result = subprocess.run(makeblastdb_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [错误] makeblastdb 失败: {result.stderr}")
        sys.exit(1)
    print(f"  BLAST 数据库已创建: {db_name}")

    # --- 2.2 运行 BLASTP ---
    print("\n--- 2.2 运行 BLASTP ---")
    out_file = str(blast_dir / "query_to_foundation.txt")

    blastp_cmd = [
        "blastp",
        "-query", query_pep,
        "-db", db_name,
        "-outfmt", "6",
        "-out", out_file,
        "-evalue", str(args.blast_evalue),
        "-num_threads", str(args.blast_threads),
        "-max_target_seqs", str(args.blast_max_targets),
        "-max_hsps", "1",
    ]
    print(f"  $ {' '.join(blastp_cmd)}")
    result = subprocess.run(blastp_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [错误] blastp 失败: {result.stderr}")
        sys.exit(1)
    print(f"  BLASTP 结果已保存: {out_file}")

    # --- 2.3 解析 BLASTP 结果 ---
    print("\n--- 2.3 解析 BLASTP 结果 ---")
    homology_map = parse_blastp_results(out_file)
    print(f"  建立同源映射: {len(homology_map)} 个 query 基因映射到 foundation 基因")
    print(f"  Step 2 完成!")
    return homology_map, out_file


def parse_blastp_results(blast_out_file):
    """
    解析 BLASTP outfmt 6 结果。

    outfmt 6 列:
    1. qseqid  2. sseqid  3. pident  4. length  5. mismatch
    6. gapopen  7. qstart  8. qend  9. sstart  10. send
    11. evalue  12. bitscore

    返回: {query_gene: [foundation_gene1, foundation_gene2, ...]}
    """
    homology_map = defaultdict(list)
    with open(blast_out_file) as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) < 2:
                continue
            qseqid = parts[0].strip()
            sseqid = parts[1].strip()
            homology_map[qseqid].append(sseqid)
    return dict(homology_map)


def load_homology_map(homology_map_file):
    """加载已有的同源映射文件"""
    print("\n" + "=" * 60)
    print("Step 2: 同源蛋白质预测 (使用已有映射)")
    print("=" * 60)
    print(f"  加载同源映射: {homology_map_file}")
    homology_map = parse_blastp_results(homology_map_file)
    print(f"  加载完成: {len(homology_map)} 个 query 基因")
    print(f"  Step 2 完成!")
    return homology_map


# ============================================================
# Step 3: 运行评分算法 (超几何分布检验)
# ============================================================
def run_scoring_algorithm(marker_csv, gene_sets, all_foundation_genes,
                          homology_map, args):
    """
    使用超几何分布检验评估每个 cluster 的 DEGs
    在 foundation gene sets 中的富集程度。

    超几何分布参数:
    - N: 背景基因总数 (所有检测到的基因)
    - K: foundation gene set 的大小
    - n: 从背景中抽取的基因数 (cluster 的 DEGs 数量)
    - k: 抽取的基因中属于 foundation gene set 的数量

    p-value = P(X >= k) = hypergeom.sf(k-1, N, K, n)
    """
    print("\n" + "=" * 60)
    print("Step 3: 运行评分算法 (Scoring Algorithm)")
    print("=" * 60)

    # --- 3.1 读取 marker 数据 ---
    print("\n--- 3.1 读取 marker 数据 ---")
    df_markers = pd.read_csv(marker_csv)
    print(f"  读取 marker 数据: {len(df_markers)} 行")

    # 检测列名 (兼容 scanpy 和 Seurat 输出)
    gene_col = None
    cluster_col = None
    for col in ["gene", "genes", "Gene", "feature", "Feature"]:
        if col in df_markers.columns:
            gene_col = col
            break
    for col in ["cluster", "Cluster", "clusterName"]:
        if col in df_markers.columns:
            cluster_col = col
            break

    if gene_col is None or cluster_col is None:
        print(f"[错误] 无法识别 marker CSV 的列。当前列: {list(df_markers.columns)}")
        print(f"  需要基因名列 (gene/genes/feature) 和分群列 (cluster/Cluster)")
        sys.exit(1)

    print(f"  基因列: '{gene_col}', 分群列: '{cluster_col}'")

    # --- 3.2 获取所有检测到的基因 (背景基因集) ---
    all_detected_genes = set(df_markers[gene_col].dropna().str.strip())
    N = len(all_detected_genes)
    print(f"\n  背景基因总数 (N): {N}")

    # --- 3.3 将 query 基因映射到 foundation 基因 ---
    print("\n--- 3.3 基因同源映射 ---")
    clusters = df_markers[cluster_col].unique()
    print(f"  共 {len(clusters)} 个 clusters")

    cluster_foundation_genes = {}
    for cluster in clusters:
        cluster_df = df_markers[df_markers[cluster_col] == cluster]
        query_deg_genes = set(cluster_df[gene_col].dropna().str.strip())

        mapped_foundation_genes = set()
        for qgene in query_deg_genes:
            if qgene in homology_map:
                for fgene in homology_map[qgene]:
                    mapped_foundation_genes.add(fgene)

        cluster_foundation_genes[cluster] = {
            "query_deg_count": len(query_deg_genes),
            "foundation_genes": mapped_foundation_genes,
        }

    # --- 3.4 超几何分布检验 ---
    print("\n--- 3.4 超几何分布检验 ---")

    results = []
    for cluster, info in cluster_foundation_genes.items():
        n = info["query_deg_count"]
        mapped_genes = info["foundation_genes"]

        if n < args.min_deg_genes:
            print(f"  [跳过] {cluster}: DEGs ({n}) < {args.min_deg_genes}")
            for ct in gene_sets:
                results.append({
                    "cluster": cluster, "cell_type": ct,
                    "n_deg": n, "n_foundation_in_deg": 0,
                    "foundation_set_size": len(gene_sets[ct]),
                    "p_value": 1.0, "neg_log10_pval": 0.0,
                })
            continue

        for ct, foundation_genes in gene_sets.items():
            K = len(foundation_genes)
            k = len(mapped_genes & foundation_genes)

            if K == 0 or n == 0:
                p_value = 1.0
            else:
                p_value = hypergeom.sf(k - 1, N, K, n)
                if p_value < 1e-300:
                    p_value = 1e-300

            neg_log10_pval = -np.log10(p_value) if p_value > 0 else 300

            results.append({
                "cluster": cluster, "cell_type": ct,
                "n_deg": n, "n_foundation_in_deg": k,
                "foundation_set_size": K,
                "p_value": p_value, "neg_log10_pval": neg_log10_pval,
            })

    df_scores = pd.DataFrame(results)
    df_scores = df_scores.sort_values(["cluster", "p_value"]).reset_index(drop=True)

    print(f"\n  评分完成: {len(df_scores)} 行 (每个 cluster × 每个 cell type)")
    print(f"  Step 3 完成!")
    return df_scores


# ============================================================
# Step 4: 定义细胞类型
# ============================================================
def define_cell_types(df_scores, args):
    """
    基于超几何分布检验的 p-value，应用顺序决策规则确定细胞类型。

    决策规则:
    1. 对每个 cluster，找到最小 p-value 对应的 cell type
    2. 如果最小 p-value < threshold:
       a. 检查第二小 p / 最小 p 的比值
          - 比值 > mixed_ratio: 明确注释为该 cell type
          - 比值 <= mixed_ratio: 混合细胞类型或亚群
    3. 如果最小 p-value >= threshold: 标注为 "Unknown"
    """
    print("\n" + "=" * 60)
    print("Step 4: 定义细胞类型 (Cell Type Definition)")
    print("=" * 60)

    threshold = args.pval_threshold
    mixed_ratio = args.mixed_ratio

    annotations = []
    clusters = df_scores["cluster"].unique()

    print(f"\n  显著性阈值: p-value < {threshold}")
    print(f"  混合判断比值阈值: 第二小 p / 最小 p > {mixed_ratio}")
    print(f"\n--- 注释结果 ---")

    for cluster in clusters:
        cluster_scores = df_scores[df_scores["cluster"] == cluster].copy()
        cluster_scores = cluster_scores.sort_values("p_value").reset_index(drop=True)

        min_p = cluster_scores.iloc[0]["p_value"]
        best_ct = cluster_scores.iloc[0]["cell_type"]
        n_deg = cluster_scores.iloc[0]["n_deg"]

        # 检查 DEG 数量
        if n_deg < args.min_deg_genes:
            decision = "Unknown (insufficient DEGs)"
            print(f"  [Cluster {cluster}] DEGs={n_deg} < {args.min_deg_genes} → Unknown")
            annotations.append({
                "cluster": cluster, "n_deg": n_deg,
                "assigned_cell_type": "Unknown",
                "best_cell_type": best_ct, "best_p_value": min_p,
                "second_best_cell_type": "", "second_best_p_value": 1.0,
                "p_ratio": 1.0, "decision": decision,
            })
            continue

        # 规则 1: 检查最小 p-value 是否显著
        if min_p < threshold:
            if len(cluster_scores) > 1:
                second_p = cluster_scores.iloc[1]["p_value"]
                second_ct = cluster_scores.iloc[1]["cell_type"]
                ratio = second_p / min_p if min_p > 0 else float("inf")
            else:
                second_p = 1.0
                second_ct = ""
                ratio = float("inf")

            # 规则 2: 判断是明确类型还是混合/亚群
            if ratio > mixed_ratio:
                decision = f"Assigned (p={min_p:.2e}, ratio={ratio:.1f})"
                assigned_ct = best_ct
                print(f"  [Cluster {cluster}] → {best_ct} "
                      f"(p={min_p:.2e}, ratio={ratio:.1f})")
            else:
                decision = (f"Mixed/Subgroup (best={best_ct} p={min_p:.2e}, "
                           f"2nd={second_ct} p={second_p:.2e}, ratio={ratio:.1f})")
                assigned_ct = f"{best_ct}/{second_ct}"
                print(f"  [Cluster {cluster}] → {best_ct}/{second_ct} (混合/亚群)")
        else:
            # 规则 3: 不显著 → Unknown
            decision = f"Unknown (best p={min_p:.2e} >= {threshold})"
            assigned_ct = "Unknown"
            second_ct = ""
            second_p = 1.0
            ratio = 1.0
            print(f"  [Cluster {cluster}] → Unknown (best p={min_p:.2e})")

        annotations.append({
            "cluster": cluster, "n_deg": n_deg,
            "assigned_cell_type": assigned_ct,
            "best_cell_type": best_ct, "best_p_value": min_p,
            "second_best_cell_type": second_ct,
            "second_best_p_value": second_p,
            "p_ratio": ratio, "decision": decision,
        })

    df_annotation = pd.DataFrame(annotations)
    print(f"\n  Step 4 完成!")
    return df_annotation


# ============================================================
# 结果输出
# ============================================================
def save_results(df_scores, df_annotation, homology_map, blast_out_file,
                 output_dir, args):
    """保存所有结果到输出目录"""
    print("\n" + "=" * 60)
    print("保存结果")
    print("=" * 60)

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    prefix = args.prefix

    # 1. 富集评分表
    scores_file = out_path / f"{prefix}_enrichment_scores.csv"
    df_scores.to_csv(scores_file, index=False)
    print(f"  富集评分表: {scores_file}")

    # 2. 注释结果表
    anno_file = out_path / f"{prefix}_annotation_results.csv"
    df_annotation.to_csv(anno_file, index=False)
    print(f"  注释结果表: {anno_file}")

    # 3. 结果摘要
    summary_file = out_path / f"{prefix}_summary.txt"
    with open(summary_file, "w") as f:
        f.write("XSpeciesSpanner 跨物种细胞类型注释结果\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Foundation genes: {args.foundation_csv}\n")
        f.write(f"Marker CSV: {args.marker_csv}\n")
        f.write(f"显著性阈值: p < {args.pval_threshold}\n")
        f.write(f"混合判断比值阈值: {args.mixed_ratio}\n\n")
        f.write(f"{'Cluster':<20} {'Assigned Cell Type':<40} "
                f"{'Best p-value':<15} {'Decision':<40}\n")
        f.write("-" * 115 + "\n")
        for _, row in df_annotation.iterrows():
            f.write(f"{str(row['cluster']):<20} "
                    f"{str(row['assigned_cell_type']):<40} "
                    f"{row['best_p_value']:<15.2e} "
                    f"{str(row['decision']):<40}\n")
    print(f"  结果摘要: {summary_file}")

    # 4. Foundation 基因统计
    gene_sets, _ = build_scoring_gene_sets(args.foundation_csv, args.saturn_genes)
    stats_file = out_path / f"{prefix}_foundation_stats.csv"
    stats_data = [{"cell_type": ct, "n_foundation_genes": len(genes)}
                  for ct, genes in gene_sets.items()]
    pd.DataFrame(stats_data).to_csv(stats_file, index=False)
    print(f"  Foundation 基因统计: {stats_file}")

    # 5. 同源映射表
    if blast_out_file and os.path.exists(blast_out_file):
        import shutil
        shutil.copy2(blast_out_file, out_path / f"{prefix}_homology_map.txt")
        print(f"  同源映射表: {out_path / f'{prefix}_homology_map.txt'}")

    print(f"\n🎉 所有结果已保存至: {out_path.resolve()}")


# ============================================================
# 主流程
# ============================================================
def main():
    args = parse_args()

    print("=" * 60)
    print("  XSpeciesSpanner — 跨物种细胞类型注释")
    print("=" * 60)
    print(f"  Foundation genes: {args.foundation_csv}")
    print(f"  Marker CSV:       {args.marker_csv}")
    print(f"  Query PEP:        {args.query_pep or 'N/A'}")
    print(f"  Foundation PEP:   {args.foundation_pep or 'N/A'}")
    print(f"  输出目录:         {args.output}")
    print("=" * 60)

    # Step 1: 构建评分基因集
    gene_sets, all_foundation_genes = build_scoring_gene_sets(
        args.foundation_csv, args.saturn_genes
    )

    # Step 2: 同源蛋白质预测
    blast_out_file = None
    if args.homology_map:
        homology_map = load_homology_map(args.homology_map)
        blast_out_file = args.homology_map
    elif args.query_pep and args.foundation_pep:
        homology_map, blast_out_file = run_blastp(
            args.query_pep, args.foundation_pep, args.output, args
        )
    else:
        print("\n[错误] 需要提供 --query_pep 和 --foundation_pep 运行 BLASTP，"
              "或使用 --homology_map 提供已有的同源映射")
        sys.exit(1)

    # Step 3: 运行评分算法
    df_scores = run_scoring_algorithm(
        args.marker_csv, gene_sets, all_foundation_genes,
        homology_map, args
    )

    # Step 4: 定义细胞类型
    df_annotation = define_cell_types(df_scores, args)

    # 保存结果
    save_results(df_scores, df_annotation, homology_map, blast_out_file,
                 args.output, args)

    print("\n" + "=" * 60)
    print("  🎉 XSpeciesSpanner 运行完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()