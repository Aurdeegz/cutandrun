"""
Kenneth P. Callahan

25 January 2021

=================================================================================================================
Python 3.8.5

filter_narrowpeak_qvalue.py
=================================================================================================================


Placememt of a docstring

"""

##########################################################################################################
#
#            Importables

import sys       # Used for obtaining system inputs (sys.argv) as a list.
import os        # Used for operating system (os) level maniputlations (moving files, stuff like that)
import glob      # Used to iterate through files in directory (as list, glob, or generator, iglob)
import math      # Math has the logarithm function

#
#
##########################################################################################################
#
#            Pre definied variables

# File extensions that the program will recognize. By default, MACS3 makes both a narrowPeak
# and an xls file to describe the data. The default in this program is to work on the xls
# files, since they have a fold enrichment data column (and that's useful)
#
# If you want to add an extension type, add it here. Then go to the function filter_all_lines()
# and add the appropriate filtering parameters.
allowed_extensions = ["narrowPeak", "xls"]

#
#
##########################################################################################################
#
#           Functions

def filter_line(line,
                value_column,
                delimiter,
                qvalue = 0.01,
                pvalue = None):
    """
    Given a line (from a file), the value_column integer (NOT CS counting) where the data of
    interest is held, the delimiter to split the line on, (optional) a q-value-default is 0.01-,
    (optional) a p value-default is None-, return:

    None:
        -If the line begins with a # character (line is a comment, not data)
        -If the line is a newline character (\n, line is not data)
        -If the line is a header line, not containing data
        -If the value of the line (as a float) is less than the log transformed p/q value

    (variable) newline
        -If the value of the line (as a float) is greater than the log transformed p/q value
         This will be reformatted back to what it was originally.
    """
    # If the line is a comment or just a newline character
    if line[0] == "#" or line == "\n":
        # Return None, this is not a data line
        return None
    # If nothing is returned, then split the line on the delimiter
    line = line.split(delimiter)
    # Assuming the column is in Math counting, turn it into computer counting.
    col = int(value_column - 1)
    # If you see the strings "pvalue" or "qvalue", this line is a header
    if "pvalue" in line[col] or "qvalue" in line[col]:
        # Return None, this is not a data line
        return None
    # If the variable pvalue is set to something other than 1,
    if pvalue != None:
        # Try to float the p value. Just to check if it is a floating point number
        try:
            float(pvalue)
        # If this fails, raise a value error and stop the program
        except:
            raise ValueError(f"{pvalue} is not a floating point number")
        # Otherwise, take the negative log of the p value (default is base 10)
        else:
            log_trans = -math.log(pvalue, 10)
    # If pvalue == None, then log transform the q value
    else:
        # Try to float the q value. Just to check if it is a floating point number
        try:
            float(qvalue)
        # IF this fails, raise a value error and stop the program
        except:
            raise ValueError(f"{qvalue} is not a floating point number")
        # Otherwise, take the negative log of the q value (default is base 10)
        else:
            log_trans = -math.log(qvalue, 10)
    # If the corrsponding data value is greater than the log transformed cutoff
    if float(line[col]) >= log_trans:
        # Then take the line! Initialize newline variable
        newline = f"{line[0]}"
        # Remove the element used for initialization
        del line[0]
        # Loop over the remaining elements of the line list
        for column in line:
            # Update the newline using string formatting and the given dfelimiter
            newline = f"{newline}{delimiter}{column}"
        return newline
    # If the corresponding data value is less than the log transformed cutoff,
    else:
        # Then return None, this line is below the specified cutoff
        return None


def filter_all_lines(file,
                     delimiter,
                     qvalue = 0.01,
                     pvalue = None,
                     ext = "narrowPeak"):
    """
    Given a file, the delimiter for the lines in the file, (optional) q value-default is 0.01-,
    (optional) p value-default is None-, (optional) extension-default is narrowPeak-,

    return:
        -list of lines that are the result of filtering by q/p value


    NOTE: If you add a file type to this program, please add an elif statement to this function.
    Please make sure that pvlaue or qvalue are valid columns in your file as well :)

    """
    # Open and read the file, call it f
    with open(file, 'r') as f:
        # Start to check the extension and the values.
        #
        # If the extension is narrowPeak and the pvalue is None
        if ext == "narrowPeak" and pvalue == None:
            # Then use the filter_line() function inside of a list comprehension
            # to get the list of new lines.
            # For info about the narrowPeak file format, go to the USCS GenomeBrowser site
            newlines = [filter_line(line,
                                    9,
                                    delimiter,
                                    qvalue = qvalue,
                                    pvalue = pvalue) for line in f if line != "\n"]
            # Once the newlines are found, filter out the lines that have information
            # (i.e., those lines that are not None)
            newlines = [l for l in newlines if l != None]
        # Or if the extension is narrowPeak but the pvalue has been changed
        elif ext == "narrowPeak" and pvalue != None:
            # Then use the filter_line() function inside of a list comprehension
            # to get the list of new lines.
            # For info about the narrowPeak file format, go to the USCS GenomeBrowser site
            newlines = [filter_line(line,
                                    8,
                                    delimiter,
                                    qvalue = qvalue,
                                    pvalue = pvalue) for line in f if line != "\n"]
            # Once the newlines are found, filter out the lines that have information
            # (i.e., those lines that are not None)
            newlines = [l for l in newlines if l != None]
        # Or if the file type is xls and the pvalue has not been changed
        elif ext == "xls" and pvalue == None:
            # Then use the filter_line() function inside of a list comprehension
            # to get the list of new lines.
            # For info about the narrowPeak file format, go to the USCS GenomeBrowser site
            newlines = [filter_line(line,
                                    9,
                                    delimiter,
                                    qvalue = qvalue,
                                    pvalue = pvalue) for line in f if line[0] != "#" or line != "\n"]
            # Once the newlines are found, filter out the lines that have information
            # (i.e., those lines that are not None)
            newlines = [l for l in newlines if l != None]
            # Depricated: An old version of this file didn't filter the header of xls files. This one does
            #newlines = newlines[1:]
        # Or if the file type is xls and the pvalue has been changed
        elif ext == "xls" and pvalue != None:
            newlines = [filter_line(line,
                                    7,
                                    qvalue = qvalue,
                                    pvalue = pvalue) for line in f if line[0] != "#" or line != "\n"]
            # Once the newlines are found, filter out the lines that have information
            # (i.e., those lines that are not None)
            newlines = [l for l in newlines if l != None]
            # Depricated: An old version of this file didn't filter the header of xls files. This one does
            #newlines = newlines[1:]
        # If none of these work, then raise a value error
        else:
            raise ValueError(f"{ext} and {pvalue} together are invalid.")
        # After getting all of the lines, close the file
        f.close()
    # and return the list of new lines.
    return newlines

def filter_macs3_outputs(macs3_dir,
                         desired_extensions,
                         delimiter,
                         qvalue = 0.01,
                         pvalue = None):
    """
    Given a directory path to a macs3_out folder, the extensions for files you wish to filter,
    a delimiter that ALL files are split on, and the optional q/pvalues shown in all other functions,
    filter the files with the desired extensions and write them to a new folder. Move all other files
    to a folder named "unmodified_outfiles"
    """
    # Use the operating system module to make the unmodified and modified directories
    os.mkdir(f"{macs3_dir}/unmodified_outfiles")
    os.mkdir(f"{macs3_dir}/modified_peakfiles")
    # Use iglob (generator, not a list) to loop over the files in the directory
    for file in glob.iglob(f"{macs3_dir}/*"):
        # If the "file" found is one of the output folders,
        if f"{file}" == f"{macs3_dir}/unmodified_outfiles" or f"{file}" == f"{macs3_dir}/modified_peakfiles":
            # Then continue to the next iteration of the loop
            continue
        # If the file is not one of the output folders, then split the file string on the period
        # character and take the last element of the list as the extension
        file_extension = file.split(".")[-1]
        # Get the file name by first splitting the file string on the period, taking the 0th element,
        # then splitting that string on the '/' character, and taking the last element. Effectively,
        # "path/to/file.narrowPeak" -> ["path/to/file", "narrowPeak"] -> "path/to/file"
        # -> ["path", "to", "file"] -> "file"
        # but in one line
        file_name = file.split('.')[0].split('/')[-1]
        # If the file extension gathered above is in the list of ones to filter
        if file_extension in desired_extensions:
            # Then use the filter_all_lines() function to get the new lines
            new_lines = filter_all_lines(file,
                                         delimiter,
                                         qvalue = qvalue,
                                         pvalue = pvalue,
                                         ext = file_extension)
            # If the q value was filtered on, then write the new file as q_filtered
            if qvalue != None and pvalue == None:
                # Get the q value string by turning qvalue into a string, splitting on . and
                # using string formatting to concatenate them
                q = f"{str(qvalue).split('.')[0]}_{str(qvalue).split('.')[1]}"
                # Open a file in the output directory, writing, as f
                with open(f"{macs3_dir}/modified_peakfiles/q_{q}_filtered_peaks.{file_extension}", 'w') as f:
                    # Use the writelines method to write all lines to the file
                    f.writelines(new_lines)
                    # Close the file
                    f.close()
            # If the p value was filtered on, then write the new file as p_filtered
            elif qvalue == None and pvalue != None:
                # Get the p value string by turning pvalue into a string, splitting on . and
                # using string formatting to concatenate them
                p = f"{str(pvalue).split('.')[0]}_{str(pvalue).split('.')[1]}"
                # Open a file in the output directory, writing, as f
                with open(f"{macs3_dir}/modified_peakfiles/p_filtered_peaks.{file_extension}", 'w') as f:
                    # Use the writelines method to write all lines to the file
                    f.writelines(new_lines)
                    # Close the file
                    f.close()
            # Once the new file is written, move the unmodified file using os.rename()
            os.rename(f"{file}", f"{macs3_dir}/unmodified_outfiles/{file_name}.{file_extension}")
        # If the file extension is not in the desired_extension list
        else:
            # Then simply move the file to the unmodified directory, it is not of interest to us
            os.rename(f"{file}", f"{macs3_dir}/unmodified_outfiles/{file_name}.{file_extension}")

def filter_all_files(directory,
                     desired_extensions,
                     delimiter,
                     qvalue = 0.01,
                     pvalue = None):
    """
    Given a file directory, a list of desired extensions, a delimiter for ALL files,
    and the optional p/qvalues defined in other functions, filter all of the macs3
    output files in the directory.

    Assumes the macs3 output files are in a folder that has the "macs3" substring
    in the file name.
    """
    # Loop over the folders in the directory using the generator iglob
    for folder in glob.iglob(f"{directory}/*"):
        # Loop over the subfolders in each folder using iglob
        for subfold in glob.iglob(f"{folder}/*"):
            # If macs3 is a substring of the subfolder name
            if "macs3" in subfold.split('/')[-1].lower():
                # Use the filter_macs3_outputs() function to filter that directory
                filter_macs3_outputs(subfold,
                                     allowed_extensions,
                                     delimiter,
                                     qvalue = qvalue,
                                     pvalue = pvalue)
                # Continue once this is done. Assumes this is the only macs3 folder in this
                # specific subdirectory
                continue

#
#
##########################################################################################################
#
#      System Argument Checking Functions

def check_dir(directory):
    """
    Given a directory, check to see if there are any empty folders in the directory.

    * Recursively checks all directories. Assumes that only file names contain . character

    returns:
        None if given a file
        False if a folder is empty
        True if neither None nor False after recursion is complete
    """
    # If the directory string name does not contain a period
    if len(directory.split('.')) == 1:
        # Then use the glob function to get a list of all files in a directory
        dirlist = glob.glob(f"{directory}/*")
        # If the number of things in a directory is 0
        if len(dirlist) == 0:
            # Then return false, this is an empty directory
            return False
        # Otherwise
        else:
            # Loop over the items in the directory list
            for fold in dirlist:
                # Run the check_dir() function on each folder
                checker = check_dir(fold)
                # If the checker is None
                if checker == None:
                    # then continue with the loop, it is just a file
                    continue
                # If the checker returns False, then return False, there is an empty directory
                elif checker == False:
                    return False
        # IF False is not returned, then return True
        return True

def check_sysargs(args):
    """
    Given a list of system arguments, check them for the proper formatting. The system
    arguments should be:

    ===================================================================================

    args[0]   :    filter_narrowpeak_qvalue.py
    args[1]   :    directory

    OPTIONAL

    args[2]   : qvalue; float, None or default (if using pvalue, default is q = 0.01)
    args[3]   : pvalue; float, None or default (if using qvalue, default is p = None)
    args[4]   : delimiter; default is '\t'

    ===================================================================================
    """
    # First, assert that the number of arguments given is less than or equal to 5.
    assert len(args) <= 5, f"a maximum of five system arguments are allowed."
    # If only two arguments were given
    if len(args) == 2:
        # Then use the check_dir() function to check if there are empty folders
        is_directory_good = check_dir(args[1])
        # If either None or False is returned
        if is_directory_good == None or is_directory_good == False:
            # Then raise a ValueError and exit
            raise ValueError(f"{args[1]} has empty folders. Please delete them and try again.")
        # Otherwise, return the 4-tuple of the form
        # directory, qvalue, pvalue, delimiter
        else:
            return args[1], 0.01, None, '\t'

    # If three arguments were given
    elif len(args) == 3:
        # Then use the check_dir() function to check if there are empty folders
        is_directory_good = check_dir(args[1])
        # If either None or False is returned
        if is_directory_good == None or is_directory_good == False:
             # Then raise a ValueError and exit
             raise ValueError(f"{args[1]} has empty folders. Please delete them and try again.")
        # Next, try to float the second argument given
        try:
            float(args[2])
        # If this fails
        except:
            # Raise a value error and exit
            raise ValueError(f"{args[2]} (qvalue) should be a floating point number.")
        else:
            qvalue = float(args[2])
        # Otherwise, return the 4-tuple of the form
        # directory, qvalue, pvalue, delimiter
        return args[1], qvalue, None, '\t'

    # If four arguments were given
    elif len(args) == 4:
        # Then use the check_dir() function to check if there are empty folders
        is_directory_good = check_dir(args[1])
        # If either None or False is returned
        if is_directory_good == None or is_directory_good == False:
            # Then raise a ValueError and exit
            raise ValueError(f"{args[1]} has empty folders. Please delete them and try again.")
        # Next, try to float the third system argument given
        try:
            float(args[3])
        # If this fails
        except:
            # Then check to see if the pvalue was set to None
            if pvalue.lower() == 'none':
                # If it was, then set the pvalue to the None object
                pvalue = None
            # Otherwise,
            else:
                # Raise a value error and exit
                raise ValueError(f"{args[3]} (pvalue) should be a floating point number.")
        # If floating the third system argument does not fail
        else:
            # Then set the pvalue variable
            pvalue = float(args[3])
        # Next, check to see if the second system argument is None and the pvalue is not None
        if args[2].lower() != 'none' and pvalue != None:
            # If pvalue is None and the qvalue slot is not None, tell the user that they fucked up
            # the inputs and auto set the qvalue to None
            print(f"A valid pvalue was given, but the qvalue was not set to None... Setting qvalue = None")
            qvalue = None
        # Or if the pvalue is None but the second system argument is not None
        elif args[2].lower() != 'none' and pvalue == None:
            # Then try and float the second system argument
            try:
                float(args[2])
            # If this fails, then raise a system argument and exit
            except:
                raise ValueError(f"{args[2]} (qvalue) should be a floating point number.")
            # If floating args[2] did not fail
            else:
                # Then set the qvalue to the floated args[2]
                qvalue = float(args[2])
        # If neither of the q/p value conditions are true, then assign qvalue to None
        else:
            qvalue = None
        # Return all of the thigns in the format
        # directory, qvalue, pvalue, delimiter
        return args[1], qvalue, pvalue, '\t'

    # Or if 5 system arguments are given
    elif len(args) == 5:
        # Then use the check_dir() function to check if there are empty folders
        is_directory_good = check_dir(args[1])
        # If either None or False is returned
        if is_directory_good == None or is_directory_good == False:
            # Then raise a ValueError and exit
            raise ValueError(f"{args[1]} has empty folders. Please delete them and try again.")
        # Next, try to float the third system argument given
        try:
            float(args[3])
        # If this fails
        except:
            # Then check to see if the pvalue was set to None
            if pvalue.lower() == 'none':
                pvalue = None
            # Otherwise,
            else:
                 # Raise a value error and exit
                raise ValueError(f"{args[3]} (pvalue) should be a floating point number.")
        # If floating the third system argument does not fail
        else:
            # Then set the pvalue variable
            pvalue = float(args[3])
        # Next, check to see if the second system argument is None and the pvalue is not None
        if args[2].lower() != 'none' and pvalue != None:
            # If pvalue is None and the qvalue slot is not None, tell the user that they fucked up
            # the inputs and auto set the qvalue to None
            print(f"A valid pvalue was given, but the qvalue was not set to None... Setting qvalue = None")
            qvalue = None
        # Or if the pvalue is None but the second system argument is not None
        elif args[2].lower() != 'none' and pvalue == None:
            # Then try and float the second system argument
            try:
                float(args[2])
            # If this fails, then raise a system argument and exit
            except:
                raise ValueError(f"{args[2]} (qvalue) should be a floating point number.")
            # If floating args[2] did not fail
            else:
                # Then set the qvalue to the floated args[2]
                qvalue = float(args[2])
        # If neither of the q/p value conditions are true, then assign qvalue to None
        else:
            qvalue = None
        # Finally, assert that the deilimiter given is one of the common delimiters
        assert args[4] in [",", ".", "\t", ";", ":", "|", "-", "_"], f"invalid delimiter given: {args[4]}"
        # Return all of the thigns in the format
        # directory, qvalue, pvalue, delimiter
        return args[1], qvalue, pvalue, args[4]

#
#
##########################################################################################################
#
#        main() function

def main():
    """
    Get the system arguments  passed in from the command line,
    check to make sure they're formatted properly,
    Filter all of the peak files from the given directory
    tell the user they're done.
    """
    args = sys.argv
    directory, qvalue, pvalue, delimiter = check_sysargs(args)
    filter_all_files(directory,
                     allowed_extensions,
                     delimiter,
                     qvalue = qvalue,
                     pvalue = pvalue)
    print("done")

main()

#
#
##########################################################################################################
