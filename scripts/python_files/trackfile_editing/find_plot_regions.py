"""
Kenny P. Callahan

9 January 2020

===========================================================================================
find_plot_regions.py

Python 3.8.5
===========================================================================================

Small python program that writes a file containing plotting regions. System arguments
required are:

-> args[0]: The first system argument is always the script name (find_plot_regions.py)
-> args[1]: Comma separated string of bedgraph files (file_1.bg,file_2.bedgraph, etc)
-> args[2]: A .genome file with format <chromosome>\t<nucleotide_count>\n (length_sorted.genome)
-> args[3]: A string for the output file name (with .txt extension).

"""

###########################################################################################
#
#    Importables

import sys

#
#
###########################################################################################
#
#     Functions

def check_sysargs(args):

    """
    given a list of system arguments, check that each system argument is
    of the required type (or format).

    returns a list of files, the .genome file string, and the output file name.
    """

    # Check that all of the system arguments have the desired characteristics.
    assert type(args) == list, "args should have type 'list'"
    assert len(args) == 4, "only three system arguments should be given"
    assert ".bg" in args[1] or ".bedgraph" in args[1], "the first system argument should be a comma separated list of bedgraph files"
    assert ".genome" in args[2], "the second system argument should be a .genome file"

    # The files list is arg[1], newline character removed (if its there), split on commas
    files = args[1].strip().split(',')
    # Loop over file in files
    for file in files:
        # Attempt to open each file
        try:
            with open(file, 'r') as f:
                f.close()
        # If we can't open the file, then raise a value error and exit
        except ValueError:
            print(f"{file} is not a valid file.")
            sys.exit()

    # Next try to open the .genome file
    try:
        with open(args[2], 'r') as f:
            # Loop over the lines in the file
            for line in f:
                # Strip the newline character and split on tabs
                line = line.strip().split("\t")
                # Try to int the last element of the line list.
                int(line[-1])
            # Close the .genome file
            f.close()
    # If this fails, raise a value error and exit
    except ValueError:
        [print(f"{args[2]} is not a valid file.")]
        sys.exit()

    # Check to see if args[3] contains the substring '.txt'
    if ".txt" not in args[3]:
        # If it does not, then assign args[3].txt to the variable outfile
        outfile = f"{args[3]}.txt"
    # If the substring is there
    else:
        # Then simplt assign args[3] to the variable outfile.
        outfile = args[3]

    # If this function has not sys.exit(), then return the files list, .genome file string,
    # and the outfile string.
    return files, args[2], outfile

def update_dictionary(dictionary,
                      line,
                      key = 0,
                      removal = -1):
    """
    given a dictionary (preset values), a line from a file (as a list), a key as an integer
    (preset to 0, first element of line as key in the dictionary), and a negative
    integer for columns to remove (preset to -1, last comlumn), update the dictionary
    with information from the line.

    This function DOES NOT return a value. Rather, it modifies the global dictionary.
    """

    # Check the inputs to make sure they are of the required values/type
    assert type(dictionary) == dict, "dictionary should be of type 'dictionary'"
    assert type(line) == list, "line should be of type 'list'"
    assert type(key) == int and key >= 0, "the key position should be a positive integer"
    assert type(removal) == int and removal < 0, "removal should be a negative integer describing \n the number of rightmost coloumns to be removed"

    # If the key(th) element of the line is already a key in the dictionary
    if line[key] in dictionary.keys():
        # Then save the key to existkey
        existkey = line[key]
        # Delete the key(th) element from the line list
        del line[key]
        # Append the line (slicing out the removal columns) as a tuple to the
        # list held in dictionary[existkey]
        dictionary[existkey].append(tuple(line[:removal]))

    # If the key(th) value of the line list is not a key in the dictionary
    else:
        # Assign the key(th) value of the list to the variable newkey
        newkey = line[key]
        # Delete the key(th) value from the line list
        del line[key]
        # Initialize a list in the dictionary under newkey, with
        # the line (slicing out the removal columns) as a tuple
        dictionary[newkey] = [tuple(line[:removal])]

def get_peaks(file_list,
              delimiter):
    """
    given a list of bedgraph files and a delimiter,
    return a dictionary containing lists of tuples of integers
    that define a peak region.
    """
    # Initialize file dictionary
    file_dictionary = {}

    # Loop over files in the file list
    for file in file_list:
        # For each file, initialize a dictionary key with an
        # empty dictionary
        file_dictionary[file] = {}
        # Open the file
        with open(file, 'r') as f:
            # Loop over the lines int he file
            for line in f:
                # Strip the newline character and split the line
                # on the delimiter
                line = line.strip().split(delimiter)
                # Update the file's dictionary using the line
                update_dictionary(file_dictionary[file],
                                  line)
            # Close the file
            f.close()
    # Return the file dictionary
    return file_dictionary

def format_numbers(file_dictionary):
    """
    given a file dictionary (generated from get_peaks()), turn all of
    the strings into integers.

    This function DOES NOT return a value, rather it modifies the global
    file dictionary in place.
    """
    # Loop over the keys in file_dictionary, which should be files
    for file in file_dictionary.keys():
        # Loop over the keys, values in the subdictionary. Key should
        # be a chromosome name/identifier, value should be a list of
        # tuples of the form (region_start, region_end).
        for key, value in file_dictionary[file].items():
            # Reassign the value of the chromosome key using nested list
            # comprehension: int the region_start and end, then tuple it.
            file_dictionary[file][key] = [tuple([int(item) for item in value[i]])
                                           for i in range(len(value))]

def compare_regions(region_1,
                    region_2,
                    end_distance,
                    max_length):
    """
    given two regions in the form (region_start, region_end), a distance
    for before/after the start and end sites of a region, and the maximum
    length of a chromosome, return one of the following:

    -> 'pass' if region_1 is inside of region_2
    -> (region_2_start, region_1_end + end_distance) if the end 3' end of region_1 is greater than
       the 3' end of region_2 (region_1 ends later than region_2)
    -> (region_1_start - end_distance, region_2_end) if the 5' end of region_1 is less than the
       5' end of region_2 (region_1 begins before region_2)
    -> (region_1_start - end_distance, region_1_end + end_distance) if region_2 is inside of region_1
    -> 'break' if region_1 and region_2 are disjoint intervals
    """

    # If region_1 is inside of region_2
    if  region_1[0] >= region_2[0] and region_1[0] <= region_2[1] and region_1[1] >= region_2[0] and region_1[1] <= region_2[1]:
        # return the string 'pass'
        return 'pass'
    # Or if region_1 starts inside region_2 and ends outside of region_2
    elif region_1[0] >= region_2[0] and region_1[0] <= region_2[1] and region_1[1] > region_2[1]:
        # Initialize the beginning and ending variables
        beginning = region_2[0]
        ending = region_1[1] + end_distance
        # Check to make sure the beginning and end are within the chromosome
        if beginning < 0:
            beginning = 0
        if ending > max_length:
            ending = max_length
        # Return the tuple (beginning, ending)
        return (beginning, ending)
    # If region_1 starts outside of region_2 but ends inside of region_2
    elif region_1[0] < region_2[0] and region_1[1] >= region_2[0] and region_1[1] <= region_2[1]:
        # Initialize the beginning and end variables
        beginning = region_1[0] - end_distance
        ending = region_2[1]
        # Check to make sure they are within the chromosome
        if beginning < 0:
            beginning = 0
        if ending > max_length:
            ending = max_length
        # Return the tuple (beginning, ending)
        return (beginning, ending)
    # If region_2 is inside of region_1
    elif region_1[0] < region_2[0] and region_1[0] < region_2[1] and region_1[1] > region_2[0] and region_1[1] > region_2[1]:
        # Initialize the beginning and ending variables
        beginning = region_1[0] - end_distance
        ending = region_1[1] + end_distance
        # Make sure that the beginning and end are within the chromosome
        if beginning < 0:
            beginning = 0
        if ending > max_length:
            ending = max_length
        # Return the tuple (beginning, ending)
        return (beginning, ending)
    # If region_1 and region_2 are disjoint intervals
    else:
        # Return the string 'break'
        return 'break'

def find_regions(file_dictionary,
                 end_distances,
                 max_lengths):
    """
    given a file dictionary (from get_peaks(), cleaned with format_regions()),
    the end distances ('overhang' from reg_start and reg_end), and max_lengths
    (dictionary of key = chrom, value = length), return a list of dictionaries
    that define regions.

    Each region dictionary is relative to ONE file. These regions will be merged
    using a later function, but this ensures that no regions are missed (which could
    happen if only one file is used for reference).

    This function is kind of long and complicated, but I couldn't find a nicer way
    to do these comparisons. Hopefully I'll think of something cleaner in the future.
    """
    # Initialize the regions list
    regions_list = []
    # Get the list of files from the keys of the dictionary
    files = list(file_dictionary.keys())
    # Loop over the files in the list
    for file_1 in files:
        # Initialize the regions dictionary for file_1
        regions = {}
        # Loop over the keys and values in the file_1 subdictionary
        for key, value in file_dictionary[file_1].items():
            # Initialze a list in the regions dictionary for the key
            regions[key] = []
            # Loop over the region tuples in value
            for reg in value:
                # Initialize the holder region for this iteration using overhang
                holder = (reg[0] - end_distances[key], reg[1] + end_distances[key])
                # Check to make sure that the holder values are within the chromosome
                if holder[0] < 0:
                    holder = (0, holder[1])
                if holder[1] > max_lengths[key]:
                    holder = (holder[0], max_lengths[key])
                # Loop over the files list again
                for file_2 in files:
                    # If the second file is not the same as the first file, then we
                    # want to compare the regions of these files
                    if file_2 != file_1:
                        # Attempt to compare regions: item from file_2[chrom], holder from file_1[chrom]
                        try:
                            # Loop over items in the chromosome list for file_2
                            for item in file_dictionary[file_2][key]:
                                # next_reg is found by comparing item to holder
                                next_reg = compare_regions(item,
                                                           holder,
                                                           end_distances[key],
                                                           max_lengths[key])
                                # If item is inside of the holder region
                                if next_reg == 'pass':
                                    # then pass
                                    pass
                                # If item and holder are disjoint
                                elif next_reg == 'break':
                                    # then break the loop, we found a new region!
                                    break
                                # Otherwise, update the holder
                                else:
                                    holder = next_reg
                        # If the comparison fails (it does, I forgot what condition makes it happen though)
                        except:
                            # then just pass to the next iteration
                            pass
                # Once the loop breaks, if there are not items in the regions[key] list
                if len(regions[key]) == 0:
                    # Then add the holder to the list as the first plotting region found.
                    regions[key].append(holder)
                # Otherwise
                else:
                    # Compare the holder region with the previously found region.
                    next_reg = compare_regions(holder,
                                               regions[key][-1],
                                               end_distances[key],
                                               max_lengths[key])
                    # If the holder region is within the previously found region,
                    if next_reg == 'pass':
                        # then pass, this region isn't new
                        pass
                    # Or if the holder region and the previously found region are disjoint,
                    elif next_reg == 'break':
                        # Then add the holder region, it is unique.
                        regions[key].append(holder)
                    # If the comparison is neither 'pass' nor 'break', then the comparison
                    # returned a region combining the two regions.
                    else:
                        # So reassign the previous region as this new, extended region.
                        regions[key][-1] = next_reg
        # After the regions dictionary for the first file is complete, add it to the regions list.
        regions_list.append(regions)
    # at the end of it all, return the regions list.
    return regions_list

def get_chrom_lengths(length_genome,
                      delimiter):
    """
    given a .genome file and a delimiter, return a dictionary
    with key=chromosome/identifier, value=number of nucleotides
    """
    # Initialize the dictionary
    dictionary = {}
    # Open the .genome file
    with open(length_genome, 'r') as f:
        # Loop over the lines in the file
        for line in f:
            # Stip the newline character and split on the delimiter
            line = line.strip().split(delimiter)
            # Add the first element as key, integer of second element
            # as value to the dictionary.
            dictionary[line[0]] = int(line[1])
        # Close the file, save some RAM
        f.close()
    # Return the dictionary at the end
    return dictionary



def make_end_distances(chrom_length_dict):
    """
    given the dictionary of chromosome lengths, return
    a dictionary of 'end_distances' (the overhang for a region)
    """
    # Factors dictionary, used to get the overhang factor based
    # on the length of the chromosome
    factors = {'100000'  : 0.1,
               '1000000' : 0.05,
               '10000000': 0.01,
               '100000000' : 0.005,
               '1000000000' : 0.001}
    # Initialize the end_distances dictioanry
    end_distances = {}
    # Loop over the keys and values in the chromosome length dictioanry
    for key, value in chrom_length_dict.items():
        # Initialize the list of length comparisons
        facts = list(factors.keys())
        # Make each length comparison an integer
        facts = [int(f) for f in facts]
        # Initialize the count, used to end comparisons
        count=0
        # Loop over the lengths in facts
        for f in facts:
            # If the value (chrom length) is less than f and the count is zero
            if value < f and count == 0:
                # Then save the factor associated with the length and increase count
                factor = factors[str(f)]
                count+=1
        # Add the end_distance to the dictionary at the key=chrom
        end_distances[key] = value * factor
    # Return the end_distances dictionary
    return end_distances

def check_the_keys(base_regions_dict,
                   remaining_regions_list):
    """
    given a regions dictionary and a list containing other
    regions dictionaries, return a list of keys that exist
    in the remaining regions dictionaries that are NOT in
    the base regions dictionary.
    """
    # Initialize the list of not found keys
    not_found = []
    # Get the list of keys in the base regions dictionary
    base_keys = list(base_regions_dict.keys())
    # Loop over the regions in the remaining regions list
    for region in remaining_regions_list:
        # Loop over the keys in the region
        for key in region.keys():
            # If the key is not in the base keys list
            if key not in base_keys:
                # Then add that key to the not found list
                not_found.append(key)
            # Otherwise, just pass
            else:
                pass
    # Return the not found list
    return not_found


def merge_all_regions(regions_list):
    """
    given a regions list (list of regions dictionaries), return a
    dictionary of lists of sorted tuples.

    This assumes that the regions dictionary with the most keys is
    saturated: that is, there were peaks in all chromosomes. This
    function might fail if there 
    """
    # Make a list of tuples: (number of keys, region_dict)
    lengths = [(len(region), region) for region in regions_list]
    # Sort the list by the number of keys in each region
    lengths.sort(key=lambda l: l[0])
    # Sort is by smallest > highest, so we want to reverse the list
    lengths = lengths[::-1]
    # We really only want the dictionaries sorted, so remove
    # the number of keys
    lengths = [lengths[i][1] for i in range(len(lengths))]
    # Assign the regions variable to be the list with the most keys
    regions = lengths[0]
    # Delete that dictionary from the list, will be used for all
    # subsequent comparisons as the base.
    del lengths[0]
    # Check to see if any keys will give us trouble
    not_found = check_the_keys(regions, lengths)
    # Loop over the keys in the regions dictionary
    for key in regions.keys():
        # and for the other region dictionaries in the lengths list
        for reg in lengths:
            # Attempt to add the list in reg to the list in regions
            # at the same key. This will fail if reg does not have
            # this key
            try:
                regions[key] += reg[key]
            # IF this fails
            except:
                pass
        # Then sort the list in regions[key]
        regions[key].sort(key=lambda s: s[0])
    # If there are no unused keys
    if not_found == []:
        # Then return the regions dictionary :)
        return regions
    # Otherwise, we need to update this dictionary with unused keys
    else:
        # Loop over the keys in not_found
        for key in not_found:
            # and loop over the regions dictionaries in lengths
            for reg in lengths:
                # If the key is in the region and is not in base region
                if key in reg.keys() and key not in regions.keys():
                    # Then initialize that key in the base regions dict and sort
                    regions[key] = reg[key]
                    regions[key].sort(key=lambda s: s[0])
                # If the key is in the region and is in the base region
                elif key in reg.keys() and key in regions.keys():
                    # Then append the list from reg into the regions list and sort
                    regions[key] += reg[key]
                    regions[key].sort(key=lambda s: s[0])
                # Otherwise, simply pass
                else:
                    pass
        # and return the regions dictionary at the end.
        return regions

def clean_merged_regions(merged_dictionary,
                         max_lengths):
    """
    given a merged dictionary and a dictionary of maximum
    chromosome lengths, return a dictionary of cleaned regions
    """
    # Initialize the cleaned_regiosn dictionary
    cleaned_regions = {}
    # Loop over the keys and values in the merged dictionary
    for key, value in merged_dictionary.items():
        # Initialize the list in cleaned_region[key]
        cleaned_regions[key] = []
        # loop over the regions in the merged dictionary list at key=chrom
        for reg in value:
            # If there has not been a value added to the list yet
            if cleaned_regions[key] == []:
                # Then add this first region
                cleaned_regions[key].append(reg)
            # Otherwise, compare this region to the last region
            else:
                next_reg = compare_regions(reg,
                                           cleaned_regions[key][-1],
                                           0,
                                           max_lengths[key])
                # If the comparison yields pass, then pass as this region
                # is not unique
                if next_reg == "pass":
                    pass
                # If this comparison yield break, then this region is unique
                elif next_reg == "break":
                    cleaned_regions[key].append(reg)
                # Otherwise, the two regions overlapped so we need to reassign
                # the last calue in cleaned_regions[key]
                else:
                    cleaned_regions[key][-1] = next_reg
    # Finally, return the cleaned regions dictionary
    return cleaned_regions

def get_lines(cleaned_regions):
    """
    given a dictionary of cleaned regions, return a list of lines to be
    written to a file.
    """
    # Initialize lines list
    lines = []
    # Loop over keys and values in the cleaned_regions dictionary
    for key, value in cleaned_regions.items():
        # loop over the regions in the list cleaned_regions[key]
        for reg in value:
            # The line should be tab separated, key in first column
            # region start in the middle and region end in the last
            line = f"{key}\t{int(reg[0])}\t{int(reg[1])}\n"
            # Add the line to the list
            lines.append(line)
    # Return the lines at the end
    return lines

def write_regions_file(lines, outfilename):
    """
    given a list of line and an output filename, write the file.
    """
    # OPen the file and write
    with open(outfilename, 'w') as f:
        # use this lovely command to write the entire file
        f.writelines(lines)
        # And close the file to save RAM
        f.close()

#
#
###########################################################################################
#
#        main() function


def main():

    """
    given valid system arguments, write a file containing unique regions for
    each chromosome which correspond to peaks found using peak calling.
    """

    # Get the system arguments
    args = sys.argv

    # Check that they are valid
    file_list, chromfile, outfile = check_sysargs(args)

    # Get the chromosome length dictionary
    chrom_lengths = get_chrom_lengths(chromfile, '\t')

    # Get the dictionary of overhang values for each chromosome
    end_distance = make_end_distances(chrom_lengths)

    # Get the dictionary of peak regions
    peaks_dictionary = get_peaks(file_list, '\t')

    # Turn the peak region strings into numbers
    format_numbers(peaks_dictionary)

    # Get the regions list (dictionary of regions with overhang per file)
    regions_by_file = find_regions(peaks_dictionary,
                                   end_distance,
                                   chrom_lengths)

    # Merge the regions dictionaries into one sorted dictionary
    merged_regions_dict = merge_all_regions(regions_by_file)

    # Merge all of the regions that overlap
    cleaned_regions_merged = clean_merged_regions(merged_regions_dict,
                                                  chrom_lengths)

    # Get the lines to write to each file
    lines_to_write = get_lines(cleaned_regions_merged)

    # Write the regions file.
    write_regions_file(lines_to_write, outfile)

main()

#
#
###########################################################################################
#
#
