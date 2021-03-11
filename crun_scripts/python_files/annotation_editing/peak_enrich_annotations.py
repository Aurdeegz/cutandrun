"""
Kenneth P. Callahan

26 January 2021

==============================================================================================================
Python 3.8.5

peak_enrich_annotations.py
==============================================================================================================

This python file is meant to search through a cutandrun sequencing file directory, identify a macs3_out folder
and subfolders, compare the peak regions identified by macs3 to annotations (with a little wiggle room),
combine all of the annotations/peaks found, and write those to a file. The system arguments are

    args[0]   :   peak_enrich_annotations.py
    args[1]   :   directory to the experimental files.
    args[2]   :   directory to annotation files
    OPTIONAL
    args[3]   :   delimiter  default \t
    args[4]   :   file type, default xls

This program assumes that the filter_macs3out_files.py program was run prior to this program running. Please
check out the main function and helper functions for more details about this program.

"""

##############################################################################################################
#
#         Importables


import sys          # Used for getting the system argument inputs
import os           #
import subprocess   # Used for invoking shell commands in python
import glob         # Used for iterating over files in a directory

#
#
##############################################################################################################
#
#         Pre-defined variables

# Dictionary containing the columns (in computer scientist counting) of each file type
# that will be retained, along with the information that they encode.
#
# The keys are used to identify the column in the split line, the value are used
# for writing the headers.
# If you use this on it's own and your filetype is not included here, then simply
# add that file extension as a key in the dictionary, and define the subdictionary
# with the columns you wish to keep.
filetype_formatting={"narrowPeak" : {'0' : 'chrom',                  # output from macs3, which tells
                                     '1' : 'chromStart',             # us useful stats about the peak
                                     '2' : 'chromEnd',               # regions.
                                     '6' : 'signalValue',
                                     '7' : 'pValue (-log base 10)',
                                     '8' : 'qValue (-log base 10)',
                                     '9' : 'peak'},
                     "xls" : {'0' : 'chrom',                         # Also macs3 output, but this file
                              '1' : 'chromStart',                    # type shows us the fold enrichment
                              '2' : 'chromEnd',                      # also. This is the default filetype
                              '5' : 'peak_position',                 # for peak files
                              '6' : 'pValue (-log base 10)',
                              '7' : 'fold_enrichment',
                              '8' : 'qValue (-log base 10)'},
                     "bed" : {'0' : 'chrom',                         # Annotation files are bed files with
                               '1' : 'chromStart',                   # seven columns: bed6 + annote type
                               '2' : 'chromEnd',                     # These are required for comparing
                               '3' : 'identifier',                   # peak regions
                               '5' : 'strandedness',
                               '6' : 'annotation_type'} }

# The titles of the folders should encode the information regarding the experiments.
# These folders must include one of the following substrings, as described in the
# README file.
title_folder_formats = ["_exp_",            # experiment
                        "_exper_",          # experiment
                        "_experiment_",     # experiment
                        "_rep_",            # replicate (experiment)
                        "_replicate_",      # replicate (experimient)
                        "_enrich_",         # enrichment (experiment)
                        "_enrichment_"]     # enrichment (experiment)

#
#
##############################################################################################################
#
#         Functions: Relating to comparing one file


def get_exper_title(directory,
                    title_format_list):
    """
    Given a directory and the list of acceptable title formats
    (substrings that are in the folder string), either return
    the folder string containing a suitable title substring.
    If no path is found, then return an error message
    """
    # Split the directory path on '/' to get a list of folders
    split_dirpath = directory.split('/')
    # Loop over the acceptable title formats
    for t in title_format_list:
        # Loop over the folders in the path
        for fold in split_dirpath:
            # If a folder contains a title substring
            if t in fold:
                # Then return that folder
                return fold
    # If the list completes without returning a value,
    # then return an error string.
    return "No title folder found"

def get_bound_keys(formatting_dictionary,
                   file_type):
    """
    Given a dictionary with formatting rules and the type
    of file (file extension), return the keys (integers)
    corresponding to the chromosome name, the strand/region
    start, and the strand/region end.
    """
    # Loop over the keys and values in the subdictionary
    # which defines the formatting for the given file type
    for key, value in formatting_dictionary[file_type].items():
        # If the value is "chrom"
        if value == "chrom":
            # Then assign the chrom_key variable as the key
            chrom_key = int(key)
        # Or if the value is "chromStart"
        elif value == "chromStart":
            # Then assign the start_key variable as the key
            start_key = int(key)
        # Or if the value is "chromEnd"
        elif value == "chromEnd":
            # Then assign the end_key variable as the key
            end_key = int(key)
    # Once the loop completes, return the keys found
    return chrom_key, start_key, end_key

def compare_regions(peak_chrom,     #Chromosome associated with peak
                    peak_start,     #Start associated with peak
                    peak_end,       #End associated with peak
                    region_chrom,   #Chromosome associated with region
                    region_start,   #Start associated with region
                    region_end):    #End associated with region
    """
    Given information regarding a peak region and an annotation region,
    return one of the following values

    True:
        peak_end and region_start overlap
        peak_start and region_end overlap
        peak_start and peak_end between region start and region end
        region_start and region_end between peak_start and peak_end

    'continue'
        peak_chrom and region_chrom are not the same

    'break'
        peak_start and peak_end are less than region_start and region_end

    False
        If none of the other conditions are met

    This function is used inside of a loop, so the break string and continue
    string correspond to leaving the loop and continueing to the next iteration
    """
    # If the peak chromosome and region chromosome are different
    if peak_chrom != region_chrom:
        # Then continue, these annotation are on different chromosomes
        return 'continue'
    # Or if the peak end is between the region start and region end
    elif peak_start <= region_end and peak_end >= region_end:
        # Then return True, as the peak and annotation overlap
        return True
    # Or if the peak start is between the region start and end
    elif peak_start <= region_start and peak_end >= region_start:
        # Then return True, the peak and annotation overlap
        return True
    # Or if the region consumes the entire peak
    elif peak_start >= region_start and peak_end <= region_end:
        # Then return True
        return True
    # Or if the peak consumes the entire region
    elif peak_start <= region_start and peak_end >= region_end:
        # Then return True
        return True
    # Or if the chromosome is the same (checked in the first if) and the
    # region is further along the chromosome than the peak
    elif peak_start <= region_start and peak_end <= region_end:
        # Then return 'break', all subsequent annotations are beyond the peak
        return 'break'
    # If none of these conditions are met, then return False
    else:
        # This means that we are on the right chromosome, but the peak and annotations
        # do not overlap, but the peak is still upstream of the annotation
        return False


def check_line_annotes(annot_file,
                       annot_extension,
                       peak_chrom,
                       peak_start,
                       peak_end,
                       delimiter,
                       formatting_dictionary,
                       region_wiggle = 1000):
    """
    Given an annotation file, the file extension of the annotation file, the
    peak region chromosome, the peak region start, the peak region end, the
    delimiter for the files, the formatting dictionary, and an integer that
    defines the "wiggle room" on either end of a peak region (number of nucleotides
    that will be included in the annotation region), return a list of strings
    formatted to include the annotation region and the peak associated with that
    region.
    """
    # Initialize the list that holds regions/peaks whose comparison was True
    true_compared = []
    # Use the get_bound_keys() function to get the chrom, start, and end
    # keys for the region
    reg_chrom_key, reg_start_key, reg_end_key = get_bound_keys(formatting_dictionary,
                                                               annot_extension)
    # Open and read the annotation file, call it a
    with open(annot_file, 'r') as a:
        # Loop over the lines in a
        for line in a:
            # strip the newline character and split the line on the delimiter
            split_line = line.strip().split(delimiter)
            # Assign the region_chrom as the reg_chrom_key(th) element of the split line
            region_chrom = split_line[reg_chrom_key]
            # Assign the region_start as the reg_start_key(th) element minus region_wiggle
            region_start = int(split_line[reg_start_key]) - region_wiggle
            # Assign the region_start as the reg_end_key(th) element plus region_wiggle
            region_end = int(split_line[reg_end_key]) + region_wiggle
            # Use the compare_regions() function to compare the peak to the region
            compare = compare_regions(peak_chrom, peak_start, peak_end,
                                      region_chrom, region_start, region_end)
            # If the comparison returns True
            if compare == True:
                # Then create a formatted line for the comparison using format_line()
                newline = format_line(formatting_dictionary, annot_extension,
                                      split_line, delimiter)
                # Print the newline so the user can see where the program is at
                print(newline)
                # And add the newline to the true_compare list
                true_compared.append(newline)
            # If the comparison returns continue
            elif compare == 'continue':
                # Then continue
                continue
            # If the comparison returns 'break'
            elif compare == 'break':
                # then break the loop
                break
        # Close the file after the loop is completed
        a.close()
    # and return the comparison list
    return true_compared

def make_compared_lines(true_compared_lines,
                        title,
                        peak_file_line):
    """
    Given a list of valid compared lines, the title associated with the peaks,
    and the line from the peak file, use list comprehension to create a list
    of tuples containing the comparions, the title, and the peak file line.
    """
    return [(line, title, peak_file_line) for line in true_compared_lines]

def format_line(formatting_dictionary,
                file_extension,
                a_split_line,
                delimiter):
    """
    Given the formatting dictioanry, the file extension for a file, a split
    line (list), and the delimiter to separate line elements, return a
    line in the form

    <split_line[0]><delimiter><split_line[1]><delimiter>...<split_line[n-1]>\n

    for a split line with n elements.
    """
    # Use list comprehension to create a list of formatting keys
    # This will help us get only the elements of the lines we want
    # for the new line
    indice = [int(key) for key in formatting_dictionary[file_extension].keys() ]
    # Sort the index list (smallest to largest, default)
    indice = sorted(indice)
    # Initialize the newline variable as the 0th element of the index list.
    newline = f"{a_split_line[indice[0]]}"
    # Loop over the indices in the index list
    for index in indice:
        # If the index is the already used index
        if index == indice[0]:
            # then continue to the next iteration
            continue
        # Otherwise
        else:
            # build the newline string using the split line, delimiter, and newline
            newline = f"{newline}{delimiter}{a_split_line[index]}"
    # At the end, add a newline character (\n) to the end of the line
    newline = f"{newline}\n"
    # and return the new line
    return newline

def make_header(formatting_dictionary,
                file_type,
                delimiter):
    """
    Given a formatting dictionary, the desired file type and the desired
    delimiter, return a line containing the header information
    """
    # Use list comprehension to get the positions of the desired headers
    positions = [int(key) for key in formatting_dictionary[file_type].keys()]
    # And sort the list (smallest to largest, default)
    positions = sorted(positions)
    # Initialize the newline variable with the zeroth element of positions
    newline = f"{formatting_dictionary[file_type][str(positions[0])]}"
    # Delete the zeroeth element of positions, as it is already used
    del positions[0]
    # Loop over the remaining keys in positions
    for position in positions:
        # and build the newline variable
        newline = f"{newline}{delimiter}{formatting_dictionary[file_type][str(position)]}"
    # Add a newline character the variable newline
    newline = f"{newline}\n"
    # and return the new line
    return newline

def get_enrich_annote_lines(filtered_file_dir,
                            annot_dir,
                            formatting_dictionary,
                            title_format_list,
                            delimiter,
                            file_type = "xls"):
    """
    Given the directory to filtered data files (xls or narrowPeak from MACS3),
    the directory path to the annotation files, a formatting dictionary which
    has all of the desired values from the files, a delimiter that the files
    use (tab is the most common I see), and a file type (auto set to xls, as
    these files include the enrichment value from MACS3), return a dictionary of lists,
    where each key is a file and each value is a comparison list between
    the peaks in that file and the annotations from annot_dir.
    """
    # Use the get_exper_title() function to extract the titlefrom the folder path
    title = get_exper_title(filtered_file_dir, title_format_list)
    # If no title folder was found
    if title == "No title folder found":
        # Then raise a value error and exit.
        raise ValueError(f"Unable to extract a title from the folderpath.")
    # If no value error is raised, then make the header for the file type
    header = make_header(formatting_dictionary, file_type, delimiter)
    # Initialize the annotation header string
    annot_header = ""
    # Initialize the comparison holder list
    comp_holder = []
    # Initialize the comparisons dictionary
    comparisons = {}
    # Loop over the files in the filtered file directory of the specified type
    for file in glob.iglob(f"{filtered_file_dir}/*.{file_type}"):
        # Tell the user that the program is finding annotated regions that overlap
        # With the given peak file
        print(f"Finding annotated regions that overlap with peaks from {file}\n")
        # Get the peak chromosome, start, and end key using get_bound_keys()
        peak_chrom_key, peak_start_key, peak_end_key = get_bound_keys(formatting_dictionary, file_type)
        # Initialize the file comparisons list
        file_comparisons = []
        # Open the file and read, call it f
        with open(file, 'r') as f:
            # Loop over the (l)ines in the file
            for l in f:
                # Strip the line and split on the delimiter
                splitted = l.strip().split(delimiter)
                # Use the format_line() function to reformat the line
                reformed_line = format_line(formatting_dictionary, file_type,
                                            splitted, delimiter)
                # Get the chromosome, peak start and peak end information
                peak_chrom = splitted[peak_chrom_key]
                peak_start = int(splitted[peak_start_key])
                peak_end = int(splitted[peak_end_key])
                # Loop over the annotation files in the annotation directory
                for annot_file in glob.iglob(f"{annot_dir}/*"):
                    # Get the annotation file extension
                    annot_extension = annot_file.split('.')[-1]
                    # Or if the annotation extension is txt or if region is in the file
                    # then simply continue, those files are not of interest
                    if annot_extension == 'txt' or "region" in annot_file:
                        continue
                    # If the annotation header has not yet been updated
                    if annot_header == "":
                        # Then use make_header() to update the annotation header
                        annot_header = make_header(formatting_dictionary, annot_extension, delimiter)
                    # Use the check_line_annotes() function to get a list of comparisons
                    # for the given annotation file and peak region combination
                    new_comparisons = check_line_annotes(annot_file,
                                                         annot_extension,
                                                         peak_chrom,
                                                         peak_start,
                                                         peak_end,
                                                         delimiter,
                                                         formatting_dictionary)
                    # Make these comparisons into strings (lines)
                    new_comparisons = make_compared_lines(new_comparisons,
                                                          title,
                                                          reformed_line)
                    # and add those lines to the files_comparisons list
                    file_comparisons += new_comparisons
            # After looping over every line in the file and every annoatation file, close
            # the file
            f.close()
        # Make the headers tuple using annot_header, exp_title, file_comparisons
        headers = (annot_header, "exp_title", header)
        # Update the comparisons dictionary with the headers and the
        # comparisons list, under the filename as the key
        comparisons[file] = headers, file_comparisons
    # Return the comparisons dictionary at the end
    return comparisons

#
#
##############################################################################################################
#
#               Functions: Relating to merging lines between files

def make_empty(formatting_dictionary,
               file_type,
               delimiter):
    """
    Given a formatting dictionary, a file type, and a delimiter,
    return a string of '-' characters separated by the delimiter.
    """
    # Get the number of delimiters required. This is the number of keys in
    # the formatting dictionary [file_type] subdictionary minus 1
    delim_num = len(list(formatting_dictionary[file_type].keys())) - 1
    # Initialize the new line
    newline = f"-"
    # Loop over the number of delimiters needed
    for _ in range(delim_num):
        # Update the new line with the current line, delim, and -
        newline = f"{newline}{delimiter}-"
    # Add a newline character to the end
    newline = f"{newline}\n"
    # and return the newline
    return newline

def merge_comparison_lists(comparisons_list,
                           extensions_list,
                           formatting_dictionary,
                           delimiter):
    """
    Given a list of lists containing formatted compared regions strings,
    a list of extensions for each file, a formatting dictionary, and a
    delimiter, return a list of output strings that merge all lists in the
    comparisons list.

    This works by looping over the comparisons list twice, and comparing
    the sublists in the comparisons list to  the other sublists.

    The outstrs list will look like:
    ["annotation_region_information", ["All", "peaks", "associated"],
     "annotation_region_information", ["All", "peaks", "associated"],
     etc.]

    The annotation region information will be in even elements, and list
    of the peaks will be on the odd elements.
    """
    # Initialize the outstrings list. This list will be returned
    outstrs = []
    # Initialize the list of regions that we have already seen
    seen = []
    # Initailize the counter variable for list 1
    listcount_1 = 0
    # Loop over the lists in the comparisons list. Call it list_1
    for list_1 in comparisons_list:
        # Loop over the sublists in list_1
        for sublist_1 in list_1:
            # Initialize the list_1 outstring list
            l1_outstr = []
            # If the 0th element of sublist_1 is not in the seen list
            if sublist_1[0] not in seen:
                # Then add it (This is the annotation region)
                seen.append(sublist_1[0])
                # Add thos region to the l1_outstr list
                l1_outstr.append(sublist_1[0])
                # And add the remaining elemtns of the sublist to the l1_outstr list.
                l1_outstr.append([list(sublist_1)[1:]])
            # Or if the sublist is in the seen list,
            elif sublist_1[0] in seen:
                # Then just continue
                continue
            # Initialize list count 2
            listcount_2 = 0
            # Loop over the lists in comparisons_list again, call it list_2
            for list_2 in comparisons_list:
                # If list_1 and list_2 are the same
                if list_1 == list_2:
                    # Then continue, there's no need to compare them
                    continue
                #Otherwise
                else:
                    # Initialize the found variable as false
                    found = False
                    # And loop over the sublists in list 2
                    for sublist_2 in list_2:
                        # If the annotation region in sublist_1 is the same as in sublist 2
                        if sublist_1[0] == sublist_2[0]:
                            # Then we found it!
                            found = True
                            # Add the peak information from sublist_2 to the l1_outstr sublist
                            l1_outstr[1].append(list(sublist_2)[1:])
                            # and break the subloop
                            break
                    # After the loop ends, if we didn't find the same annotation in list_2
                    if found == False:
                        # Then get the title information from list_2
                        title = list_2[0][1]
                        # And create an empty line to add to the outstrings list
                        newline = make_empty(formatting_dictionary,
                                             extensions_list[listcount_2],
                                             delimiter)
                        # and append this outstring to the l1_outstr sublist
                        l1_outstr[1].append([title, newline])
                # At the end of this iteration over lsit_2, increase the listcount_2 by one
                listcount_2 += 1
            # At the end of the sublist_1 loop, add all of the l1_outstr elements to the
            # formal outstrs list
            outstrs += l1_outstr
        # At the end of the list_1 loop, increase the listcount_1 loop by 1
        listcount_1 += 1
    # At the very end, delete the seen list
    del seen
    # and return the outstrs list.
    return outstrs


def merge_headers_lists(headers_list, delimiter):
    """
    Given a list of lists of headers and a delimiter, merge
    all of the headers into one line and return the line.
    """
    # Initialize the outstr local variable
    outstr = []
    # Loop over the head(ers) in the headers list
    for head in headers_list:
        # If the stripped headers is already in the outstr list
        if head[0].strip() in outstr:
            # Then loop over the indexes 1 through the length of the head lsit
            for i in range(1,len(head)):
                # and add each subheader to the list
                outstr.append(head[i].strip())
        # Or if we have not seen the header yet
        else:
            # Then just add everything to the outstr list
            for i in range(len(head)):
                outstr.append(head[i].strip())
    # Start to build the newline
    newline = f"{outstr[0]}"
    # Delete the 0th element of the outstr, as it is already used
    del outstr[0]
    # Loop over the strings in outstr
    for string in outstr:
        # and use string formatting to update the newline string
        newline = f"{newline}{delimiter}{string}"
    # At the end, delete the outstr list
    del outstr
    # Add the newline character to the new line
    newline = f"{newline}\n"
    # And return it
    return newline

def make_a_line(an_annote,
                lines_lists,
                delimiter):
    """
    Given an annotation, a list of lines, and a delimiter, return
    a delimiter separated line.
    """
    # Initialzie the newline variable
    newline = f"{an_annote.strip()}"
    # Sort the lines list based on the title index
    # NOTE: lines_list is a list of lists, where the 0th element
    # of each sublist is the title string. The title string is assumed
    # to have the index at the end.
    # trans_fact_experiment_index
    # The lambda function says: for each list, use the 0th element,
    # split that element, and use the last characrter set to order.
    ordlist = sorted(lines_lists, key = lambda x: x[0].split('_')[-1])
    # Loop over the lines in the ordlist
    for l in ordlist:
        # And loop over the strings in each line
        for string in l:
            # Strip each string of its newline character
            st = string.strip()
            # And update the newline variable
            newline = f"{newline}{delimiter}{st}"
    # Add a newline character to the new line
    newline = f"{newline}\n"
    # and return the newline
    return newline

def format_comparison_lines(comparison_list,
                            delimiter):
    """
    Given the list of comparisons and a delimiter, return a list
    of new lines using the make_a_line() function
    """
    # Get the lenght of the loop. Since the list contains annotations on even numbers and
    # the peak regions on odd numbers, the loop length is divided by two
    loop_len = len(comparison_list) // 2
    # Use list comprehension to make each line of th new file.
    newlines = [make_a_line(comparison_list[2*i], comparison_list[2*i+1], delimiter) for i in range(loop_len)]
    # And return the newlines
    return newlines

def merge_comparison_dicts(formatting_dictionary,
                           delimiter,
                           *args):
    """
    Given a formatting dictionary, a delimiter, and a list of comparison dictioanries,
    return a list of fomratted lines to write to a new file.
    """
    # Loop over the optional arguments
    for arg in args:
        # and assure that they are all dictionaries
        assert type(arg) == dict, f"all arguments should be dictionaries"
    # Initialize the headers list
    headers = []
    # Initialize the comparisons list
    comparisons = []
    # Initialize the extensions list
    extensions = []
    # Loop over the optional arguments
    for arg in args:
        # Loop over the keys and values in each optional argument
        for key, value in arg.items():
            # Add the 0th value of the value to the headers
            headers.append(value[0])
            # Add the 1th value of the value to the comparisons
            comparisons.append(value[1])
            # Split they key on '.' and take the last element as extension, add to lsit
            extensions.append(key.split('.')[-1])
    # Use the merge_headers_lists() function to merge the headers together
    headers = merge_headers_lists(headers, delimiter)
    # Use the merge_comparisons_lists() function to merge the comparisons together
    merged_comps = merge_comparison_lists(comparisons,
                                          extensions,
                                          formatting_dictionary,
                                          delimiter)
    # Use the format_comparisons_lines() function to format the lines for file writing
    merged_comps = format_comparison_lines(merged_comps, delimiter)
    # Add the headers and the formatted lines together
    lines = [headers] + merged_comps
    # and return the lines list.
    return lines

def get_all_dictionaries(directory,
                         annot_dir,
                         formatting_dictionary,
                         title_format_list,
                         delimiter,
                         file_type = 'xls'):
    """
    Given a test directory, an annotation directory, a formatting dictionary, a list
    of acceptable title file formats, a delimiter, and a file_type (set to xls),
    return a list of dictionaries, where each dictionary compares the lines from
    a peak file to the annotation files.
    """
    # Initialize the dictionary list
    dict_list = []
    # Loop over the folders in the directory.
    for folder in glob.iglob(f"{directory}/*"):
        # Use glob to make alist of the subdirectories in the folder.
        subdirs = glob.glob(f"{folder}/*")
        # If there is no subsubfolder named macs3_out, then continue to the next iteration
        if f"{folder}/macs3_out" not in subdirs:
            continue
        # Otherwise
        else:
            # Use glob to get a list of folders in the macs3_out folder
            subsubdirs = glob.glob(f"{folder}/macs3_out/*")
            # If there is not a folder named "modified_peakfiles" in the macs3_out folder
            if f"{folder}/macs3_out/modified_peakfiles" not in subsubdirs:
                # Then continue, although I should probably value error or run the
                # filtering program here.
                continue
            # If there is a modified peaksfile folder
            else:
                # Then use the get_enrich_annote_lines() function to get a dictionary of
                # line comparisons for the file in the folder
                new_dict = get_enrich_annote_lines(f"{folder}/macs3_out/modified_peakfiles",
                                                   annot_dir,
                                                   formatting_dictionary,
                                                   title_format_list,
                                                   delimiter,
                                                   file_type = file_type)
                # And add the dictionary to the dict_list
                dict_list.append(new_dict)
    # If the dictioanry list is empty at the end
    if dict_list == []:
        # Then raise a value error
        raise ValueError(f"Modified macs3 output files could not be found in {directory} with extension {file_type}")
    # Otherwise, return the dictonary list.
    else:
        return dict_list

#
#
##############################################################################################################
#
#               Functions: Relating to checking system arguments

def check_dir(directory):
    """
    Given a directory, recursively check to see if there are empty folders
    in the directory
    """
    # If the given directory is not a file
    if len(directory.split('.')) == 1:
        # Make a list of subdirectories in the directory
        dirlist = glob.glob(f"{directory}/*")
        # If dirlist has no elements
        if len(dirlist) == 0:
            # Return false, the directory is empty
            return False
        # Otherwise
        else:
            # Loop over the folders in the directory
            for fold in dirlist:
                # Use check dir to check the directory
                checker = check_dir(fold)
                # If this returns None, then continue
                if checker == None:
                    continue
                # IF this returns false, then return false
                elif checker == False:
                    return False
        # If neither None nor False are returned at the end, return True
        return True

def check_sysargs(args):
    """
    Given the following arguments

    args[0]   :   peak_enrich_annotations.py
    args[1]   :   directory to the experimental files.
    args[2]   :   directory to annotation files
    OPTIONAL
    args[3]   :   delimiter  default \t
    args[4]   :   file type, default xls

    Check to make sure that they are somewhat valid.
    """
    # Assert that there can only be 3-5 arguments given
    assert 3 <= len(args) <= 5, "Three or four system arguments should be given"
    # Check to make sure that the first two arguments are valid directories
    is_dir1_good = check_dir(args[1])
    is_dir2_good = check_dir(args[2])
    # If either of them are None or False, raise error and stop.
    if is_dir1_good == None or is_dir1_good == False:
        raise ValueError(f"{args[1]} has empty folders. Please delete them and try again.")
    if is_dir2_good == None or is_dir2_good == False:
        raise ValueError(f"{args[2]} has empty folders. Please delete them and try again.")
    # IF the length of the arguments is 4
    if len(args) == 4:
        # Then check to make sure the delimiter is in the list of valid delimiters
        assert arg[3] in ['\t', ':', ",", ';', '|','-']
        # and return the args that matter
        return args[1], args[2], args[3]
    # If the length of the arguments is 5
    elif len(args) == 5:
        # Then check for a valid delmiter
        assert arg[3] in ['\t', ':', ",", ';', '|','-']
        # And a valid filetype
        assert arg[4] in filetype_formatting.keys(), "Invalid filetype given"
        # And if these pass, return the arguments
        return args[1], args[2], '\t', arg[4]
    # Otherwise, return the arguments with tab as the delimiter
    else:
        return args[1], args[2], '\t'

#
#
##############################################################################################################
#
#        Functions: Relating to the annotations and the bash script calling

def get_fields_list(annot_dir):
    """
    Given the annotation directory, find the fields.txt file and turn
    the fields into a list.
    """
    # Use glob to create a lsit of files
    annot_dir_files = glob.glob(f"{annot_dir}/*")
    # If fields.txt is not in the annotation file directory
    if f"{annot_dir}/fields.txt" not in annot_dir_files:
        # Then return False
        return False
    # Otherwise
    else:
        # Open and read fields.txt
        with open(f"{annot_dir}/fields.txt", 'r') as f:
            # Use list comprehension to create a lsit of the fields
            field_list = [line.strip() for line in f]
            # Close the file
            f.close()
    # And return the fields list.
    return field_list

def filter_by_annot(annot_dir,
                    peak_dir,
                    lines_to_write):
    """
    Given the annotation diredctorym the peak file directory name, and the
    lines to write to the file, create the all_annotes_by_peak file and
    filter them by annotation (if fields.txt exists)


    NOTE: See the readme file for a discussion of the bash syntax used in these commands
    """
    # Make the peak file directory
    os.mkdir(f"{peak_dir}")
    # Open and write to a temporary file in that directory
    with open(f"{peak_dir}/temp.txt", 'w') as f:
        # Write all of the lines except the header to that file
        f.writelines(lines_to_write[1:])
        # and close the file
        f.close()
    # Assign the 0th element of the lines to write as the header.
    header = lines_to_write[0]
    # Sort the temporary file on columns 1 and 2 using bash syntax
    subprocess.call(f"sort -k 1,1 -k 2,2n {peak_dir}/temp.txt > {peak_dir}/temp_sorted.txt", shell=True)
    # Use echo to write the header to the all_annotes_by_peak file
    subprocess.call(f'echo "{header}" > {peak_dir}/all_annotes_by_peak.txt', shell = True)
    # Use cat to concatenate the temp file and the all annotes by peak file
    subprocess.call(f"cat {peak_dir}/all_annotes_by_peak.txt {peak_dir}/temp_sorted.txt > {peak_dir}/all_annotes_by_peak_sorted.xls", shell = True)
    # Remove the temporary text file
    subprocess.call(f"rm {peak_dir}/temp.txt",shell = True)
    # Use the get_fields_list() function to get the fields list
    field_list = get_fields_list(annot_dir)
    # If the fields list is False
    if field_list == False:
        # Then fields.txt couldn't be found, so remove the text files and return a nice message
        subprocess.call(f"rm {peak_dir}/temp_sorted.txt",shell = True)
        subprocess.call(f"rm {peak_dir}/all_annotes_by_peak.txt",shell = True)
        return f"Filtered peak regions and their annotations are written in {peak_dir}/all_annotes_by_peak_sorted.xls"
    # Otherwise, loop over the fields in the fields list
    else:
        for field in field_list:
            # Use awk to filter the files based on the field
            subprocess.call(f"""awk 'BEGIN{{OFS="\t"}}{{if ($6 == "{field}") {{ print }} }}' {peak_dir}/temp_sorted.txt > {peak_dir}/temp_{field}_sorted.txt""", shell = True)
            # Concatenate the header and the filtered file
            subprocess.call(f"cat {peak_dir}/all_annotes_by_peak.txt {peak_dir}/temp_{field}_sorted.txt > {peak_dir}/field_{field}_by_peak_sorted.xls", shell = True)
            # remove the temporary field file
            subprocess.call(f"rm {peak_dir}/temp_{field}_sorted.txt", shell = True)
        # Remove the temporary text files and tell the user that everything is done
        subprocess.call(f"rm {peak_dir}/temp_sorted.txt",shell = True)
        subprocess.call(f"rm {peak_dir}/all_annotes_by_peak.txt",shell = True)
        return f"Filtered peak regions and their annotations are written in {peak_dir} as .xls files"

#
#
##############################################################################################################
#
#        main() function

def main():
    """
    Given system arguments (defined in check_sysargs()), compare the peak regions
    to the annotated regions and determine which peaks correspond to which annotaions.
    Write those annotations to a file, and filter that file based on the fields.txt
    file in the anntoation directory.
    """
    # Get the system arguments
    args = sys.argv
    # If three or four system arguments were given
    if len(args) == 4 or len(args) == 3:
        # Then check the system arguments and assign them accordingly
        exp_dir, annot_dir, delim = check_sysargs(args)
        # Get the list of dictionaries using get_all_dictionaries() function
        dict_list = get_all_dictionaries(exp_dir,
                                         annot_dir,
                                         filetype_formatting,
                                         title_folder_formats,
                                         delim)
        # Use merge_comparison_dicts() to create list of lines to write to file
        newlines = merge_comparison_dicts(filetype_formatting,
                                          delim, *dict_list)
    # Or if there are five system arguments given
    elif len(args) == 5:
        # Then check the system arguments and assign them accordingly
        exp_dir, annot_dir, delim, f_type = check_sysargs(args)
        # Get the list of dictionaries using get_all_dictionaries() function
        dict_list = get_all_dictionaries(directory,
                                         annot_dir,
                                         filetype_formatting,
                                         title_folder_formats,
                                         delim,
                                         file_type = f_type)
        # Use merge_comparison_dicts() to create list of lines to write to file
        newlines = merge_comparison_dicts(filetype_formatting,
                                          delim,
                                          *dict_list)

    # Run filter_by_annot() to write the file and filter it using bash commands
    printer = filter_by_annot(annot_dir, f"{exp_dir}/peak_annotations", newlines)
    # Print the resulting statement
    print(printer)

# Run the main function when the file is called.
main()

#
#
##############################################################################################################
