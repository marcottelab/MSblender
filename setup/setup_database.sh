
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
$WORK/msblender/MSblender/pre/fasta-reverse.py $contam_file 

echo "combining contam, reverse and input"
combined_file=${contam_file/.fasta/.combined.fasta}
full_combined_file=`readlink -f $combined_file`
cat $contam_file.* > $combined_file 

echo "Creating pro file"
$WORK/msblender/MSblender/extern/fasta_pro.exe $combined_file 

echo "Creating MSGFPlus db files"
java -Xmx4000M -cp $WORK/msblender/MSblender/extern/MSGFPlus.jar edu.ucsd.msjava.msdbsearch.BuildSA -d $combined_file -tda 0

echo "Changing dir to ../tandemK/"
cd ../tandemK/

echo "Creating tandemK xml files"
$WORK/msblender/MSblender/search/prepare-tandemK-high.py ../mzXML/ ../DB/$combined_file.pro


echo "Changing dir to ../"
cd ../

echo "Updating DB variables in scripts"
sed -i 's|XXX_DB_COMBINED_FASTA_TEMPLATE_XXX|'$full_combined_file'|' ./MSGF+/stampede_MSGF+.sh 
sed -i 's|XXX_DB_COMBINED_FASTA_TEMPLATE_XXX|'$full_combined_file'|' ./comet/stampede_comet.sh
sed -i 's|XXX_DB_COMBINED_FASTA_TEMPLATE_XXX|'$full_combined_file'|' ./run_msblender.sh


