version 1.0
workflow Anno_singler{
  input{
    File input_query_rds
    File? input_query_fa
    String query_cluster_key
    File input_ref_rds
    File? input_ref_fa
    String ref_cluster_key
    String umap_name
    String type='nucleotide' # 'nucleotide' or 'protein'
    Int mem_alignment=8
    Int mem_singler=16
  }
  call alignment{
    input:
    input_ref_rds=input_ref_rds,
    input_ref_fa=select_first([input_ref_fa, input_query_rds]),
    input_query_fa=select_first([input_query_fa, input_query_rds]),
    type=type,
    mem_alignment=mem_alignment,
  }
  call singler{
    input:
    input_query_rds=input_query_rds,
    query_cluster_key=query_cluster_key,
    input_ref_rds=alignment.result,
    ref_cluster_key=ref_cluster_key,
    umap_name=umap_name,
    mem_singler=mem_singler,
  }
  output{
    File result=singler.result
  }
}

task alignment{
  input {
    File input_ref_rds
    File input_ref_fa
    File input_query_fa
    String type
    Int mem_alignment
  }
  command {
    input_ref_rds="~{input_ref_rds}"
    input_ref_fa="~{input_ref_fa}"
    input_query_fa="~{input_query_fa}"
    type="~{type}"
    case "$input_query_fa" in
        *.rds) whether_blast=no  ;;
        *)     whether_blast=yes ;;
    esac
    echo "------ Whether do blast: $whether_blast"
    
    case "$whether_blast" in
      yes)
        echo "---------- Alignemnt..."
        sh /WDL/Alignment/v1.0.0/diamond_blast.sh $input_ref_fa $input_query_fa ~{type} "diamond" 2
        reciprocal_best_txt="reciprocal_best.txt"
        /opt/software/miniconda3/envs/Seurat/bin/Rscript /Annos/Anno-singler/v1.0.0/map2rds.R \
        --input_ref_rds $input_ref_rds --reciprocal_best_txt $reciprocal_best_txt
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
  }
  runtime {
    docker_url: "stereonote_hpc/yangdong_3f318a76639c4101af0f17bd2fbf6f62_private:latest"
    req_cpu: 2
    req_memory: "~{mem_alignment}Gi"
  }
  output {
    File result = glob('*.rds')[0]
  }
}

task singler{
  input {
    File input_query_rds
    String query_cluster_key
    File input_ref_rds
    String ref_cluster_key
    String umap_name
    Int mem_singler
  }
  command {
    mkdir anno_singler
    cd anno_singler
    #!/bin/bash
    input_ref_rds="~{input_ref_rds}"
    input_query_rds="~{input_query_rds}"
    query_cluster_key="~{query_cluster_key}"
    ref_cluster_key="~{ref_cluster_key}"
    umap_name="~{umap_name}"

    echo "--------- Running singler..."
    /software/miniconda/envs/Seurat/bin/Rscript /Annos/Anno-singler/v1.0.0/anno_singler.R \
    --input_ref_rds $input_ref_rds --query_cluster_key $query_cluster_key --input_query_rds $input_query_rds \
    --ref_cluster_key $ref_cluster_key --umap_name $umap_name
  }
  runtime {
    docker_url: "stereonote_hpc/yangdong_70adefe011184f429219920c9910677d_private:latest"
    req_cpu: 4
    req_memory: "~{mem_singler}Gi"
  }
  output {
    File result="anno_singler"
  }
}