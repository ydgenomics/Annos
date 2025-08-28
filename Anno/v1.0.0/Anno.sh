input_file=$1
input_csv=$2
reduction_key=$3

ext="${input_file##*.}"
echo "input file extension is: $ext"
if [ "$ext" == "h5ad" ]; then
    echo "Annotating .h5ad file ..."
    /opt/conda/bin/python /Annos/Anno/v1.0.0/anno_csv.py \
    --input_h5ad $input_file --input_csv $input_csv --reduction_key $reduction_key
elif [ "$ext" == "rds" ]; then
    echo "Annotating .rds file ..."
    /opt/conda/bin/Rscript /Annos/Anno/v1.0.0/anno_csv.R \
    --input_rds $input_file --input_csv $input_csv --reduction_key $reduction_key
else
    echo "Error: Unsupported ext "$ext". Only '.h5ad' and '.rds' are supported."
fi