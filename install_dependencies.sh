#!/bin/bash

# This is meant to install all of the packages that cut_run_pipeline_v1.sh requires.

# It might also move the cut and run folder to the softwares folder in the home
# directory.

# Start with python3

echo " "
echo " Thank you for using my cut and run pipeline. This installation program is meant to"
echo " install all of the packages required when using the main program."
echo " "
echo " This program should be run with administrative privelages (sudo). You will be prompted"
echo " for the password you created when installing the Windows Subsystem for Linux (Ubuntu)."
echo " Your password IS REQUIRED for this program to run properly, so please make sure you "
echo " have it ready."
echo " "
echo " This program was created on (and for) the Ubuntu 20.04 LTS distribution of the Windows"
echo " Subsystem for Linux. This pipeline might also work on a pure Ubuntu linux distribution,"
echo " but I have not tested it."
echo " "
echo " Theses are the commands that this program will run:"
echo " "
echo " Install numpy, scipy, glob and pyGenomeTracks modules for Python 3.8.5"
echo " "
echo " sudo python3 -m pip install numpy scipy glob pyGenomeTracks macs3"
echo " "
echo " Install bowtie2 (genome alignment tool), bedtools (tools for working with aligned sequence files)"
echo " and samtools (another tool for working with aligned sequence files)"
echo " "
echo " sudo apt-get install bowtie2"
echo " sudo apt-get install bedtools"
echo " sudo apt-get install samtools"
echo " sudo apt-get install bedops"
echo " sudo apt-get install fastqc"
echo " sudo apt-get install r-base-core"
echo " sudo apt-get install tree"
echo " "
echo " Install sambamba-0.8.0 from binaries. This requires making a directory, downloading the sources"
echo " unpacking them, and creating a symbolic link in the local bin."
echo " "
echo " sudo mkdir /usr/softwares"
echo " sudo wget https://github.com/biod/sambamba/releases/download/v0.8.0/sambamba-0.8.0-linux-amd64-static.gz -P /usr/softwares"
echo " sudo gunzip /usr/softwares/sambamba-0.8.0-linux-amd64-static.gz"
echo " sudo mv /usr/softwares/sambamba-0.8.0-linux-amd64-static /usr/softwares/sambamba-0.8.0"
echo " sudo chmod +x /usr/softwares/sambamba-0.8.0"
echo " sudo ln -s /usr/softwares/sambamba-0.8.0 /usr/local/bin/sambamba"
echo " "
echo " Install the GenomeBrowser applications developed by researchers at the University"
echo " of California at Santa Cruz. This requires copying each tool from the source, and"
echo " creating symbolic links in the local bin for the specific tools used in the pipeline."
echo " The benefit of downloading ALL GenomeBrowser apps at once is that, if you ever need"
echo " to use one, you can simply create a symbolic link in the local bin and it will be "
echo " available."
echo " "
echo " sudo rsync -aP rsync://hgdownload.soe.ucsc.edu/genome/admin/exe/linux.x86_64/ /usr/softwares"
echo " sudo ln -s /usr/softwares/bigWigToBedGraph /usr/local/bin/bigWigToBedGraph"
echo " sudo ln -s /usr/softwares/bedGraphToBigWig /usr/local/bin/bedGraphToBigWig"
echo " sudo ln -s /usr/softwares/bedClip /usr/local/bin/bedClip"
echo " "
echo " These are all of the required installations for the pipeline to run. I have made some"
echo " quality of life changes to the source code of pyGenomeTracks (making the x-axis on the"
echo " bottom of the plot, adding some space at the top and bottom of the plot, stuff like that)."
echo " Those files are kept in the ./scripts/GenomeTracks_edited folder, and will be copied to"
echo " the proper folder."
echo " "
echo ' pygt_path=$(python3 -c "import pygenometracks as _ ; print(_.__path__) ")'
echo ' pygt_path="${pygt_path:2}"'
echo ' pygt_path="${pygt_path::-2}"'
echo ' sudo cp ./scripts/pyGenomeTracks_edited/makeTracksFile.py "${pygt_path}/"'
echo ' sudo cp ./scripts/pyGenomeTracks_edited/BigWigTrack.py "${pygt_path}/tracks/"'
echo ' sudo cp ./scripts/pyGenomeTracks_edited/GenomeTrack.py "${pygt_path}/tracks/"'
echo ' '
echo " "
echo " This installation program will install gnuplot. Gnuplot is not used in the "
echo " cut and run pipeline, but it seems to be used as a plotting tool for genomic data."
echo " As such, I figured it would be worthwhile to install. Gnuplot installation is broken"
echo " on WSL2 Ubuntu, and I found a fix after a few hours of searching."
echo " "
echo " sudo apt-get install gnuplot qtchooser"
echo " sudo strip --remove-section=.note.ABI-tag /usr/lib/x86_64-linux-gnu/libQt5Core.so.5"
echo " "
echo " Lastly, the cut and run folder will be moved to the /usr/softwares directory, and the"
echo " cut_run_pipeline.sh will be symbolically linked in the local bin as cutandrun."
echo " "
echo ' full_path=$(dirname $(realpath install_dependencies.sh))'
echo ' sudo cp -R "${full_path}" /usr/softwares'
echo ' sudo ln -s /usr/softwares/cut_run_pipeline/cut_run_pipeline_v3.sh /usr/local/bin/cutandrun'
echo ' sudo rm -r "${full_path}"'

echo " "
echo " If you DO want to proceed with the installation, simply press enter at the prompt below. "
echo " If you DO NOT want to proceed with the installation, type 'q' or 'quit' at the prompt below."
read quitters
if [ "${quitters:1}" == q ]
    then echo " Have a lovely day!"
    else echo " "
         echo " Installation beginning. Please press 'y' when prompted."
         echo " "

         sudo python3 -m pip install numpy scipy glob pyGenomeTracks macs3

         # The user should accept all of these installations

         sudo apt-get install bowtie2

         sudo apt-get install bedtools

         sudo apt-get install samtools

         sudo apt-get install bedops

         sudo apt-get install fastqc

         sudo apt-get install r-base-core

         sudo apt-get install tree

         # Now for the softwares directory

         sudo mkdir /usr/softwares

         # Installation of sambamba-0.8.0

         sudo wget https://github.com/biod/sambamba/releases/download/v0.8.0/sambamba-0.8.0-linux-amd64-static.gz -P /usr/softwares

         sudo gunzip /usr/softwares/sambamba-0.8.0-linux-amd64-static.gz

         sudo mv /usr/softwares/sambamba-0.8.0-linux-amd64-static /usr/softwares/sambamba-0.8.0

         sudo chmod +x /usr/softwares/sambamba-0.8.0

         sudo ln -s /usr/softwares/sambamba-0.8.0 /usr/local/bin/sambamba

         # installation of GenomeBrowser apps and symbolic link to bin

         sudo rsync -aP rsync://hgdownload.soe.ucsc.edu/genome/admin/exe/linux.x86_64/ /usr/softwares

         sudo ln -s /usr/softwares/bigWigToBedGraph /usr/local/bin/bigWigToBedGraph
         sudo ln -s /usr/softwares/bedGraphToBigWig /usr/local/bin/bedGraphToBigWig
         sudo ln -s /usr/softwares/bedClip /usr/local/bin/bedClip

         # Move all of the modified pyGenomeTracks items to the proper directory

         pygt_path=$(python3 -c "import pygenometracks as _ ; print(_.__path__) ")
         pygt_path="${pygt_path:2}"
         pygt_path="${pygt_path::-2}"

         sudo cp ./scripts/pyGenomeTracks_edited/makeTracksFile.py "${pygt_path}/"
         sudo cp ./scripts/pyGenomeTracks_edited/BigWigTrack.py "${pygt_path}/tracks/"
         sudo cp ./scripts/pyGenomeTracks_edited/GenomeTrack.py "${pygt_path}/tracks/"

         # installation of gnuplot. This isn't used, but seems to be helpful in the field.

         sudo apt-get install gnuplot qtchooser
         sudo strip --remove-section=.note.ABI-tag /usr/lib/x86_64-linux-gnu/libQt5Core.so.5

         # Move the cut and run folder to softwares and symbolic link it up.

         full_path=$(dirname $(realpath install_dependencies.sh))

         IFS="/" read -ra ADDR <<< "${full_path}"
         folder="${ADDR[-1]}"

         sudo cp -R "${full_path}" /usr/softwares

         sudo ln -s "/usr/softwares/${folder}/cut_run_pipeline_v3.sh" /usr/local/bin/cutandrun

         sudo rm -r "${full_path}"

         echo " Installation complete. To use the cut and run pipeline, simply type 'cutandrun' "
         echo " into the command line, and follow the instructions :) "

fi
