#!/bin/bash


# Ask the user whether or not to generate an index
# using bowtie2. If the user elects to do so, then the
# program will ask for a folder containing the reference
# sequence(s).
#
# When building my Drosophila reference, I downloaded
# fasta files for each chromosome individually.


get_array () {
    # This angers me on a new level :(
    string="$1"
    delim="$2"
    if [[ ( "${delim}" != "\t" ) || ( "${delim}" != "\n" ) ]]
        then IFS="$delim"
    else IFS=$'$delim'
    fi
    read -ra arrayy <<< "$string"
    for item in "${arrayy[@]}"
    do
        echo "$item"
    done
}

check_file_extension () {
    # Check the file extension of the file(s)

    declare -a extensions

    arr_count=0
    for f in "$1"/*
    do
        file=($( get_array "$f" "." ))
        if [[ ( ${#extensions} -eq 0 ) && ( ${#file} -gt 1 ) ]]
            then extensions[0]="${file[-1]}"
                 arr_count=$(( $arr_count + 1 ))
        else count=0
             for ext in "${extensions[@]}"
             do
                 if [ "$ext" == "${file[-1]}" ]
                     then count=$(( $count + 1 ))
                 fi
             done
             if [ $count -lt 1 ]
                 then extensions[$arr_count]="${file[-1]}"
             fi
             arr_count=$(( $arr_count + 1 ))
        fi
    done

    count=0
    exten=""

    for ext in "${extensions[@]}"
    do
        if [[ ( "${ext}" != "bt2" ) && ( "${ext}" != "genome" ) ]]
            then if [[ ( "${ext}" == "fa" ) || ( "${ext}" == "fna" ) || ( "${ext}" == faa ) || ( "${ext}" == ffa ) || ( "${ext}" == fasta ) && ("${ext}" != "${exten}" ) ]]
                     then count=$(( $count + 1 ))
                          exten="${ext}"
                 fi
        fi
    done

    if [[ ( $count -gt 1 ) || ( "${exten}" == "" ) ]]
        then echo "mixed"
    else echo "${exten}"
    fi

}


echo " "
date
echo " "

stopper=0

# While loop ensures that the only answers given are yes or no
while [ $stopper -eq 0 ];
do
    echo " Would you like to create a bowtie2 index for your REFERENCE GENOME (yes/no)?"
    read ind_ans
    echo " "
    echo " Your answer: $ind_ans"
    echo " "
    if [ "$ind_ans" == yes ]
        then stopper=1
        elif [ "$ind_ans" == no ]
        then stopper=1
        else echo " That was not a yes or no answer. Please try again"
    fi
done

# If the user elects to create a bowtie2 index
if [ "${ind_ans,,}" == yes ]

    #Then ask the user for the directory containing the sequences
    then echo " Please enter the directory with the genomic FASTA file(s)"
         echo " (example: drosophila/drosophila_genome)"
         read b_index
         echo " "
         echo " Your answer: $b_index"
         echo " "
         echo " "
         echo " Please enter the name you would like to give the index"
         echo " (Example: flygenes)"
         read ind_name
         echo " "
         echo " Your answer: $ind_name"
         echo " "

         ./scripts/shell_scripts/bowtie2_scripts/bt2_make_index.sh -d "${b_index}" -i "${ind_name}"

         ext=$( check_file_extension "${b_index}" )
         if [ "${ext}" == "mixed" ]
             then echo " Failed to make .genome file. exiting..."
                  exit
         fi


         echo "================================================================= "
         echo " "
         echo " "
         echo " Making the file length_sort.genome, which contains two columns"
         echo " <chormosome>    <length>"
         echo " and is sorted by the chromosome, using the commands"
         echo " "
         echo " python3 ./scripts/python_files/make_genomefile/count_genome_chars.py $b_index"
         echo " sort -k1,1 ${b_index}/length.genome>${b_index}/length_sort.genome"
         echo " rm ${b_index}/length.genome"

         python3 ./scripts/python_files/make_genomefile/count_genome_chars.py "$b_index" "false" "${ext}"
         sort -k1,1 "${b_index}/length.genome">"${b_index}/length_sort.genome"
         rm "${b_index}/length.genome"

         echo " "
         echo " "
         echo "================================================================="

# If the user decides not to construct an index , this means they have one
elif [ "${ind_ans,,}" == no ]

    # Ask the user for the filepath to the index. Do not include .bt2 in this
    # as bowtie2 handles this automatically.
    then echo " Please enter the directory which has the bowtie2 index"
         echo " (example: drosophila/drosophila_genome)"
         read b_index
         echo " "
         echo " Your answer: $b_index"
         echo " "
         echo " Please enter the name of the bowtie2 index."
         echo " (example: flygenes)"
         read ind_name
         echo " "
         echo " Your answer: $ind_name"
         echo " "
         ind_name="${b_index}/${ind_name}"

         ext=$( check_file_extension "${b_index}" )
         if [ "${ext}" == "mixed" ]
             then echo " Failed to make .genome file..."
                  exit
         fi
         echo " ext    $ext"
         echo "================================================================= "
         echo " "
         echo " "
         echo " Making the file length_sort.genome, which contains two columns"
         echo " <chormosome>    <length>"
         echo " and is sorted by the chromosome, using the commands"
         echo " "
         echo " python3 ./scripts/python_files/make_genomefile/count_genome_chars.py $b_index"
         echo " sort -k1,1 ${b_index}/length.genome>${b_index}/length_sort.genome"
         echo " rm ${b_index}/length.genome"

         python3 ./scripts/python_files/make_genomefile/count_genome_chars.py "$b_index" "false" "${ext}"
         sort -k1,1 "${b_index}/length.genome">"${b_index}/length_sort.genome"
         rm "${b_index}/length.genome"

         echo " "
         echo " "
         echo "================================================================="

fi

# While loop ensures that the only answers given are yes or no
while [ $stopper -eq 1 ];
do
    echo " Would you like to perform spike-in alignments/evaluation (yes/no)?"
    read spike_ans
    echo " "
    echo " Your answer: $spike_ans"
    echo " "
    if [ "${spike_ans,,}" == yes ]
        then stopper=2
        elif [ "${spike_ans,,}" == no ]
        then stopper=2
        else echo " That was not a yes or no answer. Please try again"
    fi
done

if [ "${spike_ans,,}" == yes ]
    then echo " "
         echo " You have indicated that you wish to use spike-in alignments/evaluation."
         echo " This requires the reference genome for the spike-in fragments (usually"
         echo " E. coli)."
         echo " "
         spike_stop=0
         while [ $spike_stop -eq 0 ];
         do
         echo " Has the bowtie2 index for the SPIKE-IN GENOME been created (yes/no)?"
         echo " "
         read spike_dir
         echo " "
         echo " Your answer: $spike_dir"
         echo " "
         if [ "${spike_dir}" == no ]
             then spike_stop=1
                  echo " "
                  echo " Please input the directory path to the spike-in genome FASTA file"
                  echo " (NOTE: It can be a gzipped file or it can be unzipped.)"
                  echo " "
                  read spike_dir
                  echo " "
                  echo " Your answer: $spike_dir"
                  echo " "
                  echo " "
                  echo " The bowtie2 index will be named 'spike_index'."
                  echo " "
                  spike_ind="spike_index"

                  ./scripts/shell_scripts/bowtie2_scripts/bt2_make_index.sh -d "${spike_dir}" -i "spike_index"

         elif [ "${spike_dir}" == yes ]
             then spike_stop=1
                  echo " "
                  echo " Please input the directory path to the spike-in index"
                  echo " (Without the index name)"
                  echo " "
                  read spike_dir
                  echo " "
                  echo " Your answer: $spike_dir"
                  echo " "
                  echo " "
                  echo " What is the name of your spike-in genome's bowtie2 index?"
                  echo " (IF generated via this program, it is called 'spike_index')"
                  echo " "
                  read spike_ind
                  echo " "
                  echo " Your answer: $spike_ind"
                  echo " "

                  spike_name="${spike_dir}/${spike_ind}"

         else echo " Your answer was neither yes nor no. Please try again."
              echo " "
         fi
         done
elif [ "${spike_ans,,}" == no ]
    then echo " "
         echo " Proceeding without spike-in evaluation."
         echo " "
fi




while [ $stopper -eq 2 ];
do
    echo " Do you plan to use gene annotations for region plotting?"
    echo " "
    read using_annotations
    echo " "
    echo " Your answer: $using_annotations"
    echo " "
    if [ "${using_annotations}" == yes ]
        then stopper=3
        elif [ "${using_annotations}" == no ]
        then stopper=3
        else echo " That was not a yes or no answer. Please try again"
    fi
done

if [ "${using_annotations}" == yes ]
    then echo " "
         echo " Have the parsed annotation files been created yet?"
         echo " (these files would be in a directory with names like annotation_<annotation_type>.bed6"
         echo " If you have this directory, then your answer should be yes. Otherwise, please download"
         echo " an annotation file in GFF format from NCBI, and place it in your desired directory)"
         echo " "
         read annotations_made
         echo " "
         echo " Your answer: $annotations_made"
         echo " "
         while [ $stopper -eq 3 ];
         do
             if [ "${annotations_made}" == yes ]
                 then stopper=4
                      echo " "
                      echo " You have indicated that your annotation files have been created."
                      echo " Please provide the filepath to your annotation file directory."
                      echo " (Example: drosophila/drosophila_annotations/annotation_types)"
                      echo " "
                      read annot_dir
                      echo " "
                      echo " Your answer: $annot_dir"
                      echo " "

                 elif [ "${annotations_made}" == no ]
                 then stopper=4
                      echo " "
                      echo " You have indicated that your annotation files have not been created."
                      echo " If you have not already downloaded the GFF format file for your genome,"
                      echo " please go to the NCBI genome browser "
                      echo " (https://www.ncbi.nlm.nih.gov/genome/browse#!/overview/)"
                      echo " find your organism, and download the annotations as a GFF file. Move"
                      echo " this gzipped file to your desired directory, and please input that"
                      echo " file path now."
                      echo " "
                      read annot_dir
                      echo " "
                      echo " Your answer: $annot_dir"
                      echo " "
                      echo " Creating your annotation_types directory"

                      ./scripts/shell_scripts/bedops_scripts/bps_make_filter_annotations.sh -d "${annot_dir}"

                      annot_dir="${annot_dir}/annotation_types"

                      echo " "
                      echo " The annotation file has been parsed and formatted to .bed6 files."
                      echo " Those files will be located in the following directory:"
                      echo " ${annot_dir}"
                      echo " Please DO NOT delete the fields.txt file. This is used to hold"
                      echo " the annotation types, and is used by the program in later steps"
                      echo " "

                 else echo " Your answer was not a yes or no answer. Please try again."
                      read annotations_made
             fi
         done
     echo " "
     echo " Your genome has the following annotations:"
     echo " "
     declare -a ants_allowed
     while IFS= read -r line;
     do
         echo " $line"
         ants_allowed+=("$line")
     done < "${annot_dir}/fields.txt"
     echo " "
     echo " Please input the annotations you would like to use, separated by commas."
     echo " NOTE: case sensitive, no spaces"
     echo " (Example: gene,CDS,lnc_RNA)"
     echo " "
     read annot_list
     echo " "
     echo " Your answer: $annot_list"
     echo " "
     holder="."
     IFS=","
     read -ra ARRD <<< "$annot_list"
     for annot in "${ARRD[@]}"
     do
         same="no"
         for allowed_annot in "${ants_allowed[@]}"
         do
             if [ "${annot}" == "${allowed_annot}" ]
                 then same="yes"
             fi
         done
         if [ "${same}" == "no" ]
             then echo " "
                  echo " $annot is not a valid annotation."
                  echo " "
             else if [ "${holder}" == "." ]
                      then holder="${annot}"
                  else holder="${holder},${annot}"
                  fi
         fi
     done

     if [ "${holder}" == "." ]
         then echo " "
              echo " No valid annotations were given. Proceeding without annotations"
              echo " "
              annot_dir="no"
              annot_list="no"
         else annot_list="${holder}"
     fi

elif [ "${using_annotations}" == no ]
    then echo " "
         echo " You have indicated that you do not want to proceed"
         echo " with annotations. Regions will therefore be plotted"
         echo " without annotations below."
         echo " "
         annot_dir="no"
         annot_list="no"
fi


# Once you have the index, ask the user if they are aligning one or multiple files
while [ $stopper -eq 4 ];
do
    # Ask the user if they have multiple sequences to align
    echo " Do you wish to align multiple Paired-End sequencing sets (yes/no)?"
    read align_multiple
    echo " "
    echo " Your answer: $align_multiple"
    echo " "
    # If the user is aligning multiple sequences or they are not, then end the loop
    if [ "${align_multiple,,}" == yes ]
        then stopper=5
        elif [ "${align_multiple,,}" == no ]
        then stopper=5
        # Otherwise, tell them that their input was invalid and try again
        else echo " That was not a yes or no answer. Please try again"
    fi
done


# If the align_multiple is yes, ask if there are control folders in the filepath
if [ "${align_multiple}" == yes ]
    then while [ $stopper -eq 5 ];
         do
             # Ask the user if they have multiple sequences to align
             echo " Are you including control folders in the directory?"
             echo " These controls would be used for MACS3 peak calling."
             read using_controls
             echo " "
             echo " Your answer: $using_controls"
             echo " "
             # If the user is aligning multiple sequences or they are not, then end the loop
             if [ "${using_controls,,}" == yes ]
                 then stopper=6
             elif [ "${using_controls,,}" == no ]
                 then stopper=6
             # Otherwise, tell them that their input was invalid and try again
             else echo " That was not a yes or no answer. Please try again"
             fi
         done
fi



printf "=============================================================================================\n"
printf "\n"
printf "\n"
printf "\n"
bowtie2 --help
printf "\n"
printf "\n"
printf "============================================================================================="
printf "\n"
printf "\n"
printf "\n"
printf "\n This program uses bowtie2 to align sequences with a reference genome. "
printf "\n Bowtie2 many options which can be changed during alignment of sequences."
printf "\n This program uses the preset values below:"
printf "\n --local --very-sensitive-local --no-unal --no-mixed --no-discordant --phred33 -I 10 -X 700"
printf "\n You, as the user, are welcome to input your own commands from the bowtie2 list above."
printf "\n Your input MUST be in the same format as the preset values, following the general "
printf "\n style defined here: http://bowtie-bio.sourceforge.net/bowtie2/manual.shtml#bowtie2-options-align-paired-reads"
printf "\n Be Warned: If you use your own settings, and they are incorrectly formatted,"
printf "\n then bowtie2 may fail. This program has been tested with the preset values."
printf "\n"
printf "\n"
printf "\n"


# Ask the user if they would like to use the preset values for the alignment.
# the presets come from the paper
# Targeted in situ genome-wide profiling with high efficiency for low cell numbers,
# by Peter J. Skene, Jorja G. Henikoff and Steven Henikoff

echo " Would you like to use the preset values for bowtie2 alignment?"
read presets
echo " "
echo " Your answer: $presets"
echo " "

# If the user wants to use the preset values
if [ "${presets,,}" == yes ]

    # Assign the preset values to the variable presets
    then presets="--end-to-end --very-sensitive --no-mixed --no-discordant --phred33 -I 10 -X 700"
         echo " "
         echo " Alignment settings: $presets"
         echo " "
         if [ "${spike_ans,,}" == yes ]
             then spike_presets="--end-to-end --very-sensitive --no-unal --no-dovetail --no-overlap --no-mixed --no-discordant --phred33 -I 10 -X 700"
         fi
    # Otherwise, ask the user for the values they wish to use.
    else echo " Please input the settings you would like to use."
         read presets
         echo " "
         echo " Alignment settings: $presets"
         echo " "
         if [ "${spike_ans,,}" == yes ]
             then spike_presets="${presets} --no-dovetail -- no-overlap"
         fi
fi

# This portion will actually perform the alignments. If the user elected to
# align multiple paired end sequences at the same time
if [ "${align_multiple,,}" == yes ]

    # then ask for the filepath to the folder containing folders of
    # paired end sequence files
    then echo " Please input the filepath to the folders containing"
         echo " each set of paired end fastq.gz files."
         read foldpath_fastqs
         echo " "
         echo " Your answer: $foldpath_fastqs"
         echo " "

         echo " "
         echo " Would you like the program to provide FASTQC analysis"
         echo " of your sequencing sets (OPTIONAL)?"
         echo " "
         read fastqc_svar
         if [ "${fastqc_svar,,}" == yes ]
             then ./scripts/shell_scripts/fastqc_scripts/fastqc_analysis.sh -m "${align_multiple}" -f "${foldpath_fastqs}"
         else echo " "
              echo " Proceeding without FASTQC analysis"
              echo " "
         fi

         # Run the alignments using the bt2_multi_alignment script
         ./scripts/shell_scripts/bowtie2_scripts/bt2_multi_alignment.sh -i "$ind_name" -f "$foldpath_fastqs" -p "${presets}"

         # Use macs3 to call peaks, including the controls if applicable.
         ./scripts/shell_scripts/macs3_scripts/macs3_callpeak_wrapper.sh -b "${foldpath_fastqs}" -m "${align_multiple,,}" -c "${using_controls,,}"

         if [ "${spike_ans,,}" == yes ]
             then ./scripts/shell_scripts/bowtie2_scripts/bt2_spike_in.sh -f "${foldpath_fastqs}" -m "${align_multiple}" -s "${spike_dir}" -n "spike_index" -p "${spike_presets}"
         fi

         # Need to add an analysis python file here. Loop through bowtie2_output folders, make
         # plots of alignment rates, depth (pairs aligned), fragments aligned (depth aligned 0 times)
         # for both experiments and controls; repeat for spike in

         # NO LONGER IN USE Call the peaks using the bed_peak_calling script.
         # ./scripts/shell_scripts/bedtools_scripts/bed_peak_calling.sh -b "$foldpath_fastqs" -m "$align_multiple"

         # Turn the .bg files into .bw files (used for graphing)
         ./scripts/shell_scripts/bedtools_scripts/bed_bigwig_conversion.sh -b "$foldpath_fastqs" -g "${b_index}/length_sort.genome" -m "$align_multiple" -t made

         # Make some plots :)
         ./scripts/shell_scripts/pygenometracks_scripts/pygt_plotting_chroms.sh -b "$foldpath_fastqs" -g "${b_index}/length_sort.genome" -m "$align_multiple" -p "scripts/python_files/trackfile_editing"

         # NEED TO UPDATE for narrowPeaks files   | Make some more plots :))
#         ./scripts/shell_scripts/pygenometracks_scripts/pygt_plotting_regions.sh -b "$foldpath_fastqs" -g "${b_index}/length_sort.genome" -m "$align_multiple" -p "scripts/python_files/trackfile_editing" -a "${annot_dir}" -l "${annot_list}" -u "${using_annotations}"

    # If the user is only aligning one set of paired end sequencing sets
    elif [ "${align_multiple,,}" == no ]

    # then get the filepath to the folder containing the two files
    then echo " Please input the filepath to the folder containing the paired end fastq.gz files."
         read foldpath_fastqs
         echo " "
         echo " Your answer: $foldpath_fastqs"
         echo " "

         echo " "
         echo " Would you like the program to provide FASTQC analysis"
         echo " of your sequencing sets (OPTIONAL)?"
         echo " "
         read fastqc_svar
         if [ "${fastqc_svar,,}" == yes ]
             then ./scripts/shell_scripts/fastqc_scripts/fastqc_analysis.sh -m "${align_multiple}" -f "${foldpath_fastqs}"
         else echo " "
              echo " Proceeding without FASTQC analysis"
              echo " "
         fi

         # Run the alignment using the bt2_single_alignment
         ./scripts/bt2_single_alignment.sh -i "$ind_name" -f "$foldpath_fastqs" -p "$presets"

         # NO LONGER IN USE Call the peaks using the bed_peak_calling script.
#         ./scripts/bed_peak_calling.sh -b "$foldpath_fastqs" -m "$align_multiple"

         # Use macs3 to call peaks, including the controls if applicable.
         ./scripts/shell_scripts/macs3_scripts/macs3_callpeak_wrapper.sh -b "${foldpath_fastqs}" -m "${align_multiple,,}" -c "${using_controls,,}"

         # Turn the .bg files into .bw files (used for graphing)
         ./scripts/bed_bigwig_conversion.sh -b "$foldpath_fastqs" -g "${b_index}/length_sort.genome" -m "$align_multiple" -t made

         # Make some plots :)
         ./scripts/pygt_plotting_chroms.sh -b "$foldpath_fastqs" -g "${b_index}/length_sort.genome" -m "$align_multiple" -p ./scripts/

         # NEED TO UPDATE for narrowPeaks fiels     |  Make some more plots :))
#         ./scripts/shell_scripts/pygenometracks_scripts/pygt_plotting_regions.sh -b "$foldpath_fastqs" -g "${b_index}/length_sort.genome" -m "$align_multiple" -p "scripts/python_files/trackfile_editing" -a "${annot_dir}" -l "${annot_list}"-u "${using_annotations}"
fi
