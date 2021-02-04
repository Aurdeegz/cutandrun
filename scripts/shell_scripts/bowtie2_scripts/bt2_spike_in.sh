#!/bin/bash

while getopts f:s:n:p: options
do
case "$options"
in
f) A=${OPTARG};;
s) C=${OPTARG};;
n) D=${OPTARG};;
p) E=${OPTARG};;
bt) F=${OPTARG};;
esac
done

foldpath_fastqs=${A:-None}
spike_ind_dir=${C:-None}
spike_ind_name=${D:-None}
presets=${E:-None}

if [ "${foldpath_fastqs}" == None ]
    then echo " "
         echo " You have not given the directory of the experiment(s)"
         echo " to be analyzed."
         echo " "
         echo " "
         echo " Because you are aligning FASTQ files from multiple experiments,"
         echo " Please make sure that your directory has the following format:"
         echo " "
         echo " -path/to/folder/----|"
         echo "                     |"
         echo "                     |----trans_factor_rep_1/---|"
         echo "                     |                          |---A_sequence_file_R1.fastq.gz "
         echo "                     |                          |---A_sequence_file_R2.fastq.gz "
         echo "                     |                          "
         echo "                     |----trans_factor_rep_2/---|"
         echo "                     |                          |---B_sequence_file_R1.fastq.gz "
         echo "                     |                          |---B_sequence_file_R2.fastq.gz "
         echo "                     |                          "
         echo "                     |----igg_control_1/--------| "
         echo "                     |                          |---C_sequence_file_R1.fastq.gz  "
         echo "                     |                          |---C_sequence_file_R2.fastq.gz  "
         echo "                     |                      "
         echo "                     |----igg_control_2/--------|"
         echo "                                                |---D_sequence_file_R1.fastq.gz "
         echo "                                                |---D_sequence_file_R2.fastq.gz "
         echo "                                         "
         echo " "
         echo " (If there is more than one sequencing file set per experiment, just put"
         echo " all of them into the same folder)."
         echo " "
         echo " Please input the directory path to the folder containing folders of"
         echo " paired-end sequencing sets (path/to/folder  in the diagram above, no"
         echo " / character at the end)"
         echo " "
         read foldpath_fastqs
         echo " "
         echo " Your answer: $foldpath_fastqs"
         echo " "
fi

if [ "${spike_ind_dir}" == None ]
    then echo " "
         echo " You have not indicated the directory path to your 'spike in' genome."
         echo " Please input the directory path to your spike in genome"
         echo " "
         echo " (Example: genomes/ecoli/whole_genome)"
         echo " "
         read spike_ind_dir
         echo " "
         echo " Your answer: ${spike_ind_dir}"
         echo " "
fi

if [ "${spike_ind_name}" == None ]
    then echo " "
         echo " You have not indicated the directory path to your 'spike in' genome."
         echo " Please input the directory path to your spike in genome"
         echo " "
         echo " (Example: spike_index)"
         echo " "
         read spike_ind_name
         echo " "
         echo " Your answer: ${spike_ind_name}"
         echo " "
fi

if [ "${presets}" == None ]
    then echo " "
         echo " You have not provided settings to be used for bowtie2 sequence alignment."
         echo " The cut_run_pipeline_v3.sh program uses the following default values:"
         echo " "
         echo " --end-to-end --very-sensitive --no-mixed --no-discordant --phred33 -I 10 -X 700"
         echo " "
         echo " You are welcome to use other settings for the alignment, however it is"
         echo " CRITICAL that all settings between the spike in and experimental mapping "
         echo " are the same, except the spike in must include --no-dovetail and --no-overlap."
         echo " Therefore, the default spike in settings are"
         echo " "
         echo " --end-to-end --very-sensitive --no-dovetail --no-overlap --no-mixed --no-discordant --phred33 -I 10 -X 700"
         echo " "
         stopper=0
         while [ "${stopper}" -eq 0 ]
         do
         echo " Would you like to use the default settings (yes/no)?"
         echo " "
         read preset_svar
         if [ "${preset_svar,,}" == yes ]
             then stopper=1
                  presets="--end-to-end --very-sensitive --no-dovetail --no-overlap --no-mixed --no-discordant --phred33 -I 10 -X 700 -S alignment_spike.sam"
                  echo " "
                  echo " Using settings: $presets"
                  echo " "
         elif [ "${preset_svar,,}" == no ]
             then stopper=1
                  echo " What settings would you like to use for alignment?"
                  echo " "
                  read presets
                  echo " "
                  echo " Your answer: $presets"
                  echo " "
         else echo " Your answer was neither yes nor no. Please try again."
              echo " "
         fi
         done
fi

# Initialize the counting variable
count=0
# Loop over the folders in the folderpath given
for folder in "${foldpath_fastqs}"/*
do
    # Initialize the R1 and R2 file holder variables
    r1_files=""
    r2_files=""
    # Create the save using count and the output file name
    save="${folder}/spikein_alignment_${count}"
    savesam="${save}.sam"
    # Loop over the .gz files in the folder. Assumes the
    # user did not unzip the sequencing files.
    for file in "${folder}"/*.gz
    do
    # If the substring _R1 is in the file name
    if [[ "${file}" == *"_R1"* ]]
        # Then add it to the r1 files variable string
        then r1_files="${r1_files},${file}"
    # And if the file has the _R2 substring in it
    elif [[ "${file}" == *"_R2"* ]]
        # Then add it to the r2 files variable string.
        then r2_files="${r2_files},${file}"
    fi
    done

    # Now we create the file line to pass into Bowtie2.
    # the flag -1 is for r1 files, and the flag -2 is for r2 files.
    fileline=" -1 ${r1_files:1} -2 ${r2_files:1}"

    echo "================================BEGIN=============================================== "
    echo " "
    echo " "
    echo " Spike-In Alignment beginning..."
    echo " "
    bowtie_args="-x ${spike_ind_dir}/${spike_ind_name} ${fileline:1} ${presets} -S ${savesam}"
    bowtie2 $bowtie_args &> "${folder}/bowtie2_output/spike_in_align_${count}.txt"
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

    # This bam file is temporary, and can be deleted at the very end.
    rm "${savebam}"

    # Increase the align count by one
    count=$(($count + 1))

done
























