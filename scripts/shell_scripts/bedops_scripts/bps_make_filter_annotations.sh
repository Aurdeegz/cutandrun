#!/bin/bash

# Use the getops to get optional input. In this case,
# the only optional input is the directory holding a
# .gff.gz annotation file.
while getopts d: options
do
case "$options"
in
d) A=${OPTARG};;
esac
done

# If the user does not assign a directory, set the
# directory to None
directory=${A:-None}

# Then, if the directory hasn't been given, ask
# the user to put the directory.
if [ "$directory" == None ]
    then echo " "
         echo " You have not given the path to a folder containing a"
         echo " .gff.gz annotation file. The annotation file can be"
         echo " found for a specific organism using the NCBI genome"
         echo " database:"
         echo " "
         echo " https://www.ncbi.nlm.nih.gov/genome/browse#!/overview/"
         echo " "
         echo " Once you have the .gff.gz file in the desired directory,"
         echo " please input the directory path in the form:"
         echo " "
         echo " path/to/folder"
         echo " "
         read directory
         echo " "
         echo " Your answer: $directory"
         echo " "
fi

# Once the directory has been given, then begin processing
# the annotation file
for file in "$directory"/*.gz
do
    # The file name, after unzipping, will be the same
    # without the .gz extension
    newfile="${file::-3}"

    # Use gunzip to unzip the file
    echo "=============================BEGIN================================ "
    echo " "
    echo " Unzipping the file ${file} using the command"
    echo " "
    echo " gunzip ${file}"
    echo " "
    gunzip "$file"
    echo " "
    echo " "
    echo "=============================END================================== "

    # Make the bed_file name for the annotation file
    bed_file="${directory}/annotations.bed"

    echo "=============================BEGIN================================ "
    echo " "
    echo " Converting the .gff annotation file to a .bed file using"
    echo " "
    echo " gff2bed < ${newfile} > ${bed_file}"
    echo " "
    gff2bed < "$newfile" > "$bed_file"
    echo " "
    echo " "
    echo "=============================END================================== "

    echo "=============================BEGIN================================ "
    echo " "
    echo " Finding the annotation fields (or types). In the bed file, these"
    echo " fields are located in column 8, and include things like:"
    echo " gene, CDS, exon, lnc_RNA"
    echo " "
    echo " First, a file ($directory/fields.txt) will be generated with only"
    echo " the values from column 8, using the command"
    echo " "
    echo " cut -f8 $bed_file > $directory/fields.txt"
    echo " "
    cut -f8 "$bed_file" > "$directory/fields.txt"
    echo " "
    echo " Next, a while loop will be used to check for new fields, and add"
    echo " them to an array. This part takes a few mintues..."
    echo " "

    # Variable used for finding the first new field
    firstline=0
    # Declare the array ants, used to hold 'ANnoTationS'
    declare -a ants
    # Loop over the lines in the fields file
    while IFS= read -r line;
    do
        # Initialize counter variables. If add and count
        # are equal, then we have a new field
        add=0
        count=0
        # Loop over the items in the ants array. If the
        # item in the current line of fields is diferent
        # then the item in ants, then we add one to add.
        # Always add one to count.
        for item in "${ants[@]}"
        do
            if [ "$item" != "$line" ]
                then add=$(($add + 1))
            fi
            count=$(($count + 1))
        done

        # If add and count are different, then at least one element
        # of ants was equal to the field. If they are equal, then
        # the line contains a new item!!
        if [ $add -eq $count ]
            # Check to see whether this is the first line of fields
            then if [ $firstline -eq 0 ]
                     # If so, then add it as the first element of ants,
                     # stripping the newline character if needed
                     then ants+=("${line//[$'\n']}")
                          echo " New field found!     ${line}"
                          echo " "
                          firstline=$(($firstline + 1))
                          count=0
                          add=0
                     # If this isn't the first line, then make sure
                     # that the add variable is greater than zero
                     elif [ $add -gt 0 ]
                     # If so, then add the next element to the ants
                     # array and continue.
                     then ants+=("${line//[$'\n']}")
                          echo " New field found!     ${line}"
                          echo " "
                          count=0
                          add=0
                 fi
        fi
    done <"$directory/fields.txt"

    # All specific annotation bed files will be stored in this
    # directory
    annot_dir="${directory}/annotation_types"

    # and make said directory
    mkdir "$annot_dir"

    # Next, we loop over the fields we found in ants.
    # We will first write the fields file to be all of
    # the annotations, and then we will use awk to sort
    # the file based on that annotation. The sorted file
    # will be saved in the annotation_types directory
    for item in "${ants[@]}"
    do
        if [ $firstline == 1 ]
            then echo "$item">"$directory/fields.txt"
                 firstline=$(($firstline + 1))
            else echo "$item">>"$directory/fields.txt"
        fi
        filename="${annot_dir}/annotation_${item}.bed"
        awk 'BEGIN{OFS="\t"}{ if($8 == "'$item'") { print $1,$2,$3,$4,0,$6,$8} }' "$bed_file" > "$filename"
    done
    # Move the fields.txt file to the annotation_types directory
    mv "${directory}/fields.txt" "${annot_dir}/fields.txt"
done
