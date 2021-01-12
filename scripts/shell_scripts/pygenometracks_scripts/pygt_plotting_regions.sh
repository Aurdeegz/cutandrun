#!/bin/bash

# Use getopts to get the optional arguments
# for this scripts
while getopts b:g:m:p:a:l: option
do
case "${option}"
in
b) A=${OPTARG};;  # b) -> bedgraph file directory
g) C=${OPTARG};;  # g) -> .genome file directory
m) B=${OPTARG};;  # m) -> multiple file argument
p) D=${OPTARG};;  # p) -> path to write_overlay.py
a) E=${OPTARG};;  # annotation directory
l) F=${OPTARG};;  # list of annotations, comma separated
esac
done

# Set all of the inputs to the default value of None
bg_dir=${A:-None}
multi_align=${B:-None}
genome=${C:-None}
pathto=${D:-None}
annot_dir=${E:-None}
annot_list=${F:-gene,CDS}

# If the user gave a value for multi_align, then pass.
if [ "${multi_align,,}" == yes ]
    then echo " "
    elif [ "${multi_align,,}" == no ]
    then echo " "

    # If the user did not give a value, then ask them if they are plotting
    # multiple bigwig files from multiple directories.
    else echo " "
         echo " You have not indicated whether you will be plotting "
         echo " bigwig files from one folder or multiple folders in a"
         echo " directory. Here are the options for this program:"
         echo " "
         echo " MULTIPLE: The multiple option refers to using one directory"
         echo " that contains multiple folders, and within each folder is one"
         echo " or more bigwig files. This option is meant to work with "
         echo " the 'align_multiple' setting in cut_run_pipeline_v1.sh."
         echo " (NOTE: this option is equivalent to 'yes' in the question)"
         echo " "
         echo " SINGLE: The single option refers to using one folder that "
         echo " contains one or more bigwig files. This option is meant"
         echo " to be used with the cut_run_pipeline_v1.sh, where the user"
         echo " elects to align only one experiment with the reference genome."
         echo " (NOTE: this option is equivalent to 'no' in the question)"
         echo " "
         echo " "
         stop=1
         while [ $stop -eq 1 ]
         do
             echo " Are you finding the plotting bigwig files that in"
             echo " different folders (yes/no)?"
             read multi_align
             echo " "
             echo " Your answer: $multi_align"
             echo " "
             if [ "$multi_align" == yes  ]
                 then stop=0
                 elif [ "$multi_align" == no ]
                 then stop=0
                 else echo " "
                      echo " That was not a yes or no answer. Please try again."
                      echo " "
             fi
         done
fi

if [ "$bg_dir" == None ]

    # If the user is plotting bigwig files from one folder
    then if [ "${multi_align,,}" == no ]
             then echo " You have not given the filepath to the folder"
                  echo " containing the bigwig files to be plotted."
                  read bg_dir
                  echo " "
                  echo " Your answer: $bg_dir"
                  echo " "
    # If the user is plotting bigwig files from multiple folders
             elif [ "${multi_align,,}" == yes ]
             then echo " You have not given the filepath to the folders"
                  echo " holding the bigwig files to be plotted."
                  read bg_dir
                  echo " "
                  echo " Your answer: $bg_dir"
                  echo " "
         fi
fi

# IF the user did not give a value for the genome file
if [ "${genome}" == None ]
    then echo " "
         echo " You have not specified the location of a sorted reference genome."
         echo " A reference genome file should have the following structure:"
         echo " "
         echo " |------------------------|------------------------------------|"
         echo " | chromosome             |number_of_nucleotides_in_chromosome |"
         echo " |------------------------|------------------------------------|"
         echo " "
         echo " (for the example files, this is drosophila_genome/length_sort.genome)"
         echo " "
         echo " Please input the filepath to the sorted .genome file"
         read genome
         echo " "
         echo " Your answer: $genome"
         echo " "
fi

# IF the user did not give a path to the python file edit_tracksfile.py
if [ "${pathto}" == None ]
    then echo " "
         echo " You have not specified the filepath to genomtracks editing python files"
         echo " If you do not know where this file is, then you should take a minute to "
         echo " locate it. "
         echo " "
         echo " If you gitcloned the cut_run_pipeline, then the trackfile editing python files will"
         echo " be located in the 'scripts/python_files/trackfile_editing' folder, in the primary cut_run folder. "
         echo " "
         echo " If you ran the installation.sh file to install all required modules, then"
         echo " the python file folder will be located in ~/softwares/cut_run/scripts/python_files/trackfile_editing"
         echo " "
         read pathto
         echo " "
         echo " Your answer: $pathto"
         echo " "

fi

if [ "${annot_dir}" == None ]
    then echo " "
         echo " "
         echo " "
         read " "
         echo " "
         echo " Your answer: $annot_dir"
         echo " "
         if [ "${annot_dir,,}" == no ]
             then continue
         fi
fi

# functions for getting the height of the plots
get_highest_wrapper_bgfile () {
    region="$2"
    regionparts=($(echo $region | tr ":" "\n"))
    chrom="${regionparts[0]}"
    regions=($(echo ${regionparts[1]} | tr "-" "\n"))
    count=0
    declare -a holder
    files=($(echo ${1} | tr "," "\n" ))
    for file in "${files[@]}"
    do
        awk '{ if( "'$chrom'" == $1 && "'${regions[0]}'" <= $2 && "'${regions[1]}'" >= $3 ) { print } }' "${file}" > "temp.bg"
        next=$( get_highest_integer "temp.bg" "0" )
        holder[$count]=$next
        count=$(($count + 1))
    done
    outputty="0"
    for item in "${holder[@]}"
    do
        if [ "$item" -gt "$outputty" ]
            then outputty="$item"
        fi
    done
    echo "$outputty"
    rm "temp.bg"
}

get_highest_integer () {
    file="$1"
    highest="$2"
    while IFS= read -r line
    do
        if [ "$line" == "" ]
            then break
        else line=($( echo ${line} | tr $'\t' "\n" ))
             datavalue="${line[3]}"
             if [ "$highest" -lt "$datavalue" ]
                 then highest="$datavalue"
                      highest=$(($highest + 0))
             fi
        fi
    done <"${file}"
    echo "$highest"
}


if [ "${multi_align,,}" == "yes" ]
    then peak_files=None
         sorted_files=None

         count=0

         for folder in "${bg_dir}"/*
         do
         if [ "${folder}" == "${bg_dir}/tracks" ]
             then count=$(($count + 1))
                  continue
         else for file in "${folder}"/*.bg
              do

                  if [[ "${file}" == *"peaks"* ]]

                      then echo " current peakfile =    ${peak_files}"

                           if [ "${peak_files}" == None ]
                               then peak_files="${file}"
                                    echo " new peakfile :       ${peak_files}"
                           else peak_files="${peak_files},${file}"
                                echo " updating peaksfile"
                           fi
                      else if [ "${sorted_files}" == None ]
                               then sorted_files="${file}"
                           else sorted_files="${sorted_files},${file}"
                           fi
                  fi
              done
         fi
         done

         if [ "$count" != "1" ]
             then mkdir "${bg_dir}/tracks"
         fi

         regionsfile="${bg_dir}/tracks/plot_regions.txt"

#         echo " $peak_files        $genome           $regionsfile               "

         python3 "${pathto}/find_plot_regions.py" "${peak_files}" "${genome}" "${regionsfile}"

         while IFS= read -r line
         do

             line=($( echo ${line} | tr $'\t' "\n" ))
             chrom="${line[0]}"
             beginning="${line[1]}"
             ending="${line[2]}"
             chromregion="${chrom}:${beginning}-${ending}"

             echo " "
             echo " $chrom         $beginning           $ending              $chromregion"
             echo " "

             max_peaks=$(get_highest_wrapper_bgfile "${peak_files}" "${chromregion}")

             max_sorted=$(get_highest_wrapper_bgfile "${sorted_files}" "${chromregion}")

             maxs="${max_peaks},${max_sorted}"

             echo " "
             echo " $maxs "
             echo " "

             mkdir "${bg_dir}/tracks/${chrom}"

             if [ "${annot_dir}" == "no" ]
                 then python3 "${pathto}/write_overlay.py" "${peak_files},${sorted_files}" "${bg_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.ini" "true" "${maxs}"
                      pyGenomeTracks --tracks "${bg_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.ini" --region "${chromregion}" --outFileName "${bg_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.pdf"

             else for annot_file in "${annot_dir}"/*
                  do
                      annotes=($( echo ${annot_list} | tr "," "\n" ))
                      for annot in "${annotes[@]}"
                       do
                          if [[ "${annot_file}" == *"_${annot}."* ]]
                              then echo "we made it $annot_file "
                                   python3 "${pathto}/write_overlay.py" "${peak_files}" "${sorted_files}" "${annot_file}" "${bg_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}_${annot}.ini" "true" "${maxs}"

                                   echo " ${bg_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}_${annot}.ini"

                                   pyGenomeTracks --tracks "${bg_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}_${annot}.ini" --region "${chromregion}" --outFileName "${bg_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}_${annot}.pdf"
                              else echo " ${annot_file}"
                          fi
                       done
                  done
             fi
         done < "${regionsfile}"

elif [ "${multi_align,,}" == "no" ]
    then echo " "
fi


