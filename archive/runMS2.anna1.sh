#!/bin/bash

#CDM: Note skipping myrimatch b/c SegmentationFault

#The setup is a folder for each experiment
#Each experiment folder contains a folder call "mzXML" which contains
#  all the mzXMLs for that experiment
#  WORKDIR is folder in the experiment folder
#  Each run processes as single mzxml


#Example experiment setup
#exp_dir
#----mzXML
#--------exp_MSrun.mzXML
#----working
#----output
#----DB
#--------proteome.contam.combined.fasta


#Example start run command
#bash /work/03491/cmcwhite/MS1-quant-pipeline/runMs1Quant.sh /scratch/03491/cmcwhite/metazoans/Ce_1104/mzXML/WAN1100427_OT2_Celegans_HCW_P1A01.mzXML /scratch/03491/cmcwhite/metazoans/Ce_1104/DB/uniprot-proteome%3AUP000001940_caeel_contam.combined.fasta /scratch/03491/cmcwhite/metazoans/Ce_1104/working /scratch/03491/cmcwhite/metazoans/Ce_1104/output



THREADS=2
f=${1##*/}
INPUTFILE=${f%.mzXML} #mzXML file
FASTAFILE=$2 #fasta protein database
WORKDIR=$3
OUTPUTDIR=$4
#Use this if using searchgui exes and openMS binaries
SEARCHGUIDIR=$5


if [ ! -f "$1" ]
    then
    echo "mzXML $1 not found!"
    exit 0
fi
if [ ! -f "$FASTAFILE" ]
    then
    echo "Fasta $FASTAFILE not found!"
    exit 0
fi

if [ -z "$f" ]
   then
   echo "mzXML $f not found"
   exit 0
fi

if [ -z "$WORKDIR" ]
   then
   echo "workdir $WORKDIR not found"
   exit 0
fi

if [ -z "$OUTPUTDIR" ]
   then
   echo "outputdir $OUTPUTDIR not found"
   exit 0
fi

if [ -z "$SEARCHGUIDIR" ]
   then
   echo "searchgui dir $SEARCHGUIDIR not found"
   exit 0
fi



####
#Reserved for futue MS1 analysis
#OPENMSDIR=$6
###

#Get location of this script
this_script_loc="$(readlink -f ${BASH_SOURCE[0]})"

## Get pipeline folder location
## Something like /work/MSblender
PIPELINEDIR="$(dirname $this_script_loc)"
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$PIPELINEDIR/lib
echo $PIPELINEDIR

TANDEMDIR=$WORKDIR/${INPUTFILE}_tandem
MZXMLDIR=$(dirname "$1")
echo $MZXMLDIR

#### Change to where this actually is if it's somewhere else
MSBLENDER_BIN=$PIPELINEDIR/src/msblender
#MSBLENDER_BIN=$WORK/MSblender/src/msblender

if [ ! -f "$MSBLENDER_BIN" ]
    then
    echo "msblender binary $MSBLENDER_BIN not found!"
    exit 0
fi
module load gsl


DBNAME=${FASTAFILE/.fasta/}
DBNAME=${DBNAME##*/}
COMETOUT=${INPUTFILE}"."$DBNAME".comet"
COMETPARAM="${PIPELINEDIR}/params/comet.params.new"
if [ ! -f "$COMETPARAM" ]
    then
    echo "comet parameter file $COMETPARAM not found!"
    exit 0
fi
#

COMETEXE="${PIPELINEDIR}/exe/comet.linux.exe"

if [ ! -f "$COMETEXE" ]
    then
    echo "comet executable $COMETEXE not found!"
    exit 0
fi
#
##MYRIMATCHEXE="$SEARCHGUIDIR/resources/MyriMatch/linux/linux_64bit/myrimatch"
#MYRIMATCHEXE="$PIPELINEDIR/exe/myrimatch"


#If using searchgui executables
MSGFplus_JAR="$SEARCHGUIDIR/resources/MS-GF+/MSGFPlus.jar"
if [ ! -f "$MSGFplus_JAR" ]
    then
    echo "msgfplus jar $MSGFplus_JAR not found!"
    exit 0
fi

### Create MS-GF+ parameter string.
MSFGplus_MODFILE="${PIPELINEDIR}/params/MSGFplus_mods.txt"
if [ ! -f "$MSFGplus_MODFILE" ]
then
    echo "MSGF+ modification file $MSFGplus_MODFILE not found! Using default of static C+57 and no optional modifications."
    MSGFplus_MODPARAM=""
else
    MSGFplus_MODPARAM=" -mod $MSFGplus_MODFILE"
fi

# Read and parse MS-GF+ param file. Append modification file parameter.
MSGFplus_PARAMFILE="${PIPELINEDIR}/params/MSGFplus_params.txt"
if [ ! -f "$MSGFplus_PARAMFILE" ]
then
    echo "MSGF+ parameter file $MSGFplus_PARAMFILE not found!"
    exit 0
else
    MSGFplus_PARAMSTR=$(grep -v "#" "$MSGFplus_PARAMFILE" | tr -s '\n\r' ' ')"$MSGFplus_MODPARAM"
fi


#
#####
#Researved for MS1 future analysis
#OMSSAEXE="$SEARCHGUIDIR/resources/OMSSA/linux/omssacl"
#####

#XTANDEMEXE="$SEARCHGUIDIR/resources/XTandem/linux/linux_64bit/tandem"
XTANDEMEXE="${PIPELINEDIR}/extern/tandem.linux.exe"

if [ ! -f "$XTANDEMEXE" ]
    then
    echo "xtandem executable $XTANDEMEXE not found!"
    exit 0
fi
#
MSGFOUT=$WORKDIR/${INPUTFILE}.MSGF+


#make sure working directories exist if not make them.
mkdir -p $WORKDIR
mkdir -p $OUTPUTDIR
mkdir -p $TANDEMDIR



#######################################################
# Reserved for future MS1 analysis

   
# convert mzXML to mzML file as
#$OPENMSDIR/bin/FileConverter -in $1 -out $WORKDIR/${INPUTFILE}.mzML


#do database searches (MS2 identification)
  #MSblender searches

   #####~/OpenMS-2.0.0/bin/MSGFPlusAdapter -in $WORKDIR/${INPUTFILE}.mzML -out $WORKDIR/${INPUTFILE}.MSGF.idXML -database $FASTAFILE -fixed_modifications 'Carbamidomethyl (C)' -variable_modifications 'Oxidation (M)' -threads $THREADS -executable $MSGFplus_JAR

   #need to export libs for myrimatch. how to fix this more perminently.
   #export LC_ALL=C

   #$OPENMSDIR/bin/OMSSAAdapter -in $WORKDIR/${INPUTFILE}.mzML -out $WORKDIR/${INPUTFILE}.OMSSA.idXML -database $FASTAFILE -fixed_modifications 'Carbamidomethyl (C)' -variable_modifications 'Oxidation (M)' -threads $THREADS -omssa_executable $OMSSAEXE


        #Skipping doing MyriMatch
        #SEARCHGUIDIR/bin/MyriMatchAdapter -in $WORKDIR/${INPUTFILE}.mzML -out $WORKDIR/${INPUTFILE}.Myri.idXML -database $FASTAFILE -fixed_modifications 'Carbamidomethyl (C)' -variable_modifications 'Oxidation (M)' -threads $THREADS -myrimatch_executable $MYRIMATCHEXE -debug 2 -log 'myrilog'


        #$OPENMSDIR/bin/XTandemAdapter -in $WORKDIR/${INPUTFILE}.mzML -out $WORKDIR/${INPUTFILE}.Xtandem.idXML -database $FASTAFILE -fixed_modifications 'Carbamidomethyl (C)' -variable_modifications 'Oxidation (M)' -threads $THREADS -xtandem_executable $XTANDEMEXE
        #
########################################################


   #comet search

   $COMETEXE -p   
   $COMETEXE -P$COMETPARAM -D${FASTAFILE} -N$COMETOUT $1
   mv $COMETOUT.pep.xml $WORKDIR/${INPUTFILE}..comet.pep.xml

   
        echo $1
        #This all gos to tandemdir
   python $PIPELINEDIR/msblender-scripts/prepare-tandemK-high.py $1 $FASTAFILE $TANDEMDIR $XTANDEMEXE
   

        #Need to find this script CDM
        #It's saving to the dir where I start the whole process...
        #Should go to tandemDir
   bash $TANDEMDIR/run-tandemK.sh
   
        #mv $TANDEMDIR/*tandemK.xml $WORKDIR
   #MSGF+
   TBL=${MSGFOUT/.mzid}.tsv
   time java -Xmx20000M -jar $MSGFplus_JAR -d $FASTAFILE -s $1 -o ${MSGFOUT}.mzid -tda 0 $MSGFplus_PARAMSTR
   time java -Xmx20000M -cp $MSGFplus_JAR edu.ucsd.msjava.ui.MzIDToTsv -i ${MSGFOUT}.mzid -o $TBL -showQValue 1 -showDecoy 1 -unroll 0


        echo -e "\ncomet_pepxml-to-xcorr_hit_list"
   python $PIPELINEDIR/msblender-scripts/comet_pepxml-to-xcorr_hit_list.py $WORKDIR/${INPUTFILE}..comet.pep.xml

   #mv ${1%.mzXML}.${DBNAME}.tandemK.out ${1%.mzXML}.tandemK.out #hacky but I don't know how else to fix the namming issue
   #mv ${1%.mzXML}.${DBNAME}.tandemK.xml ${1%.mzXML}.tandemK.xml
        #What was this move for? cdm

        ls -ltr $WORKDIR
        ls -ltr $TANDEMDIR

        echo $DBNAME
        echo $INPUTFILE
   mv $TANDEMDIR/${INPUTFILE}.${DBNAME}.tandemK.out $WORKDIR/${INPUTFILE}.tandemK.out #hacky but I don't know how else to fix the naming issue





   mv $TANDEMDIR/${INPUTFILE}.${DBNAME}.tandemK.xml $WORKDIR/${INPUTFILE}.tandemK.xml

        echo -e "\ntandem_out-to-logE_hit_list"
   python $PIPELINEDIR/msblender-scripts/tandem_out-to-logE_hit_list.py $WORKDIR/${INPUTFILE}.tandemK.out


        ls -ltr $WORKDIR
        ls -ltr $TANDEMDIR


        echo -e "\nMSGF+_tsv-to-logSpecE_hit_list"
   python $PIPELINEDIR/msblender-scripts/MSGF+_tsv-to-logSpecE_hit_list.py ${MSGFOUT}.tsv


        echo -e "\nselect-best-psm tandemK"
   python $PIPELINEDIR/msblender-scripts/select-best-PSM.py $WORKDIR/${INPUTFILE}.tandemK.out.logE_hit_list

        echo -e "\nselect-best-psm comet"
   python $PIPELINEDIR/msblender-scripts/select-best-PSM.py $WORKDIR/${INPUTFILE}..comet.pep.xml.xcorr_hit_list

        echo -e "\nselect best psm MSGF+"
   python $PIPELINEDIR/msblender-scripts/select-best-PSM.py ${MSGFOUT}.tsv.logSpecE_hit_list
   
   
   echo comet       $WORKDIR/${INPUTFILE}..comet.pep.xml.xcorr_hit_list_best > ${INPUTFILE}.conf
   #echo MSGF+      ${MSGFOUT}.tsv.logSpecE_hit_list_best >> ${INPUTFILE}.conf
   #echo X!Tandem         ${1%.mzXML}.tandemK.out.logE_hit_list_best >> ${INPUTFILE}.conf


        echo -e "\nmake-msblender_in conf file making"
   python $PIPELINEDIR/msblender-scripts/make-msblender_in.py ${INPUTFILE}.conf

        echo -e "\nrun msblender using conf file"
   $MSBLENDER_BIN ${INPUTFILE}.msblender_in
   
        echo -e "\nfilter-msblender"
   python $PIPELINEDIR/msblender-scripts/filter-msblender.py ./${INPUTFILE}.msblender_in.msblender_out 001 > msblender.filter


        echo -e "\nmsblender_out-to-pep_count-FDRpsm"
   python $PIPELINEDIR/msblender-scripts/msblender_out-to-pep_count-FDRpsm.py ${INPUTFILE}.msblender_in.msblender_out 0.01 mFDRpsm

        echo -e "\npep_count_with_fasta-to-prot_count"
   python $PIPELINEDIR/msblender-scripts/pep_count_with_fasta-to-prot_count.py *.pep_count_mFDRpsm001 $FASTAFILE


   wait

   echo comet           $WORKDIR/${INPUTFILE}..comet.pep.xml.xcorr_hit_list_best > ${INPUTFILE}.conf
        echo MSGF+          ${MSGFOUT}.tsv.logSpecE_hit_list_best >> ${INPUTFILE}.conf
        echo X!Tandem       $WORKDIR/${INPUTFILE}.tandemK.out.logE_hit_list_best >> ${INPUTFILE}.conf

        echo -e "\nmake-msblender_in conf file making"
        python $PIPELINEDIR/msblender-scripts/make-msblender_in.py ${INPUTFILE}.conf

        echo -e "\nrun msblender using conf file"
        $MSBLENDER_BIN ${INPUTFILE}.msblender_in

        echo -e "\nfilter-msblender"
        python $PIPELINEDIR/msblender-scripts/filter-msblender.py ${INPUTFILE}.msblender_in.msblender_out 001 > msblender.filter

        echo -e "\nmsblender_out-to-pep_count-FDRpsm"
        python $PIPELINEDIR/msblender-scripts/msblender_out-to-pep_count-FDRpsm.py ${INPUTFILE}.msblender_in.msblender_out 0.01 mFDRpsm

        echo -e "\npep_count_with_fasta-to-prot_count"
        python $PIPELINEDIR/msblender-scripts/pep_count_with_fasta-to-prot_count.py ${INPUTFILE}.pep_count_mFDRpsm001 $FASTAFILE


   wait


   mv ${INPUTFILE}.prot_count_mFDRpsm001 $OUTPUTDIR
   mv ${INPUTFILE}.prot_count_mFDRpsm001.group $OUTPUTDIR
        mv ${INPUTFILE}.prot_count_mFDRpsm001.log $OUTPUTDIR
        mv ${INPUTFILE}.prot_list $OUTPUTDIR
        mv ${INPUTFILE}.pep_count_mFDRpsm001 $OUTPUTDIR
        mv ${INPUTFILE}.pep_count_mFDRpsm001.log $OUTPUTDIR


   mv ${INPUTFILE}.* $WORKDIR/
   

###
#Reserved for future MS1 analysis   
#clean up mzML file because it's huge
#rm $WORKDIR/${INPUTFILE}.mzML
####



