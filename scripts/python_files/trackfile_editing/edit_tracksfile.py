"""
Kenny P. Callahan
30 December 2020

==========================================================
edit_tracksfile.py
==========================================================
Python Version:

Python 3.8.5
==========================================================

This little program is meant to be used with the program

cut_run_pipeline_v1.sh

It takes command line arguments as follows:

|        1        |        2        |
--------------------------------------
| tracksfile_path | output_filename |

-> tracksfile_path is the path to a tracks.ini file produced 
using the pyGenomeTracks file make_tracks_file.py

-> output_filename is the name of the output tracks file, and
should include .ini extension. If the user does not provide 
the extension, it will be appended to whatever input the user
does provide.

"""
#####################################################################################
#
#            Imports

import sys

#
#
#####################################################################################
#
#            Defined variables. Modify as needed


# These colours should work with matplotlib.pyplot, which is what the pyGenomeTracks
# programs uses to make plots. If you would like to add more colours to this, a list
# can be found here: https://matplotlib.org/3.1.1/gallery/color/named_colors.html

colors = ['blue', 
          'deepskyblue',
          'red', 
          'hotpink'
          'black', 
          'slategray',
          'violet', 
          'indigo',  
          'orange', 
          'green',
          'springgreen',
          'turquoise',
          'mediumpurple',
          'darkviolet',
          'magenta']

#colors = ['red',
#          'orangered',
#          'limegreen',
#          'springgreen',
#          'turquoise',
#          'deepskyblue',
#          'mediumpurple',
#          'darkviolet',
#          'magenta',
#          'hotpink']

# This is a dictionary of settings that will be changed in the tracks.ini file 
# used to configure the pyGenomeTracks program. If there are other variables in
# the tracks.ini file you would like to change, then simply add those variables
# to the dictionary keys with the desired value. Note that title is determined 
# by the folder holding the bw files, and color is determined using the list 
# of colours above. 
settings = {'title' : '',
            'color' : '',
            'min_value' : 'min_value = 0'}

#
#
#####################################################################################
#
#            Functions

def check_sysargs(args):
    
    """
    Given sys.argsv (arguments passed in from the command line),
    determine whether or not:
    
    -> a valid tracksfile is given     (sys.argv[1])
    and/or
    -> a valid output file is given.   (sys.argv[2])
    
    The zeroeth value of sys.argv is the file name, thus the program
    evaluates the first and second arguments for a tracksfile and
    an output file, respectively.
    """
    
    assert type(args) == list, "args must have type 'list'"
    assert 2 <= len(args) <= 3, "more than two system arguments were given"
    
    # If there are two system arguments,
    if len(args) == 2:
        
        # then try to open args[1], which should have the folderpath
        # and name of the tracks.ini file.
        try:
            with open(args[1]) as f:
                
                # If opening succeeds, then this is a valid tracksfile
                tracksfile = args[1]
                f.close()
                
        # If opening the file fails, then raise a value error
        except ValueError:
            
            # and return the invalid argument string, and None
            return f"The argument {args[1]} is not a file.", None
        
        # If the try block succeeds without error
        else:
            
            # Then create the tracks_edited.ini string
            outfile = args[1].split("/")
            outfile[-1] = "tracks_edited.ini"
            outfile = "/".join(outfile)
            
            # And return the tracksfile and outfile strings.
            return tracksfile, outfile
    
    # If there is not two elements in args, then there is three
    else:
        
        # Again, try to open the tracks.ini file given
        try:
            with open(args[1]) as f:
                
                # If this succeeds, then this is a valid track file
                tracksfile = args[1]
                f.close()
        
        # If this fails, then raise a value error
        except ValueError:
            
            # and return the error string and None
            return f"The argument {args[1]} is not a file.", None
        
        # If the try block succeeds
        else:
            
            # Then ensure that the outfile has extension .ini
            if ".ini" in args[2]:
                outfile = args[2]
                
                # and return the tracksfile and the outfile
                return tracksfile, outfile
            
            # Otherwise, add the .ini extension to the outfile
            else:
                outfile = f"{args[2]}.ini"
                
                # and return the tracksfile and outfile.
                return tracksfile, outfile
            

def set_values(value_dict,
               **kwargs):
    
    """
    Given a value dictionary and keyword arguments,
    add values to the value dictionary that correspond
    to the keyword arguments. 
    
    This function assumes that the value dictionary is already
    defined, and that the keys corresponding to the keyword
    arguments are already defined.
    
    This function DOES NOT return a value, it modifies the input
    dictionary instead. 
    """
    
    assert type(value_dict) == dict, "value_dict must have type 'dict'"
    
    # loop over each key in the value dictionary
    for key in value_dict.keys():
        # If the key is also a keyword argument
        if key in kwargs.keys():
            # Add the value string to the value dict at that key
            value_dict[key] = f"{key} = {kwargs[key]}"


def write_lines(first_word,
                lines,
                line_string,
                value_dict):
    
    """
    Given the first word in a line from a file, the list of lines
    to be written to a new file, the current line of the file, and
    the dictionary of values to be edited, then update the list of lines.
    
    This function DOES NOT return a value. Rather, it modifies the
    global lines list.
    """
    
    assert type(first_word) == str, "first_word must have type 'str'"
    assert type(value_dict) == dict, "value_dict must have type 'dict'"
    assert type(lines) == list, "lines must have type 'list'"
    
    # If the first word in the line is also a key in the value dictionary
    if first_word in value_dict.keys():
        
        # then append the value string in the dictionary to the lines list
        lines.append(f"{value_dict[first_word]}\n")
    # If the first word in the line is not a key in the value dictionary
    else:
        # Then append the original line to the lines list
        lines.append(f"{line_string}\n")

def finding_a_folderpath(line_string,
                         value_dict,
                         color_string):
    
    """
    Given the current line in a file, 
    the dictionary containing line values to modify, and a colour,
    then determine whether or not we are now in a folder of bw files
    or whether we are on a spacer/axis.
    
    This function returns either an empty string or the 'current_folder'
    variable. The empty string denotes that we have not found a file 
    line (indicating that the block is not a data block in the tracks
    file) or the current folder variable (if the block is a data block)
    
    This function also modifies the global value_dict in place, if the 
    block is a data block
    """
    
    assert type(line_string) == str, "line_string must be of type 'str'"
    assert type(value_dict) == dict, "value_dict must be of type 'dict'"
    assert type(color_string) == str, "color_string must be of type 'str'"
    
    # Split the given line on the spaces
    words = line_string.split(" ")
    
    # If the first word of the line is 'file'
    if words[0] == 'file':
        # Then we are in a data block. Split the last element of words
        # on '/', as this has the folderpath
        split_line_string = words[-1].split("/")

        # The current folder is the second to last element of the folderpath
        # split
        current_folder = split_line_string[-2]
        
        # Remove the underbars from the folder path for title string
        title_string = current_folder.replace("_", " ")
        
        # Set the values of the in the value dict to be used for line formatting
        set_values(value_dict,
                   title = title_string,
                   color = color_string)
        
        # return the current folder, used in decisions later on
        return current_folder
    
    # If the first word of the line is not file
    else:
        # Return an empty string as this is not a data block
        return ""
    
def same_folderpath(line_string,
                    value_dict,
                    color_string,
                    last_folder_seen):
    
    """
    Given the current line, the dictionary of line values,
    a colour, and the last folder encountered, determine whether
    the current folder is the same as the previous folder, and
    whether or not the value dictionary should change.
    
    This function returns the last folder seen (or the next folder).
    
    This function can also modify the global value_dict if we 
    encounter a new folder.
    """
    
    # Split the current line on the spaces
    words = line_string.split(" ")
                
    # If the first word in the line is file
    if words[0] == 'file':
        
        # Then split the last word of the line (which has the filepath)
        # on the '/' characters
        next_folder = words[-1].split('/')
        
        # If the last folder seen is the same as the current folder
        if next_folder[-2] == last_folder_seen:
            #title = last_folder_seen.replace("_", " ")
            #set_values(value_dict,
            #           title = title,
            #           color = color_string)
            
            # Then simply return the last folder seen
            return last_folder_seen
        
        # If the current folder is not the same as the last folder seen
        else:
            
            # Save the next folder to the next folder variable
            next_folder = next_folder[-2]
            
            # Get the next title string
            title = next_folder.replace("_", " ")
            set_values(value_dict,
                       title = title,
                       color = color_string)
            
            # Return the next folder
            return next_folder
        
    # If the first word is not file, then this is not a data block
    else:
        # So we return an empty string
        return ""

def get_lines(file,
              value_dict,
              colors):
    
    """
    Given a file, a dictionary of initialized values, and
    a list of colours, return a list of lines to be written
    to a new file. 
    
    This is the main wrapper function of this module. It loops
    over the lines in the .ini file, then determines what changes
    should be made. The desired changes are saved in the value
    dict (in this module, it is called settings), and a list of 
    colours accepted by matplotlib are given in the colors list.
    """
    
    # Initialize lines list.
    lines = []
    
    # Open the given file, call it f
    with open(file, "r") as f:
        
        # Initialize area string to empty. This holds the 
        # block title in the tracks.ini file for reference.
        area = ""
        
        # Initializes a variable to store the last folder 
        # seen when reading lines of the file
        last_folder = ""
        
        # Initializes a variable to store the next folder
        # seen when reading lines of the file.
        next_folder = ""
        
        # Initializes counter to determine which colour
        # to use for a given file. 
        count = 0
        
        # Begin to loop over each line in the file.
        for line in f:
            
            # Strip the newline character ('\n') from line
            line = line.strip()
            
            # Split the line on space and save to splt
            splt = line.split(" ")
            
            # If the first string has both [ and ], then we are 
            # at a new block
            if '[' in splt[0] and ']' in splt[0]:

                print(count)
                
                # Reassign area to be the string containing the new block
                area = splt[0]
                
                # Append the block string to the lines
                lines.append(f"{line}\n")
                
                # Save read the next line and save it to a variable
                next_line = f.readline()

                #
                lines.append(next_line)
                
                # If the last folderline did not contain a folder
                if last_folder == "":
                    
                    # then try to find the next folderpath
                    try:
                        next_folder = finding_a_folderpath(next_line,
                                                           value_dict,
                                                           colors[count])
                    # If this fails, then print the exception and exit
                    except:
                        print(" The colour list did not have enough colours \n for these datasets.")
                        sys.exit()
                    else:
                    	# If we have reached a new folderpath
                    	if next_folder != last_folder:
                        
                            # Then increase the count and save the next folder
                            count += 1
                            last_folder = next_folder
                
                # If the last folderline is not an empty string, then we have
                # seen a folder previously.
                else:
                    try:
                        next_folder = same_folderpath(next_line,
                                                      value_dict,
                                                      colors[count],
                                                      last_folder)
                    except:
                        print(" The colour list did not have enough colours \n for these datasets.")
                        sys.exit()
                    else:
                        # If we have reached a new folderpath
                        if next_folder != last_folder:
                        
                            # Then increase the count and save the next folderpath
                            count += 1
                            last_folder = next_folder
            
            # If the line is not a line containing a block ([ and ])
            else:
                
                # Try to determine if the line is commented out.
                # splt[0][0] will fail if the string is empty.
                try:
                    # If the first character is a number symbol
                    if splt[0][0] == "#":
                        
                        # Then run writelines without the number symbol
                        write_lines(splt[0][1:],
                                    lines,
                                    line,
                                    value_dict)
                    # If the first character is not the number symbol,
                    # then simply run write lines.
                    else:
                        write_lines(splt[0],
                                lines,
                                line,
                                value_dict)
                # If there is an empty string
                except:
                    # then just run write lines
                    write_lines(splt[0],
                                lines,
                                line,
                                value_dict)
    # Close the file and return the lines.
    f.close()
    return lines

def write_newfile(lines,
                  outfile):
    
    """
    Given a list of strings to be written to a file
    and a filename, write a file at that name. 
    """
    
    assert type(lines) == list, "lines must have type 'list'"
    assert type(outfile) == str, "outfile must have type 'str'"
    
    with open(outfile, 'w') as f:
        f.writelines(lines)
        f.close()
    return f"{outfile} has been written."

#
#
#####################################################################################
#
#            main() function and invokation

def main():
    
    """
    The main function is a wrapper for all functions and variables 
    in the program.
    """
    
    # Get the arguments passed in the command line
    args = sys.argv
    #print(args)
    # Check to make sure the inputs are valid
    tracksfile, outfile = check_sysargs(args)
    
    # IF they are not, then exit the program.
    if outfile == None:
        print(tracksfile)
        sys.exit(tracksfile)
        
    # Use get_lines() to get the lines to write to the new file
    lines = get_lines(tracksfile,
                      settings,
                      colors)
    
    # Wrote the new file 
    finish = write_newfile(lines,
                           outfile)
    
    # print the finishing statement
    print(finish)
    
main()

#
#
#####################################################################################
#
#
