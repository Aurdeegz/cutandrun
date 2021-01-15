#!/bin/bash

# Use getopts to get the optional arguments
# for this scripts
while getopts b:g:m:p:a:l:u: option
do
case "${option}"
in
b) A=${OPTARG};;  # b) -> bedgraph file directory
g) C=${OPTARG};;  # g) -> .genome file directory
m) B=${OPTARG};;  # m) -> multiple file argument
p) D=${OPTARG};;  # p) -> path to write_overlay.py
a) E=${OPTARG};;  # annotation directory
l) F=${OPTARG};;  # list of annotations, comma separated
u) G=${OPTARG};;  # Using annotations
esac
done

# Set all of the inputs to the default value of None
bg_dir=${A:-None}
multi_align=${B:-None}
genome=${C:-None}
pathto=${D:-None}
using_annot=${G:-None}
annot_dir=${E:-None}
annot_list=${F:-None}

echo "===================BEGIN================================== "
echo " "
echo " Plotting all regions with peaks!!"
echo " "
echo "===================END==================================== "

# If the user gave a value for multi_align, then pass.
if [ "${multi_align,,}" == yes ]
    then echo " "
    elif [ "${multi_align,,}" == no ]
    then echo " "

    # If the user did not give a value, then ask them if they are plotting
    # multiple bigwig files from multiple directories.
    else echo " "
         echo " You have not indicated whether you will be plotting "
         echo " bedgraph files from one folder or multiple folders in a"
         echo " directory. Here are the options for this program:"
         echo " "
         echo " MULTIPLE: The multiple option refers to using one directory"
         echo " that contains multiple folders, and within each folder is one"
         echo " or more bigwig files. This option is meant to work with "
         echo " the 'align_multiple' setting in cut_run_pipeline_v2.sh."
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
                  echo " containing the bedgraph files to be plotted."
                  read bg_dir
                  echo " "
                  echo " Your answer: $bg_dir"
                  echo " "
    # If the user is plotting bigwig files from multiple folders
             elif [ "${multi_align,,}" == yes ]
             then echo " You have not given the filepath to the folders"
                  echo " holding the bedgraph files to be plotted."
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
         echo " (for the example files, this is drosophila/drosophila_genome/length_sort.genome)"
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
         echo " be located in the 'scripts/python_files/trackfile_editing' folder, in the primary cutandrun folder. "
         echo " "
         echo " If you ran the installation.sh file to install all required modules, then"
         echo " the python file folder will be located in usr/softwares/cut_run/scripts/python_files/trackfile_editing"
         echo " "
         read pathto
         echo " "
         echo " Your answer: $pathto"
         echo " "

fi

if [ "${using_annot}" == None ]
    then echo " "
         echo " You have not indicated whether you would like to use"
         echo " annotations in your regions plots."
         echo " "
         stop=0
         while [ $stop -eq 0 ]
         do
             echo " Would you like to use annotations?"
             echo " "
             read using_annot
             echo " "
             echo " Your answer: $using_annot"
             echo " "
             if [ "${using_annot,,}" == "no" ]
                 then stop=1
                      annot_dir="no"
                      annot_list="no"
             elif [ "${using_annot,,}" == "yes" ]
                 then stop=1
             else echo " Your answer was neither yes nor no. Please try again."
                  echo " "
             fi
         done
fi

if [ "${using_annot,,}" == "yes" ]
# If the user did not give a path to the directory with annotation files,
# then request that the user gives this directory.
    then if [ "${annot_dir}" == None ]
             then echo " "
                  echo " You have not indicated the directory containing annotation bed files."
                  echo " If this directory was generated using the cut_run_pipeline_v2.sh, then"
                  echo " it will be locatedin a subfolder named annotation_types within your"
                  echo " annotations folder."
                  echo " "
                  echo " You may also write 'no'. In this case, no annotations will be used."
                  echo " "
                  read annot_dir
                  echo " "
                  echo " Your answer: $annot_dir"
                  echo " "
         fi

         # If no annotation list was given, then request one from the user.
         # If the user answered no to the previous question, then this is
         # automatically set to no.
        if [ "${annot_list}" == None ]
            then if [ "${annot_dir,,}" == no ]
                     then annot_list="no"
                 else echo " "
                      echo " The following annotations are available for your selected genome:"
                      echo " "
                      # Print a list of the allowed annotations using the fields.txt file.
                      # Save those fields to an array
                      declare -a ants_allowed
                      while IFS= read -r line;
                      do
                          echo "$line"
                          ants_allowed+=("$line")
                      done < "${annot_dir}/fields.txt"
                      echo " "
                      echo " Please write the annotations that you would like to use, separated"
                      echo " by commas. Note that your answer is case sensitive."
                      echo " "
                      echo " Example: gene,CDS,lnc_RNA"
                      read annot_list
                      echo " "
                      echo " Your answer: $annot_list"
                      echo " "
                      # Once the user gives you an answer, check that their answers are
                      # alowed annotations.
                      holder=","
                      IFS=","
                      read -ra ARRD <<< $annot_list
                      # Loop over the users answers
                      for ant in "${ARRD[@]}"
                      do
                          seen="no"
                          # Loop over the allowed annotations
                          for al_ant in "${ants_allowed[@]}"
                          do
                              # IF the allowed annotation and user's answers are the same
                              if [ "$al_ant" == "$ant" ]
                                  # Change the seen variable to yes
                                  then seen="yes"
                              fi
                          done
                          # If the seen variable went unchanged
                          if [ "$seen" == "no" ]
                          # Then tell the user that the specific value is not allowed
                          then echo " $ant is not in the list of allowable annotations and will be excluded."
                               echo " "
                          # Otherwise, build holder.
                          else holder="${holder},${ant}"
                          fi
                      done
                      # finally, if none of the users inputs were valid
                      if [ "${holder}" != "," ]
                          then annot_list="${holder:2}"
                      # then set annot_list to no
                      else annot_list="no"
                      fi
                      echo " "
                      echo " Using annotations: $annot_list"
                      echo " "
                 fi
       fi
fi
# functions for getting the height of the plots
get_highest_wrapper_bgfile () {
    # Argument two should be of form chrom:beg-end
    region="$2"
    # Split the region by colon
    regionparts=($(echo $region | tr ":" "\n"))
    # Assign chroms as the 0th part
    chrom="${regionparts[0]}"
    # split the second part on -
    regions=($(echo ${regionparts[1]} | tr "-" "\n"))
    # count is used to assign the highest peak from each file
    # to a part of the holder array
    count=0
    declare -a holder
    # File list, comma separated should be argument 1
    files=($(echo ${1} | tr "," "\n" ))
    # loop over the files in the files array
    for file in "${files[@]}"
    do
        # Filter the files for only those peaks within the region
        awk '{ if( "'$chrom'" == $1 && "'${regions[0]}'" <= $2 && "'${regions[1]}'" >= $3 ) { print } }' "${file}" > "temp.bg"
        # use get_highest integer() to find the highest integer in the section
        next=$( get_highest_integer "temp.bg" "0" )
        # add that integer to the holder array
        holder[$count]=$next
        # increase the count by 1
        count=$(($count + 1))
    done
    # outputty is my terrible name for the highest integer amongst all files
    outputty="0"
    # loop over the holder array elements
    for item in "${holder[@]}"
    do
        # if the item is greater than the current highest integer
        if [ "$item" -gt "$outputty" ]
            # then reassign outputty as that next highest integer
            then outputty="$item"
        fi
    done
    # echo the output integer, so it can be saved in another script if needed
    echo "$outputty"
    # remove the temporary file
    rm "temp.bg"
}

# Small function to get the highest data value from a bedgraph file
get_highest_integer () {
    # File should be the first argument
    file="$1"
    # the current highest integer should be the second argument
    # This didn't work as expected, so ive been using 0
    highest="$2"
    # Loop over the lines in the file
    while IFS= read -r line
    do
        # If the line is empty, the file is empty, so we break
        if [ "$line" == "" ]
            then break
       # Otherwise the file is not empty, so we can split the line
        else line=($( echo ${line} | tr $'\t' "\n" ))
             # The datavalue is the 3th argument
             datavalue="${line[3]}"
             # If the current highest is less than the datavalue
             if [ "$highest" -lt "$datavalue" ]
                 # Then reassign the highest
                 then highest="$datavalue"
                      highest=$(($highest + 0))
             fi
        fi
    done <"${file}"
    # echo the highest so it can be assigned to a variable in
    # another script.
    echo "$highest"
}

get_array () {
    # This angers me on a new level :(
    string="$1"
    IFS=$'\t'
    read -ra arrayy <<< "$string"
    for item in "${arrayy[@]}"
    do
        echo "$item"
    done
}

# If the multi align setting is yes, then the program will find
# the bedgraph files in the subfolders and use those for
# region plotting
if [ "${multi_align,,}" == "yes" ]
    # Initialize the peak files, sorted files and count variables
    then peak_files=None
         sorted_files=None
         count=0
         # Loop over folders in the given bedgraph directory
         for folder in "${bg_dir}"/*
         do
         # If the folder is the tracks folder, the increase the count
         # and continue
         if [ "${folder}" == "${bg_dir}/tracks" ]
             then count=$(($count + 1))
                  continue
         # Otherwise, loop over the bedgraph files in the directory
         # Note: I should change this to include extension .bedgraph
         else for file in "${folder}"/*.bg
              do
              # IF the file contains the substring peaks
              if [[ "${file}" == *"peaks"* ]]
                  # Then if the peak_files is still None
                  then if [ "${peak_files}" == None ]
                           # Then initiailize peak files
                           then peak_files="${file}"
                       # Otherwise, just extend the current peak files
                       else peak_files="${peak_files},${file}"
                       fi
                  # Or if the peaks substring is not in the file and
                  # the sorted_files is still None
                  else if [ "${sorted_files}" == None ]
                           # then initialize the sorted file
                           then sorted_files="${file}"
                       # Otherwise add the file to the sorted files list
                       else sorted_files="${sorted_files},${file}"
                       fi
              fi
              done
         fi
         done

         # If count doesn't equal 1, then there was no tracks directory.
         # Thus, we must make one.
         if [ "$count" != "1" ]
             then mkdir "${bg_dir}/tracks"
         fi

         # Initialize name for the file containign plot regions
         regionsfile="${bg_dir}/tracks/plot_regions.txt"

         echo "===================BEGIN================================== "
         echo " "
         echo " Writing the regions to plot to a file using"
         echo " "
         echo " python3 ${pathto}/find_plot_regions.py ${peak_files} ${genome} ${regionsfile}"
         echo " "
         python3 "${pathto}/find_plot_regions.py" "${peak_files}" "${genome}" "${regionsfile}"
         echo " "
         echo " "
         echo "===================END==================================== "

         last_chrom="."

         # Loop over the lines in the plot_regions.txt file
         while IFS= read -r line
         do
             echo "===================BEGIN================================== "
             echo " "
             echo " Plotting the region with $annot_list annotations"

             # Split the line: chrom, beg, end
#             n_line=($( echo "${line}" | tr $'\t' "\n"))
             n_line=($(get_array "$line"))
             chrom="${n_line[0]}"
             beginning="${n_line[1]}"
             ending="${n_line[2]}"
             # Format chrom region required for pyGenomeTracks
             chromregion="${n_line[0]}:${n_line[1]}-${n_line[2]}"

             echo " $chromregion ."
             echo " The maximum values in this region are:"

             # Get the maxiumum values for reads in the region
             max_peaks=$(get_highest_wrapper_bgfile "${peak_files}" "${chromregion}")
             max_sorted=$(get_highest_wrapper_bgfile "${sorted_files}" "${chromregion}")
             maxs="${max_peaks},${max_sorted}"

             echo " For the peak file(s):     $max_peaks"
             echo " For the raw files(s):     $max_sorted"
             echo " "

             # Make a directory to save the files to, if this directory has not been made yet
             if [ "${line[0]}" != "${last_chrom}" ]
                 then echo " "
                      echo " Making a directory for this chromosome using"
                      echo " mkdir ${bg_dir}/tracks/${line[0]}"
                      mkdir "${bg_dir}/tracks/${chrom}"
                      echo " "
                      last_chrom="${line[0]}"
             fi

             # IF the user did not want to use annotations
             if [ "${annot_dir}" == "no" ]
                 # Then use write overaly to write the configuration file
                 then python3 "${pathto}/write_overlay.py" "${peak_files}" "${sorted_files}" "${bg_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.ini" "true" "${maxs}"
                      # and pyGenomeTracks to plot the tracks
                      pyGenomeTracks --tracks "${bg_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.ini" --region "${chromregion}" --outFileName "${bg_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.pdf"

             else annotes=($( echo ${annot_list} | tr "," "\n" ))
                  ant_beds="."
                  for annot_file in "${annot_dir}"/*
                  do
                      for annot in "${annotes[@]}"
                       do
                          if [[ "${annot_file}" == *"_${annot}."* ]]
                              then if [ "${ant_beds}" == "." ]
                                      then ant_beds="${annot_file}"
                                   else ant_beds="${ant_beds} ${annot_file}"
                                   fi
                          fi
                       done
                  done

                  echo " ant beds        $ant_beds       "
                   python3 "${pathto}/write_overlay.py" "${peak_files}" "${sorted_files}" $ant_beds "${bg_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.ini" "true" "${maxs}"

                   pyGenomeTracks --tracks "${bg_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.ini" --region "${chromregion}" --outFileName "${bg_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.pdf"
             fi
         echo " "
         echo " Done plotting region $chromregion, the graph is saved here:"
         echo " ${bg_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.pdf"
         echo " "
         echo "===================END==================================== "
         done < "${regionsfile}"

elif [ "${multi_align,,}" == "no" ]
    then peak_files=None
         sorted_files=None
         count=0
         # Otherwise, loop over the bedgraph files in the directory
         # Note: I should change this to include extension .bedgraph
         for file in "${bg_dir}"/*
         do
             if [ "${file}" == "${bg_dir}/tracks" ]
                 then count=$(($count + 1))
             elif [[ "${file}" == *".bg"* ]]
                 # IF the file contains the substring 'peaks'
                 then if [[ "${file}" == *"peaks"* ]]
                      # Then if the peak_files is still None
                      then if [ "${peak_files}" == None ]
                              # Then initiailize peak files
                               then peak_files="${file}"
                           # Otherwise, just extend the current peak files
                           else peak_files="${peak_files},${file}"
                           fi
                      # Or if the peaks substring is not in the file and
                      # the sorted_files is still None
                      else if [ "${sorted_files}" == None ]
                               # then initialize the sorted file
                               then sorted_files="${file}"
                           # Otherwise add the file to the sorted files list
                           else sorted_files="${sorted_files},${file}"
                           fi
                      fi
             fi
         done

         # If count doesn't equal 1, then there was no tracks directory.
         # Thus, we must make one.
         if [ "$count" != "1" ]
             then mkdir "${bg_dir}/tracks"
         fi

         # Initialize name for the file containign plot regions
         regionsfile="${bg_dir}/tracks/plot_regions.txt"

         # Use find_plot_regions.py to write the plot_regions.txt file

         echo "===================BEGIN================================== "
         echo " "
         echo " Writing the regions to plot to a file using"
         echo " "
         echo " python3 ${pathto}/find_plot_regions.py ${peak_files} ${genome} ${regionsfile}"
         echo " "
         python3 "${pathto}/find_plot_regions.py" "${peak_files}" "${genome}" "${regionsfile}"
         echo " "
         echo " "
         echo "===================END==================================== "

         last_chrom="."
         # Loop over the lines in the plot_regions.txt file
         while IFS= read -r line
         do

             echo "===================BEGIN================================== "
             echo " "
             echo " Plotting the region with $annot_list annotations"

             # Split the line: chrom, beg, end
             line=($( get_array "$line" ))
             chrom="${line[0]}"
             beginning="${line[1]}"
             ending="${line[2]}"
             # Format chrom region required for pyGenomeTracks
             chromregion="${chrom}:${beginning}-${ending}"

             echo " $chromregion ."
             echo " The maximum values in this region are:"

             # Get the maxiumum values for reads in the region
             max_peaks=$(get_highest_wrapper_bgfile "${peak_files}" "${chromregion}")
             max_sorted=$(get_highest_wrapper_bgfile "${sorted_files}" "${chromregion}")
             maxs="${max_peaks},${max_sorted}"

             echo " For the peak file(s):     $max_peaks"
             echo " For the raw files(s):     $max_sorted"
             echo " "

             # Make a directory to save the files to, if this directory has not been made yet
             if [ "${chrom}" != "${last_chrom}" ]
                 then echo " "
                      echo " Making a directory for this chromosome using"
                      echo " mkdir ${bg_dir}/tracks/${chrom}"
                      mkdir "${bg_dir}/tracks/${chrom}"
                      echo " "
                      last_chrom="${chrom}"
             fi

             # IF the user did not want to use annotations
             if [ "${annot_dir}" == "no" ]
                 # Then use write overaly to write the configuration file
                 then python3 "${pathto}/write_overlay.py" "${peak_files}" "${sorted_files}" "${bg_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.ini" "true" "${maxs}"
                      # and pyGenomeTracks to plot the tracks
                      pyGenomeTracks --tracks "${bg_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.ini" --region "${chromregion}" --outFileName "${bg_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.pdf"

             else annotes=($( echo ${annot_list} | tr "," "\n" ))
                  ant_beds="."
                  for annot_file in "${annot_dir}"/*
                  do
                      for annot in "${annotes[@]}"
                       do
                          if [[ "${annot_file}" == *"_${annot}."* ]]
                              then if [ "${ant_beds}" == "." ]
                                      then ant_beds="${annot_file}"
                                   else ant_beds="${ant_beds} ${annot_file}"
                                   fi
                          fi
                       done
                  done
                   python3 "${pathto}/write_overlay.py" "${peak_files}" "${sorted_files}" ${ant_beds} "${bg_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.ini" "true" "${maxs}"
                   pyGenomeTracks --tracks "${bg_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.ini" --region "${chromregion}" --outFileName "${bg_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.pdf"
             fi
         echo " "
         echo " Done plotting region $chromregion, the graph is saved here:"
         echo " ${bg_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.pdf"
         echo " "
         echo "===================END==================================== "
         done < "${regionsfile}"
fi


