#!/bin/bash

# Directory containing protein files
prot_dir="./SAMap/tmp/pep"
n_threads=40  # 每个BLAST进程使用的线程数，建议改小

# Create an array to hold the base names of the protein files
declare -a names

# Read all pep files from the processed directory
index=0
for file in ${prot_dir}/*.pep; do
  base_name=$(basename $file .pep)  # Extract the base name without extension
  names[$index]=$base_name
  let "index++"
  
  # Create BLAST database with proper output name
  makeblastdb -in $file -dbtype prot -out ${prot_dir}/${base_name}
done

# Function to run blastp for two given sequences
run_blastp() {
  local query=$1
  local db=$2
  local output_dir="./SAMap/tmp/maps/${query}${db}"
  
  mkdir -p ${output_dir}
  
  # Forward BLAST
  blastp -query ${prot_dir}/${query}.pep \
         -db ${prot_dir}/${db} \
         -outfmt 6 \
         -out ${output_dir}/${query}_to_${db}.txt \
         -num_threads ${n_threads} \
         -max_hsps 1 \
         -evalue 1e-6 &

  # Reverse BLAST  
  blastp -query ${prot_dir}/${db}.pep \
         -db ${prot_dir}/${query} \
         -outfmt 6 \
         -out ${output_dir}/${db}_to_${query}.txt \
         -num_threads ${n_threads} \
         -max_hsps 1 \
         -evalue 1e-6 &
  
  # 等待当前对的BLAST完成，控制并发
  wait
}

# Loop through all pairs of names for the two-way BLASTp
total_pairs=$(( ${#names[@]} * (${#names[@]} - 1) / 2 ))
current_pair=0

for (( i=0; i<${#names[@]}; i++ )); do
  for (( j=i+1; j<${#names[@]}; j++ )); do
    ((current_pair++))
    echo "Processing pair ${current_pair}/${total_pairs}: ${names[i]} vs ${names[j]}"
    run_blastp ${names[i]} ${names[j]}
  done
done

echo "All BLAST jobs completed"