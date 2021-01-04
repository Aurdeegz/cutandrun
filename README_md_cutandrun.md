Cut and Run Pipeline
=================

***A small bash script to plot preliminary cut and run data***

**Author:** *Kenneth P. Callahan*

# Table of Contents
1. [Introduction](#Introduction)
2. [Setting Things Up](#Setting-Things-Up)
    * [The Windows Subsystem for Linux (Ubuntu 20.04 LTS)](#The-Windows-Subsystem-for-Linux)
        - [Enabling WSL2](#Enabling-WSL2)
        - [Ubuntu 20.04 LTS on Windows 10](#Ubuntu-20.04-LTS-on-Windows-10)
        - [Navigating the Command Line (Basics)](#Navigating-the-Command-Line)
    * [Git Clone the Repository](#Git-Clone-the-Repository)
    * [Finding Your Reference Genome](#Finding-Your-Reference-Genome)
        - [NCBI Reference Genomes](#NCBI-Reference-Genomes)
        - [Downloading Each Chromosome](#Downloading-Each-Chromosome)
        - [Moving the Reference to the cutandrun Folder](#Moving-the-Reference-to-the-cutandrun-Folder)
    * [Running install_dependencies.sh](#Installing-Dependencies)
3. [Organizing Directories](#Organizing-Directories)
    * [Single Experiments](#Single-Experiments)
    * [Multiple Experiments](#Multiple-Experiments)
4. [Using the cutandrun Command](#Using-the-cutandrun-Command)
    * [Required Inputs](#Required-Inputs)
    * [Dependencies](#Dependencies)
5. [All Scripts](#All-Scripts)
    * [install_dependencies.sh](#install_dependencies.sh)
    * [cut_run_pipeline_v1.sh](#cut_run_pipeline_v1.sh)
    * [bed_bigwig_conversion.sh](#bed_bigwig_conversion.sh)
    * [bed_peakcalling.sh](#bed_peakcalling.sh)
    * [bt2_make_index.sh](#bt2_make_index.sh)
    * [bt2_multi_alignment.sh](#bt2_multi_alignment.sh)
    * [bt2_single_alignment.sh](#bt2_single_alignment.sh)
    * [pygt_plotting_chroms.sh](#pygt_plotting_chroms.sh)
    * [count_genome_chars.py](#count_genome_chars.py)
    * [edit_tracksfile.py](#edit_tracksfile.py)
6. [Bibliography](#Bibliography)

# Introduction

[\\]: <> (All aspects of survival, whether within multicellular or single celled organisms, relies on efficient, controlled regluation of transcription. Transcription factors, through interactions with DNA, can either promote or ablate RNA polymerase complex construction on a gene, directly influencing trascription and therefore cell functioning. As such, researchers are extremely interested in measuring these dynamic protein-DNA interaction to elucidate which transcription factors are active in response to different stimuli.)

This program does the entire process of cut and run data processing, up to preliminary plotting. The steps include
* Reference genome formatting (if it has not been done previously on your computer)
* Paired end sequence alignment with the reference genome (there is currently no option for single end alignments)
* Peak calling (using an algorithm found [here](https://github.com/Henikoff/Cut-and-Run/blob/master/py_peak_calling.py), but more on that in a later section).
* File format conversions (fastq.gz -> sam -> bam -> bedgraph -> bigwig) and temporary file storage (the temporary files are NOT automatically deleted, but more on that in a later section)
* Track file creation for gene region plots
* Plotting whole chromosomes

Beyond this program, there are still steps that should be taken. For example, researchers are often interested in which specific genes a transcription factor interacts with, which requires plotting more specific regions of the genome (amongst other things). However, the tracks file created in this program can be easily adapted for plotting specific genomic regions, and future versions of this program will include p- and q-value determination for called peaks. 



*It should be noted that I am new to shell scripting. This is the first full program I have written for the command line. As such, there are almost certainly aspects of this program that can be more efficient. I would love some feedback if anyone has done this before :)*

# Setting Things Up

This program was designed using the Windows Subsystem for Linux 2 (Ubnutu 20.04 LTS distribution). While many aspects of the program *should* work on other linux distributions, I do not think the install_dependencies.sh script will work on other linux distributions. Therefore, the set up for this program will outline exactly how I have my computer set up. I cannot promise that this program will work if your computer is configured differently. 

## The Windows Subsystem for Linux

The Windows Subsystem for Linux (WSL) is a linux command line interface that is integrated into the Windows 10 operating system. With WSL, users have (almost) full access to a Linux OS *within* Windows 10, rather than having to dualboot Windows and a Linux distribution. The WSL is therefore ideal for people who are familiar with linux, or who need the command line tools provided by major linux distributions. This subsection will focus on enabling WSL and installing Ubuntu 20.04 LTS.

### Enabling WSL

* Open "Settings", and navigate to "Apps"
* In "Related Settings", click "Programs and Features"
* On the left hand side of the window, click "Turn Windows features on or off" (requires administrative priveleges)
* Scroll down to "Windows Subsystem for Linux" and click the box next to it.
    - If you wish to use the Windows Susbsystem for Linux 2, you must also select the "Virtual Machine Platdform" option.
* Restart your computer to complete enabling WSL.

***This is sufficient to use the Windows Subsystem for Linux 1, which the cutandrun program works on. However, if you would like to update to the Windows Subsystem for Linux 2, please use the following steps:***

* Check the Windows Build Version by opening the command prompt (use the search bar on the bottom of your screen and type "cmd").
    - If you DO NOT have a 64 bit machine, then you cannot use WSL2.
    - If your version is BELOW 10.0.1863.1049 and you have a 64 bit machine, then navigate to "Updates and Security" in the settings and check for an update. If there are no available updates, then WSL2 is not supported on your machine. 
    - If your version is ABOVE 10.0.1863.1049, and you have a 64 bit machine, then proceed with the following steps.
* Download and run [this installation file](https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi). When prompted for administrative permissions, select 'yes'.
* Open the command prompt and type the following:
```
>wsl --set-default-version 2
```
* If you have a previously installed linux distribution and you have just updated to WSL2, then run the following command in the command prompt
```
>wsl --set-version <distribution-name> <wsl-version>
```
In my case, this was
```
>wsl --set-version Ubuntu 2
```

For a more detailed installation guide, see [the Microsoft WSL documentation](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
. With this, you should be ready to install a linux distribution.

### Ubuntu 20.04 LTS on Windows 10

For this guide, we will install and use Ubuntu 20.04 LTS. Ubuntu is a very popular, open source linux distribution that is well supported and includes many open source softwares. The acronym "LTS" stands for *Long Term Support*, and means that the distribution will recieve support for about five years. Therefore this distribution will be stable for the near future, and can easily be updated once another Ubuntu LTS is released. 

***Some users have described issues when using Ubuntu 20.04 LTS on WSL1. Personally, I never encountered any debilitating issues when using 20.04 LTS on WSL1, but it is good to be aware of this. If you are at all worried, then consider installing Ubuntu 18.04 LTS instead. You can always update from 18.04 to 20.04 later.***

To install Ubuntu 20.04 LTS on Windows 10:
* Open the Windows Store and search "Ubuntu"
* Click "Ubuntu 20.04 LTS" and select "Install".
* Once the installation is complete, either:
   - Click the start menu, navigate to Ubuntu, and open the application
   - Open the command prompt and type 'ubuntu2004' (if that does not work, try 'ubuntu'). 
* The first time you open the WSL, you will be asked for a username and a password. **These are extremely important. Do NOT forget them.**
* After supplying the username and password, Ubuntu will begin configuration. Wait for it to complete.
* You now have access to Ubuntu in Windows!!

### Navigating the Linux Command Line

This is a list of some simple tools available in the linux command line. They will likely be useful when using linux.

* `cd <directory-path>` change directory to the new directory path
* `pwd` prints the current working directory
* `mkdir <directory-path>` make a new directory with the given path
    * `mkdir <folder1> <folder2> ... <foldern>` create n folders in the current directory
* `rm <path-to-file>` delete the given file
    * `rm -r <path-to-folder>` delete entire folder (this can be a dangerous command)
* `ls` list the folders/files in the current directory
* `echo "some string"` print the string to the terminal
    * `echo "some string" > output.txt` print the string to the (newly created) file output.txt. If this file already exists, then it will overwrite the file.
    * `echo "some string" >> output.txt` print the string to the (newly created) file output.txt. If this file already exists, then it will write the string as a new line at the end of the file.
* `cat <file>` view the contents of a file.
    * `cat <file1> <file2> ... <filen>` view the contents of n files.
* `sudo <command> ` use root privelages to perform command
    * `sudo apt-get update` use root to update Ubuntu
    * `sudo apt-get upgrade` use root to upgrade all packages
    * `sudo apt-get install <package-name>` use root to install package
    * `sudo apt-get --purge remove <package-name>` use root to uninstall package 
* `mv [option] <path-to-origin> <path-to-destination>` move file from origin to destination
    * `mv -r <path-to-origin> <path-to-destination>` move folder from origin to destination
* `cp [option] <path-to-origin> <path-to-destination>` copy file from origin to destination
    * `cp -r <path-to-origin> <path-to-destination>` copy folder from origin to destination
* `git` : see [here](https://www.toolsqa.com/git/version-control-system/) for an introduction to the git version control system and GitHub.

For further information on a lot of these commands, see [this tutorial](https://ubuntu.com/tutorials/command-line-for-beginners#1-overview).

## Git Clone the Repository

In order to use the cutandrun command, you first need to clone my repository onto your computer. I would reccomend cloning the repository to the documents folder on your computer first. The commands would look something like this:
```
cd /mnt/c/Users/<cpu-username>/documents
git clone https://github.com/kendeegz/cutandrun.git
```
This will create a folder named 'cutandrun' in your documents directory, which has all files in the cutandrun GitHub directory. 

## Finding Your Reference Genome

Each sequencing project will require the proper reference genome. This subsection will be a guide to help you find the proper reference genome, how to download it, and where to put it for ease of use. 

### NCBI Reference Genomes

NCBI has a database of genomic information, organized by organism ([NCBI Genome Information by Organism](https://www.ncbi.nlm.nih.gov/genome/browse/#!/overview/)). To find your reference genome, simply search the scientific name of your organism, and select that organism from the list.

### Downloading Each Chromosome

### Moving the Reference to the cutandrun Folder

## Installing-Dependencies

# Organizing Directories

## Single Experiments

## Multiple Experiments

# Using the cutandrun Command

## Required Inputs

## Dependencies

# All Scripts

## install_dependencies.sh

## cut_run_pipeline_v1.sh

## bed_bigwig_conversion.sh

## bed_peakcalling.sh

## bt2_make_index.sh

## bt2_multi_alignment.sh

## bt2_single_alignment.sh

## pygt_plotting_chroms.sh

## count_genome_chars.py

## edit_tracksfile.py

# Bibliography


```python

```


```python

```
