#!/bin/bash

PROG='runMSblender.sh'
__RUNMSB_VERSION__="v.2021_05_09"

# ============================================================================
# Command Line Arguments
# ============================================================================
IN_MZXML=$1
FASTAFILE=$2
WORKDIR=$3
OUTPUTDIR=$4
SEARCHGUIDIR=$5
MIN_ENGINES=${6:-${MIN_ENGINES:-2}} # Allow setting as ENV var "MIN_ENGINES"

usage() { echo \
"--------------------------------------------------------------------------
$PROG $__RUNMSB_VERSION__
--------------------------------------------------------------------------
Usage: $PROG mzXML DBfasta [workdir outdir searchGUI minEngines(2)]
  mzXML      (required) MS spectra input file in mzXML format.
  DBfasta    (required) Search database fasta file
                        (i.e., a collapsed_contam.combined fasta file)
  workdir    (optional) Directory for execution log files.
                        Defaults to a 'working' sub-directory at the
                        same level as the mzXML file mzXML directory.
  outdir     (optional) Directory for final output files.
                        Defaults to a 'working' sub-directory at the
                        same level as the mzXML file mzXML directory.
  searchGUI  (optional) Path to the SearchGUI directory. Defaults based
                        on run environment when POD or TACC.
  minEngines (optional) Minimum number of search engines that must succeed.
                        Must be 2 or 3. Default 2.
"; exit 1
}
if [[ "$FASTAFILE" == "" || "$IN_MZXML" == "" ]]; then usage; fi

# ============================================================================
# Automatic Logging
# ============================================================================
OUT_PFX=${IN_MZXML##*/}
OUT_PFX=${OUT_PFX%.mzXML}
echo "Output prefix: $OUT_PFX"

# Direct our STDERR and STDOUT to log file
LOG_TAG='runMSblender'
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
# Shorter format dates
date2()    { date '+%Y-%m-%d %H:%M:%S'; }
dateStr()  { date '+%Y-%m-%d.%H_%M_%S'; }
dateOnly() { date '+%Y_%m_%d'; }
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
# Optionally reports status info when FAILURE_INFO is 1
err() {
  if [[ "$FAILURE_INFO" == "1" ]]; then report_status_info "FAILURE"; fi
  echo_se "** ERROR: $@ ...exiting"; exit 255;
}
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
# Checks that its 1st argument is an integer
#   arg 1 - (required) the value
#   arg 2 - name of the value (optional)
#   arg 3 - text describing the value (optional)
check_integer() {
  local val="$1"; local name="$2"; shift; shift;
  local info=${@:-"Value $name ($val) is not an integer"}
  local res=$( echo "$val" | grep -P '^[-]?\d+$' )
  if [[ "$res" == "" ]]; then err "$info"
  else maybe_echo "..var '$name' $val OK (is an integer)"; fi
}
# Checks that its 1st argument is an integer of the specified type
#   arg 1 - the value to check (required)
#   arg 2 - the type (optional); One of:
#           pos (default), neg, nonneg, or another integer value
#   arg 3 - name of the value (optional)
#   arg 4 - text describing the value (optional)
check_integer_type() {
  local val="$1"; local int_type=${2:-'pos'}
  local name="$3"; shift; shift; shift;
  local info="$@"
  local res=$( echo "$val" | grep -P '^[-]?\d+$' )
  if [[ "$res" == "" ]]; then err "Value $name ($val) is not an integer"; fi
  case "$int_type" in
  pos) if [[ $val -gt 0 ]]; then
         maybe_echo "..var '$name' $val OK (is a positive integer)"
       else
         info=${info:-"Value $name ($val) is not a positive integer"}
         err "$info"
       fi
    ;;
  neg) if [[ $val -lt 0 ]]; then
         maybe_echo "..var '$name' $val OK (is a negative integer)"
       else
         info=${info:-"Value $name ($val) is not a negative integer"}
         err "$info"
       fi
    ;;
  nonneg) if [[ $val -ge 0 ]]; then
            maybe_echo "..var '$name' $val OK (is a non-negative integer)"
          else
            info=${info:-"Value $name ($val) is not a non-negative integer"}
            err "$info"
          fi
    ;;
  *) local int_val=$( echo "$int_type" | grep -P '^[-]?\d+$' )
     if [[ "$int_val" == "" ]]; then
       err "Expected integer type '$int_type' is not one of (pos neg nonneg) or an integer"
     elif [[ $val -eq $int_val ]]; then
       maybe_echo "..var '$name' value $val is correct"
     else
       info=${info:-"Value $name ($val) is not equal to $int_val"}
       err "$info"
     fi
    ;;
  esac
}

# Function that determines what environment we are running in:
#   POD (1), TACC (3/4) or Other (0).
# Sets the ENV_TYPE, ENV_TAG and ENV_NUM environment variables,
#   echos the three values to standard output,
#   and returns the ENV_NUM number as its return code.
check_run_env() {
  ENV_NUM=0; ENV_TYPE='Other'; ENV_HOST='';
  if [[ "$TACC_SYSTEM" == "ls5" ]];         then ENV_NUM="3"; ENV_TYPE='TACC'; ENV_TAG='ls5'
  elif [[ "$TACC_SYSTEM" == "stampede2" ]]; then ENV_NUM="4"; ENV_TYPE='TACC'; ENV_TAG='stampede2'
  else
    ENV_TAG=`hostname | sed 's/[.].*//'`
    if [[ `hostname | grep '[.]ccbb[.]utexas[.]edu'` != "" ]]; then
      ENV_NUM=1; ENV_TYPE='POD'
    fi
  fi
  RUN_ENV="$ENV_TYPE $ENV_TAG $ENV_NUM"
  echo "$RUN_ENV"
  return $ENV_NUM
}

# ============================================================================
# Environment Setup and Defaulting
# ============================================================================
# Make sure pipes return an error code when a non-terminal command errors
# Careful, though. This means, for example, that head -1000 will generate
#   an error when the input has fewer than 1000 lines.
set -o pipefail
shopt -s nullglob   # have globs expand to nothing when they don't match

check_run_env
if [[ "$ENV_TYPE" == "TACC" ]]; then
  module load gsl # needed by msblender binary
fi

IN_MZXML0=$IN_MZXML; FASTAFILE0=$FASTAFILE
IN_MZXML=`realpath $IN_MZXML`
FASTAFILE=`realpath $FASTAFILE`

# Default working and output to same level as mzXML if not provided
WORKDIR0=$WORKDIR; OUTPUTDIR0=$OUTPUTDIR
if [[ "$WORKDIR" != "" ]]; then
  WORKDIR=`realpath $WORKDIR`
else
  tmp=`dirname $IN_MZXML0 | perl -pe '~s|/mzXML.*||' `
  WORKDIR=`realpath $tmp/working`
fi
TMP_DIR="$WORKDIR/$OUT_PFX.temp"
if [[ "$OUTPUTDIR" != "" ]]; then
  OUTPUTDIR=`realpath $OUTPUTDIR`
else
  tmp=`dirname $IN_MZXML0 | perl -pe '~s|/mzXML.*||' `
  OUTPUTDIR=`realpath $tmp/output`
fi
# Default Search GUI depending on environment
SEARCHGUIDIR0=$SEARCHGUIDIR
if [[ "$SEARCHGUIDIR" == "" ]]; then
  SEARCHGUIDIR='Unknown'
  if [[ "$ENV_TYPE" == "TACC" ]]; then
    SEARCHGUIDIR=/work/projects/BioITeam/common/opt/SearchGUI-3.3.5
  elif [[ `echo "$ENV_TAG" | grep -P '^(marc|hfog)'` != "" ]]; then
    SEARCHGUIDIR=/project/Software/SearchGUI-3.3.5
  fi
fi
# In case original IN_MZXML was a symlink...
OUT_PFX2=`basename $IN_MZXML`
OUT_PFX2=${OUT_PFX2%%.mzXML}

# Get the MSblender code directory
this_script_loc="$(readlink -f ${BASH_SOURCE[0]})"
PIPELINEDIR="$(dirname $this_script_loc)"
PIPELINEDIR=`realpath $PIPELINEDIR`
MSBLENDER_BIN=$PIPELINEDIR/src/msblender
MIN_BEST_HITS=${MIN_BEST_HITS:-2}

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
function_info "$PROG $__RUNMSB_VERSION__" \
  "Minimum Number of Search Engines: $MIN_ENGINES" \
  "Min best hits:  $MIN_BEST_HITS" \
  "Execution info: $RUN_ENV" \
  "Output prefix:  $OUT_PFX" \
  "Real out pfx:   $OUT_PFX2" \
  "mzXML file:     $IN_MZXML0" \
  "  realpath:     $IN_MZXML" \
  "DB fasta:       $FASTAFILE0" \
  "  realpath:     $FASTAFILE" \
  "DB name:        $DBNAME" \
  "Working dir:    $WORKDIR0" \
  "  using:        $WORKDIR" \
  "Temp dir:       $TMP_DIR" \
  "Output dir:     $OUTPUTDIR0" \
  "  using:        $OUTPUTDIR" \
  "Search GUI:     $SEARCHGUIDIR0" \
  "  using:        $SEARCHGUIDIR" \
  "MSblender dir:  $PIPELINEDIR" \
  "MSblender:      $MSBLENDER_BIN" \
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

mkdir -p $WORKDIR; mkdir -p $TMP_DIR; mkdir -p $OUTPUTDIR;
check_dir $OUTPUTDIR    "Output"
check_dir $WORKDIR      "Working"
check_dir $TMP_DIR      "Temporary"
check_dir $SEARCHGUIDIR "Search GUI"
check_dir $PIPELINEDIR  "MSblender"

check_integer_type $MIN_ENGINES 'pos' "min number of search engines"
if [[ $MIN_ENGINES   -lt 2 ]]; then err "Minimum search engines must be 2 or 3"; fi
if [[ $MIN_ENGINES   -gt 3 ]]; then err "Minimum search engines must be 2 or 3"; fi
if [[ $MIN_BEST_HITS -lt 2 ]]; then err "Minumum number of best hits must be at least 2"; fi

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
FAILURE_INFO="1"  # err function will call report_status_info now
function report_status_info() {
  local tag=${1:-"STATUS"}
  local info="$tag: Min search engines $MIN_ENGINES, num run $NUM_ENG_RUN, num ok $NUM_ENG_OK $OK_ENGINES;"
  if [[ "$NO_SPECTRA" != "" ]];    then info="$info NO_SPECTRA: $NO_SPECTRA;"; fi
  if [[ "$PARSE_XML_ERR" != "" ]]; then info="$info PARSE_XML_ERR: $PARSE_XML_ERR;"; fi
  if [[ "$NO_PROT_IDS" != "" ]];   then info="$info NO_PROT_IDS: $NO_PROT_IDS;"; fi
  section $info
}
NUM_ENG_OK=0; NUM_ENG_RUN=0; COMET_OK=0; XTAN_OK=0; MSGF_OK=0;
NO_SPECTRA=""; PARSE_XML_ERR=""; OK_ENGINES=""; NO_PROT_IDS=""

# -- Comet ------------------------------------
section "Running Comet"
$COMETEXE -P$COMETPARAM -D${FASTAFILE} -N$COMETOUT $IN_MZXML 2>&1 | tee ${OUT_PFX}.run_comet.txt
code=$?
NUM_ENG_RUN=$(( $NUM_ENG_RUN + 1 ))
check_file_not_empty ${OUT_PFX}.run_comet.txt "Comet run"
# Comet can fail (return a non-0 exit code) on a "hard" error, but can also return 0
# but not produce valid output. The text looks something like this:
#   "No index list offset found. File will not be read.
#     Warning - no spectra searched."
# - or this -
#   "Syntax error parsing XML"
no_spectra=$(grep 'no spectra searched' ${OUT_PFX}.run_comet.txt)
parse_err=$(grep 'Syntax error parsing XML' ${OUT_PFX}.run_comet.txt)
if [[ "$no_spectra" != "" ]]; then NO_SPECTRA="$NO_SPECTRA Comet"; fi
if [[ "$parse_err"  != "" ]]; then PARSE_XML_ERR="$PARSE_XML_ERR Comet"; fi
if [[ $code -eq 0 || $MIN_ENGINES -eq 3 ]]; then # check when all 3 engines required
  check_return_code $code "Comet"
  if [[ "$no_spectra" == "" && "$parse_err" == "" ]]; then # really ok
    check_file_not_empty $COMETOUT.pep.xml "Comet peptides"
    mv $COMETOUT.pep.xml $WORKDIR/${OUT_PFX}..comet.pep.xml
    check_file_not_empty $WORKDIR/${OUT_PFX}..comet.pep.xml "renamed Comet peptides"
    NUM_ENG_OK=$(( $NUM_ENG_OK + 1 )); COMET_OK=1; OK_ENGINES="$OK_ENGINES Comet"
  elif [[ "$no_spectra" != "" ]]; then
    echo_ex "WARNING: Comet found no spectra, skipping (min engines $MIN_ENGINES, num ok $NUM_ENG_OK)"
  else
    echo_ex "WARNING: Comet syntax error parsing mzXML, skipping (min engines $MIN_ENGINES, num ok $NUM_ENG_OK)"
  fi
else
  echo_ex "WARNING: Comet returned non-0 exit code $code, skipping (min engines $MIN_ENGINES, num ok $NUM_ENG_OK)"
fi
report_status_info

# -- Xtandem ------------------------------------
section "Running XTandem"
echo_ex "Preparing run-tandemK.sh script.."
python $PIPELINEDIR/msblender-scripts/prepare-tandemK-high.py \
  $IN_MZXML $FASTAFILE $TMP_DIR $XTANDEMEXE
check_return_code $? "prepare-tandemK-high.py"
check_file_not_empty $TMP_DIR/run-tandemK.sh "run-tandemK.sh"
echo_ex "Running run-tandemK.sh"
bash $TMP_DIR/run-tandemK.sh 2>&1 | tee ${OUT_PFX}.run_tandemK.txt
code=$?

NUM_ENG_RUN=$(( $NUM_ENG_RUN + 1 ))
check_file_not_empty ${OUT_PFX}.run_tandemK.txt "XTandem run"
no_spectra=$(grep -P \
  '(does not have any valid spectra|No input spectra met the acceptance criteria)' \
   ${OUT_PFX}.run_tandemK.txt)
if [[ "$no_spectra" != "" ]]; then NO_SPECTRA="$NO_SPECTRA XTandem"; fi
if [[ $code -eq 0 || $NUM_ENG_OK -eq 0 ]]; then # check everything when Comet already failed
  check_return_code $code "run-tandemK.sh (when NUM_ENG_OK=$NUM_ENG_OK)"
  check_file_not_empty $TMP_DIR/$OUT_PFX2.$DBNAME.tandemK.out 'XTandem out'
  check_file_not_empty $TMP_DIR/$OUT_PFX2.$DBNAME.tandemK.xml 'XTandem xml'

  mv $TMP_DIR/${OUT_PFX2}.${DBNAME}.tandemK.out $WORKDIR/${OUT_PFX}.tandemK.out
  mv $TMP_DIR/${OUT_PFX2}.${DBNAME}.tandemK.xml $WORKDIR/${OUT_PFX}.tandemK.xml
  check_file_not_empty $WORKDIR/${OUT_PFX}.tandemK.out 'renamed XTandem out'
  check_file_not_empty $WORKDIR/${OUT_PFX}.tandemK.xml 'renamed XTandem xml'
  NUM_ENG_OK=$(( $NUM_ENG_OK + 1 )); XTAN_OK=1; OK_ENGINES="$OK_ENGINES XTandem"
else
  echo_ex "WARNING: run-tandemK.sh returned non-0 exit code $code, skipping (min engines $MIN_ENGINES, num ok $NUM_ENG_OK)"
fi
report_status_info

# -- MS-GF+ ------------------------------------
section "Running MS-GF+"
echo_ex "Read/parse MS-GF+ param file. Append modification file parameter."
MSGFplus_PARAMSTR=$(grep -v "#" "$MSGFplus_PARAMFILE" | tr -s '\n\r' ' ')"$MSGFplus_MODPARAM"
echo_se "MSGF+ parameters: '$MSGFplus_PARAMSTR'"
echo_ex "Executing MSGF+ jar"
java -Xmx20000M -jar $MSGFplus_JAR -d $FASTAFILE -s $IN_MZXML \
  -o ${MSGFOUT}.mzid -tda 0 $MSGFplus_PARAMSTR 2>&1 | tee ${OUT_PFX}.run_msgf.txt
code=$?
NUM_ENG_RUN=$(( $NUM_ENG_RUN + 1 ))
check_file_not_empty ${OUT_PFX}.run_msgf.txt "MSGF run"

parse_err=$( grep 'ParseError' ${OUT_PFX}.run_msgf.txt)
no_spectra=$(grep -P \
  '(does not have any valid spectra|No input spectra met the acceptance criteria)' \
   ${OUT_PFX}.run_msgf.txt)
if [[ "$parse_err" != "" ]]; then PARSE_XML_ERR="$PARSE_XML_ERR MSGF";
elif [[ "$no_spectra" != "" ]]; then NO_SPECTRA="$NO_SPECTRA MSGF"; fi
if [[ $code -eq 0 || $NUM_ENG_OK -lt 2 ]]; then # check when another engine already failed
  check_return_code $code "java `basename $MSGFplus_JAR` (when NUM_ENG_OK=$NUM_ENG_OK)"
  check_file_not_empty ${MSGFOUT}.mzid "MSGF+ mzid"

  echo_se "Running MSGF+ MzIDToTsv"
  TBL=${MSGFOUT/.mzid}.tsv
  java -Xmx20000M -cp $MSGFplus_JAR edu.ucsd.msjava.ui.MzIDToTsv -i ${MSGFOUT}.mzid \
    -o $TBL -showQValue 1 -showDecoy 1 -unroll 0
  check_return_code $? "MSGF+ MzIDToTsv"
  check_file_not_empty $TBL "MSGF+ tsv"
  NUM_ENG_OK=$(( $NUM_ENG_OK + 1 )); MSGF_OK=1; OK_ENGINES="$OK_ENGINES MSGF"
else
  echo_ex "WARNING: `basename $MSGFplus_JAR` returned non-0 exit code $code, skipping (min engines $MIN_ENGINES)"
fi
report_status_info

# -- Hit lists/Best hits ------------------------------------
section "Creating hit lists and selecting best hits"
nBestComet=0; nBestXTan=0; nBestMSGF=0

if [[ "$COMET_OK" == "1" ]]; then
  echo_ex "Running comet_pepxml-to-xcorr_hit_list.py"
  check_file_not_empty $WORKDIR/${OUT_PFX}..comet.pep.xml "Comet pep.xml"
  python $PIPELINEDIR/msblender-scripts/comet_pepxml-to-xcorr_hit_list.py \
    $WORKDIR/${OUT_PFX}..comet.pep.xml
  check_return_code $? "comet_pepxml-to-xcorr_hit_list.py"
  check_file_not_empty \
    $WORKDIR/${OUT_PFX}..comet.pep.xml.xcorr_hit_list 'Comet xcorr hits'

  echo_ex "Running select-best-psm.py on comet"
  python $PIPELINEDIR/msblender-scripts/select-best-PSM.py \
    $WORKDIR/${OUT_PFX}..comet.pep.xml.xcorr_hit_list
  check_return_code $? "select-best-PSM.py comet"
  check_file_not_empty \
    $WORKDIR/${OUT_PFX}..comet.pep.xml.xcorr_hit_list_best 'Comet best hits'
  nBestComet=`grep -v '^#' $WORKDIR/${OUT_PFX}..comet.pep.xml.xcorr_hit_list_best | wc -l`
else echo_se "Skipping Comet hit list (Comet not run)"
fi
if [[ "$XTAN_OK" == "1" ]]; then
  echo_ex "Running tandem_out-to-logE_hit_list.py"
  check_file_not_empty $WORKDIR/${OUT_PFX}.tandemK.out "XTandem out"
  python $PIPELINEDIR/msblender-scripts/tandem_out-to-logE_hit_list.py \
    $WORKDIR/${OUT_PFX}.tandemK.out
  check_return_code $? "tandem_out-to-logE_hit_list.py"
  check_file_not_empty \
    $WORKDIR/${OUT_PFX}.tandemK.out.logE_hit_list 'XTandem logE hits'

  echo_ex "Running select-best-psm.py on tandemK"
  python $PIPELINEDIR/msblender-scripts/select-best-PSM.py \
    $WORKDIR/${OUT_PFX}.tandemK.out.logE_hit_list
  check_return_code $? "select-best-PSM.py tandemK"
  check_file_not_empty \
    $WORKDIR/${OUT_PFX}.tandemK.out.logE_hit_list_best 'XTandem best hits'
  nBestXTan=`grep -v '^#' $WORKDIR/${OUT_PFX}.tandemK.out.logE_hit_list_best | wc -l`
else echo_se "Skipping XTandem hit list (XTandem not run)"
fi
if [[ "$MSGF_OK" == "1" ]]; then
  echo_ex "Running MSGF+_tsv-to-logSpecE_hit_list.py"
  check_file_not_empty ${MSGFOUT}.tsv 'MSGF+ tsv'
  python $PIPELINEDIR/msblender-scripts/MSGF+_tsv-to-logSpecE_hit_list.py \
    ${MSGFOUT}.tsv
  check_return_code $? "MSGF+_tsv-to-logSpecE_hit_list.py"
  check_file_not_empty \
    ${MSGFOUT}.tsv.logSpecE_hit_list 'MS-GF logSpecE hits'

  echo_ex "Running select-best-psm.py on msgf+"
  python $PIPELINEDIR/msblender-scripts/select-best-PSM.py \
    ${MSGFOUT}.tsv.logSpecE_hit_list
  check_return_code $? "select-best-PSM.py msgf+"
  check_file_not_empty \
    ${MSGFOUT}.tsv.logSpecE_hit_list_best 'MSGF+ best hits'
  nBestMSGF=`grep -v '^#' ${MSGFOUT}.tsv.logSpecE_hit_list_best | wc -l`
else echo_se "Skipping MSGF hit list (MSGF+ not run)"
fi

# -- MSblender ------------------------------------
section "Running MSblender"

echo_ex "Showing top hit statistics"
echo "Comet   $COMET_OK $nBestComet" >  ${OUT_PFX}.best_stats.txt
echo "XTandem $XTAN_OK $nBestXTan"   >> ${OUT_PFX}.best_stats.txt
echo "MSGF+   $MSGF_OK $nBestMSGF"   >> ${OUT_PFX}.best_stats.txt
cat ${OUT_PFX}.best_stats.txt

# reset these so that failure can include no best hits now
OK_ENGINES=''; NUM_ENG_OK=0
rm -f ${OUT_PFX}.conf; touch ${OUT_PFX}.conf
if [[ "$COMET_OK" == "1" && $nBestComet -ge $MIN_BEST_HITS ]]; then
  echo comet      $WORKDIR/${OUT_PFX}..comet.pep.xml.xcorr_hit_list_best >> ${OUT_PFX}.conf;
  OK_ENGINES="$OK_ENGINES Comet"; NUM_ENG_OK=$(( $NUM_ENG_OK + 1 ))
fi
if [[ "$XTAN_OK" == "1"  && $nBestXTan  -ge $MIN_BEST_HITS ]]; then
  echo 'X!Tandem' $WORKDIR/${OUT_PFX}.tandemK.out.logE_hit_list_best     >> ${OUT_PFX}.conf;
  OK_ENGINES="$OK_ENGINES XTandem"; NUM_ENG_OK=$(( $NUM_ENG_OK + 1 ))
fi
if [[ "$MSGF_OK" == "1"  && $nBestMSGF  -ge $MIN_BEST_HITS ]]; then
  echo 'MSGF+'    ${MSGFOUT}.tsv.logSpecE_hit_list_best                  >> ${OUT_PFX}.conf;
  OK_ENGINES="$OK_ENGINES MSGF"; NUM_ENG_OK=$(( $NUM_ENG_OK + 1 ))
fi
report_status_info
nLine=`cat ${OUT_PFX}.conf | wc -l`
if [[ $nLine -lt $MIN_ENGINES ]]; then
  err "${OUT_PFX}.conf must have at least $MIN_ENGINES entries (search engines w/at least $MIN_BEST_HITS best hits)"
fi

echo_ex "Running make-msblender_in.py to make msblender conf file"
python $PIPELINEDIR/msblender-scripts/make-msblender_in.py ${OUT_PFX}.conf
check_return_code $? "make-msblender_in.py"
check_file_not_empty ${OUT_PFX}.msblender_in "MSblender input"

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
# Note: these two will exist and be non-empty even when there are no IDs due to comment lines
check_file_not_empty ${OUT_PFX}.prot_count_mFDRpsm001       "proteins FDRpsm"
check_file_not_empty ${OUT_PFX}.prot_count_mFDRpsm001.group "proteins FDRpsm group"
check_file_not_empty ${OUT_PFX}.prot_list                   "proteins list"
# This file should exist, but can be empty when there are no IDs
check_file ${OUT_PFX}.prot_count_mFDRpsm001.log "proteins FDRpsm log"
nLine=`cat ${OUT_PFX}.prot_count_mFDRpsm001.log | wc -l`
if [[ $nLine -eq 0 ]]; then
  NO_PROT_IDS='MSblender';
  err "No FDRpsm001 proteins identified by MSblender"
fi

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

section "$PROG $OUT_PFX completed successfully! ($NUM_ENG_OK engines: $OK_ENGINES)"
exit 0

