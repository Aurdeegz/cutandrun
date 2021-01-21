#!/bin/bash

while getopts f:m:s:n:p: options
do
case "$options"
in
f) A=${OPTARG};;
m) B=${OPTARG};;
s) C=${OPTARG};;
n) D=${OPTARG};;
p) E=${OPTARG};;
bt) F=${OPTARG};;
esac
done

foldpath_fastqs=${A:-None}
multi_align=${B:-None}
spike_ind_dir=${C:-None}
spike_ind_name=${D:-None}
presets=${E:-None}
#multiple_aligns_command=${F:-None}


if [ "${multi_align}" == None ]
    then echo " "
         echo " You have not indicated whether or not you are analyzing"
         echo " multiple experiments. Each experiment should be in a "
         echo " separate folders within the same folder path."
         echo " "
         stopper=0
         while [ $stopper -eq 0 ]
         do
             echo " Will you be analyzing multiple experiments (yes/no)?"
             echo " "
             read multi_align
             if [[ ( "${multi_align,,}" == yes ) || ( "${multi_align,,}" == no ) ]]
                 then stopper=1
             else echo " Your answer was neither yes nor no. Please try again."
                  echo " "
             fi
         done
fi

if [ "${foldpath_fastqs}" == None ]
    then echo " "
         echo " You have not given the directory of the experiment(s)"
         echo " to be analyzed."
         echo " "
         if [ "${multi_align,,}" == yes ]
             then echo " "
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
         elif [ "${multi_align,,}" == no ]
             then echo " "
                  echo " Because you are aligning FASTQ files from one experiment,"
                  echo " Please make sure that your directory has the following format:"
                  echo " "
                  echo " -path/to/folder/----|"
                  echo "                     |---A_sequence_file_R1.fastq.gz "
                  echo "                     |---A_sequence_file_R2.fastq.gz "
                  echo "                                         "
                  echo " "
                  echo " (If there is more than one sequencing file set per experiment, just put"
                  echo " all of them into the same folder)."
                  echo " "
                  echo " Please input the directory path to the folder containing folders of"
                  echo " paired-end sequencing sets (path/to/folder  in the diagram above, no "
                  echo " / character at the end)"
                  echo " "
                  read foldpath_fastqs
                  echo " "
                  echo " Your answer: $foldpath_fastqs"
                  echo " "
         fi
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


if [ "${multi_align,,}" == yes ]
    then count=0
         for folder in "${foldpath_fastqs}"/*
         do
         r1_files=""
         r2_files=""

         save="${folder}/spikein_alignment_${count}"
         savesam="${save}.sam"
         for file in "${folder}"/*.gz
         do
         if [[ "${file}" == *"_R1"* ]]
             then r1_files="${r1_files},${file}"
         elif [[ "${file}" == *"_R2"* ]]
             then r2_files="${r2_files},${file}"
         fi
         done

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

elif [ "${multi_align,,}" == no ]
    then # Get the directory and name of the save file, which is the same folder
         # containing the paired end sequence files with the name
         # alignment_${align_counter}.sam. The user is free to change these
         # names after the end of the program.
         save="${foldpath_fastqs}/spikein_alignment"
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
             if [[ "${f}" == *"_R1" ]]
                 then r1_files="${r1_files},$f"
             elif [[ "${f}" == *"_R2" ]]
                 then r2_files="${r2_files},$f"
             fi
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
        bowtie_args="-x ""${spike_ind_dir}/${spike_ind_name}""${fileline}"" -S ""${savesam}"" ${presets}"
        bowtie2 "$bowtie_args" &> "${foldpath_fastqs}/bowtie2_output/spikein_align.txt"

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

fi
























