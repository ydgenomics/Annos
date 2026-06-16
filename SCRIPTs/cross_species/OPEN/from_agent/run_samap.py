#!/usr/bin/env python3
"""
跨物种单细胞整合主流程 (SAMap)
===============================
基于 from_zly 方案改进，简化参数传递，增加灵活配置。

用法:
    python run_samap.py --species sp1:h5ad/sp1.h5ad,pep/sp1.pep \\
                        --species sp2:h5ad/sp2.h5ad,pep/sp2.pep \\
                        --aligner diamond --threads 20 \\
                        --replace_id yes --subsample 0.1

依赖:
    pip install samap samalg scanpy anndata pandas matplotlib
    conda install -c bioconda blast diamond
"""

import argparse
import os
import sys
import subprocess
import random
import pickle
from pathlib import Path

import scanpy as sc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from samap.mapping import SAMAP
from samap.analysis import (
    get_mapping_scores, GenePairFinder,
    sankey_plot, chord_plot, CellTypeTriangles,
    ParalogSubstitutions, FunctionalEnrichment,
    convert_eggnog_to_homologs, GeneTriangles,
)
from samalg import SAM


# ============================================================
# 1. 参数解析
# ============================================================
def parse_args():
    parser = argparse.ArgumentParser(
        description="跨物种单细胞整合 (SAMap) - 简化版",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 两个物种整合，使用 diamond，替换基因ID，10% 亚采样
  python run_samap.py \\
    --species sp1:data/sp1.h5ad,data/sp1.pep \\
    --species sp2:data/sp2.h5ad,data/sp2.pep \\
    --aligner diamond --threads 20 \\
    --replace_id yes --subsample 0.1

  # 三个物种，使用 blastp，不替换ID，不亚采样
  python run_samap.py \\
    --species sp1:data/sp1.h5ad,data/sp1.pep \\
    --species sp2:data/sp2.h5ad,data/sp2.pep \\
    --species sp3:data/sp3.h5ad,data/sp3.pep \\
    --aligner blastp --threads 40 \\
    --replace_id no

  # 从已有 maps 目录直接运行（跳过比对）
  python run_samap.py \\
    --species sp1:data/sp1.h5ad,data/sp1.pep \\
    --species sp2:data/sp2.h5ad,data/sp2.pep \\
    --maps_dir ./maps --skip_align
        """,
    )

    # --- 物种参数 ---
    parser.add_argument(
        "--species", "-s",
        action="append",
        required=True,
        help="物种信息，格式: name:h5ad_path,pep_path (可多次使用)",
    )

    # --- 比对参数 ---
    parser.add_argument(
        "--aligner", "-a",
        choices=["blastp", "diamond"],
        default="diamond",
        help="比对工具: blastp 或 diamond (默认: diamond)",
    )
    parser.add_argument(
        "--threads", "-t",
        type=int,
        default=40,
        help="比对线程数 (默认: 40)",
    )
    parser.add_argument(
        "--evalue",
        type=float,
        default=1e-6,
        help="BLAST/DIAMOND E-value 阈值 (默认: 1e-6)",
    )
    parser.add_argument(
        "--maps_dir",
        default="./maps",
        help="同源基因映射表输出目录 (默认: ./maps)",
    )
    parser.add_argument(
        "--skip_align",
        action="store_true",
        help="跳过比对步骤，使用已有 maps 目录",
    )

    # --- 基因ID替换 ---
    parser.add_argument(
        "--replace_id",
        choices=["yes", "no"],
        default="no",
        help="是否将基因ID中的 '_' 替换为 '-' (默认: no)",
    )

    # --- 亚采样参数 ---
    parser.add_argument(
        "--subsample",
        type=float,
        default=None,
        help="按细胞群亚采样比例，如 0.1 表示保留每个群10%%的细胞 (默认: 不采样)",
    )
    parser.add_argument(
        "--subsample_seed",
        type=int,
        default=42,
        help="亚采样随机种子 (默认: 42)",
    )

    # --- 预处理参数 ---
    parser.add_argument(
        "--batch_key",
        type=str,
        default=None,
        help="Harmony 整合的批次 key (如 orig.ident)",
    )
    parser.add_argument(
        "--cluster_key",
        type=str,
        default="celltype",
        help="细胞类型列名 (默认: celltype)",
    )
    parser.add_argument(
        "--raw_layer",
        type=str,
        default="counts",
        help="原始 counts 所在的 layer (默认: counts)",
    )

    # --- 输出参数 ---
    parser.add_argument(
        "--out_dir",
        default="./samap_result",
        help="输出目录 (默认: ./samap_result)",
    )
    parser.add_argument(
        "--prefix",
        default="samap",
        help="输出文件前缀 (默认: samap)",
    )

    return parser.parse_args()


# ============================================================
# 2. 解析物种信息
# ============================================================
def parse_species(args):
    """解析 --species 参数，返回物种信息列表"""
    species_list = []
    for s in args.species:
        try:
            name, paths = s.split(":", 1)
            h5ad_path, pep_path = paths.split(",", 1)
            species_list.append({
                "name": name.strip(),
                "h5ad": h5ad_path.strip(),
                "pep": pep_path.strip(),
            })
        except ValueError:
            print(f"[错误] 物种参数格式错误: '{s}'")
            print("  正确格式: name:h5ad_path,pep_path")
            print("  示例: sp1:data/sp1.h5ad,data/sp1.pep")
            sys.exit(1)

    # 检查文件是否存在
    for sp in species_list:
        for key in ["h5ad", "pep"]:
            if not os.path.exists(sp[key]):
                print(f"[错误] 文件不存在: {sp[key]} (物种: {sp['name']})")
                sys.exit(1)

    return species_list


# ============================================================
# 3. 亚采样 (按细胞群)
# ============================================================
def subsample_by_cluster(adata, fraction, cluster_key, seed=42):
    """按细胞群进行亚采样，保留每个群指定比例的细胞"""
    if fraction is None or fraction >= 1.0:
        return adata

    if cluster_key not in adata.obs.columns:
        print(f"[警告] 亚采样: 找不到列 '{cluster_key}'，跳过亚采样")
        return adata

    random.seed(seed)
    n_cells_before = adata.n_obs

    # 对每个细胞群独立采样
    clusters = adata.obs[cluster_key].unique()
    selected_indices = []

    for cluster in clusters:
        cluster_mask = adata.obs[cluster_key] == cluster
        cluster_indices = np.where(cluster_mask)[0]
        n_select = max(1, int(len(cluster_indices) * fraction))
        selected = random.sample(list(cluster_indices), n_select)
        selected_indices.extend(selected)

    adata = adata[selected_indices].copy()
    n_cells_after = adata.n_obs

    print(f"[亚采样] {cluster_key}: {n_cells_before} -> {n_cells_after} 细胞 "
          f"(保留 {fraction:.0%})")

    return adata


# ============================================================
# 4. 数据预处理
# ============================================================
def preprocess_species(species_list, args):
    """
    对每个物种进行预处理:
    1. 读取 h5ad
    2. 添加物种标签
    3. 亚采样 (可选)
    4. 保存预处理后的 h5ad
    """
    print("\n" + "=" * 60)
    print("步骤1: 数据预处理")
    print("=" * 60)

    preprocessed = []
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for sp in species_list:
        name = sp["name"]
        print(f"\n--- 处理物种: {name} ---")

        # 读取数据
        adata = sc.read_h5ad(sp["h5ad"])
        print(f"  读取: {sp['h5ad']} ({adata.n_obs} 细胞, {adata.n_vars} 基因)")

        # 检查 layers 中是否存在原始 counts，存在则恢复为 .X
        # SAMap 内部 preprocess_data() 会做 sum_norm + log 变换，
        # 如果 .X 已经是 log-normalize 后的数据，会导致二次归一化错误
        if "counts" in adata.layers:
            print(f"  ✓ 检测到 layers['counts']，恢复原始 counts 到 .X")
            adata.X = adata.layers["counts"].copy()
            if adata.raw is not None:
                del adata.raw
        else:
            print(f"  - 未检测到 layers['counts']，直接使用 .X 中的现有数据")

        # 添加物种标签
        adata.obs["species"] = name

        # 计算 QC 指标
        sc.pp.calculate_qc_metrics(adata, inplace=True)

        # 亚采样
        if args.subsample is not None:
            adata = subsample_by_cluster(
                adata, args.subsample, args.cluster_key, args.subsample_seed
            )

        # 保存预处理后的数据
        out_path = out_dir / f"{name}_preprocessed.h5ad"
        adata.write(out_path, compression="gzip")
        print(f"  保存: {out_path}")

        preprocessed.append({
            "name": name,
            "adata_path": str(out_path),
            "pep_path": sp["pep"],
        })

    return preprocessed


# ============================================================
# 5. 运行 SAM 预处理 (每个物种独立降维)
# ============================================================
def run_sam_preprocess(preprocessed, args):
    """
    对每个物种独立运行 SAM 降维
    """
    print("\n" + "=" * 60)
    print("步骤2: 各物种独立 SAM 降维")
    print("=" * 60)

    sam_objects = {}
    out_dir = Path(args.out_dir)

    for sp in preprocessed:
        name = sp["name"]
        print(f"\n--- SAM 降维: {name} ---")

        fn = sp["adata_path"]
        sam = SAM()
        sam.load_data(fn)
        sam.preprocess_data()

        if args.batch_key:
            print(f"  使用 batch_key: {args.batch_key}")
            sam.run(batch_key=args.batch_key)
        else:
            sam.run()

        pkl_path = str(out_dir / f"{name}_sam.pkl")
        sam.save(pkl_path)
        print(f"  保存 SAM 对象: {pkl_path}")

        sam_objects[name] = sam

    return sam_objects


# ============================================================
# 6. 同源基因比对 (BLASTp / DIAMOND)
# ============================================================
def run_homology_mapping(preprocessed, args):
    """
    运行 pairwise 同源基因比对
    支持 blastp 和 diamond 两种工具
    """
    print("\n" + "=" * 60)
    print("步骤3: 同源基因比对")
    print("=" * 60)

    maps_dir = Path(args.maps_dir)
    maps_dir.mkdir(parents=True, exist_ok=True)

    names = [sp["name"] for sp in preprocessed]
    pep_files = {sp["name"]: sp["pep_path"] for sp in preprocessed}

    # 创建 BLAST/DIAMOND 数据库
    print("\n--- 创建比对数据库 ---")
    for name, pep in pep_files.items():
        print(f"  处理: {name} ({pep})")
        if args.aligner == "blastp":
            _run_cmd(f"makeblastdb -in {pep} -dbtype prot")
        else:  # diamond
            db_path = str(Path(pep).with_suffix(".dmnd"))
            if not os.path.exists(db_path):
                _run_cmd(f"diamond makedb --in {pep} --db {db_path}")
            else:
                print(f"    数据库已存在: {db_path}")

    # 两两比对
    print("\n--- 两两比对 ---")
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            q_name, d_name = names[i], names[j]
            q_pep, d_pep = pep_files[q_name], pep_files[d_name]
            pair_dir = maps_dir / f"{q_name}{d_name}"
            pair_dir.mkdir(parents=True, exist_ok=True)

            print(f"\n  比对: {q_name} <-> {d_name}")

            # 正向比对: query -> db
            out_fwd = pair_dir / f"{q_name}_to_{d_name}.txt"
            _run_align(q_pep, d_pep, out_fwd, args)

            # 反向比对: db -> query
            out_rev = pair_dir / f"{d_name}_to_{q_name}.txt"
            _run_align(d_pep, q_pep, out_rev, args)

            # 基因ID替换 (可选)
            if args.replace_id == "yes":
                _replace_gene_id(pair_dir, q_name, d_name)

    print(f"\n  同源映射表已保存至: {maps_dir}")
    return str(maps_dir)


def _run_align(query_pep, db_pep, out_path, args):
    """执行单次比对"""
    if args.aligner == "blastp":
        cmd = (
            f"blastp -query {query_pep} -db {db_pep} "
            f"-outfmt 6 -out {out_path} "
            f"-num_threads {args.threads} "
            f"-max_hsps 1 -evalue {args.evalue}"
        )
    else:  # diamond
        db_path = str(Path(db_pep).with_suffix(".dmnd"))
        cmd = (
            f"diamond blastp --query {query_pep} --db {db_path} "
            f"--outfmt 6 --out {out_path} "
            f"--threads {args.threads} "
            f"--max-hsps 1 --evalue {args.evalue}"
        )
    _run_cmd(cmd)


def _replace_gene_id(pair_dir, name1, name2):
    """将基因ID中的 '_' 替换为 '-'"""
    for fname in [f"{name1}_to_{name2}.txt", f"{name2}_to_{name1}.txt"]:
        fpath = pair_dir / fname
        if fpath.exists():
            # 检查是否包含 '_'
            with open(fpath) as f:
                lines = f.readlines()
            if len(lines) >= 2 and ("_" in lines[1]):
                print(f"    替换基因ID: {fname} (_ -> -)")
                _run_cmd(f"sed -i 's/_/-/g' {fpath}")
            else:
                print(f"    无需替换: {fname}")


def _run_cmd(cmd):
    """运行 shell 命令"""
    print(f"  $ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [错误] 命令失败: {cmd}")
        print(f"  stderr: {result.stderr}")
        sys.exit(1)
    return result


# ============================================================
# 7. SAMap 跨物种整合
# ============================================================
def run_samap_integration(sam_objects, maps_dir, args):
    """
    运行 SAMap 跨物种整合
    """
    print("\n" + "=" * 60)
    print("步骤4: SAMap 跨物种整合")
    print("=" * 60)

    # 构建 filenames 字典
    filenames = {}
    keys = {}
    neigh_from_keys = {}

    for name, sam in sam_objects.items():
        filenames[name] = sam
        keys[name] = args.cluster_key
        neigh_from_keys[name] = True

    # 初始化 SAMAP
    print("\n初始化 SAMAP...")
    sm = SAMAP(filenames, f_maps=maps_dir, keys=keys)

    # 运行整合
    print("运行 SAMap 整合 (这可能耗时较长)...")
    sm.run(pairwise=True, neigh_from_keys=neigh_from_keys)

    return sm


# ============================================================
# 8. 结果输出
# ============================================================
def save_results(sm, args):
    """
    保存整合结果:
    - 细胞类型映射关系
    - 基因对关系
    - UMAP 图
    - 整合后的 h5ad
    """
    print("\n" + "=" * 60)
    print("步骤5: 保存结果")
    print("=" * 60)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    prefix = args.prefix

    samap = sm.samap

    # 5.1 细胞类型映射分数
    print("\n--- 细胞类型映射 ---")
    keys = {}
    for sp in samap.adata.obs["species"].unique():
        keys[sp] = args.cluster_key

    D, MappingTable = get_mapping_scores(sm, keys, n_top=0)
    D.to_csv(out_dir / f"{prefix}_celltype_relationship.csv")
    MappingTable.to_csv(out_dir / f"{prefix}_MappingTable.csv")
    print(f"  细胞类型关系: {out_dir / f'{prefix}_celltype_relationship.csv'}")
    print(f"  映射表: {out_dir / f'{prefix}_MappingTable.csv'}")

    # 5.2 Sankey 图
    try:
        print("\n--- 绘制 Sankey 图 ---")
        sankey_plot(MappingTable, align_thr=0.05)
        plt.savefig(str(out_dir / f"{prefix}_sankey.pdf"), bbox_inches="tight")
        plt.close()
        print(f"  Sankey 图: {out_dir / f'{prefix}_sankey.pdf'}")
    except Exception as e:
        print(f"  [警告] Sankey 图绘制失败: {e}")

    # 5.3 UMAP 图
    print("\n--- 绘制 UMAP ---")
    sm.scatter()
    plt.savefig(str(out_dir / f"{prefix}_umap.pdf"), bbox_inches="tight")
    plt.close()
    print(f"  UMAP: {out_dir / f'{prefix}_umap.pdf'}")

    # 5.4 基因对
    print("\n--- 基因对分析 ---")
    try:
        gpf = GenePairFinder(sm, keys=keys)
        gene_pairs = gpf.find_all(align_thr=0.2)
        gene_pairs.to_csv(out_dir / f"{prefix}_gene_pairs.csv")
        print(f"  基因对: {out_dir / f'{prefix}_gene_pairs.csv'}")
    except Exception as e:
        print(f"  [警告] 基因对分析失败: {e}")

    # 5.5 保存整合后的 h5ad
    print("\n--- 保存整合数据 ---")
    adata = samap.adata
    adata.obs["celltype"] = samap.adata.obs.get(
        "celltype;celltype_mapping_scores",
        samap.adata.obs.get(args.cluster_key, "unknown"),
    )
    adata.obsm["wPCA"] = samap.adata.obsm["X_umap"]

    h5ad_path = out_dir / f"{prefix}_integrated.h5ad"
    adata.write(str(h5ad_path), compression="gzip")
    print(f"  整合数据: {h5ad_path}")

    # 5.6 保存完整 SAMap 对象
    pkl_path = out_dir / f"{prefix}_samap.pkl"
    with open(pkl_path, "wb") as f:
        pickle.dump(sm, f)
    print(f"  SAMap 对象: {pkl_path}")

    print("\n" + "=" * 60)
    print("🎉 跨物种整合完成!")
    print(f"   输出目录: {out_dir.resolve()}")
    print("=" * 60)


# ============================================================
# 主流程
# ============================================================
def main():
    args = parse_args()

    print("=" * 60)
    print("  跨物种单细胞整合 (SAMap) - from_agent")
    print("=" * 60)
    print(f"  比对工具: {args.aligner}")
    print(f"  线程数: {args.threads}")
    print(f"  替换基因ID: {args.replace_id}")
    print(f"  亚采样: {args.subsample or '无'}")
    print(f"  物种数: {len(args.species)}")
    for s in args.species:
        print(f"    - {s}")
    print("=" * 60)

    # 1. 解析物种
    species_list = parse_species(args)

    # 2. 预处理
    preprocessed = preprocess_species(species_list, args)

    # 3. 同源基因比对 (可选)
    if args.skip_align:
        maps_dir = args.maps_dir
        print(f"\n[跳过比对] 使用已有 maps 目录: {maps_dir}")
        if not os.path.isdir(maps_dir):
            print(f"[错误] maps 目录不存在: {maps_dir}")
            sys.exit(1)
    else:
        maps_dir = run_homology_mapping(preprocessed, args)

    # 4. SAM 降维
    sam_objects = run_sam_preprocess(preprocessed, args)

    # 5. SAMap 整合
    sm = run_samap_integration(sam_objects, maps_dir, args)

    # 6. 保存结果
    save_results(sm, args)


if __name__ == "__main__":
    main()
