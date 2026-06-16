#!/bin/bash
# ============================================================
# 同源基因比对脚本 (支持 BLASTp 和 DIAMOND)
# ============================================================
# 用法:
#   bash run_align.sh <pep_dir> <maps_dir> [aligner] [threads] [evalue] [replace_id]
#
# 参数:
#   pep_dir     - 存放 .pep 蛋白文件的目录
#   maps_dir    - 输出映射表的目录
#   aligner     - 比对工具: blastp 或 diamond (默认: diamond)
#   threads     - 线程数 (默认: 40)
#   evalue      - E-value 阈值 (默认: 1e-6)
#   replace_id  - 是否替换基因ID: yes 或 no (默认: no)
#
# 示例:
#   bash run_align.sh ./pep_files ./maps diamond 40 1e-6 yes
#   bash run_align.sh ./pep_files ./maps blastp 20 1e-6 no
# ============================================================

set -e

# --- 解析参数 ---
pep_dir="$1"
maps_dir="$2"
aligner="${3:-diamond}"
threads="${4:-40}"
evalue="${5:-1e-6}"
replace_id="${6:-no}"

if [ $# -lt 2 ]; then
    echo "用法: bash run_align.sh <pep_dir> <maps_dir> [aligner] [threads] [evalue] [replace_id]"
    echo "  aligner: blastp | diamond (默认: diamond)"
    echo "  replace_id: yes | no (默认: no)"
    exit 1
fi

# 检查比对工具
if [ "$aligner" = "blastp" ]; then
    command -v makeblastdb >/dev/null 2>&1 || { echo "错误: 未找到 makeblastdb，请安装 BLAST+"; exit 1; }
    command -v blastp >/dev/null 2>&1 || { echo "错误: 未找到 blastp，请安装 BLAST+"; exit 1; }
elif [ "$aligner" = "diamond" ]; then
    command -v diamond >/dev/null 2>&1 || { echo "错误: 未找到 diamond，请安装 DIAMOND"; exit 1; }
else
    echo "错误: 不支持的比对工具 '$aligner'，请使用 blastp 或 diamond"
    exit 1
fi

mkdir -p "$maps_dir"

echo "=========================================="
echo "  同源基因比对"
echo "  蛋白目录: $pep_dir"
echo "  输出目录: $maps_dir"
echo "  比对工具: $aligner"
echo "  线程数:   $threads"
echo "  E-value:  $evalue"
echo "  替换ID:   $replace_id"
echo "=========================================="

# --- 收集所有 .pep 文件 ---
pep_files=("$pep_dir"/*.pep)
if [ ${#pep_files[@]} -eq 0 ]; then
    echo "错误: $pep_dir 中没有 .pep 文件"
    exit 1
fi

names=()
for f in "${pep_files[@]}"; do
    base=$(basename "$f" .pep)
    names+=("$base")
done

echo "发现物种: ${names[*]}"

# --- 创建数据库 ---
echo ""
echo "--- 创建比对数据库 ---"
for f in "${pep_files[@]}"; do
    base=$(basename "$f" .pep)
    echo "  处理: $base"
    if [ "$aligner" = "blastp" ]; then
        makeblastdb -in "$f" -dbtype prot
    else
        db_path="$pep_dir/${base}.dmnd"
        if [ ! -f "$db_path" ]; then
            diamond makedb --in "$f" --db "$db_path"
        else
            echo "    数据库已存在: $db_path"
        fi
    fi
done

# --- 两两比对 ---
echo ""
echo "--- 两两比对 ---"
n=${#names[@]}

for ((i=0; i<n; i++)); do
    for ((j=i+1; j<n; j++)); do
        q_name="${names[i]}"
        d_name="${names[j]}"
        q_pep="$pep_dir/${q_name}.pep"
        d_pep="$pep_dir/${d_name}.pep"
        pair_dir="$maps_dir/${q_name}${d_name}"

        mkdir -p "$pair_dir"
        echo ""
        echo "  比对: $q_name <-> $d_name"

        # 正向比对
        out_fwd="$pair_dir/${q_name}_to_${d_name}.txt"
        if [ "$aligner" = "blastp" ]; then
            blastp -query "$q_pep" -db "$d_pep" \
                -outfmt 6 -out "$out_fwd" \
                -num_threads "$threads" \
                -max_hsps 1 -evalue "$evalue"
        else
            diamond_db="$pep_dir/${d_name}.dmnd"
            diamond blastp --query "$q_pep" --db "$diamond_db" \
                --outfmt 6 --out "$out_fwd" \
                --threads "$threads" \
                --max-hsps 1 --evalue "$evalue"
        fi

        # 反向比对
        out_rev="$pair_dir/${d_name}_to_${q_name}.txt"
        if [ "$aligner" = "blastp" ]; then
            blastp -query "$d_pep" -db "$q_pep" \
                -outfmt 6 -out "$out_rev" \
                -num_threads "$threads" \
                -max_hsps 1 -evalue "$evalue"
        else
            diamond_db="$pep_dir/${q_name}.dmnd"
            diamond blastp --query "$d_pep" --db "$diamond_db" \
                --outfmt 6 --out "$out_rev" \
                --threads "$threads" \
                --max-hsps 1 --evalue "$evalue"
        fi

        # 基因ID替换 (可选)
        if [ "$replace_id" = "yes" ]; then
            for fname in "${q_name}_to_${d_name}.txt" "${d_name}_to_${q_name}.txt"; do
                fpath="$pair_dir/$fname"
                if [ -f "$fpath" ]; then
                    # 检查第二行是否包含 '_'
                    second_line=$(awk 'NR==2{print $0}' "$fpath" 2>/dev/null)
                    if echo "$second_line" | grep -q "_"; then
                        echo "    替换基因ID: $fname (_ -> -)"
                        sed -i 's/_/-/g' "$fpath"
                    else
                        echo "    无需替换: $fname"
                    fi
                fi
            done
        fi
    done
done

echo ""
echo "=========================================="
echo "  比对完成!"
echo "  映射表目录: $maps_dir"
echo "=========================================="
