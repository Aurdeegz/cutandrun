#!/bin/bash

# This program will perform peak calling as layed out in
# https://github.com/Henikoff/Cut-and-Run/blob/master/py_peak_calling.py
# Merging peaks will be the standard, for now. Eventually I will add some
# other features to this

#Use GETOPTS command to get the optional arguments from the user.
while getopts b:m:c:o: option
do
case "${option}"
in
b) A=${OPTARG};;
m) B=${OPTARG};;
c) C=${OPTARG};;
o) F=${OPTARG};;
#bo) H=${OPTARG};; was going to ask for a bedfile output name, decided not to
esac
done

# Use the default syntax to assign values to all variables the user does not
# input into the script.

bam=${A:-None}
using_controls=${C:-no}
multi_align=${B:-None}
output_file=${F:-None}

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

check_foldtype () {
    # Check the folder string for the type of data
    fold="$1"
    allowed_ctrls=("control" "cont" "ctrl")
    allowed_exps=("experiment" "exp" "treatment" "treat" "enrichment" "enrich" "rep" "replicate")
    fold_type=None
    # Try experiments first
    for type in "${allowed_exps[@]}"
    do
        if [[ "${fold,,}" == *"$type"* ]]
            then fold_type="experiment"
                 break
        fi
    done
    # If not experiments
    if [ "${fold_type}" == None ]
        then for type in "${allowed_ctrls[@]}"
             do
                 if [[ "${fold,,}" == *"$type"* ]]
                     then fold_type="control"
                          break
                 fi
             done
    fi
    # Echo the foldtype
    echo "$fold_type"
}

check_replicate_num () {
    # get the two arrays.
    # Assumes: folder_name_stuff_experiment_identifier
    #          folder_name_stuff_control_identifier
    # IF the identifiers after exp/ctrl are the same,
    # This will return True
    local -n array_1=$1
    local -n array_2=$2
    array1_size=$(( ${#array_1[@]} - 1 ))
    array2_size=$(( ${#array_1[@]} - 1 ))
    for (( n=0; n<=$array1_size; n++ ))
    do
        foldtype_1=$( check_foldtype "${array_1[$n]}" )
        if [[ ( "${foldtype_1}" == "experiment" ) || ( "${foldtype_1}" == "control" ) ]]
            then foldplace_1=$(( $n + 1 ))
                 break
        fi
    done
    for (( n=0; n<=$array2_size; n++ ))
    do
        foldtype_2=$( check_foldtype "${array_2[$n]}" )
        if [[ ( "${foldtype_2}" == "experiment" ) || ( "${foldtype_2}" == "control" ) ]]
            then foldplace_2=$(( $n + 1 ))
                 break
        fi
    done
    # Check element after exp/ctrl

#    echo "a1 = ${array_1[$foldplace_1]}     a2 = ${array_2[foldplace_2]}"

    if [ "${array_1[$foldplace_1]}" == "${array_2[foldplace_2]}" ]
        then echo "True"
    else echo "False"
    fi
}

make_filepath () {
    # Given split filepath, return folderpath.
    # IF arg2 is true, then this is folder
    # IF false, then remove last element.
    local -n  path_array=$1

    if [ "$2" == "true" ]
        then loop_length=$(( ${#path_array[@]} - 1 ))
    else loop_length=$(( ${#path_array[@]} - 2 ))
    fi
    folder=""
    for n in "${!path_array[@]}"
    do
        if [ $n -gt $loop_length ]
            then break
        else folder="${folder}/${path_array[$n]}"
        fi
    done
    echo "${folder:1}"
}

# If the user elects to evaluate multiple BAM files at the same
# time, then this is the decision path that will be used.

if [[ ( "${multi_align,,}" == yes ) && ( "${using_controls,,}" == yes ) ]]

    # First, loop over all of the folders in the given
    # file directory
    then declare -a controls
         declare -a experiments
         declare -a no_folder_designation

         for fold in "$bam"/*
         do
             foldtype=$( check_foldtype "$fold" )
             echo " fold_type : $foldtype"
             # Second, loop over the BAM file within each folder.
             # If all portions of the program I wrote were used,
             # then the only BAM file in each folder should be the
             # filtered and sorted one.
             for bam_file in "$fold"/*.bam
             do
                 echo " bam : $bam_file"
                 if [ "${foldtype}" == "control" ]
                     then controls+=("${bam_file}")
                 elif [ "${foldtype}" == "experiment" ]
                     then experiments+=("${bam_file}")

                 elif [[ "${fold}" == *"tracks"* ]]
                     then echo " passing $fold : tracks folder"
                 else no_folder_designation+=("${bam_file}")
                 fi
             done
         done

         echo " controls : ${#controls[@]}    expers : ${#experiments[@]}   none : ${#no_folder_designation[@]}"

         if [[ ( ${#controls[@]} -eq ${#experiments[@]} ) && ( ${#no_folder_designation[@]} -eq 0 ) ]]
             then paired_paths=None
                  for path in "${experiments[@]}"
                  do
                      echo " path : $path"
                      exp_path=($( get_array "${path}" "/" ))

                      interest_fold=$((${#exp_path[@]} - 2 ))
                      interest_exp="${exp_path[${interest_fold}]}"
                      echo " interest_exp :    ${interest_exp}"
                      exp_fold_arrd=($( get_array "${interest_exp}" "_" ))
                      for cont in "${controls[@]}"
                      do
                          ctrl_path=($( get_array "${cont}" "/" ))
                          interest_ctrl="${ctrl_path[${interest_fold}]}"
                          echo " interest_ctrl :    ${interest_ctrl}"
                          ctrl_fold_arrd=($( get_array "${interest_ctrl}" "_" ))
                          same=$( check_replicate_num exp_fold_arrd ctrl_fold_arrd )

                          if [ "$same" == "True" ]
                              then paired_paths="-t ${path} -c ${cont}"
                                   break
                          fi
                      done

                      folder=$( make_filepath exp_path "false" )

                      if [ "${paired_paths}" != None ]
                          then macsdir="${folder}/macs3_out"

                               mkdir "${macsdir}"

                               macs3 callpeak ${paired_paths} -f BAM -n exp_w_ctrl -q 1 -B --call-summits -g dm --outdir "${macsdir}"

                               Rscript "${macsdir}/exp_w_ctrl_model.r"

                               mv "exp_w_ctrl_model.pdf" "${macsdir}/exp_w_ctrl_model.pdf"

                      elif [ "${paired_paths}" == None ]
                          then echo " "
                               echo " Unable to find paired experiment and control paths. Proceeding with"
                               echo " peak calling without using control sequencing data..."
                               echo " "
                               for fold in "${bam}"/*
                               do
                                   for bam_file in "${fold}"/*.bam
                                   do
                                       mkdir "${fold}/macs3_out"

                                       macs3 callpeak ${bam_file} -f BAM -n exp_no_ctrl -q 1 --call-summits -g dm --outdir "${fold}/macs3_out"

                                       Rscript "${macsdir}/exp_no_ctrl_model.r"

                                       mv "expnow_ctrl_model.pdf" "${macsdir}/exp_no_ctrl_model.pdf"

                                   done
                               done
                               break
                      fi

                  done
         elif [[ ( ${#no_folder_designation[@]} -gt 0 ) ]]
             then echo " Something went wrong b"
         fi

elif [[ ( "${multi_align,,}" == yes ) && ( "${using_controls,,}" == no ) ]]
    then echo " "
         echo " You have indicated that controls will not be used, and you are"
         echo " processing bam files from multiple sequencing experiments."
         echo " "
         echo " Beginning peak calling without controls."
         echo " "
         for fold in "${bam}"/*
         do
             for bam_file in "${fold}"/*.bam
             do

                 mkdir "${fold}/macs3_out"

                 macs3 callpeak -t ${bam_file} -f BAM -n exp_no_ctrl -q 1 --call-summits -g dm --outdir "${fold}/macs3_out"

                 Rscript "${fold}/macs3_out/exp_no_ctrl_model.r"

                 mv "exp_no_ctrl_model.pdf" "${fold}/macs3_out/exp_no_ctrl_model.pdf"

             done
         done

elif [[ ( "${multi_align,,}" == no ) && ( "${using_controls,,}" == no )  ]]
    then echo " "
         echo " You have indicated that you will be calling peaks for a single experiment"
         echo " with no control. "
         echo " "
         echo " Beginning peak calling on one experiment, without controls."
         echo " "
         for bam_file in "${bam}"/*.bam
         do

             mkdir "${bam}/macs3_out"

             macs3 callpeak -t ${bam_file} -f BAM -n exp_no_ctrl -q 1 --call-summits -g dm --outdir "${bam}/macs3_out"

             Rscript "${bam}/macs3_out/exp_no_ctrl_model.r"

             mv "exp_no_ctrl_model.pdf" "${bam}/macs3_out/exp_no_ctrl_model.pdf"

         done

else echo " "
     echo " Invalid options were given:  multiple experiments = $multi_align   &&  controls = $using_controls"
     echo " exiting..."
     exit

fi

# If the user is only analyzing one BAM file, then this
# decision path will be used
#if [ "${multi_align,,}" == no ]

    # First, loop over the BAM file within the folder.
    # If all portions of the program I wrote were used,
    # then the only BAM file in each folder should be the
    # filtered and sorted one.
#    then for bam_file in "$bam"/*.bam
#         do
#         done
#fi
