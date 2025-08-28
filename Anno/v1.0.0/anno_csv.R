### Date: 250828 anno_csv.R

# Load necessary libraries
suppressPackageStartupMessages({
    library(optparse)
    library(Seurat)
    library(tools) #file_path_sans_ext
    library(ggplot2)
})

# Define command-line options
option_list <- list(
    make_option("--input_rds",
                            type="character",
                            default="/data/work/Single-Cell-Pipeline/output/dataget/peanut_merge/H1314.hr.rds",
                            help="Path to the input rds file. [default: %default]"),
    make_option("--input_csv",
                            type="character",
                            default="/data/work/Single-Cell-Pipeline/Anno/input/anno_H1314.csv",
                            help="Path to the input CSV file. [default: %default]"),
    make_option("--reduction_key",
                            type="character",
                            default="umap",
                            help="The reduction key of single cell data")
)

opt_parser <- OptionParser(option_list = option_list)
opts <- parse_args(opt_parser)
input_rds <- opts$input_rds
input_csv <- opts$input_csv
reduction_key <- opts$reduction_key

# Read the rds file
seurat_obj <- readRDS(input_rds)
print(seurat_obj)

# Read the mapping CSV file (both columns as strings)
mapping_df <- read.csv(input_csv, stringsAsFactors = FALSE)
old_col <- names(mapping_df)[1]
new_col <- names(mapping_df)[2]

# Warn if new annotation column exists; note it will be overwritten.
if(new_col %in% colnames(seurat_obj@meta.data)){
    message(sprintf("Warning: Column '%s' already exists in meta data, it will be overwritten.", new_col))
}

# Print unique values of the old column in the metadata
message(" --- Unique values in the '", old_col, "' column ---")
print(unique(seurat_obj@meta.data[[old_col]]))

# Create a mapping vector: names are old values, elements are new values.
map_dict <- mapping_df[[2]]
names(map_dict) <- mapping_df[[1]]

# Apply mapping to create a new metadata column.
# (Ensure the new values are character strings.)
seurat_obj@meta.data[[new_col]] <- as.character(map_dict[seurat_obj@meta.data[[old_col]]])

# Prepare output filenames
file_name <- basename(input_rds)
base_name <- file_path_sans_ext(file_name)
output_rds <- paste0(base_name, "_anno.rds")
output_pdf <- paste0(base_name, "_anno.pdf")

message("Output rds file: ", output_rds)
saveRDS(seurat_obj, file = output_rds)

# Create UMAP plots colored by the old and new annotation columns.
# Assumes that the UMAP reduction is present as 'umap'
pdf(output_pdf)
DimPlot(seurat_obj, reduction = reduction_key, group.by = old_col, label = TRUE) + ggtitle(old_col)
DimPlot(seurat_obj, reduction = reduction_key, group.by = new_col, label = TRUE) + ggtitle(new_col)
dev.off()