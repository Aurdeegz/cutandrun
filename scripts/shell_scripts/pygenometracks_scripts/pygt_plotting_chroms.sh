#!/bin/bash

# Use getopts to get the optional arguments
# for this scripts
while getopts b:g:p: option
do
case "${option}"
in
b) A=${OPTARG};;  # b) -> bigwig file directory
g) C=${OPTARG};;  # g) -> .genome file directory
p) D=${OPTARG};;  # p) -> path to edit_tracksfile.py
esac
done

# Set all of the inputs to the default value of None
bw_dir=${A:-None}
genome=${C:-None}
pathto=${D:-None}

# If the user did not give a value for the bigwig directory
if [ "$bw_dir" == None ]

    # If the user is plotting bigwig files from one folder
    then echo " You have not given the filepath to the folders"
         echo " holding the bigwig files to be plotted."
         read bw_dir
         echo " "
         echo " Your answer: $bw_dir"
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
# Initialize the files string and the count
files=""
count=0

# loop over the folders in the bigwig directory
for fold in "${bw_dir}"/*
do
if [[ ( "${fold}" == "${bw_dir}/tracks" ) || ( "${fold}" == "${bw_dir}/peak_annotations" ) ]]
    then continue
    # Loop over the bigwig files in the current directory
else for f in "${fold}"/*.bw
     do
         # If the count is zero, then initialize the file string
         if [ $count -eq 0 ]
             then files="${f}"
                  count=$(($count + 1))
         # Otherwise add the next file to the end of the string
         else files="${files} ${f}"
         fi
     done
fi
done

echo "=======================BEGIN================================"
echo " "
echo " Making directory for the tracks.ini file at"

trackdir="${bw_dir}/tracks"
#mkdir "${trackdir}"

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
