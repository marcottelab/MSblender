#!/bin/bash

PROG='runMS2_fixed.sh';
__RUNMS2_VERSION__="v.2021_04_15"

# ============================================================================
# Command Line Arguments
# ============================================================================
IN_MZXML=$1
FASTAFILE=$2
WORKDIR=$3
OUTPUTDIR=$4
SEARCHGUIDIR=$5

usage() {
  echo "--------------------------------------------------------------------------"
  echo "$PROG $__RUNMS2_VERSION__"
  echo "--------------------------------------------------------------------------"
  echo ""
  exit 1
}
if [[ "$SEARCHGUIDIR" == "" ]]; then usage; fi

# ============================================================================
# Automatic Logging
# ============================================================================
OUT_PFX=${IN_MZXML##*/}
OUT_PFX=${OUT_PFX%.mzXML}
echo "Output prefix: $OUT_PFX"

# Direct our STDERR and STDOUT to log file
LOG_TAG='runMS2'
show_only=${show_only:-0}
if [[ "$show_only" == "0" ]]; then
  exec 1> >(tee ./$OUT_PFX.$LOG_TAG.log) 2>&1
  echo "Logging to ./$OUT_PFX.$LOG_TAG.log - `date`"
fi

# ============================================================================
# Common Functions
# From __CBB_COMMON_FUNCTIONS_VERSION__="v.2021_03_17"
# ============================================================================
# Shorter format date
date2()   { date '+%Y-%m-%d %H:%M:%S'; }
dateStr() { date '+%Y-%m-%d.%H:%M:%S'; }
# Echo arguments to std error (no date)
echo_se0() { echo -e "$@" 1>&2; }
maybe_echo0() {
  local do_echo=${ECHO_VERBOSE:-1}
  if [[ "$do_echo" == "1" ]]; then echo_se0 "$@"; fi
}
# Echo to std error followed by the date
echo_se() { echo_se0 "$@ - `date2`"; }
# Echo to std error after '@@ ' (so can be easily grep'd)
maybe_echo() { maybe_echo0 "$@ - `date2`"; }
# Echo to std error after a token that can be easily grep'd (e.g. '@@ ', '# ')
echo_ex0() { echo_se0 "@@  $@"; }
echo_ex()  { echo_se  "@@  $@"; }
maybe_echo_ex() { maybe_echo "@@  $@"; }
section() {
  echo_se0 "==============================================================================="
  echo_se0 "## $@ - `date2`"
  echo_se0 "==============================================================================="
}
section2() {
  echo_se0 "-------------------------------------------------------------------------"
  echo_se0 "# $@ - `date2`"
  echo_se0 "-------------------------------------------------------------------------"
}
function_usage() { echo_se0 "$@"; exit 1; }
function_info() {
  local str
  echo_se0 "==============================================================================="
  echo_ex  "$1"; shift;
  for str in "$@"; do echo_se0 " *  $str"; done
  echo_se0 "==============================================================================="
}
# General function that exits after printing its text argument
#   in a standard format which can be easily grep'd.
err() { echo_se "** ERROR: $@ ...exiting"; exit 255; }
# Checks the return code of programs.
# Exits with standard message if code is non-zero.
# Otherwise displays completiong message and date.
#   arg 1 - the return code (usually $?)
#   arg 2 - text describing what ran
check_return_code() {
  local code=$1; shift
  if [[ $code == 0 ]]; then maybe_echo "..Done $@"
  else err "$@ returned non-0 exit code $code"; fi
}
# Checks if a file exists
#   arg 1 - the file name
#   arg 2 - text describing the file (optional)
check_file() {
  local val="$1"; shift
  if [[ ! -f "$val" ]]; then err "$@ File '$val' not found"
  else maybe_echo "..$@ file '$val' exists"; fi
}
# Checks if a file exists & has non-0 length, else exits.
#   arg 1 - the file name
#   arg 2 - text describing the file (optional)
check_file_not_empty() {
  local val="$1"; shift
  if [[ ! -f "$val" ]]; then err "$@ File '$val' not found"
  elif [[ ! -s "$val" ]]; then err "$@ File '$val' is empty"
  else maybe_echo ".. $@ file '$val' exists and is not empty"; fi
}
# Checks if a directory exists and exits if not.
#   arg 1 - the directory name
#   arg 2 - text describing the directory (optional)
check_dir() {
  local val="$1"; shift
  if [[ ! -d "$val" ]]; then err "$@ Directory '$val' not found"
  else maybe_echo "..$@ directory '$val' exists"; fi
}
# Changes to the specified directory (arg 1)
change_dir() {
  local dirpath="$1"
  local dir_info=${2:-"change_dir"}
  dirpath=$( echo "$dirpath" | sed 's/[/]$//' )
  local path="`realpath $dirpath`"
  check_dir "$path" "$dir_info"
  cd "$path/"  # trailing slash needed if symlink
  if [[ "$PWD" != "$path" ]]; then
    err "Could not change into directory '$dirpath' ($path)"
  else maybe_echo "..cd $dirpath OK"; fi
}
# Checks whether show_only mode is in effect (show_only == 1) and exits if so.
check_show_only() { if [[ "$show_only" == "1" ]]; then err "show_only"; fi }
# Function that checks whether the spcified program can be found
check_program() {
  local prog="$1"
  local prog_path=$(command -v "$prog")
  if [[ "$prog_path" == "" ]]; then
    err "program '$prog' not found"
  else maybe_echo "..program '$prog' ok"; fi
}
# Checks that its 1st argument is not empty
#   arg 1 - the value
#   arg 2 - name of the value
#   arg 3 - text describing the value (optional)
check_value_not_empty() {
  local val="$1"; local name="$2";
  local info=${3:-"Value '$name' is empty"}
  if [[ "$val" == "" ]]; then err "$info"
  else maybe_echo "..var '$name' OK (not empty)"; fi
}
# Checks whether the two values supplied are equal (as strings)
#   arg 1 - 1st value
#   arg 2 - 2nd value
#   arg 3 - text describing 1st value (optional)
#   arg 4 - text describing 2nd value (optional)
check_equal() {
  local val1="$1"; local val2="$2";
  local tag1=${3:-'check_equal'}
  local tag2=${4:-'check_equal'}
  if [[ "$1" == "$2" ]]; then maybe_echo "..$tag1 '$val1' OK"
  else
    err "$tag2:
    expected '$val1'
    got      '$val2'
   "; fi
}

# ============================================================================
# Environment Setup and Defaulting
# ============================================================================
module load gsl # For TACC (needed by msblender binary)

IN_MZXML=`realpath $IN_MZXML`
FASTAFILE=`realpath $FASTAFILE`
WORKDIR=`realpath $WORKDIR`
OUTPUTDIR=`realpath $OUTPUTDIR`
SEARCHGUIDIR=`realpath $SEARCHGUIDIR`

OUT_PFX2=`basename $IN_MZXML`
OUT_PFX2=${OUT_PFX2%.mzXML}

# Get the MSblender code directory
this_script_loc="$(readlink -f ${BASH_SOURCE[0]})"
PIPELINEDIR="$(dirname $this_script_loc)"
PIPELINEDIR=`realpath $PIPELINEDIR`
MSBLENDER_BIN=$PIPELINEDIR/src/msblender

MZXMLDIR=$(dirname "$IN_MZXML")
TMP_DIR="$WORKDIR/$OUT_PFX.temp"
TANDEMDIR=$WORKDIR/${OUT_PFX}_tandem

DBNAME=${FASTAFILE/.fasta/}
DBNAME=${DBNAME##*/}

COMETOUT=${OUT_PFX}"."$DBNAME".comet"
COMETPARAM="${PIPELINEDIR}/params/comet.params.new"
COMETEXE="${PIPELINEDIR}/exe/comet.linux.exe"

# Create MS-GF+ parameter string.
MSGFplus_MODFILE="${PIPELINEDIR}/params/MSGFplus_mods.txt"
if [[ ! -f "$MSGFplus_MODFILE" ]]; then
  MSGFp_note='(default static C+57 and no optional modifications)'
  MSGFplus_MODPARAM=""
else
  MSGFplus_MODPARAM="-mod $MSGFplus_MODFILE"
  MSGFp_note=''
fi
MSGFplus_JAR="$SEARCHGUIDIR/resources/MS-GF+/MSGFPlus.jar"
MSGFplus_PARAMFILE="${PIPELINEDIR}/params/MSGFplus_params.txt"
MSGFOUT=$WORKDIR/${OUT_PFX}.MSGF+

XTANDEMEXE="${PIPELINEDIR}/extern/tandem.linux.exe"

# ============================================================================
# Display Computed Parameters (before error checking)
# ============================================================================
function_info "$PROG $__RUNMS2_VERSION__" \
  "Output prefix:  $OUT_PFX" \
  "Real out pfx:   $OUT_PFX2" \
  "mzXML file:     $IN_MZXML" \
  "mzXML dir:      $MZXMLDIR" \
  "DB fasta:       $FASTAFILE" \
  "DB name:        $DBNAME" \
  "Working dir:    $WORKDIR" \
  "Temp dir:       $TMP_DIR" \
  "Output dir:     $OUTPUTDIR" \
  "Search GUI:     $SEARCHGUIDIR" \
  "MSblender dir:  $PIPELINEDIR" \
  "MSblender:      $MSBLENDER_BIN" \
  "Tandem dir:     $TANDEMDIR" \
  "Comet:          $COMETEXE" \
  "Comet out:      $COMETOUT" \
  "Comet params:   $COMETPARAM" \
  "MSGF+ jar:      $MSGFplus_JAR" \
  "MSGF+ modfile:  $MSGFplus_MODFILE" \
  "MSGF+ modparam: '$MSGFplus_MODPARAM' $MSGFp_note"\
  "MSGF+ parmfile: $MSGFplus_PARAMFILE" \
  "MSGF+ outfile:  $MSGFOUT" \
  "XTandem:        $XTANDEMEXE"

# ============================================================================
# Initial Error Checking
# ============================================================================
check_file $IN_MZXML  "Input mzXML"
check_file $FASTAFILE "Protein DB fasta"

mkdir -p $WORKDIR;   mkdir -p $TMP_DIR;
mkdir -p $TANDEMDIR; mkdir -p $OUTPUTDIR;
check_dir $OUTPUTDIR    "Output"
check_dir $WORKDIR      "Working"
check_dir $TMP_DIR      "Temporary"
check_dir $TANDEMDIR    "XTandem"
check_dir $SEARCHGUIDIR "Search GUI"
check_dir $MZXMLDIR     "mzXML"
check_dir $PIPELINEDIR  "MSblender"

check_program $MSBLENDER_BIN      "msblender binary"
check_program $COMETEXE           "comet binary"
check_program $XTANDEMEXE         "xtamdem binary"
check_file    $MSGFplus_JAR       "msgf+ jar"
check_file    $MSGFplus_MODFILE   "msgf+ mods"
check_file    $MSGFplus_PARAMFILE "msgf params"
check_file    $COMETPARAM         "comet params"

change_dir $TMP_DIR "Temporary working"
check_show_only

# ============================================================================
# Do The Real Work
# ============================================================================

# -- Comet ------------------------------------
section "Running Comet"
$COMETEXE -p
$COMETEXE -P$COMETPARAM -D${FASTAFILE} -N$COMETOUT $IN_MZXML
check_return_code $? "Comet search"
check_file_not_empty $COMETOUT.pep.xml "Comet peptides"
mv $COMETOUT.pep.xml $WORKDIR/${OUT_PFX}..comet.pep.xml
check_file_not_empty $WORKDIR/${OUT_PFX}..comet.pep.xml "renamed Comet peptides"

# -- Xtandem ------------------------------------
section "Running XTandem"
echo_ex "Preparing run-tandemK.sh script.."
python $PIPELINEDIR/msblender-scripts/prepare-tandemK-high.py \
  $IN_MZXML $FASTAFILE $TANDEMDIR $XTANDEMEXE
check_return_code $? "prepare-tandemK-high.py"
check_file_not_empty $TANDEMDIR/run-tandemK.sh "run-tandemK.sh"

echo_ex "Running run-tandemK.sh"
bash $TANDEMDIR/run-tandemK.sh
check_return_code $? "run-tandemK.sh"
check_file_not_empty $TANDEMDIR/$OUT_PFX2.$DBNAME.tandemK.out 'XTandem out'
check_file_not_empty $TANDEMDIR/$OUT_PFX2.$DBNAME.tandemK.xml 'XTandem xml'

cp $TANDEMDIR/${OUT_PFX2}.${DBNAME}.tandemK.out $WORKDIR/${OUT_PFX}.tandemK.out #hacky but I don't know how else to fix the naming issue
cp $TANDEMDIR/${OUT_PFX2}.${DBNAME}.tandemK.xml $WORKDIR/${OUT_PFX}.tandemK.xml
check_file_not_empty $WORKDIR/${OUT_PFX}.tandemK.out 'renamed XTandem out'
check_file_not_empty $WORKDIR/${OUT_PFX}.tandemK.xml 'renamed XTandem xml'

# -- MS-GF+ ------------------------------------
section "Running MS-GF+"
echo_ex "Read/parse MS-GF+ param file. Append modification file parameter."
MSGFplus_PARAMSTR=$(grep -v "#" "$MSGFplus_PARAMFILE" | tr -s '\n\r' ' ')"$MSGFplus_MODPARAM"
echo_se "MSGF+ parameters: '$MSGFplus_PARAMSTR'"

echo_ex "Executing MSGF+ jar (note: java ParseError may occur)"
java -Xmx20000M -jar $MSGFplus_JAR -d $FASTAFILE -s $IN_MZXML \
  -o ${MSGFOUT}.mzid -tda 0 $MSGFplus_PARAMSTR
check_return_code $? "java `basename $MSGFplus_JAR`"
check_file_not_empty ${MSGFOUT}.mzid "MSGF+ mzid"

echo_se "Running MSGF+ MzIDToTsv"
TBL=${MSGFOUT/.mzid}.tsv
java -Xmx20000M -cp $MSGFplus_JAR edu.ucsd.msjava.ui.MzIDToTsv -i ${MSGFOUT}.mzid \
  -o $TBL -showQValue 1 -showDecoy 1 -unroll 0
check_return_code $? "MSGF+ MzIDToTsv"
check_file_not_empty $TBL "MSGF+ tsv"

# -- Hit lists ------------------------------------
section "Creating hit lists"
echo_ex "Running comet_pepxml-to-xcorr_hit_list.py"
check_file_not_empty $WORKDIR/${OUT_PFX}..comet.pep.xml "Comet pep.xml"
python $PIPELINEDIR/msblender-scripts/comet_pepxml-to-xcorr_hit_list.py \
  $WORKDIR/${OUT_PFX}..comet.pep.xml
check_return_code $? "comet_pepxml-to-xcorr_hit_list.py"
check_file_not_empty \
  $WORKDIR/${OUT_PFX}..comet.pep.xml.xcorr_hit_list 'Comet xcorr hits'

echo_ex "Running tandem_out-to-logE_hit_list.py"
check_file_not_empty $WORKDIR/${OUT_PFX}.tandemK.out "XTandem out"
python $PIPELINEDIR/msblender-scripts/tandem_out-to-logE_hit_list.py \
  $WORKDIR/${OUT_PFX}.tandemK.out
check_return_code $? "tandem_out-to-logE_hit_list.py"
check_file_not_empty \
  $WORKDIR/${OUT_PFX}.tandemK.out.logE_hit_list 'XTandem logE hits'

echo_ex "Running MSGF+_tsv-to-logSpecE_hit_list.py"
check_file_not_empty ${MSGFOUT}.tsv 'MSGF+ tsv'
python $PIPELINEDIR/msblender-scripts/MSGF+_tsv-to-logSpecE_hit_list.py \
  ${MSGFOUT}.tsv
check_return_code $? "MSGF+_tsv-to-logSpecE_hit_list.py"
check_file_not_empty \
  ${MSGFOUT}.tsv.logSpecE_hit_list 'MS-GF logSpecE hits'

# -- Best hits ------------------------------------
section "Selecting best hits"
echo_ex "Running select-best-psm.py on comet"
python $PIPELINEDIR/msblender-scripts/select-best-PSM.py \
  $WORKDIR/${OUT_PFX}..comet.pep.xml.xcorr_hit_list
check_return_code $? "select-best-PSM.py comet"
check_file_not_empty \
  $WORKDIR/${OUT_PFX}..comet.pep.xml.xcorr_hit_list_best 'Comet best hits'

echo_ex "Running select-best-psm.py on tandemK"
python $PIPELINEDIR/msblender-scripts/select-best-PSM.py \
  $WORKDIR/${OUT_PFX}.tandemK.out.logE_hit_list
check_return_code $? "select-best-PSM.py tandemK"
check_file_not_empty \
  $WORKDIR/${OUT_PFX}.tandemK.out.logE_hit_list_best 'XTandem best hits'

echo_ex "Running select-best-psm.py on msgf+"
python $PIPELINEDIR/msblender-scripts/select-best-PSM.py \
  ${MSGFOUT}.tsv.logSpecE_hit_list
check_return_code $? "select-best-PSM.py msgf+"
check_file_not_empty \
  ${MSGFOUT}.tsv.logSpecE_hit_list_best 'MSGF+ best hits'

echo comet      $WORKDIR/${OUT_PFX}..comet.pep.xml.xcorr_hit_list_best >  ${OUT_PFX}.conf
echo MSGF+      ${MSGFOUT}.tsv.logSpecE_hit_list_best                  >> ${OUT_PFX}.conf
echo 'X!Tandem' $WORKDIR/${OUT_PFX}.tandemK.out.logE_hit_list_best     >> ${OUT_PFX}.conf
nLine=`cat ${OUT_PFX}.conf | wc -l`
check_equal "$nLine" "3" "${OUT_PFX}.conf lines" "expected #lines"

echo_ex "Showing top hit statistics"
cat ${OUT_PFX}.conf | awk '{print $2}' | xargs wc -l

# -- MSblender ------------------------------------
section "Running MSblender"
echo_ex "Running make-msblender_in.py to make msblender conf file"
python $PIPELINEDIR/msblender-scripts/make-msblender_in.py ${OUT_PFX}.conf
check_return_code $? "make-msblender_in.py"
check_file_not_empty ${OUT_PFX}.msblender_in "MSblender conf"

echo_ex "Running msblender using conf file"
$MSBLENDER_BIN ${OUT_PFX}.msblender_in
check_return_code $? "msblender"
check_file_not_empty ${OUT_PFX}.msblender_in.msblender_out "MSblender out"

echo_ex "Running filter-msblender.py"
python $PIPELINEDIR/msblender-scripts/filter-msblender.py \
  ${OUT_PFX}.msblender_in.msblender_out 001 > ${OUT_PFX}.msblender.filter
check_return_code $? "filter-msblender.py"
check_file_not_empty ${OUT_PFX}.msblender.filter "MSblender filtered"

echo_ex "Running msblender_out-to-pep_count-FDRpsm.py"
python $PIPELINEDIR/msblender-scripts/msblender_out-to-pep_count-FDRpsm.py \
  ${OUT_PFX}.msblender_in.msblender_out 0.01 mFDRpsm
check_return_code $? "msblender_out-to-pep_count-FDRpsm.py"
check_file_not_empty ${OUT_PFX}.pep_count_mFDRpsm001     "peptides FDRpsm"
check_file_not_empty ${OUT_PFX}.pep_count_mFDRpsm001.log "peptides FDRpsm log"

echo_ex "Running pep_count_with_fasta-to-prot_count.py"
python $PIPELINEDIR/msblender-scripts/pep_count_with_fasta-to-prot_count.py \
  ${OUT_PFX}.pep_count_mFDRpsm001 $FASTAFILE
check_return_code $? "pep_count_with_fasta-to-prot_count.py"
check_file_not_empty ${OUT_PFX}.prot_count_mFDRpsm001       "proteins FDRpsm"
check_file_not_empty ${OUT_PFX}.prot_count_mFDRpsm001.log   "proteins FDRpsm log"
check_file_not_empty ${OUT_PFX}.prot_count_mFDRpsm001.group "proteins FDRpsm group"
check_file_not_empty ${OUT_PFX}.prot_list                   "proteins list"

# ============================================================================
# Clean up and Declare Victory
# ============================================================================
# Rename remaining files in temporary directory
# These go to output dir
mv ${OUT_PFX}.pep_count_mFDRpsm001        $OUTPUTDIR/
mv ${OUT_PFX}.pep_count_mFDRpsm001.log    $OUTPUTDIR/
mv ${OUT_PFX}.prot_count_mFDRpsm001       $OUTPUTDIR/
mv ${OUT_PFX}.prot_count_mFDRpsm001.group $OUTPUTDIR/
mv ${OUT_PFX}.prot_count_mFDRpsm001.log   $OUTPUTDIR/
mv ${OUT_PFX}.prot_list                   $OUTPUTDIR/
# Everything else to working
mv ${OUT_PFX}.*                           $WORKDIR/

section "All $PROG $OUT_PFX tasks completed successfully!"
exit 0

