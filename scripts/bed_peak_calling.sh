#!/bin/bash

# This program will perform peak calling as layed out in
# https://github.com/Henikoff/Cut-and-Run/blob/master/py_peak_calling.py
# Merging peaks will be the standard, for now. Eventually I will add some
# other features to this

#Use GETOPTS command to get the optional arguments from the user.
while getopts b:m:t:min:max:ipd:o: option
do
case "${option}"
in
b) A=${OPTARG};;
m) B=${OPTARG};;
t) G=${OPTARG};;
min) C=${OPTARG};;
max) D=${OPTARG};;
ipd) E=${OPTARG};;
o) F=${OPTARG};;
#bo) H=${OPTARG};; was going to ask for a bedfile output name, decided not to
esac
done

# Use the default syntax to assign values to all variables the user does not
# input into the script.

bam=${A:-None}
multi_align=${B:-None}
declare -i threshold=${G:-69}
declare -i min_length=${C:-69}
declare -i max_length=${D:-100000}
declare -i inter_peak_distance=${E:-69}
output_file=${F:-None}
#bed_out=${H:-bed_output.bg}

echo "==================================================================================== "
echo " "
echo " "
echo " Begining peak calling. This program uses the algorithm defined by the Henikoff lab"
echo " (https://github.com/Henikoff/Cut-and-Run/blob/master/py_peak_calling.py)"
echo " however it is adapted to run as a bash script and not as a Python script."
echo " "
echo " "
echo "==================================================================================== "

# If a BAM file is not given, ask the user to direct the program to a BAM
# file. If the user is analyzing multiple BAM files, then direct the program
# to the directory containing folders, each with a BAM file.
if [ "$bam" == None ]
    then echo " Please input the path to the folder containing"
         echo " the sorted bam file to be analyzed."
         echo " NOTE: If you wish to analyze multiple bam files,"
         echo " then input the path to folders containing the bedgraph files."
         echo " "
         echo " Please make sure that each folder contains only the sorted"
         echo " and filtered BAM file, not the temporary BAM file."
         read bam
         echo " "
         echo " Your answer: $bam"
         echo " "
fi

# If the user does not specify whether they are analyzing multiple BAM files
if [ "$multi_align" == None ]
    # Then ask the user whether or not they are analyzing multiple BAM files,
    # and only end when they give a yes or no answer.
    then stop=0
#         echo "$multi_align"
         while [ $stop -eq 0 ];
         do
             echo " Are you analyzing multiple bam files (yes/no)?"
             read multi_align
             echo " "
             echo " Your answer: $multi_align"
             echo " "
             if [ "${multi_align,,}" == yes ]
                 then stop=1
                      echo " Please make sure that your bam files are all in separate folders,"
                      echo " and that all of those folders are in the same filepath"
                      echo " (example: path/to/folder/containing/files)"
                 elif [ "${multi_align,,}" == no ]
                 then stop=1
                 else echo " That was not a yes or no answer. Please try again."
             fi
         done
fi

# If the user did not give a threshold value for the minimum number of
# continuous bases required for a peak to be evaluated
if [ $threshold -eq 69 ]
    # Then ask the user to provide that minimum threshold value.
    then echo " Please input the threshold for the minimum number of continuous"
         echo " bases required to be considered a bonifide sequence."
         echo " (NOTE: Only integers, no floating point numbers or string characters)"
         read threshold
         echo " "
         echo " Your answer: $threshold"
         echo " "
         declare -i threshold=$threshold
fi

# If the user did not give a minimum width (minimum number of continuous
# bases above threshold)
if [ $min_length -eq 69 ]
    # Then ask the user to provide that minimum width
    then echo " Please enter the number of bases above the threshold"
         echo " that define the minimum width of a read to be considered."
         echo " (NOTE: Only integers, no floating point numbers or string characters)"
         read min_length
         echo " "
         echo " Your answer: $min_length"
         echo " "
         declare -i min_length=$min_length
fi

# If the user does not specify what the maximum width is
stop=0
while [ $stop -eq 0 ]
do
    # Then inform them that they may use the default value (currently it is very high)
    echo " This program defaults to a maximum width of $max_length."
    echo " Would you like to use this default value (yes/no)"
    read max_svar
    echo " "
    echo " Your answer: $max_svar"
    echo " "
    if [ "${max_svar,,}" == yes ]
        then echo " Using the default max width = ${max_length}"
             echo " "
             stop=1
        elif [ "${max_svar,,}" == no ]
        then echo " Please input the maximum width you would like to use."
             echo " (NOTE: Only integers, no floating point numbers or string characters)"
             read max_length
             echo " "
             echo " Your answer: ${max_length}"
             echo " "
             declare -i max_length=$max_length
             stop=1
        else echo " The answer given was not yes or no. Please try again."
    fi
done

# If the user does not provide the distance (nucleotides) which constitutes
# different peaks
if [ $inter_peak_distance -eq 69 ]
    # Then ask the user for the distance between unique peaks
    then echo " Please enter the allowable distnace between two adjacent peaks."
         echo " If peaks two peaks are closer than this distance, then they "
         echo " will be merged and their bedgraph scores will be summed."
         echo " (NOTE: Only integers, no floating point numbers or string characters)"
         read inter_peak_distance
         declare -i inter_peak_distance=$inter_peak_distance
         echo " "
         echo " Your answer: ${inter_peak_distance}"
         echo " "
fi


# If the user elects to evaluate multiple BAM files at the same
# time, then this is the decision path that will be used.

if [ "${multi_align,,}" == yes ]

    # First, loop over all of the folders in the given
    # file directory
    then for fold in "$bam"/*
         do

             # Second, loop over the BAM file within each folder.
             # If all portions of the program I wrote were used,
             # then the only BAM file in each folder should be the
             # filtered and sorted one.
             for bam_file in "$fold"/*.bam
             do

                 # This little loop splits the BAM file string
                 # by a period, saves this as an array, then
                 # loops over the items in the array. The first
                 # item in the array is the filepath and the
                 # name of the BAM file, and we use this to
                 # to make all temporary files used during peak
                 # calling.
                 IFS="."
                 read -ra ADDR <<< "$bam_file"
                 count=0
                 for path in "${ADDR[@]}"
                 do
                     if [ $count -eq 0 ]
                         then bed_out="${path}.bg"
                              output="${path}_peaks.bg"
                              temp="${path}_thr_step1.bg"
                              temp2="${path}_sort_step2.bg"
                              temp3="${path}_merge_step3.bg"
                              temp4="${path}_fltr_step4.bg"
                              count=$(($count + 1))
                     fi
                 done

                 # Get the directory path to the BAM file
                 directory=$(dirname "$bam_file")

                 # Make the string for the temporary file directory
                 temp_files="${directory}/temp_files"

                 # Make the string for the name of the settings text file
                 settings="${directory}/peak_call_settings.txt"

                 # Write the settings for peak caling to the settings file
                 echo "input file:   $bam_file " >> "$settings"
                 echo "output file:    $output" >> "$settings"
                 echo "threshold:    $threshold" >> "$settings"
                 echo "min length:    $min_length" >> "$settings"
                 echo "max length:    $max_length" >> "$settings"
                 echo "inter peak distance: $inter_peak_distance" >> "$settings"

                 echo "==========================BEGIN================================"
                 echo " "
                 echo " "
                 echo " BAM file converted to bedgraph format using the command"
                 echo " bedtools genomecov -bg -ibam $bam_file>$bed_out"
                 echo " "

                 bedtools genomecov -bg -ibam "$bam_file">"$bed_out"

                 echo " Bedgraph format: Chromosome strand_start strand_end BG_value"
                 echo " "
                 echo " "
                 echo "==========================END=================================="

                 echo "==========================BEGIN================================"
                 echo " "
                 echo " "
                 echo " BG file filtered based on BG value greater than threshold ($threshold)"
                 echo " "
                 echo " awk -v x=$threshold '$4 > x' $bed_out>$temp"

                 awk -v x=$threshold '$4 > x' "$bed_out">"$temp"

                 echo " "
                 echo " "
                 echo "==========================END=================================="

                 sort -k1,1 -k2,2n "$temp">"$temp2"

                 echo "==========================BEGIN================================"
                 echo " "
                 echo " "
                 echo " Merge sequences that are right next to one another, as those represent"
                 echo " reads within the same sequence or reigon"
                 echo " "
                 echo " bedtools merge -d 0 -c 4 -o sum -i $temp>$temp2"

                 bedtools merge -d 0 -c 4 -o sum -i "$temp2">"$temp3"

                 echo " "
                 echo " "
                 echo "==========================END=================================="

                 echo "==========================BEGIN================================"
                 echo " "
                 echo " "
                 echo " Filter the merged BG files based on the length of the sequences, keeping only"
                 echo " sequences between $min_length and $max_length"
                 echo " "
                 echo " "
                 echo " awk -v x=$min_length -v y=$max_length '$3 - $2 > x && $3 - $2 < y' $temp2>$temp3"

                 awk -v x=$min_length -v y=$max_length '$3 - $2 > x && $3 - $2 < y' "$temp3">"$temp4"

                 echo " "
                 echo " "
                 echo "==========================END=================================="

                 echo "========================BEGIN=================================="
                 echo " "
                 echo " "
                 echo " Merge peaks that are within $inter_peak_distance of one another"
                 echo " "
                 echo " "
                 echo " bedtools merge -d $inter_peak_distance -c 4 -o sum -i $temp4>$output"

                 bedtools merge -d $inter_peak_distance -c 4 -o sum -i "$temp4">"$output"
#                 sort -k1,1 "$output">"$output"

                 echo " "
                 echo " "
                 echo "========================END===================================="


                 mkdir "$temp_files"
                 mv "$temp" "$temp2" "$temp3" "$temp4" "$temp_files"
             done
         done
fi

# If the user is only analyzing one BAM file, then this
# decision path will be used
if [ "${multi_align,,}" == no ]

    # First, loop over the BAM file within the folder.
    # If all portions of the program I wrote were used,
    # then the only BAM file in each folder should be the
    # filtered and sorted one.
    then for bam_file in "$bam"/*.bam
         do

             # This little loop splits the BAM file string
             # by a period, saves this as an array, then
             # loops over the items in the array. The first
             # item in the array is the filepath and the
             # name of the BAM file, and we use this to
             # to make all temporary files used during peak
             # calling.
             IFS="."
             read -ra ADDR <<< "$bam_file"
             count=0
             for path in "${ADDR[@]}"
             do
                 if [ $count -eq 0 ]
                     then bed_out="${path}.bg"
                          output="${path}_peaks.bg"
                          temp="${path}_thr_step1.bg"
                          temp2="${path}_sort_step2.bg"
                          temp3="${path}_merge_step3.bg"
                          temp4="${path}_fltr_step4.bg"
                          count=$(($count +1))
                 fi
             done

             # Get the directory path to the BAM file
             directory=$(dirname "$bam_file")

             # Make the string for the temporary file directory
             temp_files="${directory}/temp_files"

             # Make the string for the name of the settings text file
             settings="${directory}/peak_call_settings.txt"

             echo "input file:    $bam_file" >> "$settings"
             echo "output file:    $output" >> "$settings"
             echo "threshold:    $threshold" >> "$settings"
             echo "min length:    $min_length" >> "$settings"
             echo "max length:    $max_length" >> "$settings"
             echo "inter peak distance:    $inter_peak_distance" >> "$settings"



             echo "==========================BEGIN================================"
             echo " "
             echo " "
             echo " BAM file converted to bedgraph format using the command"
             echo " bedtools genomecov -bg -ibam $bam_file>$bed_out"
             echo " "

             bedtools genomecov -bg -ibam "$bam_file">"$bed_out"

             echo " Bedgraph format: Chromosome strand_start strand_end BG_value"
             echo " "
             echo " "
             echo "==========================END=================================="

             echo "==========================BEGIN================================"
             echo " "
             echo " "
             echo " BG file filtered based on BG value greater than threshold ($threshold)"
             echo " "
             echo " awk -v x=$threshold '$4 > x' $bed_out>$temp"

             awk -v x=$threshold '$4 > x' "$bed_out">"$temp"

             echo " "
             echo " "
             echo "==========================END=================================="

             sort -k1,1 -k2,2n "$temp">"$temp2"

             echo "==========================BEGIN================================"
             echo " "
             echo " "
             echo " Merge sequences that are right next to one another, as those represent"
             echo " reads within the same sequence or reigon"
             echo " "
             echo " bedtools merge -d 0 -c 4 -o sum -i $temp>$temp2"

             bedtools merge -d 0 -c 4 -o sum -i "$temp2">"$temp3"

             echo " "
             echo " "
             echo "==========================END=================================="

             echo "==========================BEGIN================================"
             echo " "
             echo " "
             echo " Filter the merged BG files based on the length of the sequences, keeping only"
             echo " sequences between $min_length and $max_length"
             echo " "
             echo " "
             echo " awk -v x=$min_length -v y=$max_length '$3 - $2 > x && $3 - $2 < y' $temp2>$temp3"

             awk -v x=$min_length -v y=$max_length '$3 - $2 > x && $3 - $2 < y' "$temp3">"$temp4"

             echo " "
             echo " "
             echo "==========================END================================"

             echo "========================BEGIN=================================="
             echo " "
             echo " "
             echo " Merge peaks that are within $inter_peak_distance of one another"
             echo " "
             echo " "
             echo " bedtools merge -d $inter_peak_distance -c 4 -o sum -i $temp3>$output"

             bedtools merge -d $inter_peak_distance -c 4 -o sum -i "$temp4">"$output"

             echo " "
             echo " "
             echo "========================END===================================="

             mkdir "$temp_files"
             mv "$temp" "$temp2" "$temp3" "$temp4" "$temp_files"
         done
fi
