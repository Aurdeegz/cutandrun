#!/bin/bash

# Use getopts to get the optional inputs
while getopts i:f:p: option
do
case "${option}"
in
i) A=${OPTARG};;
f) B=${OPTARG};;
p) C=${OPTARG};;
esac
done

# If no optional inputs are given assign none to
# the corresponding variables
ind_name=${A:-None}
foldpath_fastqs=${B:-None}
presets=${C:-None}


# If a value for the index name is not give
if [ $ind_name == None ]
    # Then ask the user for the filepath to the index
    then echo " Please enter the filepath to the bowtie2 index"
         echo " including the index name but NOT the file extension"
         echo " (ex: drosophila_genome/flygenes)"
         read ind_name
         echo " "
         echo " Your answer: $ind_name"
         echo " "
fi

# If a value for the folder containing fastq.gz files is not given
if [ $foldpath_fastqs == None ]
    # Then ask the user for that filepath
    then echo " Please enter the filepath to the folder containing"
         echo " the paired-end fastq files to be aligned."
         read foldpath_fastqs
         echo " "
         echo " Your answer: $foldpath_fastqs"
         echo " "
fi

# If a bowtie2 alignment option is not given
if [ "${presets}" == None ]
    # Then print the bowtie2 help to show the user options
    then printf "================================================================================="
         printf "\n"
         printf "\n"
         printf "\n"
         bowtie2 --help
         printf "\n"
         printf "\n"
         printf "\n"
         printf "================================================================================="
         printf "\n"
         printf "\n"
         printf "\n"
         printf "\n This program uses bowtie2 to align sequences with a reference genome."
         printf "\n Bowtie2 takes many options which can be changed during the alignment of sequences."
         printf "\n This program has preset options, which are shown below"
         printf "\n "
         printf "\n --local --very-sensitive-local --no-unal --no-mixed --no-discordant --phred33 -I 10 -X 700"
         printf "\n "
         printf "\n You, as the user, are welcome to change these settings if you choose to."
         printf "\n To change the settings, refer to the commands listed above, or find the "
         printf "\n bowtie2 manual online (just google it and you will find it)."
         printf "\n WARNING: This program may fail if you use your own settings. This program"
         printf "\n has been tested using the preset settings, and they will work."
         printf "\n "

         # Ask the user whether or not they would like to use the given preset values
         echo "Would you like to use the preset values for bowtie2 alignment (yes/no)?"
         read presets
         echo " "
         echo " Your answer: $presets"
         echo " "

         # If they do want to use the preset values
         if [ "${presets,,}" == yes ]

             # then assign the bowtie2 alignment values defined in the paper
             # Targeted in situ genome wide profiling with high efficiency for low cell numbers
             # by Skene et al.
             then presets="--local --very-sensitive-local --no-unal --no-mixed --no-discordant --phred33 -I 10 -X 700"
                  echo " "
                  echo " Alignment settings: $presets"
                  echo " "
             # Otherwise, ask the user for the settings they would like to use
             else echo "Please input the bowtie2 settings you would like to use for alignment."
                  read presets
                  echo " "
                  echo " Alignment settings: $presets"
                  echo " "
         fi
fi


# Get the directory and name of the save file, which is the same folder
# containing the paired end sequence files with the name
# alignment_${align_counter}.sam. The user is free to change these
# names after the end of the program.
save="${foldpath_fastqs}/alignment"
savesam="${save}.sam"

# Initialize the string that will hold the forwards and backwards
# alignments parameters in bowtie2. The format for the string is
#  -1 path/to/file_R1.fastq.gz -2 path/to/file_R2.fastq.gz


r1_files=""
r2_files=""

# Loop over each file in the folder. The folder should consist of
# all R1 and R2 files from the given experiment
for f in "${foldpath_fastqs}"/*.gz
do

    # Make a temporary file variable. The first time I made one of
    # these loops, all changes I made to $f were saved, so this
    # was my work around
    file="$f"

    # IFS is the delimiter for the string. We split the string on
    # _ and save the strigns to an array, then loop over the
    # items in the array.
    IFS="_"
    read -ra ADDR <<< "$f"
    for item in "${ADDR[@]}"
    do

        # Get the first two letters of the string. All of the
        # files have R1 or R2 immediately after a _
        item="${item:0:2}"

        # The syntax in the bracket is to lower the string.
        # If we find R1 or R2, then we need to save that file
        # to the r1_files or r2_files string, respectively.
        if [ "${item,,}" == r1 ]
            then r1_files="${r1_files},${file}"
            elif [ "${item,,}" == r2 ]
            then r2_files="${r2_files},${file}"
        fi
    done
done

fileline=" -1 ${r1_files:1} -2 ${r2_files:1}"

echo "===============================BEGIN================================================ "
echo " "
echo " "
echo " Alignment begining..."
echo " "
echo " "

# Create the bowtie2 parameter string in the format
# -x path/to/index_name -1 path/to/file_R1.fastq.gz -2 path/to/file_R2.fastq.gz [PRESETS]
bowtie_args="-x ""${ind_name}""${fileline}"" -S ""${savesam}"" ${presets}"
bowtie2 "$bowtie_args"

echo " "
echo " "
echo " Alignment complete..."
echo " Saved as ${savesam} "
echo " "
echo " "
echo "===============================END================================================== "

# Name of the temporary bam file
savebam="${save}.bam"

echo "===============================BEGIN================================================ "
echo " "
echo " "
echo " SAM file converted to temporary BAM file using"
echo " "
echo " samtools view -h -S -b -o ${savebam} ${savesam}"

# Covert the sam file to a bam file and save it as temporary name
samtools view -h -S -b -o "${savebam}" "${savesam}"

echo " "
echo " "
echo "===============================END================================================== "

# Name of the sorted bam file, which is NOT temporary
savesortbam="${save}_sorted.bam"

echo "===============================BEGIN================================================ "
echo " "
echo " "
echo " BAM file sorted and saved using"
echo " "
echo " sambamba sort -t 2 -o  ${savesortbam} ${savebam}"

# Sort the bam file, and save it to sorted.bam
sambamba sort -t 2 -o "${savesortbam}" "${savebam}"

echo " "
echo " "
echo "===============================END================================================== "

echo "===============================BEGIN================================================ "
echo " "
echo " "
echo " sorted BAM file filtered using the following criteria"
echo " "
echo " sambamba view -t 2 -h -f -F [XS] == null and not unmapped and not duplicate ${savesortbam}>${savebam}"

# Filter the sorted bam based on the criteria below
sambamba view -t 2 -h -f -F "[XS] == null and not unmapped and not duplicate" "${savesortbam}">"${savebam}"

echo " "
echo " "
echo "===============================END================================================== "

# Remove the temporary bam file.
rm "${savebam}"

echo "==================================================================================== "
echo " "
echo " "
echo " The alignment is complete. IF this is all you are doing,"
echo " check the directories with the fastq.gz files for your "
echo " alignment.sam files, as well as the sorted .bam files."
echo " "
echo " "
echo "==================================================================================== "
