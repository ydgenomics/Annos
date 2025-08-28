# ---------------------------- Old way: blastp ------------------------------
# # input
# fasta1="/data/work/0.peanut/GRN/cotton_blast/TM-1_V2.1.gene.pep.fa"
# fasta2="/data/work/0.peanut/GRN/cotton_blast/Ghirsutum_gene_peptide_trimmed.fasta"
# n_cpu=8

# # make database
# name1=$(basename "$fasta1")
# makeblastdb -in $fasta1 -dbtype prot -out $name1
# name2=$(basename "$fasta2")
# makeblastdb -in $fasta2 -dbtype prot -out $name2

# # do blast
# mkdir result
# blastp -query $fasta1 -db $name2 -out "./result/blastp_results_$name1.txt" -outfmt 6 -evalue 1e-5 -num_threads $n_cpu
# blastp -query $fasta2 -db $name1 -out "./result/blastp_results_$name2.txt" -outfmt 6 -evalue 1e-5 -num_threads $n_cpu

# # get reciprocal result
# echo -e "Query_ID\tRefer_ID\tIdentity(%)\tAlignment_Length\tMismatches\tGap_Openings\tQ_Start\tQ_End\tS_Start\tS_End\tE-value\tBit_Score" > header.tsv
# n=0
# for i in $(ls */*.txt)
# do 
#   cat header.tsv $i > "$n".txt
#   awk -F '\t' '$3 >= 70' "$n".txt > "$n"_filter.txt
#   awk '!seen[$1]++' "$n"_filter.txt > "$n"_unique.tsv
#   let n++
# done

# awk 'NR==FNR{a[$2"_"$1]=$1}NR!=FNR{if(a[$1"_"$2])print $1"\t"a[$1"_"$2]}' 0_unique.tsv 1_unique.tsv > reciprocal_best.txt

# ---------------------------- New way: diamond blastp ------------------------------
# [DIAMOND:快又准的蛋白序列比对软件](https://mp.weixin.qq.com/s/5UhthY9PHfN7zxZbJdZaJA)
# get reciprocal result
echo -e "Query_ID\tRefer_ID\tIdentity(%)\tAlignment_Length\tMismatches\tGap_Openings\tQ_Start\tQ_End\tS_Start\tS_End\tE-value\tBit_Score" > header.tsv
n=0
for i in $(ls */*.txt)
do 
  cat header.tsv $i > "$n".txt
  awk -F '\t' '$3 >= 70' "$n".txt > "$n"_filter.txt
  awk '!seen[$1]++' "$n"_filter.txt > "$n"_unique.tsv
  let n++
done

awk 'NR==FNR{a[$2"_"$1]=$1}NR!=FNR{if(a[$1"_"$2])print $1"\t"a[$1"_"$2]}' 0_unique.tsv 1_unique.tsv > reciprocal_best.txt