
echo "combining contam.fasta and input fasta"
if [[ $1 == *".fasta" ]]
then
	echo "fasta ext"
	contam_file=${1/.fasta/_contam.fasta} 
elif [[ $1 == *".fa" ]]
then
	echo "fa ext"
	contam_file=${1/.fa/_contam.fasta} 
else
	echo "input fasta should have .fa or .fasta extension"
	exit
fi

echo "input and contam fasta filename: $contam_file"

cat contam.fasta $1 > $contam_file

echo "building reverse fasta"
$WORK/MSblender/msblender-scripts/fasta-reverse.py $contam_file 

echo "combining contam, reverse and input"
combined_file=${contam_file/.fasta/.combined.fasta}
full_combined_file=`readlink -f $combined_file`
cat $contam_file.* > $combined_file 

