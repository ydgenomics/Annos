version 1.0
workflow Anno_sctype{
  input{
    Array[File] input_query_rds
    Array[String] assay_key
    Array[File] input_marker_csv
    Array[String] prefix
    Array[String] tissue
    Array[String] cluster_key
    Array[String] reduction_key
    Int mem_sctype=8
  }
  Int jobn=length(input_query_rds)
  scatter(index in range(jobn)){
    call sctype{
      input:
      input_query_rds=input_query_rds[index],
      assay_key=assay_key[index],
      input_marker_csv=input_marker_csv[index],
      prefix=prefix[index],
      tissue=tissue[index],
      cluster_key=cluster_key[index],
      reduction_key=reduction_key[index],
      mem=mem_sctype,
    }
  }
  output{
    Array[File] result=sctype.result
  }
}

task sctype{
  input {
    File input_query_rds
    String assay_key
    File input_marker_csv
    String prefix
    String tissue
    String cluster_key
    String reduction_key
    Int mem
  }
  command {
    mkdir ~{prefix}
    cd ~{prefix}
    
    input_rds="~{input_query_rds}"
    markers_csv="~{input_marker_csv}"
    cell_type="~{tissue}"
    cluster_key="~{cluster_key}"
    umap_name="~{reduction_key}"

    echo "!!! Plotting marker genes ..."
    /software/miniconda/envs/Seurat/bin/Rscript /Annos/Anno-sctype/v1.0.0/plot.R \
    --input_rds $input_rds --markers_csv $markers_csv --cell_type $cell_type --cell_type $cell_type --cluster_key $cluster_key
    echo "!!! Running sctype do annotation ..."
    /software/miniconda/envs/Seurat/bin/Rscript /Annos/Anno-sctype/v1.0.0/anno_sctype.R \
    --input_query_rds $input_rds --input_marker_csv $markers_csv --assay_key ~{assay_key} \
    --tissue $cell_type  --cluster_key $cluster_key --umap_name $umap_name --n_circle 5
  }
  runtime {
    docker_url: "public-library/yangdong_70adefe011184f429219920c9910677d_public:latest"
    req_cpu: 2
    req_memory: "~{mem}Gi"
  }
  output {
    File result="~{prefix}"
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

task samap{
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
