#!/bin/bash

#Then ask the user for the directory containing the sequences
echo "Please enter the directory with the index sequences"
read b_index

# Create a cumulative variable named files. This will hold
# all of the paths/to/files.fasta needed for bowtie2-build
files=""

# Tell the user which files were located while populating
# the files variable
printf "\n Files found in the given index directory:\n"
for entry in "$b_index"/*
do
    files="$entry"",${files}"
    printf "$entry\n"
done

# Ask the user to name the index you are about to create
echo "Please enter the name you would like to give the new index"
read ind_name

# Save the index in the same filepath as the original genome sequences
ind_name="$b_index""/""$ind_name"

# Run bowtie2-build <path/to/file1.fasta,path/to/file2.fasta,...,path/to/filen.fasta> <path/to/ind_name>
bowtie2-build "$files" "$ind_name"

printf "\n "
printf "\n Your index files are"
printf "\n "

for fil in "$b_index"/*.bt2
do
    printf "\n $fil"
done
printf "\n "
printf "\n are your index files. When using them with in bowtie2,"
printf "\n type ${ind_name} (directory to them, plus the name but"
printf "\n NOT the file extension)."
