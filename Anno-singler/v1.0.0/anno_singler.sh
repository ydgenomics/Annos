#!/bin/bash
cd /data/work/SingleR/test
input_ref_rds="/data/work/SingleR/convert/Sv.hr.rds"
input_ref_fa="/data/input/Files/zhangzijian/cross/pep/Sviridis_500_v2.1.protein1.fa"
input_query_rds="/data/work/SingleR/convert/Os.hr.rds"
input_query_fa="/data/input/Files/zhangzijian/cross/pep/Osativa_323_v7.0.protein1.fa"
ref_cluster_key="celltypes"
umap_name="Xumap_"
whether_blast="yes"
whether_protein="yes"

case "$whether_blast" in
  yes)
    case "$whether_protein" in
      yes)
        echo "-------- Running BLAST on protein FASTA..."
        fasta1="$input_ref_fa"
        fasta2="$input_query_fa"

        source /software/miniconda/bin/activate
        conda info --envs
        conda activate blast
        name1=$(basename "$fasta1")
        diamond makedb --in $fasta1 --db $name1
        name2=$(basename "$fasta2")
        diamond makedb --in $fasta2 --db $name2
        # do blast
        mkdir result
        diamond blastp --db $name2 -q $fasta1 -o "./result/blastp_"$name1"_vs_"$name2".txt"
        diamond blastp --db $name1 -q $fasta2 -o "./result/blastp_"$name2"_vs_"$name1".txt"
        sh /script/reciprocal_result.sh
        reciprocal_best_txt="reciprocal_best.txt"
        /software/miniconda/envs/Seurat/bin/Rscript /script/anno/map2rds.R \
        --input_ref_rds $input_ref_rds --reciprocal_best_txt $reciprocal_best_txt
        ;;
      no)
        echo "--------- Running BLAST on nucleotide FASTA..."
        # 放核酸比对命令
        ;;
      *)
        echo "Error: whether_protein must be 'yes' or 'no'. Got '$whether_protein'"
        exit 1
        ;;
    esac
    ;;
  no)
    echo "---------- Skipping BLAST..."
    cp $input_ref_rds .
    ;;
  *)
    echo "Error: whether_blast must be 'yes' or 'no'. Got '$whether_blast'"
    exit 1
    ;;
esac

input_ref_rds=$(find . -maxdepth 1 -type f -name "*.rds" | head -n 1)
echo $input_ref_rds

echo "--------- Running singler..."
/software/miniconda/envs/Seurat/bin/Rscript /script/anno/anno_singler.R \
--input_ref_rds $input_ref_rds --input_query_rds $input_query_rds \
--ref_cluster_key $ref_cluster_key --umap_name $umap_name