# MSblender 
MSblender: a probabilistic approach for integrating peptide identifications
from multiple database search engines
 
See http://www.marcottelab.org/index.php/MSblender for more (somewhat outdated) information.
 Citation

    T. Kwon*, H. Choi*, C. Vogel, A.I. Nesvizhskii, and E.M. Marcotte, MSblender: a probabilistic approach for integrating peptide identifications from multiple database search engines. J. Proteome Research, 10(7): 2949–2958 (2011) Link 


## About

   This version is modified from JRH MS1-Quant-Pipeline but minus any MS1 quantification
   
   It has been further modified to make parameters more consistent across search algorithms.
   MS-GF+ options and PTMs are now defined in dedicated parameter files.
   
   This repo contains:

    -  msblender MS2 analysis

    -  helper scripts

    -  accessory files and parameters used MS intepretation programs


   Available search engines:

    - X!Tandem

    - Comet

    - MS-GF+

   All programs are external from SearchGUI except X!tandem

  

### To do

   - Myrimatch currently not working b/c of library issue 
  
   - Separate Xtandem from this repo
  
   - Add on MS1 quantification
  

# How to run

   Instructions for running are in https://github.com/marcottelab/run_msblender

   contains:
 
    - sample directory structure
 
    - instructions for how to run

    - an example analysis
   
   
   ## Search parameter configuration

   Search engine parameter docs: [X!Tandem](https://www.thegpm.org/TANDEM/api/index.html), [Comet-2013020](http://comet-ms.sourceforge.net/parameters/parameters_201302/), and [MS-GF+](https://bix-lab.ucsd.edu/pages/viewpage.action?pageId=13533355).


   Search parameters can be modified as necessary, but try to keep parameters consistent across search algorithms.

   The default were selected with our standard MS experiments in mind:
   
   - high-res MS (10ppm precursor tolerance)
   
   - low-res MS/MS (ion trap) \*
   
   - tryptic digestion, no non-enzymatic termini
   
   - fixed cysteine carbamidomethylation (+57.021464, from iodoacetamide alkylation)
   
   - optional methionine oxidation (+15.9949)


   _\* X!Tandem purportedly ignores fragment mass tolerance settings when using k-scoring and/or no "spectrum conditioning". (And it recommends turning conditioning off when using k-score.)_


### Tips on changing search parameters

   Comet parameter and MS-GF+ param and modification files are found in ./params

   Comments within each should offer sufficient documentation.

   X!Tandem parameters are found in ./search/tmpl/tandemK.high.xml
 
 
# Compile msblender 

Navigate to src/ and execute './compile'

You'll need GNU Scientific Library (gsl) and will likely have to modify the gsl path for your gsl version in src/compile -> 


Change the two gcc commands to:


`gcc -Wall -I/opt/apps/gcc5_2/gsl/2.2.1/include/ -c *.c *.h`


`gcc *.o -lgsl -L/opt/apps/gcc5_2/gsl/2.2.1/lib/ -lgslcblas -lm -o ./msblender`

This generates 'msblender' and 'msblender.h.gch'


#Building OpenMS on your own machine...oof

### This will only be necessary for the upcoming MS1 quantification

### OpenMS will not build with default settings on TACC

Download tarball of OpenMS-2.0.0 or above

Make sure it's a release version, which comes with the dependencies ready t nstall

Unzip

Go into directory OpenMS-2.0.0 directory

```
git clone  https://github.com/OpenMS/contrib.git

mkdir contrib-build

cd contrib-build
```
Source of this: http://ftp.mi.fu-berlin.de/pub/OpenMS/release-documentation/html/install_linux.html


Show  the available builds

```
cmake -DBUILD_TYPE=LIST ../contrib
```


try doing: 

```
cmake -DBUILD_TYPE=ALL ../contrib
```

to install all at once, but I had to do each independently,

libsvm wouldn't work, so I downloaded and build it independently

example of the individual installations
```
cmake -DBUILD_TYPE=SEQAN ../contrib

cmake -DBUILD_TYPE=WILDMAGIC ../contrib

cmake -DBUILD_TYPE=EIGEN ../contrib
```

Note: I originally did 'module load gsl' on TACC prior to running, but this isn't necessary apparently??


## Configuring

Back one level out of the OpenMS directory

```
mkdir OpenMS-build

cd OpenMS-build

cmake -DCMAKE_PREFIX_PATH="/PATH/TO/contrib-build;/usr;/usr/local" -DBOOST_USE_STATIC=OFF ../OpenMS

export PATH=$PATH:/PATH/TO/OpenMS/bin

ccmake .
```

In the menu that come up, change WITH_GUI to Off

Maybe also change HAS_XSERVER to Off

then

```
make
```


#Build SearchGUI on own machine

# MSBlender Docker

A full docker image with MSblender installed is available here: https://hub.docker.com/r/kdrew/msblender

To run: 
```
docker pull kdrew/msblender

docker run -v /project/kdrew/nextflow/test_data/:/data msblender /data/xl_animalcaps_SEC_Control_20a_20181121.mzXML /data/combined_contam_rev_file.fasta /data/working /data/output /searchgui
```




	
