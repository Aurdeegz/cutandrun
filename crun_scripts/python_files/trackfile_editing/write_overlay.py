"""
Kenneth P. Callahan
7 January 2020

==========================================================================
Python 3.8.5
write_overlay.py
==========================================================================

This python file can be used to write the configuration file to be used
for pyGenomeTracks. Currently, this file only supports bedgraph, bigwig
and bed files. Bed files should be for annotations (genes, CDS, exons, etc)
and bedgraph/bigwig files should be for plotting.

If you wish to make changes to the automated plot, you can either do them
post hoc (once this script creates the .ini file), or you can edit the
formatting dictionaries below. As always, consult the pyGenomeTracks
documentation if you have any questions regarding their plotting system.

As a side note, this is named 'write_overlay.py' because it is used to
generate configuration files for overlayed tracks (or that was the
intended purpose of it)

==========================================================================
At least five system arguments are required:

-> args[0] : This argument is always the file name (write_overlay.py)
-> args[1] : First comma separated string of file names (These should
             be some .bg or .bw files for plotting tracks)
-> ...
    .
    .
    .
-> ...
-> args[-4] : Last comma separated string of file names (if using annotations,
              this is where you want to put them).
-> args[-3] : configuration file name WITH extension (.ini)
-> args[-2] : 'true' or 'false' string.
             -- 'true' : Plots will be overlayed
             -- 'false': Plots will not be overlayed
-> args[-1] : comma separated string of maximum heights (y-values) OR 'None'
             -- y-values should be in the same order as the files (value 0
             for file list 0, value 1 for file list 1, etc)
             -- None should be used if you do not want to specify the height.
             If None is used, then the height will be determined by the
             FIRST file in each files list.


"""

##########################################################################
#
#           Imports

import sys

#
#
##########################################################################
#
#           Formatting for Bedgraphs and bed files

# These dictionaries is used for writing lines to the .ini file.
# The keys in these dictionaries correspond to keys in the bedgraph_keys and
# bed_keys dictionaries. If the formatting dictionaries have a key value pair,
# then that key, value pair will be written to the file. If the value is
# 'default', then the value in the _keys dictionary will be written to the
# file instead.
bedgraph_formatting = {'file' : '',
                       'color' : '',
                       'file_type' : '',
                       'height' : '7',
                       'overlay_previous' : 'default',
                       'min_value' : 'default',
                       'max_value' : 'default',
                       'alpha' : 'default'}

bed_formatting = {'file' : '',
                  'color' : 'default',
                  'style' : 'flybase',
                  'display' : 'stacked',
                  'border_color' : 'indigo',
                  'height' : '7',
                  'arrow_interval' : '2000',
                  'line_width' : 'default',
#                  'arrow_length' : '5000',
                  'arrowhead_included' : 'true',
                  'merge_transcripts' : 'false',
                  'all_labels_inside' : 'false',
                  'labels_in_margin' : 'true',
                  'file_type' : 'bed',
                  'fontsize' : 'default',
                  'height_utr' : '0.2',
                  'color_utr' : 'red'}

narrow_formatting = {'file' : '',
#                     'title' : '',
                     'file_type' : '',
                     'height' : 'default',
                     'show_data_range' : 'default',
                     'show_labels' : 'false',
                     'use_summit' : 'default',
                     'type' : 'default',
                     'width_adjust' : '2',
                     'line_width' : '0.5',
                     'color' : '',
                     'max_value' : 'default'}

#
#
##########################################################################
#
#           Defaults: colour list and dictionaries

# List of colours that matplotlib recognizes. If you have more than 8
# experiments to evaluate at the same time, then you should either do
# them in batches or add more colours to this list.

colours = ['blue', 'red', 'black', 'violet', 'indigo', 'orange', 'green']

# This dictionary has file extensions as keys, and the corresponding
# file type as the value. pyGenomeTracks takes more than just
# these file types, so if you require another file type then you must
# add that file to the extensions dictionary, add a formatting dictionary
# above, and edit the main lines script to include your file type.

extensions = {'bg' : 'bedgraph',
              'bdg' : 'bedgraph',
              'bedgraph' : 'bedgraph',
              'bw' : 'bigwig',
              'bigwig' : 'bigwig',
              'bed' : 'bed',
              'narrowPeak' : 'narrow_peak'}

# bed_keys and bedgraph_keys are dictionaries with default values for
# allowable values for bed and bedgraph files, respectively. The arguments
# and their allowable values can be found in the pyGenomeTracks documentation
#
# https://pygenometracks.readthedocs.io/en/latest/
#
# under 'All Available Tracks'

bed_keys = {'file' : '',
            'title' : '',
            'height' : '4',
            'overlay_previous' : 'no',
            'fontsize' : '8',
            'orientation' : '',
            'line_width' : '1',
            'color' : 'deepskyblue',
            'max_value' : 'auto',
            'min_value' : '0',
            'border_color' : 'black',
            'preferred_name' : 'transcript_name',
            'merge_transcripts' : 'false',
            'labels' : 'true',
            'style' : 'UCSC',
            'display' : 'stacked',
            'max_labels' : '100',
            'global_max_row' : 'false',
            'gene_rows' : '20',
            'arrow_interval' : '2',
            'arrowhead_included' : 'false',
            'color_utr' : 'grey',
            'height_utr' : '1',
            'arrow_length' : '',
            'all_labels_inside' : 'true',
            'labels_in_margin': 'false',
            'file_type' : ''}

bgr_keys = {'file' : '',
            'title' : '',
            'height' : '4',
            'overlay_previous' : 'no',
            'orientation' : '',
            'color' : 'purple',
            'alpha' : '1',
            'max_value' : 'auto',
            'min_value' : '0',
            'use_middle' : 'false',
            'show_data_range' : 'true',
            'type' : 'fill',
            'negative_color' : '',
            'nans_to_zero' : 'false',
            'summary_method' : '',
            'number_of_bins' : '700',
            'transform' : 'no',
            'log_pseudocount' : '0',
            'y_axis_values' : 'transformed',
            'second_file' : '',
            'operation' : 'file',
            'grid' : 'false',
            'rastersize' : 'false',
            'file_type' : ''}


nwp_keys = {'file' : '',
            'title' : '',
            'height' : '7',
            'overlay_previous' : 'no',
            'orientation' : '',
            'line_width' : '1',
            'color' : '#FF000080',
            'max_value' : '',
            'show_data_range' : 'true',
            'show_labels' : 'true',
            'use_summit' : 'true',
            'width_adjust' : '1.5',
            'type' : 'peak',
            'file_type' : ''}

#
#
##########################################################################
#
#       Functions

def check_sysargs(args):
    """
    Given sys.argsv (arguments passed in from the command line),
    determine whether or not:

    -> args[0] : This argument is always the file name (write_overlay.py)
    -> args[1] : First comma separated string of file names (These should
                 be some .bg or .bw files for plotting tracks)
    -> ...
        .
        .    All of these can be comma separated lists of files. This function
        .    checks that they are valid by trying to open each one of them
        .
    -> ...
    -> args[-4] : Last comma separated string of file names (if using annotations,
                  this is where you want to put them).
    -> args[-3] : configuration file name WITH extension (.ini)
    -> args[-2] : 'true' or 'false' string.
                 -- 'true' : Plots will be overlayed
                 -- 'false': Plots will not be overlayed
    -> args[-1] : comma separated string of maximum heights (y-values) OR 'None'
                 -- y-values should be in the same order as the files (value 0
                 for file list 0, value 1 for file list 1, etc)
                 -- None should be used if you do not want to specify the height.
                 If None is used, then the height will be determined by the
                 FIRST file in each files list.
    """
    assert type(args) == list, "args must have type 'list'"
    assert len(args) >= 5, "less than five system arguments were given"

    # Remove the first system argument, as it is the name of the script file
    args = args[1:]

    # Check last argument: max heights or none
    # If the max heights are none, then pass
    if args[-1].lower() == 'none':
        args[-1] = None
    # Otherwise, assume it is a comma separated string of numbers
    else:
        # Split the string on the commas
        args[-1] = args[-1].split(',')
        # Loop over the number of heights
        for i in range(len(args[-1])):
            # then check to see if the user put 'auto' or 'none' in their string
            if args[-1][i].lower() == 'auto' or args[-1][i].lower() == 'none':
                # If they did, then make that argument 'auto' as that is what pyGT takes
                args[-1][i] = 'auto'
            # Otherwise, try to float the value
            else:
                try:
                    args[-1][i] = float(args[-1][i])
                # If this fails, then it is a value error
                except ValueError:
                    print(f"The last system argument should be a comma separated string of max heights, \n\
corresponding to the max heights of the bedgraph file lists to plot.")

    # Check the second to last argument: true or false string
    # if the string (all lowercase) is not 'true' and it is not 'false'
    if args[-2].lower() != 'true' and args[-1].lower() != 'false':
        # Then raise a value error and sys.exit() the program
        raise ValueError(f"The second to last system argument was neither True nor False")
        sys.exit()
    # Otherwise, if the value is true, then give it the boolean True
    elif args[-2].lower() == 'true':
        args[-2] = True
    # OTherwise the value is false, and it should have the boolean False
    else:
        args[-2] = False

    # Check the third to last system argument
    # If .ini is not in the argument, then simply throw an error and exit
    if ".ini" not in args[-3]:
        raise ValueError(f"The third to last system argument not a .ini file")
        sys.exit()

    # Check all of the file arguments
    # Loop over all arguments in args, except the last three
    for arg in args[:-3]:
        # Split the files string on commas
        files = arg.split(',')
        # loop over each file in the files list
        for file in files:
            # If the extension is a bedfile extension (including gzipped)
            if '.bed.gz' in file or ".bed4" in file or ".bed6" in file or ".bed12" in file:
                # Then pass and assume its fine
                pass
            # Otherwise, try to open the file
            else:
                try:
                    with open(file, 'r') as f:
                        f.close()
                # If you can't open the file, then raise a ValueError and exit.
                except ValueError:
                    print(f"{file} is not a valid file")
                    sys.exit()

    # If nothing fails, then yay! return the list of file strings, outfile, boolean and heights
    return args[:-3], args[-3], args[-2], args[-1]

def get_lines(option_dictionary,
              narrowpeaks = False,
              **kwargs):
    """
    given a dictionary of options (bed_keys, bedgraph_keys) and optional arguments
    (**bed_formatting or **bedgraph_formatting are interpreted as kwargs), return
    a list of lines.

    of note, a kwarg of 'file' is required. This is used to create the block
    in the configuration file.
    """
    # Check that the option_dictionary and the kwarg 'file' are there
    assert type(option_dictionary) == dict, "option_dictionary should be of type 'dict'"
    assert 'file' in kwargs.keys(), "no file is given"

    # Initialize newlines list
    newlines = []

    # Make the field string. Split the 'file' value on / character
    field = kwargs['file'].split('/')
    # If len(field) is one, then the program is running in the same folder
    # that the file is in, and the field has shape [file_name]
    if len(field) == 1:
        block_title = field[0].split('.')[0]
        newfield = f"[{block_title}]\n"
        newlines.append(newfield)
    # OTherwise, we just want to get the file name, so we want the last element
    # of the list, without the extansion.
    else:
        block_title = field[-1].split('.')[0]
        newfield = f"[{block_title}]\n"
        newlines.append(newfield)

    # Proposed holds the kwarg values passed in by the user. We check to see
    # whether or not those are options in the option_dictionary
    proposed = kwargs.keys()
    # Loop over key, value in the option_dictionary
    for key, value in option_dictionary.items():
        # If the key is also in proposed
        if key in proposed:
            # Then check to see whether the kwarg value at that key is 'default'
            if kwargs[key] == 'default':
                # If so, then we use the value from option_dictionary for our line
                newlines.append(f"{key} = {value}\n")
            # If not,
            else:
                # Then use the value passed in by the user.
                newlines.append(f"{key} = {kwargs[key]}\n")
        elif key == 'title' and "annotation" in block_title:
            newlines.append(f"{key} = {block_title[11:]}\n")
        elif key == 'title' and narrowpeaks == True:
            for id in ["_exp_", "_exper_", "_experiment_", "_rep_", "_replicate_", "_enrich_", "_enrichment_"]:
                title = [fld for fld in field if id in fld]
                if title != []:
                    newlines.append(f"{key} = {title[0]}\n")
                    break
        # If the value is not in the proposed kwarg values list
        else:
            # Then add a commented out line to the newlines list.
            newlines.append(f"#{key} = {value}\n")
    # Finally, append a newline for niceness on the eyes
    newlines.append(f"\n")
    # And return the newlines list.
    return newlines

def get_spacer(height = 0.5):
    """
    given a number greater than zero for height, return
    a list of strings for a spacer field.
    """
    # Check that the height is in the correct domain
    assert height > 0, "height should be a positive value"
    # The spacers are well defined, so just save the strings to the list
    newlines = [f"[spacer]\n",
                f"# height of space in cm (optional)\n",
                f"height = {height}\n",
                f"\n"]
    # Return the newlines lost
    return newlines

def get_xaxis(fontsize = 10,
              where = ''):
    """
    given the optional kwargs fontsize and where, return a
    list of strings for an x-axis field.
    """

    # Check to make sure that fontsize and where are okay
    assert fontsize > 0, "fontsize should be a positive value"
    assert where.lower() == 'top' or where.lower() == 'bottom' or where == "", "where should be top, bottom, or empty string only"
    # The x axis is well defined, so just make the strings list.
    newlines = [f"[x-axis]\n",
                f"fontsize = {fontsize}\n",
                f"#where = {where}\n"
               f"\n"]
    # Return the newlines list.
    return newlines

def make_all_lines(colors,
                   overlay,
                   heights,
                   *args):
    """
    given a list of colours, a truthy value for overlay, the heights
    values (list) and args (lists of files), return a list of lines
    to be written to a file.
    """
    # Check to ensure that the input values are valid
    assert type(heights) == list or heights == None, "heights should be of type 'list' or None"
    assert type(colors) == list, "colors should be of type 'list'"
    for arg in args:
        assert type(arg) == list, "args should be lists of files"
    # Initialize the lines list and add a spacer so the plots aren't crammed at the top
    lines = []
    lines += get_spacer()

    last = ""

    # Initialize block count, which is used for getting the height value for each block
    # of files.
    blockcount = 0
    # Loop over args: each arg is a list of files
    for arg in args:
        # Divisor is used for the alpha value (transparency)
        divisor = len(arg)
        # Initialize count
        count = 0
        # Now loop over the files in the arg
        for file in arg:
            # Get the file extension
            ext = file.split('.')[-1]
            # IF the file is gzipped, then the real extension is the second to last
            # string after splitting on periods
            if ext == 'gz':
               ext = file.split('.')[-2]
            # If the file extension is one of the (many) bedfile types, then it is simply
            # a bed file
            elif ext == 'bed4' or ext == 'bed6' or ext == 'bed12':
               ext = 'bed'
            # If the extension if in the extension dictionary keys
            if ext in extensions.keys():
                # and if the value of the extensions[ext] is bedgraph or bigwig
                if extensions[ext] == 'bedgraph' or extensions[ext] == 'bigwig':
                    lines.append(f"\n")
                    # Then change the bedgraph formatting options:
                    # Note to self: write a function to get a title string here too
                    bedgraph_formatting['file'] = file
                    bedgraph_formatting['color'] = colors[count]
                    bedgraph_formatting['file_type'] = extensions[ext]
                    # Now, if the user elected to overlay the plots and we are on the first block
                    if overlay == True and count == 0:
                        # Then set these bedgraph formatting options
                        bedgraph_formatting['overlay_previous'] = 'default'
                        bedgraph_formatting['alpha'] = 1
                        # If the heights is None, then just set the max to auto
                        if heights == None:
                            bedgraph_formatting['max_value'] = 'auto'
                        # Otherwise, try to change the bedgraph formatting max value
                        else:
                            if last == "narrow_peak":
                                blockcount+=1
                            try:
                                # If this fails, then there are not enough heights in the list
                                bedgraph_formatting['max_value'] = heights[blockcount]
                                blockcount+=1
                            # So default back to auto for the max value.
                            except:
                                print("")
                                print("WARNING: Not enough height values were given for overlayed plots \n using default: max_value = auto")
                                print("")
                                bedgraph_formatting['max_value'] = 'auto'
                        # Use the get_lines function to add lines to the lines list.
                        lines += get_lines(bgr_keys,
                                           **bedgraph_formatting)
                    # If the overlay is True, but the count has increased
                    elif overlay == True:
                        # Then change the following bedgraph_formatting settings
                        bedgraph_formatting['overlay_previous'] = 'share-y'
                        bedgraph_formatting['alpha'] = 1- count*(1/divisor)
                        # and use get_lines to add more lines to the lines list.
                        lines += get_lines(bgr_keys,
                                           **bedgraph_formatting)
                    # IF the overlay value is not true, then simply add lines without changing settings.
                    else:
                        lines += get_lines(bgr_keys,
                                           **bedgraph_formatting)
                    # Increase the count by 1
                    count += 1
                # IF the extension is a narrowPeak
                elif extensions[ext] == "narrow_peak":
                    last = "narrow_peak"
                    lines.append("\n")
                    # Change some of the narrowPeak formatting options:
                    # Note to self: get a function to write a title string here.
                    narrow_formatting['file'] = file
                    narrow_formatting['color'] = colors[count]
                    narrow_formatting['file_type'] = extensions[ext]
                    # The default for narrowpeaks is to not overlay the previous. There is not a
                    # transparency parameter for narrowPeaks, otherwise I would overlay them
                    narrow_formatting['overlay_previous'] = 'default'
                    # If there was no height information given
                    if heights == None:
                        # Then let pyGenomeTracks find the peaks heights for each track
                        narrow_formatting['max_value'] = 'default'
                    # Otherwise,
                    else:
                        # Try to reassign the narrow_formatting dictionary with the heighst value
                        try:
                            # The heights value is in the heights list at index blockcount (which track
                            # we are currently on
                            narrow_formatting['max_value'] = heights[blockcount]
                        # If this fails, then tell the user that the universe is imploding
                        except:
                            print("")
                            print("WARNING: Not enough height values were given for overlayed plots \n using default: max_value = auto")
                            print("")
                            # and just let pyGenomeTracks find the default value
                            narrow_formatting['max_value'] = 'default'
                    # Once the formatting is all set, then use get_lines() and the formatting options to
                    # update the lines list were generating
                    lines += get_lines(nwp_keys,
                                       narrowpeaks = True,
                                       **narrow_formatting)
                    # and increase the count by 1 once this is complete.
                    count += 1
                # If the extension is a 'bed'
                elif extensions[ext] == 'bed':
                    # Then change the following settings for the bed file/
                    bed_formatting['file'] = file
                    bed_formatting['file_type'] = extensions[ext]
                    # and make lines using bed_formatting.
                    lines.append(f"\n")
                    lines += get_lines(bed_keys,
                                       **bed_formatting)
            # If the extension is not bg, bw, or bed
            else:
                # Then tell the user it currently is not recognized
                print(f"{file} is not recognized file.")
        # After each list of files, add a spacer.
        lines += get_spacer()
    # Once all files have been analyzed, write an x axis block
    lines += get_xaxis()
    # Return the lines list at the end.
    return lines

#
#
##########################################################################
#
#      main()

def main():
    """
    given system arguments (described above), write a configuration
    file for pyGenomeTracks.
    """
    # Get the system arguments
    args = sys.argv

    # Check that the system arguments are of the desired form
    filestrings, outfiles, overlay, heights = check_sysargs(args)

    # Extract the file lists from the file strings
    file_lists = [files.split(',') for files in filestrings]

    # Use make_all_lines() to get the lines list
    lines = make_all_lines(colours,
                           overlay,
                           heights,
                           *file_lists)

    # Write the lines to the outfile
    with open(outfiles, 'w') as f:
        f.writelines(lines)
        f.close()

    # Tell the user they've done it!!
    print("")
    print(f"{outfiles} has been written")
    print("")

main()

#
#
##########################################################################
#
#
