# MSblender 

   Modified from JRH MS1-Quant-Pipeline but minus any MS1 quantification
   
   This repo contains msblender MS2 analysis, helper scripts, and parameters used MS intepretation programs

   Available spectrum lookup programs XTandem, Comet, OMSSA, MS-GF+

   All external from SearchGUI except Xtandem

   ### To do

   - Myrimatch currently not working b/c of library issue 
  
   - Separate Xtandem from this repo
  
  


# Instructions for running in marcottelab/run_msblender

  run_msblender contains sample directory structure, instructions for how to run, and an example analysis
   
 


#Compile msblender 

Navigate to src/ and execute './compile'

You'll need GNU Scientific Library

This generates 'msblender' and 'msblender.h.gch



#Building OpenMS on your own machine...oof

### OpenMS with not build with default settings on TACC
### May these instructions help some other poor soul

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



#This shows the available builds

cmake -DBUILD_TYPE=LIST ../contrib

try doing: cmake -DBUILD_TYPE=ALL ../contrib

to install all at once, but I had to do each independently,

and do module load for at least one

libsvm wouldn't work, so I downloaded and build it independently

example of the individual
```
cmake -DBUILD_TYPE=SEQAN ../contrib

cmake -DBUILD_TYPE=WILDMAGIC ../contrib

cmake -DBUILD_TYPE=EIGEN ../contrib
```

#Configuring

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





	
