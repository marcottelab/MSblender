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

# Quick start

   ```bash
   # set up directories (replace "proj" with your project name)
   mkdir -p proj/{mzXML,db,working,output,logs}
   ```

   ```bash
   # symlink raw data to mzxml directory
   ln -s /path/to/mzxmls/*mzXML proj/mzXML
   ```

   ```bash
   # make fasta database (replace "proteome" with your fasta name)
   # there is a contam.fasta here: example_data/fastas/contam.fasta
   cat proteome.fasta contam.fasta > proj/db/proteome_contam.combined.fasta
   ```

   ```bash
   # template command
   /MS/processed/leca/MSblender_consistent/runMSblender.sh /path/to/mzXML/file /path/to/database/file /path/to/working/dir/ /path/to/output/dir
   ```

   ```bash
   # for many mzXMLs (e.g., CFMS data)
   for x in proj/mzXML/*mzXML; do echo "/MS/processed/leca/MSblender_consistent/runMSblender.sh proj/mzXML/${x} proj/db/proteome_contam.combined.fasta proj/working proj/output"; done > proj/proj.msblender.cmds
   ```
   

# Search parameter configuration

   Search engine parameter docs: [X!Tandem](https://www.thegpm.org/TANDEM/api/index.html), [Comet-2013020](http://comet-ms.sourceforge.net/parameters/parameters_201302/), and [MS-GF+](https://bix-lab.ucsd.edu/pages/viewpage.action?pageId=13533355).


   Search parameters can be modified as necessary, but try to keep parameters consistent across search algorithms.

   The default were selected with our standard MS experiments in mind:
   
   - high-res MS (10ppm precursor tolerance)
   
   - low-res MS/MS (ion trap) \*
   
   - tryptic digestion, no non-enzymatic termini
   
   - fixed cysteine carbamidomethylation (+57.021464, from iodoacetamide alkylation)
   
   - optional methionine oxidation (+15.9949)


   _\* X!Tandem purportedly ignores fragment mass tolerance settings when using k-scoring and/or no "spectrum conditioning". (And it recommends turning conditioning off when using k-score.)_


## Tips on changing search parameters

   Comet parameter and MS-GF+ param and modification files are found in ./params

   Comments within each should offer sufficient documentation.

   X!Tandem parameters are found in ./search/tmpl/tandemK.high.xml
 
# MSBlender Docker

A full docker image with MSblender installed is available here: https://hub.docker.com/r/kdrew/msblender

To run: 
```
docker pull kdrew/msblender

docker run -v /test_data/:/data msblender /data/xl_animalcaps_SEC_Control_20a_20181121.mzXML /data/combined_contam_rev_file.fasta /data/working /data/output /searchgui
```

# To do list

   - Myrimatch currently not working b/c of library issue 
  
   - Separate Xtandem from this repo
  
   - Add on MS1 quantification
