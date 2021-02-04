#!/bin/bash

# Want the user to have the option of using fastqc to view
# their files. Required arguments:
# DEPRICATED -m multi_align  ->   Fed in from cut_run_pipeline_v3
# -f fastq_dir    ->   Directory to fastq files OR folders w/ files

# Use getops syntax for optional inputs
while getopts f: options
do
case "${options}"
in
f) A=${OPTARG};;
esac
done

# Assign the optional input if given, otherwise None
fastq_dir=${A:-None}

# If the directory is not given
if [ "${fastq_dir}" == None ]
    then echo " "
         echo " You have not given a directory containing folders of FASTQ files."
         echo " "
         echo " Please input the file path to the directory containing folders"
         echo " containing FASTQ files (note, they should be gzipped)"
         echo " "
         read fastq_dir
         echo " "
         echo " Your answer: $fastq_dir"
         echo " "
fi


echo " ====================BEGIN=========================="
echo " "
echo " Beginning FASTQC Analysis of FASTQ files in subfolders"
echo " of $fastq_dir"
echo " "
# Loop over the folders in the directory
for folder in "${fastq_dir}"/*
do
    # Make the fastqc output folder
    mkdir "${folder}/fastqc"
    # Loop over the .gz files in the directory
    for file in "${folder}"/*.gz
    do
        # If there are not .gz files in the directory
        if [ "${file}" == "${folder}/*.gz" ]
            # Then check for straight up fastq files instead
            then for f in "${folder}"/*.fastq
                 do
                     # If there was neither fastq or .gz files
                     if [ "${file}" == "${folder}/*.fastq" ]
                         # Then tell the user there are no valid files in the folder
                         then echo " There were no valid files in ${folder}"
                     # Otherwise, analyze the fastq file found
                     else fastqc -o "${folder}/fastqc" "$file"
                     fi
                 done
        # Otherwise, analyze the .gz file found
        else fastqc -o "${folder}/fastqc" "$file"
        fi
    done
    echo " "
    echo " Complete. Analysis can be found in the folder"
    echo " ${folder}/fastqc"
    echo " "
done
echo " ====================END============================"
