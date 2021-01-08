#!/bin/bash

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
        line=($( echo ${line} | tr $'\t' "\n" ))
        datavalue="${line[3]}"
        if [ "$highest" -lt "$datavalue" ]
            then highest="$datavalue"
                 highest=$(($highest + 0))
        fi
    done <"${file}"
    echo "$highest"
}
