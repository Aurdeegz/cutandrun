#!/bin/bash

while getopts d:i: options
do
case "${options}"
in
d) A=${OPTARG};;
i) B=${OPTARG};;
esac
done

directory=${A:-None}
index=${B:-None}

if [ "${directory}" == None ]
    then echo " "
         echo " You have not given the directory for the fasta file(s)"
         echo " that will be made into a bowtie2 index."
         echo " "
         echo " Please input the filepath to the fasta file(s) to be used"
         echo " as a bowtie2 index."
         echo " "
         read directory
         echo " "
         echo " Your answer: $directory"
         echo " "
#         if [ "${directory:-2:-1}" == "/" ]
#             then directory="${directory::-1}"
#         fi
fi

if [ "${index}" == None ]
    then echo " "
         echo " Please input the bowtie2 index name you would like to use."
         echo " "
         read index
         echo " "
         echo " Your answer: $index"
         echo " "
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

check_for_index () {
    # Check for .bt2 files already there
    for f in "$1"/*.bt2
    do
        if [ "${f}" == "$1/*.bt2" ]
            then outstring="False"
        else outstring="True"
             break
        fi
    done
    echo "${outstring}"
}

check_file_extension () {
    # Check the file extension of the file(s)

    declare -a extensions

    arr_count=0
    for f in "$1"/*
    do
        file=($( get_array "$f" "." ))
        if [[ ( ${#extensions} -eq 0 ) && ( ${#file} -gt 1 ) ]]
            then extensions[0]="${file[-1]}"
                 arr_count=$(( $arr_count + 1 ))
        else count=0
             echo " counting"
             for ext in "${extensions[@]}"
             do
                 if [ "$ext" == "${file[-1]}" ]
                     then count=$(( $count + 1 ))
                 fi
             done
             if [ $count -lt 1 ]
                 then extensions[$arr_count]="${file[-1]}"
             fi
             arr_count=$(( $arr_count + 1 ))
        fi
    done

    count=0
    for ext in "${extensions[@]}"
    do
        count=$(( $count + 1 ))
    done

    if [ $count -eq 1 ]
        then echo "${extensions[0]}"
    else echo "mixed"
    fi
}


index_made=$( check_for_index "${directory}" )
if [ "${index_made}" == "True" ]
    then echo " An index was already found in the given directory."
         exit
fi

ext=$( check_file_extension "${directory}" )

if [ "${ext}" == "mixed" ]
    then echo " Mixed file type were found in the given directory"
         exit
elif [ "${ext}" == "gz" ]
    then for f in "${directory}"/*."${ext}"
         do
             gunzip "${f}"
         done
         ext=$( check_file_extension "${directory}" )
fi

files=""

echo " "
echo " Files found in the given directory:"
echo " "
for f in "${directory}"/*.${ext}
do
    files="${files},${f}"
done

index_path="${directory}/${index}"

echo "=====================BEGIN========================="
echo " "
echo " Building a bowtie2 index as ${index_path}"
echo " "

bowtie2-build "${files:1}" "${index_path}"

echo " "
echo " Your index files are:"
echo " "
for ind in "${directory}"/*.bt2
do
    echo " ${ind}"
done
echo " "
echo "=====================END==========================="
