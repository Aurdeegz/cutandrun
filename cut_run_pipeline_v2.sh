#!/bin/bash


# Ask the user whether or not to generate an index
# using bowtie2. If the user elects to do so, then the
# program will ask for a folder containing the reference
# sequence(s).
#
# When building my Drosophila reference, I downloaded
# fasta files for each chromosome individually.

echo " "
date
echo " "

stopper=0

# While loop ensures that the only answers given are yes or no
while [ $stopper -eq 0 ];
do
    echo " Would you like to create a bowtie2 index (yes/no)?"
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

         # Create a cumulative variable named files. This will hold
         # all of the paths/to/files.fasta needed for bowtie2-build
         files=""

         # Tell the user which files were located while populating
         # the files variable
         echo " Files found in the given index directory:\n"
         for entry in "$b_index"/*.fasta
         do
             files="$entry"",${files}"
             echo " $entry"
         done

         # Ask the user to name the index you are about to create
         echo " Please enter the name you would like to give the new index"
         echo " (example: flygenes)"
         read ind_name
         echo " "
         echo " Your answer: $ind_name"
         echo " "

         # Save the index in the same filepath as the original genome sequences
         ind_name="$b_index""/""$ind_name"

         # Run bowtie2-build <path/to/file1.fasta,path/to/file2.fasta,...,path/to/filen.fasta> <path/to/ind_name>
         bowtie2-build "$files" "$ind_name"

         echo "================================================================= "
         echo " "
         echo " "
         echo " Bowtie2 index built, saved in $ind_name with file extension .bt2"
         echo " "
         echo " bowtie2-build $files $ind_name"
         echo " "
         echo " "
         echo "================================================================= "

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

         python3 ./scripts/python_files/make_genomefile/count_genome_chars.py "$b_index" "false"
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
         python3 ./scripts/python_files/make_genomefile/count_genome_chars.py "$b_index" "false"
         sort -k1,1 "${b_index}/length.genome">"${b_index}/length_sort.genome"
         rm "${b_index}/length.genome"

         echo " "
         echo " "
         echo "================================================================="

fi

while [ $stopper -eq 1 ];
do
    echo " Do you plan to use gene annotations for region plotting?"
    echo " "
    read using_annotations
    echo " "
    echo " Your answer: $using_annotations"
    echo " "
    if [ "${using_annotations}" == yes ]
        then stopper=2
        elif [ "${using_annotations}" == no ]
        then stopper=2
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
         while [ $stopper -eq 2 ];
         do
             if [ "${annotations_made}" == yes ]
                 then stopper=3
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
                 then stopper=3
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
while [ $stopper -eq 3 ];
do
    # Ask the user if they have multiple sequences to align
    echo " Do you wish to align multiple Paired-End sequencing sets (yes/no)?"
    read align_multiple
    echo " "
    echo " Your answer: $align_multiple"
    echo " "
    # If the user is aligning multiple sequences or they are not, then end the loop
    if [ "${align_multiple,,}" == yes ]
        then stopper=4
        elif [ "${align_multiple,,}" == no ]
        then stopper=4
        # Otherwise, tell them that their input was invalid and try again
        else echo " That was not a yes or no answer. Please try again"
    fi
done




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
printf "\n -s alignment.sam --local --very-sensitive-local --no-unal --no-mixed --no-discordant --phred33 -I 10 -X 700"
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
    then presets="--local --very-sensitive-local --no-unal --no-mixed --no-discordant --phred33 -I 10 -X 700"
         echo " "
         echo " Alignment settings: $presets"
         echo " "
    # Otherwise, ask the user for the values they wish to use.
    else echo " Please input the settings you would like to use."
         read presets
         echo " "
         echo " Alignment settings: $presets"
         echo " "
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

         # Run the alignments using the bt2_multi_alignment script
         ./scripts/shell_scripts/bowtie2_scripts/bt2_multi_alignment.sh -i "$ind_name" -f "$foldpath_fastqs" -p "${presets}"

         # Call the peaks using the bed_peak_calling script.
         ./scripts/shell_scripts/bedtools_scripts/bed_peak_calling.sh -b "$foldpath_fastqs" -m "$align_multiple"

         # Turn the .bg files into .bw files (used for graphing)
         ./scripts/shell_scripts/bedtools_scripts/bed_bigwig_conversion.sh -b "$foldpath_fastqs" -g "${b_index}/length_sort.genome" -m "$align_multiple" -t made

         # Make some plots :)
         ./scripts/shell_scripts/pygenometracks_scripts/pygt_plotting_chroms.sh -b "$foldpath_fastqs" -g "${b_index}/length_sort.genome" -m "$align_multiple" -p "scripts/python_files/trackfile_editing"

         # Make some more plots :))
         ./scripts/shell_scripts/pygenometracks_scripts/pygt_plotting_regions.sh -b "$foldpath_fastqs" -g "${b_index}/length_sort.genome" -m "$align_multiple" -p "scripts/python_files/trackfile_editing" -a "${annot_dir}" -l "${annot_list}"

    # If the user is only aligning one set of paired end sequencing sets
    elif [ "${align_multiple,,}" == no ]

    # then get the filepath to the folder containing the two files
    then echo " Please input the filepath to the folder containing the paired end fastq.gz files."
         read foldpath_fastqs
         echo " "
         echo " Your answer: $foldpath_fastqs"
         echo " "

         # Run the alignment using the bt2_single_alignment
         ./scripts/bt2_single_alignment.sh -i "$ind_name" -f "$foldpath_fastqs" -p "$presets"

         # Call the peaks using the bed_peak_calling script.
         ./scripts/bed_peak_calling.sh -b "$foldpath_fastqs" -m "$align_multiple"

         # Turn the .bg files into .bw files (used for graphing)
         ./scripts/bed_bigwig_conversion.sh -b "$foldpath_fastqs" -g "${b_index}/length_sort.genome" -m "$align_multiple" -t made

         # Make some plots :)
         ./scripts/pygt_plotting_chroms.sh -b "$foldpath_fastqs" -g "${b_index}/length_sort.genome" -m "$align_multiple" -p ./scripts/

         # Make some more plots :))
         ./scripts/shell_scripts/pygenometracks_scripts/pygt_plotting_regions.sh -b "$foldpath_fastqs" -g "${b_index}/length_sort.genome" -m "$align_multiple" -p "scripts/python_files/trackfile_editing" -a "${annot_dir}" -l "${annot_list}"
fi
