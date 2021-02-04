#!/bin/bash

# Use getopts to get the optional arguments
# for this scripts
while getopts b:g:p:a:l:u:n: option
do
case "${option}"
in
b) A=${OPTARG};;  # b) -> bedgraph file directory
g) C=${OPTARG};;  # g) -> .genome file directory
p) D=${OPTARG};;  # p) -> path to write_overlay.py
a) E=${OPTARG};;  # annotation directory
l) F=${OPTARG};;  # list of annotations, comma separated
u) G=${OPTARG};;  # Using annotations
n) H=${OPTARG};;  # Using narrowpeak files
esac
done

# Set all of the inputs to the default value of None
file_dir=${A:-None}
genome=${C:-None}
pathto=${D:-None}
using_annot=${G:-None}
annot_dir=${E:-None}
annot_list=${F:-None}
using_narrow=${G:-yes}

echo "===================BEGIN================================== "
echo " "
echo " Plotting all regions with peaks!!"
echo " "
echo "===================END==================================== "

if [ "$file_dir" == None ]

    # If the user is plotting bigwig files from one folder
    then echo " You have not given the filepath to the folders"
         echo " holding the bedgraph/narrowPeak files to be plotted."
         read file_dir
         echo " "
         echo " Your answer: $file_dir"
         echo " "
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

# This is going to be depricated at some point. I should be able to
# write a script that detects the file type. This program originally
# used the bedgraph files from peak calling
if [ "${using_narrow,,}" == yes ]
    then file_type="narrowPeak"
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

# If the multi align setting is yes, then the program will find
# the bedgraph files in the subfolders and use those for
# region plotting

# Initialize the peak files, sorted files and count variables
peak_files=None
sorted_files=None
count=0
# Loop over folders in the given bedgraph directory
for folder in "${file_dir}"/*
do
    # If the folder is the tracks folder, the increase the count
    # and continue
    if [[ ( "${folder}" == "${file_dir}/tracks" ) || ( "${folder}" == "${file_dir}/peak_annotations" ) ]]
        then count=$(($count + 1))
             continue
    # Otherwise, check the file type spwcification.
    # narrowPeak indicates MACS3 peak calling was used
    # bedgraph means that Henikoff peak calling was used.
    #
    # Default should be narrowPeak, as macs3 is the current
    # peak calling algorithm
    else if [ "$file_type" == "narrowPeak" ]
         # If narrowpeak is the option, then the file path should
         # be folders of subfolders, with subsubfolders labelled
         # macs3_out.
         #
         # Loop over the subfolders in each folder
         then for subfold in "${folder}"/*
              do
                  # Check to see if the subfolder is actually the
                  # macs3_out folder, which will have all of the
                  # data files.
                  #
                  # Here, we are assuming that the filter_macs3out_files.py
                  # script has run, which will filter the data based
                  # on a specified q (or p) value.
                  if [ "${subfold}" == "${folder}/macs3_out" ]
                      # If we are in the macs3_out folder, then loop over the
                      # subfolders in this directory
                      then for subsubfold in "${subfold}"/*
                           do
                           # Filtered data files will be in the modified_peakfiles folder.
                           # Check for the modified_peakfiles folder
                           if [ "${subsubfold}" == "${subfold}/modified_peakfiles" ]
                               # If we are in the modified_peakfiles folder, then
                               # loop over the file_type specific (this case, narrowPeak)
                               # files in the directory. Note that there should only be
                               # one file of the specified type in the directory
                               then for file in "${subsubfold}"/*"${file_type}"
                                    do
                                    # We finally found the files of interest! If we
                                    # have not seen any peak files yet,
                                    if [ "${peak_files}" == None ]
                                        # then set peak_files to be this new file!
                                        then peak_files="${file}"
                                    # Otherwise, update the peak files string with the
                                    # new file
                                    else peak_files="${peak_files},${file}"
                                    fi
                                    done
                           fi
                           done
                  # We also need to find all of the sorted alignemtn bedgraph files for
                  # raw data region plotting. These files should contain the substrings
                  # "_sorted" and ".bg" (the file extension). If the subfolder has these
                  # characteristics, then we should add them to the sorted list.
                  elif [[ ( "${subfold}" == *"_sorted"* ) && ( "${subfold}" == *".bg"* ) ]]
                      # If the sorted files string is still none, then we haven't seen a
                      # sorted bedgraph file yet.
                      then if [ "${sorted_files}" == None ]
                               # So we use this file as the first file in the string
                               then sorted_files="${subfold}"
                           # Otherwise, we update the string with the next sorted bg file.
                           else sorted_files="${sorted_files},${subfold}"
                           fi
                  fi
              done
         # This is the option for the Henikoff peak calling, were the output is
         # sorted bedgraphs and sorted peaks bedgraphs. This option is currently
         # not in use in the main program, but I am keeping the code in case
         # it becomes useful in the future.
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
    fi
done

# At this point, we should have two strings: peak_files, sorted_files
# Because we are first looping through the folders in the experimental
# directory, then through every item in the subfolder, and (if narrowPeak)
# through more subsubfolders, the strings should be ordered. For example,
# the first file in the peak_files string should be the narrowPeak file
# corresponding to the first bedgraph file in sorted_files.

# If count is less than 1, then there may not have been a tracks
# directory. If this is the case, then try to make one. If this
# little block fails, the program should not crash.
if [ $count -lt 1 ]
    then mkdir "${file_dir}/tracks"
fi

echo " peak files = $peak_files"
echo " sorted files = $sorted_files"

# Initialize name for the file containign plot regions
regionsfile="${file_dir}/tracks/plot_regions.txt"

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

# Initialize the last chrom variable. This is used to
# determine when a new folder needs to be created for
# peak region plots.
last_chrom="."

# Loop over the lines in the plot_regions.txt file
while IFS= read -r line
do
    echo "===================BEGIN================================== "
    echo " "
    echo " Plotting the region with $annot_list annotations"

    # Split the line: chrom, beg, end. Before we made the get array
    # function, we used tr (translate I think). This will be an issue
    # if the directory path has spaces in it (tr also splits on spaces).
#    n_line=($( echo "${line}" | tr $'\t' "\n"))
    n_line=($( get_array "$line" "\t" ))
    # Chrom is the 0th element of the array
    chrom="${n_line[0]}"
    # the region start is the 1st element of the array
    beginning="${n_line[1]}"
    # the region end is the 2nd element of the array
    ending="${n_line[2]}"
    # Format chrom region required for pyGenomeTracks
    chromregion="${n_line[0]}:${n_line[1]}-${n_line[2]}"
    # Tell the user what the region to be plotted is.
    echo " $chromregion ."
    echo " "
    echo " Getting the maximum values in those regions..."

#    exit

    # Get the maxiumum values for reads in the region
    max_peaks=$(python3 "${pathto}/get_peak_maxs.py" "${peak_files}" "${chromregion}")
    max_sorted=$(python3 "${pathto}/get_peak_maxs.py" "${sorted_files}" "${chromregion}")
    maxs="${max_peaks},${max_sorted}"

    echo " The maximum values in this region are:"
    echo " "
    echo " For the peak file(s):     $max_peaks"
    echo " For the raw files(s):     $max_sorted"
    echo " "

    # Make a directory to save the files to, if this directory has not been made yet
    if [ "${n_line[0]}" != "${last_chrom}" ]
        then echo " "
             echo " last chrom = $last_chrom"
             echo " Making a directory for this chromosome using"
             echo " mkdir ${file_dir}/tracks/${n_line[0]}"
             mkdir "${file_dir}/tracks/${chrom}"
             echo " "
             last_chrom="${n_line[0]}"
    fi

    # IF the user did not want to use annotations
    if [ "${annot_dir}" == "no" ]
        # Then use write overaly to write the configuration file
        then python3 "${pathto}/write_overlay.py" "${peak_files}" "${sorted_files}" "${file_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.ini" "true" "${maxs}"
             # and pyGenomeTracks to plot the tracks
             pyGenomeTracks --tracks "${file_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.ini" --region "${chromregion}" --outFileName "${file_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.pdf"

    # If the user did want to use annotations
    # annotes=($( echo ${annot_list} | tr "," "\n" ))
    # Same comment as with the other translate usage. May as well use the
    # get array function to avoid any potential issues
    else annotes=($( get_array "${annot_list}" "," ))
         # Initialize the annotation_bedfile variable
         ant_beds="."
         # Loop over the annotation files in the annotation directory
         for annot_file in "${annot_dir}"/*
         do
             # Loop over the annotations in the annotation array
             for annot in "${annotes[@]}"
             do
                 # If the file name contains the substring of the annotation
                 if [[ "${annot_file}" == *"_${annot}."* ]]
                     # Then if the annotation bedfile variable is still the
                     # initiated '.'
                     then if [ "${ant_beds}" == "." ]
                              # Then this is the first file we've found, so
                              # change it in ant_beds
                              then ant_beds="${annot_file}"
                          # Otherwise, add this file to ant_beds separated by space
                          else ant_beds="${ant_beds} ${annot_file}"
                          fi
                 fi
             done
         done

         # Once this loop is completed, we should have a string containing space separated
         # annotation_files, as well as the comma separated peak files and sorted files
         # strings. We can now pass all of this into write overlay and create the overlay file.
         #
         # NOTE: Write overlay takes any number of comma separated arguments in the middle,
         # and groups the items that are comma separated for overlays. We want the annotaions
         # to be on their own tracks in the plot, which is why they are space separated.
         python3 "${pathto}/write_overlay.py" "${peak_files}" "${sorted_files}" $ant_beds "${file_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.ini" "true" "${maxs}"
         # Once the overlay is written, run pyGenomeTracks using the chromregion we were on
         # the overlay file, and a new output file.
         pyGenomeTracks --tracks "${file_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.ini" --region "${chromregion}" --outFileName "${file_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.pdf"
    fi
    echo " "
    echo " Done plotting region $chromregion, the graph is saved here:"
    echo " ${file_dir}/tracks/${chrom}/chromreg_${beginning}_${ending}.pdf"
    echo " "
    echo "===================END==================================== "
done < "${regionsfile}"



