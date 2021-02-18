"""
Kenneth P. Callahan

22 January 2021

==========================================================================================================
Python 3.8.5

get_maxs.py
==========================================================================================================

REQURIES LINUX

This is a small python script that will get the highest value from a bedgraph or narrowPeak file.
The command line arguments are:

args[0] : get_maxs.py
args[1] : comma separated list of files
args[2] : chrom:start-end

This program prints the highest value found, which can be saved as a variable using the syntax

highest_value=$(python3 get_maxs.py "file1.narrowPeak,file2.narrowPeak" chr1:0-19000)

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
    Given a list of system arguments, check that they are accepatble arguments.
    These arguments should be:

    args[0] : get_maxs.py
    args[1] : comma separated list of files
    args[2] : chrom:start-end
    """
    # Assert that only three system arguments can be given.
    assert len(args) == 3, "Only three system arguments should be given"

    # Split the first argument on the comma, it should be a comma separated list of file strings
    f_list = args[1].split(',')
    # Loop over the files in the list
    for f in f_list:
        # Try to open the file, reading. If this fails, the program will exit
        with open(f, 'r') as file:
            # Close the file if this works
            file.close()
        # Check the file format using the identify_filetype_format() function
        f_format = identify_filetype_format(f, extensions, forms)
        # IF this returns Wrong Format
        if f_format == "Wrong Format":
            # Then tell the user that the files weren't in the correct format and exit
            raise ValueError(f"The file {f} is not in the correct format.")
    # The second argument should be a GenomeBrowser region, which has the format
    # chromosome:Beginning-Ending. Use asser to make sure that the proper characters are there
    assert ':' in args[2] and '-' in args[2], "The chromosome region should have the form chr:start-end"
    # If the assert statment is True, then continue to format the regions.
    # Split on the : character
    chr_reg = args[2].split(':')
    # Initialize chrom_list variable with the chromosome (zeroeth element of list after splitting)
    chrom_list = [chr_reg[0]]
    # Split the first element of chr_reg list on the - character
    regs = chr_reg[1].split('-')
    # and concatenate chrom_list with regs. Chrom list now has
    # ["chromosome", "Beginning", "Ending"]
    chrom_list += regs
    # Return the list of files and the chrom_list
    return f_list, chrom_list

def identify_filetype_format(file,
                             extension_dict,
                             formatting_dict):
    """
    Given a file name (as a string), an extenstion dictionary (keys are extensions,
    values are the name of the file type), and a foramtting dictionary (keys are
    file types, values are dictionaries with keys as headers, value as column
    number in mathematical counting), return a dictionary with keys as one of the
    sorting areas (chrom, start, end, value) and values as the column those
    areas appear in the given file type.
    """
    # These are the columns of any file that we care about. Value depends on the
    # file type and which value is actually plotted.
    sorting_areas = ["chromosome",
                     "region_start",
                     "region_end",
                     "value"]
    # Initialize the sorting format dictionary.
    sorting_format = {}
    # Split the file on the period and save the last element of the list as the extension.
    # "path/to/file.narrowPeak" ->   ["path/to/file", "narrowPeak"]  ->  "narrowPeak"
    extension = file.split('.')[-1]
    # If the extension is in the given extension dictionary
    if extension in extension_dict.keys():
        # Save the file type to the variable ext
        ext = extension_dict[extension]
        # Loop over the sorting_areas list above
        for area in sorting_areas:
            # If the area is one of the keys of the formatting_dict
            if area in formatting_dict[ext].keys():
                # Then update the sorting_format dictionary with the area as a key
                # and the corresponding value from formatting_dict[ext].
                sorting_format[area] = formatting_dict[ext][area]
        # Return the sorting_format dict and the extension
        return sorting_format, extension
    # If the extension is not one of the defined file types
    else:
        # Then return the string "Wrong Format"
        return "Wrong Format"

def update_highest_value(file,
                         current_highest,
                         sorting_format,
                         delimiter):
    """
    Given a file, the current highest calue found, the sorting_format dictionary,
    and a delimiter for the file, return either the new highest value if a value
    in this file is greater than the previous highest value or the previous
    highest value if there are no higher values in the given file.
    """
    # Computer scientists start counting at zero. Math people start counting at 1.
    # We are math people, so we need to translate to computer people counting :)
    value_col = (int(sorting_format['value']) - 1)
    # Open the file, reading, call it f
    with open(file, 'r') as f:
        # Use list comprehension to get the values from the file. This line of code does:
        # Loops over lines in the file, strips the line, splits the line on the delimiter,
        # takes the element of the list in the value column, and turns that value into a float.
        try:
            values = [float(line.strip().split(delimiter)[value_col]) for line in f]
        # If for some reason this list comprehension fails, then a value could not be floated
        # Or that column of the file did not exist.
        except:
            raise ValueError(f"Some of the values in the value column were not floating point numbers :( ")
        # If the number of values found are zero, then just return the previous highest value
        if len(values) == 0:
            return current_highest
        # Use the sorted function to sort the values in reverse order (largest value is 0)
        values = sorted(values, reverse = True)
        # Close the file once all of this is completed.
        f.close()
    # If the current highest value is greater than the highest value found in the file
    if current_highest > values[0]:
        # then return the curent highest, as this file only has lower values
        return current_highest
    # Otherwise, the value in the file is greater than the current highest
    else:
        # So return that value
        return values[0]


def get_highest_value(file_list,
                      chrom_list,
                      delimiter,
                      extensions_dict = extensions,
                      formatting_dict = forms):
    """
    Given a list of files, the chromosome region list, and a delimiter for those files, return
    the highest value from the files

    Requires subprocess.call with shell = True to run some shell scripts
    """
    # Initialize the highest value
    highest = 0
    # Loop over the files in the file list
    for file in file_list:
        # Use identify_filetype_format() to get the sorting_format and the extension
        sort_form, extension = identify_filetype_format(file, extensions_dict, formatting_dict)
        # Use string formatting to get the conditions for awk filtering
        p1 = f'''"{chrom_list[0]}" == ${sort_form['chromosome']}'''   # Chromosome of file is the same as chromosome of interest
        p2 = f'''{chrom_list[1]} <= ${sort_form['region_start']}'''   # Region of file is between region start
        p3 = f'''{chrom_list[2]} >= ${sort_form['region_end']}'''     # and region end given
        # Combine the conditions in an awk filtering string using string formatting
        filter_file = f""" awk '{{ if( {p1} && {p2} && {p3} ) {{ print }} }}' "{file}" > "temp.{extension}" """
        # Use subprocess.call to filter the file
        subprocess.call(filter_file, shell=True)
        # Use the update_highest_value() functino to update the highest variabel
        highest = update_highest_value(f"temp.{extension}",
                                       highest,
                                       sort_form,
                                       delimiter)
        # Use string formatting to create the removal string
        removal = f"rm temp.{extension}"
        # Pass the removal string into subprocess.call to delete the temporary file
        subprocess.call(removal, shell=True)
    # At the end, return the highest value
    return highest

#
#
######################################################################
#
#           main() function

def main():
    """
    Get the system arguments
    Check that they are valid
    Use get_highest_value() to get the highest value from the files
    print the highest value so it can be saved in a shell script.
    """
    args = sys.argv
    file_list, chrom_list = check_sysargs(args)
    highest_value = get_highest_value(file_list,
                                      chrom_list,
                                      '\t')
    print(f"{highest_value}")


main()
#
#
######################################################################
