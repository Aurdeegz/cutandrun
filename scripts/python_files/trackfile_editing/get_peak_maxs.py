"""
Kenneth P. Callahan

22 January 2021

==========================================================
Python 3.8.5

get_maxs.py
==========================================================

A docstring will be placed here :)

"""

###########################################################
#
#         Imports

import subprocess  # Used for executing shell scripts in python
import sys         # Used for grabbing system inputs

#
#
###########################################################
#
#        Pre-defined variables

# File extensions that are allowed are the keys, and the
# file type associated are the values. So far, I've only
# used bedgraph and narrowPeak files, but bed files can
# easily be added.
extensions = {'bg' : 'bedgraph',
              'bdg' : 'bedgraph',
              'bedgraph' : 'bedgraph',
              'narrowPeak' : 'narrowPeak'}

# A dictionary containign dictionaries. Keys in the forms
# dictionary are file types. The values are dictionaries
# with information regarding that file type. This serves
# two purposes: for awk filtering using $1, $2, $3 (check
# out get_highest_value()) and knowing where the intensity
# value (number of reads in the case of bedgraph files,
# signal intensity in the case of narrowPeak files) is.
#
# If you add a format to this dictionary, just be sure to
# use the following keys:
#
#   Key         |     Meaning
#--------------------------------------------------------------------
# chromosome    | this is the chromosome identifier in the file
# region_start  | This is the beginning of a genomic region, in bases
# region_end    | This is the end of a genomic region, in bases
# value         | Whatever value you wish to find the maximum of
#                 ( In my case, signal intensity / number of reads)
#--------------------------------------------------------------------
#
# The functions defined below look for these keys specifically for
# awk filtering and finding the column of the file with the value
# you wish to find the maximum of.
forms = {'narrowPeak': {'chromosome' : '1',
                        'region_start' : '2',
                        'region_end' : '3',
                        'region_name' : '4',
                        'region_score' : '5',
                        'region_strand' : '6',
                        'value' : '7',
                        'p' : '8',
                        'q' : '9',
                        'peak' : '10'},
         'bedgraph' :  {'chromosome' : '1',
                        'region_start' : '2',
                        'region_end' : '3',
                        'value' : '4'} }

#
#
##################################################################
#
#       Functions

def check_sysargs(args):
    """
    args[0] : get_maxs.py
    args[1] : comma separated list of files
    args[2] : chrom:start-end
    """
    #
    assert len(args) == 3, "Only three system arguments should be given"

    # Check the files, make a list.
    f_list = args[1].split(',')
    #
    for f in f_list:
        #
        with open(f, 'r') as file:
            file.close()
        f_format = identify_filetype_format(f, extensions, forms)
        #
        if f_format == "Wrong Format":
            sys.exit()
    #
    assert ':' in args[2] and '-' in args[2], "The chromosome region should have the form chr:start-end"
    #
    chr_reg = args[2].split(':')
    chrom_list = [chr_reg[0]]
    regs = chr_reg[1].split('-')
    chrom_list += regs
    #
    return f_list, chrom_list

def identify_filetype_format(file,
                             extension_dict,
                             formatting_dict):
    """
    a
    """
    #
    sorting_areas = ["chromosome",
                     "region_start",
                     "region_end",
                     "value"]
    #
    sorting_format = {}
    #
    extension = file.split('.')[-1]
    #
    if extension in extension_dict.keys():
        #
        ext = extension_dict[extension]
        for area in sorting_areas:
            #
            if area in formatting_dict[ext].keys():
                #
                sorting_format[area] = formatting_dict[ext][area]
        return sorting_format, extension
    #
    else:
        return "Wrong Format"

def update_highest_value(file,
                         current_highest,
                         sorting_format,
                         delimiter):
    """
    a
    """
    # Compensate for lists starting at 0, subtract 1
    value_col = (int(sorting_format['value']) - 1)
    #
    with open(file, 'r') as f:
        #
        values = [float(line.strip().split(delimiter)[value_col]) for line in f]
        #
        if len(values) == 0:
            return current_highest
        #
        values = sorted(values, reverse = True)
        f.close()
    #
    if current_highest > values[0]:
        return current_highest
    #
    else:
        return values[0]


def get_highest_value(file_list,
                      chrom_list,
                      delimiter):
    """
    a
    """
    #
    highest = 0
    #
    for file in file_list:
        #
        form, extension = identify_filetype_format(file, extensions, forms)
        #
        p1 = f'''"{chrom_list[0]}" == ${form['chromosome']}'''
        p2 = f'''{chrom_list[1]} <= ${form['region_start']}'''
        p3 = f'''{chrom_list[2]} >= ${form['region_end']}'''
        #
        filter_file = f""" awk '{{ if( {p1} && {p2} && {p3} ) {{ print }} }}' "{file}" > "temp.{extension}" """
        #
        subprocess.call(filter_file, shell=True)
        #
        highest = update_highest_value(f"temp.{extension}",
                                       highest,
                                       form,
                                       delimiter)
        #
        removal = f"rm temp.{extension}"
        #
        subprocess.call(removal, shell=True)
    #
    return highest

#
#
######################################################################
#
#           main() function

def main():
    """
    a
    """
    #
    args = sys.argv
    #
    file_list, chrom_list = check_sysargs(args)
    #
    highest_value = get_highest_value(file_list,
                                      chrom_list,
                                      '\t')
    #
    print(f"{highest_value}")

#
main()
#
#
######################################################################
