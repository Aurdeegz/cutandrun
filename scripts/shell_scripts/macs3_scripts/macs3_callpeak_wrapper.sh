#!/bin/bash

# This program will perform peak calling as layed out in
# https://github.com/Henikoff/Cut-and-Run/blob/master/py_peak_calling.py
# Merging peaks will be the standard, for now. Eventually I will add some
# other features to this

#Use GETOPTS command to get the optional arguments from the user.
while getopts b:c:g:o: option
do
case "${option}"
in
b) A=${OPTARG};;
c) C=${OPTARG};;
g) D=${OPTARG};;
o) F=${OPTARG};;
#bo) H=${OPTARG};; was going to ask for a bedfile output name, decided not to
esac
done

# Use the default syntax to assign values to all variables the user does not
# input into the script.

bam=${A:-None}
using_controls=${C:-no}
gsize=${D:-None}
output_file=${F:-None}

echo "==================================================================================== "
echo " "
echo " "
echo " Begining peak calling. This program uses MACS3 for peak calling, using the settings"
echo " -f BAM -B --call-summits -q 1"
echo " The other settings used are -g (genome size, input by user or found in cutandrun),"
echo " -t (test file, found by program assuming BAM extension), -c (control, only found if"
echo " the user says they have controls and the file directories are set up appropriately),"
echo " and -outdir (output directory, will be the macs3_out folder created within directory)."
echo " "
echo " NOTE: The cutandrun program uses Bowtie2 for alignments, which produces paired end"
echo " Sequencing alignment files. MACS3 has a setting, BAMPE, for files like this. To see"
echo " if the BAMPE setting produced expected results, I ran MACS3 using BAMPE with the"
echo " control and test files as the same file (tests/test_multiple/stat92e_exp_A/alignment_0.sam)."
echo " Since these are the same files, I did not expect to see any significant peaks after peak calling."
echo " I did, however, get a lot of peaks showing up below q = 0.01. I do not know why this happend,"
echo " but whenever I use the BAM setting I see no significant peaks when using the same"
echo " test and control files. As such, I use the BAM setting, not the BAMPE setting for"
echo " MACS3 peak calling."
echo " "
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

if [ "${gsize}" == None ]
    then echo " "
         echo " You have not indicated which organism your alignments were made to."
         echo " This paramter allows for MACS3 to estimate the mappable size of the"
         echo " genome you are using. The options are:"
         echo " "
         echo " Drosophila melanogaster  :   dm"
         echo " Homo sapiens             :   hs"
         echo " Mus murine               :   mm"
         echo " Caenorhabditis elegans   :   ce"
         stopper=0
         while [ $stopper -eq 0 ]
         do
             echo " "
             echo " Please input the genome id you're using for peak calling (right column of list)"
             echo " "
             read gsize
             echo " "
             echo " Your answer: $gsize"
             echo " "
             if [[ ( "${gsize,,}" == "dm" ) || ( "${gsize,,}" == "mm" ) || ( "${gsize,,}" == "hs" ) || ( "${gsize,,}" == "ce" ) ]]
                 then gsize="${gsize,,}"
                      stopper=1
             else echo " Your answer was not a valid option. Please try again."
             fi
         done
fi

get_array () {
    # This angers me on a new level :(
    #
    # To use this function and save the output to a new variable, use the
    # syntax:
    #
    # new_array=($( get_array "string" "delimiter" ))
    #
    # I was using tr before, but this little function works well. This also
    # avoids the problem of nested IFS splits (for example, reading the lines
    # of a file and splitting the lines into an array)
    #
    # argument one should be the string
    string="$1"
    # argument two should be the delimiter
    delim="$2"
    # If the delimiter is not a special character, then set IFS normally
    if [[ ( "${delim}" != "\t" ) || ( "${delim}" != "\n" ) ]]
        then IFS="$delim"
    # Otherwise, use the notation for the special characters
    else IFS=$'${delim}'
    fi
    # Once IFS is set, then use read to read create the arrayy
    read -ra arrayy <<< "$string"
    # Loop over the items in the arrayy
    for item in "${arrayy[@]}"
    # and echo them.
    do
        echo "$item"
    done
}

check_foldtype () {
    # This function checks a folder name string for specific (and case sensitive) key words.
    # The goal here is to identify which folders contain control data, and which folders
    # contain experimental data. There are a number of acceptable words for experimental
    # data, while I could only think of a few for the control data.
    #
    # To use the function, use the following syntax
    #
    # folder_type=$( check_foldtype "folder_string" )
    #
    # Folder should be the input string.
    fold="$1"
    # Define the allowed substrings for control and experimental folders.
    allowed_ctrls=("control" "cont" "ctrl")
    allowed_exps=("experiment" "exp" "treatment" "treat" "enrichment" "enrich" "rep" "replicate")
    # Initialize the fold_type variable to None
    fold_type=None
    # First, check to see if the folder is an experimental folder. Loop over allowed
    # substrings for experiments
    for type in "${allowed_exps[@]}"
    do
        # Using wildcard, see if the substring (type) is in the folder string
        if [[ "${fold,,}" == *"$type"* ]]
            # If it is, then reassign fold_type to experiment and break
            then fold_type="experiment"
                 break
        fi
    done
    # If the fold_type is still None, then the folder was not experimental.
    if [ "${fold_type}" == None ]
        # So we check to see if it is a control experiment. Loop over the
        # allowable control folder substrings.
        then for type in "${allowed_ctrls[@]}"
             do
                 # Using wildcard, see if the substring (type) is in the folder string
                 if [[ "${fold,,}" == *"$type"* ]]
                     # If it is, then reassign fold_type as control and break
                     then fold_type="control"
                          break
                 fi
             done
    fi
    # echo the fold_type so it can be saved as a variable.
    echo "$fold_type"
}

check_replicate_num () {
    # This function is meant to pair two folders, experiment and control,
    # based on the identifier that follows the exp/control substring.
    # This function assumes that each folder name is constructed using the
    # same format and the same number of 'strings'
    #
    # example:   stat92e_ab_exp_A    and   stat92e_igg_cont_A
    # is GOOD.
    # exmaple:  stat92e_exp_A   and   stat92e_igg_cont_A
    # is NOT GOOD.
    #
    # To use this function, use the following notation:
    #
    # pairs=$( check_replicate_num "folder_string_array_1" "folder_string_array_2" )
    #
    # pairs will be True if the id in each array (last element) is the same.
    # pairs will be False if the id in each array (last element) is not the same.
    #
    # Reassign the array input to the local variables array_1 and array_2
    # this notation essentially tells the function to look for the global $1 and $2
    # in order to make the local assignment.
    local -n array_1=$1
    local -n array_2=$2
    # Get the number of elements in each array (in computer speak, so 0 to n-1 rather
    # then 1 to n)
    array1_size=$(( ${#array_1[@]} - 1 ))
    array2_size=$(( ${#array_1[@]} - 1 ))
    # Loop over the number of elements in the first array. The notation is to start at
    # 0, stop at the array1_size, and increase by 1 on each iteration
    for (( n=0; n<=$array1_size; n++ ))
    do
        # Check each element of the folder string for the folder type
        foldtype_1=$( check_foldtype "${array_1[$n]}" )
        # If check_foldtype is experiment or control
        if [[ ( "${foldtype_1}" == "experiment" ) || ( "${foldtype_1}" == "control" ) ]]
            # then save the index of the next element and stop the loop (should be id)
            then foldplace_1=$(( $n + 1 ))
                 break
        fi
    done
    # Next, loop over the number of elements in the second array (same syntax as above)
    for (( n=0; n<=$array2_size; n++ ))
    do
        # Find the folder type for each element of the second folder string array
        foldtype_2=$( check_foldtype "${array_2[$n]}" )
        # If the folder type is experiment or control
        if [[ ( "${foldtype_2}" == "experiment" ) || ( "${foldtype_2}" == "control" ) ]]
            # then save the index of the next element in the array and break (should be id)
            then foldplace_2=$(( $n + 1 ))
                 break
        fi
    done
    # If the element after experiment/control is the same in each array,
    if [ "${array_1[$foldplace_1]}" == "${array_2[foldplace_2]}" ]
        # then the folder paths should be paired, they have the same index
        then echo "True"
    # If elements after experiment/control is not the same, then they should not be paired
    else echo "False"
    fi
}

make_filepath () {
    # This function takes an array containing file path strings as an argument
    # and creates a folder path string using it. If the second argument is true,
    # then the folder path contains only the folder of interest.
    #
    # To use this function, use the following syntax:
    #
    # file_path_string=$( make_file_path file_path_array "TruthyValue" )
    #
    # Syntax to tell the function to assign the global variable $1 to the
    # local path_array
    local -n  path_array=$1
    # If the second argument is true,
    if [ "$2" == "true" ]
        # then loop length is the size of the path array - 1
        then loop_length=$(( ${#path_array[@]} - 1 ))
    # Otherwise, loop length is the size of the array -2
    else loop_length=$(( ${#path_array[@]} - 2 ))
    fi
    # Initialize folder variable
    folder=""
    # Loop over the number of elements in the array. Note that because path array points to the
    # global input $1, we use the indirect parameter expansion to effectively
    # call ${#1[@]} for whatever input 1 is
    for n in "${!path_array[@]}"
    do
        # If the number is greater than the loop lenth,
        if [ $n -gt $loop_length ]
            # then stop this
            then break
        # Otherwise, build the folder string
        else folder="${folder}/${path_array[$n]}"
        fi
    done
    # Print the folder string at the end, without the leading / character
    echo "${folder:1}"
}

# If the user elects to use controls for peak calling

if [ "${using_controls,,}" == yes ]

    # First, loop over all of the folders in the given
    # file directory
    # also, create the controls, experiments, and no designation arrays.
    then declare -a controls
         declare -a experiments
         declare -a no_folder_designation
         # Loop over the folders in the bam file directory
         for fold in "$bam"/*
         do
             # Check the folder type of each folder. Possible results:
             # experiment, control, None   (see check_foldtype function)
             foldtype=$( check_foldtype "$fold" )
             # Second, loop over the BAM file within each folder.
             # If this is being used with the cutandrun pipeline, then the
             # only BAM file in each folder will be the sorted bam file.
             for bam_file in "$fold"/*.bam
             do
                 # If the foldtype is control, then add the file to the control array
                 if [ "${foldtype}" == "control" ]
                     then controls+=("${bam_file}")
                 # Or if the foldtype is experiment, then add the file to the experiment array
                 elif [ "${foldtype}" == "experiment" ]
                     then experiments+=("${bam_file}")
                 # Or if the folder is 'tracks' or 'peak_annotations', then just pass
                 elif [[ ( "${fold}" == *"tracks"* ) || ( "${fold}" == *"peak_annotations"* ) ]]
                     then echo " passing $fold : tracks folder or peak annotations folder"
                 # Otherwise, there is no folder designation
                 else no_folder_designation+=("${bam_file}")
                 fi
             done
         done

         # After binning the BAM files based on the type of folder they're in, check to see if
         # the number of controls and the number of experiments match. Also, make sure there
         # are zero paths in the no_folder_designation array
         if [[ ( ${#controls[@]} -eq ${#experiments[@]} ) && ( ${#no_folder_designation[@]} -eq 0 ) ]]
             # If this is all good, then initialize the paired_paths variable
             then paired_paths=None
                  # Loop over the paths in the experiments array
                  for path in "${experiments[@]}"
                  do
                      # Use get_array to make the path into an array
                      exp_path=($( get_array "${path}" "/" ))
                      # The folder of interest is the total number of elements in the array
                      # - 2 (one for the BAM file at the end, one because computer people start
                      # counting at zero)
                      interest_fold=$((${#exp_path[@]} - 2 ))
                      # Save just the name of the folder with experiment to a variable
                      interest_exp="${exp_path[${interest_fold}]}"
                      # Split the name of the folder on '_' character, save as array
                      exp_fold_arrd=($( get_array "${interest_exp}" "_" ))
                      # Now, we loop over all of the controls. The goal here is to pair
                      # each experiment with a control, based on the id that comes after
                      # the experimient/control substring (stat92e_exp_A, stat92e_cont_A)
                      for cont in "${controls[@]}"
                      do
                          # As with the experiment, get the control path as an array
                          ctrl_path=($( get_array "${cont}" "/" ))
                          # Get the string containing the folder name
                          interest_ctrl="${ctrl_path[${interest_fold}]}"
                          # And split the folder name on the _ characters
                          ctrl_fold_arrd=($( get_array "${interest_ctrl}" "_" ))
                          # Use check_replicate_num to determine whether these two folders
                          # have the same id. (see check_replicate_sum for details)
                          same=$( check_replicate_num exp_fold_arrd ctrl_fold_arrd )
                          # If the exp folder and the control folder have the same id
                          if [ "$same" == "True" ]
                              # Then reassign the paired paths string and break
                              then paired_paths="-t ${path} -c ${cont}"
                                   break
                          fi
                      done
                      # Once this loop completes, we should have a paired path for an
                      # experiment and a control. We first use make_filepath to make
                      # the first portion of the output folder path for the macs3 data
                      folder=$( make_filepath exp_path "false" )
                      # If the paired paths is not equal to none, ie we found paired paths
                      if [ "${paired_paths}" != None ]
                          # Then create the macsdir string for macs3 data output
                          then macsdir="${folder}/macs3_out"
                               # use mkdir to make this directory
                               mkdir "${macsdir}"
                               # Then use macs3 to call peaks. More information on the macs3
                               # settings on the MACS3 github page https://github.com/macs3-project/MACS/blob/master/docs/callpeak.md
                               macs3 callpeak ${paired_paths} -f BAM -n exp_w_ctrl -q 1 -B --call-summits -g "${gsize}" --outdir "${macsdir}"
                               # Run the Rscript to show the peaks model
                               Rscript "${macsdir}/exp_w_ctrl_model.r"
                               # and move the ouput file to the proper folder.
                               mv "exp_w_ctrl_model.pdf" "${macsdir}/exp_w_ctrl_model.pdf"
                      # If for some reason the pairing of paths does not work, then just analyze
                      # all the BAM files separately
                      elif [ "${paired_paths}" == None ]
                          # Tell the user that the universe has exploded, and there were no survivors
                          then echo " "
                               echo " Unable to find paired experiment and control paths. Proceeding with"
                               echo " peak calling without using control sequencing data..."
                               echo " "
                               # Loop over the folders in the given directory
                               for fold in "${bam}"/*
                               do
                                   # Loop over the bam files in those folders
                                   for bam_file in "${fold}"/*.bam
                                   do
                                       # Make the macs3 output directory
                                       mkdir "${fold}/macs3_out"
                                       # Use macs3 to call peaks. For more information, see the MACS3
                                       # github page https://github.com/macs3-project/MACS/blob/master/docs/callpeak.md
                                       macs3 callpeak -t ${bam_file} -f BAM -n exp_no_ctrl -q 1 --call-summits -g "${gsize}" --outdir "${fold}/macs3_out"
                                       # Run the Rscript for the peak model
                                       Rscript "${macsdir}/exp_no_ctrl_model.r"
                                       # and move the output file to the correct directory
                                       mv "expnow_ctrl_model.pdf" "${macsdir}/exp_no_ctrl_model.pdf"
                                   done
                               done
                               # This break will stop the pairing paths loop, as this only happens when
                               # finding controls fails for some reason
                               break
                      fi
                  done
         # The other way this can fail is if a folder has no designation. If this happens,
         # Just exit completely and tell the user which folder to move.
         elif [[ ( ${#no_folder_designation[@]} -gt 0 ) ]]
             then echo " There appears to be some folders with no folder designation. This will"
                  echo " crash the program later, so we will terminate gracefully now."
                  echo " But first, move this/these folders before trying again:"
                  echo " "
                  for f in "${no_folder_designation[@]}"
                  do
                      echo " ${f}"
                  done
                  echo " Cheers! Exiting..."
                  exit
         fi
# If you are not using controls, then just analyze all bam files in the directory alone
elif [ "${using_controls,,}" == no ]
    then echo " "
         echo " You have indicated that controls will not be used, and you are"
         echo " processing bam files from multiple sequencing experiments."
         echo " "
         echo " Beginning peak calling without controls."
         echo " "
         # Loop over the folders in the given directory
         for fold in "${bam}"/*
         do
             # Loop over the bam files in each folder
             for bam_file in "${fold}"/*.bam
             do
                 # make the macs3 output directory
                 mkdir "${fold}/macs3_out"
                 # Use macs3 to call peaks. More information on parameters
                 # here: https://github.com/macs3-project/MACS/blob/master/docs/callpeak.md
                 macs3 callpeak -t ${bam_file} -f BAM -n exp_no_ctrl -q 1 --call-summits -g "${gsize}" --outdir "${fold}/macs3_out"
                 # Run the rscript to make the peak model plot
                 Rscript "${fold}/macs3_out/exp_no_ctrl_model.r"
                 # And move the peak model plot to the correct directory
                 mv "exp_no_ctrl_model.pdf" "${fold}/macs3_out/exp_no_ctrl_model.pdf"
             done
         done
fi

echo "============================================================================="
echo " "
echo " "
echo " "
echo " Peak calling complete! Check the directories for the macs3 output files."
echo " If this is in the cutandrun pipeline, then sit back and enjoy."
echo " "
echo " If it is not, then you may want to consider running the python script"
echo " scripts/python_files/macs3_narrowpeak_edits/filter_macs3out_files.py"
echo " "
echo " This python file allows you to filter the xls and narrowpeaks files"
echo " on either the q value (default, 0.01) or a p value. The current files"
echo " are not filtered (q value parameter was set to 1)."
echo " "
echo " "
echo "============================================================================="
