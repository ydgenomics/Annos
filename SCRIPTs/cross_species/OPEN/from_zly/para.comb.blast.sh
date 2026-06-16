#combining multiple combination of reciprical blast


while (($#>0))
do
first=$2
firstname=${first%.*}
i=3
while ((i<=$#))
do
second=${!i}
secondname=${second%.*}
sh /Script/map_genes.sh \
--tr1 $first \
--t1 prot \
--n1 $firstname \
--tr2 $second \
--t2 prot \
--n2 $secondname

Rscript /Script/GeneidConverter.R \
-i maps/"$firstname""$secondname"/"$firstname"_to_"$secondname".txt \
-j maps/"$firstname""$secondname"/"$secondname"_to_"$firstname".txt \
-a $firstname \
-b $secondname

if [[ "$1" == "TRUE" ]]
then
  result1=$(awk -F'\t' 'NR==2{print $1}' "$firstname"_to_"$secondname".txt|grep "_")
  result2=$(awk -F'\t' 'NR==2{print $2}' "$firstname"_to_"$secondname".txt|grep "_")
  if [[ "$result1" != "" ]] || [[ "$result2" != "" ]]
  then
    sed -i 's/_/-/g' *.txt
  fi
fi



cp "$firstname"_to_"$secondname".txt maps/"$firstname""$secondname"/
cp "$secondname"_to_"$firstname".txt maps/"$firstname""$secondname"/
echo $first
echo $second
let i++
done
shift
done

