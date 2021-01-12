#!/bin/bash

# Use getopts to get the optional arguments
# for this scripts
while getopts b:g:m:p: option
do
case "${option}"
in
b) A=${OPTARG};;  # b) -> bigwig file directory
g) C=${OPTARG};;  # g) -> .genome file directory
m) B=${OPTARG};;  # m) -> multiple file argument
p) D=${OPTARG};;  # p) -> path to edit_tracksfile.py
esac
done

# Set all of the inputs to the default value of None
bw_dir=${A:-None}
multi_align=${B:-None}
genome=${C:-None}
pathto=${D:-None}

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

# If the user did not give a value for the bigwig directory
if [ "$bw_dir" == None ]

    # If the user is plotting bigwig files from one folder
    then if [ "${multi_align,,}" == no ]
             then echo " You have not given the filepath to the folder"
                  echo " containing the bigwig files to be plotted."
                  read bw_dir
                  echo " "
                  echo " Your answer: $bw_dir"
                  echo " "
    # If the user is plotting bigwig files from multiple folders
             elif [ "${multi_align,,}" == yes ]
             then echo " You have not given the filepath to the folders"
                  echo " holding the bigwig files to be plotted."
                  read bw_dir
                  echo " "
                  echo " Your answer: $bw_dir"
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
         echo " You have not specified the filepath to the Python file edit_tracksfile.py"
         echo " If you do not know where this file is, then you should take a minute to "
         echo " locate it. "
         echo " "
         echo " If you gitcloned the cut_run_pipeline, then the edit_tracksfile.py will"
         echo " be located in the 'scripts' folder, in the primary cut_run folder. "
         echo " "
         echo " If you ran the installation.sh file to install all required modules, then"
         echo " the python file folder will be located in ~/softwares/cut_run/scripts/"
         echo " "
         read pathto
         echo " "
         echo " Your answer: $pathto"
         echo " "
fi

# If the user decided to analyze bigwig files from multiple folders
if [ "${multi_align,,}" == yes ]

    # Initialize the files string and the count
    then files=""
         count=0

         # loop over the folders in the bigwig directory
         for fold in "${bw_dir}"/*
         do

             # Loop over the bigwig files in the current directory
             for f in "${fold}"/*.bw
             do
                 # If the count is zero, then initialize the file string
                 if [ $count -eq 0 ]
                     then files="${f}"
                          count=$(($count + 1))
                 # Otherwise add the next file to the end of the string
                     else files="${files} ${f}"
                 fi
             done
         done

         echo "=======================BEGIN================================"
         echo " "
         echo " Making directory for the tracks.ini file at"

         trackdir="${bw_dir}/tracks"
         mkdir "${trackdir}"

         echo " ${trackdir}"
         echo " "
         echo "=======================END================================ "

         echo "=======================BEGIN================================"
         echo " "
         echo " Making the tracks.ini file using"
         echo " "

         trackfile="${trackdir}/tracks_bw.ini"

         echo " make_tracks_file --trackFiles ${files} -o ${trackfile}"

         make_tracks_file --trackFiles ${files} -o "${trackfile}"

         echo " "
         echo " "
         echo "=======================END================================== "

         edited_trackfile="${trackdir}/edited_trackfile_bw.ini"

         echo "=======================BEGIN================================"
         echo " "
         echo " Editing the tracks.ini file using"
         echo " "

         python3 "${pathto}/"edit_tracksfile.py "${trackfile}" "${edited_trackfile}"

         echo " python3 ${pathto}/edit_tracksfile.py ${trackfile} ${edited_trackfile}"
         echo " "
         echo " "
         echo "=======================END================================== "

         outfileroot="${trackdir}/"

         echo "=======================BEGIN================================"
         echo " "
         echo " Plotting each chromosome..."
         echo " "

         while read -r line;
         do
            count=0
            region=""
            IFS=$'\t'
            read -ra ADDR <<< "$line"
            for item in "${ADDR[@]}"
            do
                if [ $count -eq 0 ]
                    then region="${item}"
                         outfilename="${outfileroot}chr_${item}.pdf"
                         count=2
                    else region="${region}:0-${item}"
                         echo " Currently plotting $region"
                         echo " "
                fi
            done

            pyGenomeTracks --tracks "${edited_trackfile}" --region "$region" --plotWidth 25 --fontSize 8 --outFileName "${outfilename}"

         done < "${genome}"

         echo " "
         echo " "
         echo "=======================END================================== "

    # IF the user is plotting bigwig files from the same directory,
    elif [ "${multi_align}" == no ]

        # Initialize the files string and the count
        then files=""
             count=0

             # Loop over the files in the directory
             for f in "${bw_dir}"/*.bw
             do
                 # If the count is at zero
                 if [ $count -eq 0 ]

                     # then initialize the files to the first file
                     then files="${f}"
                          count=$(($count + 1))
                     # Otherwise, add the next file to the end of the string
                     else files="${files} ${f}"
                 fi
             done

         echo "=======================BEGIN================================"
         echo " "
         echo " Making directory for the tracks.ini file at"

         trackdir="${bw_dir}/tracks"
         mkdir "${trackdir}"

         echo " ${trackdir}"
         echo " "
         echo "=======================END================================ "

         echo "=======================BEGIN================================"
         echo " "
         echo " Making the tracks.ini file using"
         echo " "

         trackfile="${trackdir}/tracks_bw.ini"

         echo " make_tracks_file --trackFiles ${files} -o ${trackfile}"

         make_tracks_file --trackFiles ${files} -o "${trackfile}"

         echo " "
         echo " "
         echo "=======================END================================== "

         edited_trackfile="${trackdir}/edited_trackfile_bw.ini"

         echo "=======================BEGIN================================"
         echo " "
         echo " Editing the tracks.ini file using"
         echo " "

         python3 "${pathto}/"edit_tracksfile.py "${trackfile}" "${edited_trackfile}"

         echo " python3 ${pathto}/edit_tracksfile.py ${trackfile} ${edited_trackfile}"
         echo " "
         echo " "
         echo "=======================END================================== "

         outfileroot="${trackdir}/"

         echo "=======================BEGIN================================"
         echo " "
         echo " Plotting each chromosome..."
         echo " "

         while read -r line;
         do
            count=0
            region=""
            IFS=$'\t'
            read -ra ADDR <<< "$line"
            for item in "${ADDR[@]}"
            do
                if [ $count -eq 0 ]
                    then region="${item}"
                         outfilename="${outfileroot}chr_${item}.pdf"
                         count=2
                    else region="${region}:0-${item}"
                         echo " Currently plotting $region"
                         echo " "
                fi
            done

            pyGenomeTracks --tracks "${edited_trackfile}" --region "$region" --plotWidth 25 --fontSize 8 --outFileName "${outfilename}"
         done < "${genome}"

         echo " "
         echo " "
         echo "=======================END================================== "

fi
