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

if [ $ind_name == None ]
    then echo " Please enter the filepath to the bowtie2 index"
         echo " including the index name but NOT the file extension"
         read ind_name
         echo " "
         echo " Your answer: $ind_name"
         echo " "
fi

if [ $foldpath_fastqs == None ]
    then echo " Please enter the filepath to the folder "
         echo " containig the fastq files to be aligned."
         echo " NOTE: if aligning multiple sequences,"
         echo " then enter the filepath to the folder "
         echo " containing folders of paired end fastq.gz files"
         read foldpath_fastqs
         echo " "
         echo " Your answer: $foldpath_fastqs"
         echo
fi

if [ "${presets}" == None ]
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
         printf "\n"
         printf "\n --local --cvery-sensitive-local --no-unal --no-mixed --no-discordant --phred33 -I 10 -X 700"
         printf "\n"
         printf "\n You, as the user, are welcome to change these settings if you choose to."
         printf "\n To change the settings, refer to the commands listed above, or find the "
         printf "\n bowtie2 manual online (just google it and you will find it)."
         printf "\n WARNING: This program may fail if you use your own settings. This program"
         printf "\n has been tested using the preset settings, and they will work."
         printf "\n"
         echo "Would you like to use the preset values for bowtie2 alignment (yes/no)?"
         read presets
         echo " "
         echo " Your answer: $presets"
         echo " "
         if [ "${presets,,}" == yes ]
             then presets="--local --very-sensitive-local --no-unal --no-mixed --no-discordant --phred33 -I 10 -X 700"
                  echo " "
                  echo " Alignment settings: $presets"
                  echo " "
             else echo "Please input the bowtie2 settings you would like to use for alignment."
                  read presets
                  echo " "
                  echo " Alignment settings: $presets"
                  echo " "
         fi
fi

# A counter used for naming multiple alignment files.
align_count=0
# loop over the folders int he given folderpath
for fold in "$foldpath_fastqs"/*
do

    mkdir "${fold}/bowtie2_output"

    #Get the directory and name of the save file, which is the same folder
    # containing the paired end sequence files with the name
    # alignment_${align_counter}.sam. The user is free to change these
    # names after the end of the program.
    save="${fold}/alignment_${align_count}"
    savesam="${save}.sam"

    # Initialize the string that will hold the forwards and backwards
    # alignments parameters in bowtie2.
    r1_files=""
    r2_files=""

    # Loop over each file in the folder. The folder should consist of
    # all R1 and R2 files from the given experiment
    for f in "${fold}"/*.gz
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

    echo "================================BEGIN=============================================== "
    echo " "
    echo " "
    echo " Alignment begining..."
    echo " "

    # Create the bowtie2 parameter string in the format
    # -x path/to/index_name -1 path/to/file_R1.fastq.gz -2 path/to/file_R2.fastq.gz [PRESETS]
    bowtie_args="-x ""${ind_name}""${fileline}"" -S ""${savesam}"" ${presets}"
    bowtie2 "$bowtie_args" &> "${fold}/bowtie2_output/align_${align_count}.txt"

    echo " Alignment complete..."
    echo " Saved as ${savesam} "
    echo " "
    echo " "
    echo "================================END================================================= "

    # Name of the temporary bam file
    savebam="${save}.bam"

    echo "================================BEGIN=============================================== "
    echo " "
    echo " "
    echo " SAM file converted to temporary BAM file using"
    echo " "
    echo " samtools view -h -S -b -o ${savebam} ${savesam}"

    # Convert the sam file to the temporary bam file. Sam file is unchanged
    samtools view -h -S -b -o "${savebam}" "${savesam}"

    echo " "
    echo " "
    echo "================================END================================================= "

    # Name of the sorted bam file. NOT temporary
    savesortbam="${save}_sorted.bam"

    echo "================================BEGIN=============================================== "
    echo " "
    echo " "
    echo " BAM file sorted and saved using"
    echo " "
    echo " sambamba sort -t 2 -o  ${savesortbam} ${savebam}"

    # Sort the temporary bam file and save it as the sorted.bam file
    sambamba sort -t 2 -o "${savesortbam}" "${savebam}"

    echo " "
    echo " "
    echo "================================END================================================= "

    echo "================================BEGIN=============================================== "
    echo " "
    echo " "
    echo " sorted BAM file filtered using the following criteria"
    echo " "
    echo " sambamba view -t 2 -h -f -F [XS] == null and not unmapped and not duplicate ${savesortbam}>${savebam}"

    # Filter the sorted bam file based on these criteria
    sambamba view -t 2 -h -f -F "[XS] == null and not unmapped and not duplicate" "${savesortbam}">"${savebam}"

    echo " "
    echo " "
    echo "================================END================================================= "

    bed_out="${save}.bg"

    echo "==========================BEGIN================================"
    echo " "
    echo " "
    echo " BAM file converted to bedgraph format using the command"
    echo " bedtools genomecov -bg -ibam -pc $savesortbam>$bed_out"
    echo " "

    bedtools genomecov -bg -pc -ibam "$savesortbam">"$bed_out"

    sort -k1,1 -k2,2n "${bed_out}" > "${save}_sorted.bg"

    echo " Bedgraph format: Chromosome strand_start strand_end BG_value"
    echo " "
    echo " "
    echo "==========================END=================================="


    # This bam file is temporary, and can be deleted at the very end.
    rm "${savebam}"
    rm "${save}.bg"
    mkdir "${fold}/temp_files"
    # Increase the align count by one
    align_count=$(($align_count + 1))
done

echo "==================================================================================== "
echo " "
echo " "
echo " The alignment is complete. IF this is all you are doing,"
echo " check the directories with the fastq.gz files for your "
echo " alignment.sam files, as well as the sorted .bam files."
echo " "
echo " "
echo "==================================================================================== "
