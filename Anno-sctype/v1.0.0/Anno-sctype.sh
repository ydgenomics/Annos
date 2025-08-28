input_rds="/data/work/Single-Cell-Pipeline/Anno-sctype/input/NipLSD10_anno_merged_data.rds"
markers_csv="/data/work/Single-Cell-Pipeline/Anno-sctype/input/rice_leaf_marker.csv"
cell_type="leaf"
cluster_key="cell_type"
umap_name="umap"

echo "!!! Plotting marker genes ..."
/software/miniconda/envs/Seurat/bin/Rscript /Annos/Anno-sctype/v1.0.0/plot.R \
--input_rds $input_rds --markers_csv $markers_csv --cell_type $cell_type --cell_type $cell_type --cluster_key $cluster_key
echo "!!! Running sctype do annotation ..."
/software/miniconda/envs/Seurat/bin/Rscript /Annos/Anno-sctype/v1.0.0/anno_sctype.R \
--input_query_rds $input_rds --input_marker_csv $markers_csv \
--tissue $cell_type  --cluster_key $cluster_key --umap_name $umap_name --n_circle 5