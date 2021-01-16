#!/bin/bash

# Want the user to have the option of using fastqc to view
# their files. Required arguments:
# -m multi_align  ->   Fed in from cut_run_pipeline_v3
# -f fastq_dir    ->   Directory to fastq files OR folders w/ files
#

while getopts f:m: options
do
case "${options}"
in
f) A=${OPTARG};;
m) B=${OPTARG};;
esac
done


fastq_dir=${A:-None}
multi_align=${B:-None}

if [ "${multi_align}" == None ]
    then stopper=0
         while [ $stopper -eq 0 ]
         do
             echo " "
             echo " multi_align"
             echo " "
             read multi_align
             echo " "
             echo " Your answer: $multi_align"
             echo " "
             if [[ ( "${multi_align,,}" == yes ) || ( "${multi_align,,}" == no )  ]]
                 then stopper=1
             else echo " Your answer was neither yes nor no. Please try again."
             fi
         done
fi

if [ "${fastq_dir}" == None ]
    then echo " "
         echo " fastq_dir"
         echo " "
         read fastq_dir
         echo " "
         echo " Your answer: $fastq_dir"
         echo " "
fi



if [ "${multi_align,,}" == yes ]
    then echo " ====================BEGIN=========================="
         echo " "
         echo " Beginning FASTQC Analysis of FASTQ files in subfolders"
         echo " of $fastq_dir"
         echo " "
         for folder in "${fastq_dir}"/*
         do
             mkdir "${folder}/fastqc"
             for file in "${folder}"/*.gz
             do
                 if [ "${file}" == "${folder}/*.gz" ]
                     then echo " There were no valid files in ${folder}"
                          pass="true"
                 else fastqc -o "${folder}/fastqc" "$file"
                 fi
             done
             echo " "
             echo " Complete. Analysis can be found in the folder"
             echo " ${folder}/fastqc"
             echo " "
         done

         echo " ====================END============================"

elif [ "${multi_align,,}" == no ]
    then echo " ====================BEGIN=========================="
         echo " "
         echo " Beginning FASTQC Analysis of FASTQ files in"
         echo " $fastq_dir"
         echo " "
         mkdir "${folder}/fastqc"
         for file in "${folder}"/*.gz
         do
             if [ "${file}" == "${folder}/*.gz" ]
                 then echo " There were no valid files in ${folder}"
             else fastqc -o "${folder}/fastqc" "$file"
             fi
         done
         echo " "
         echo " Complete. Analysis can be found in the folder"
         echo " ${folder}/fastqc"
         echo " "
         echo " ====================END============================"

fi
