"""
Kenny P. Callahan
22 December 2020

A little helper to create a .genome file for bedtools.
"""
###########################################################################################
#
#        Imports

import glob
import sys

#
#
###########################################################################################
#
#        Functions

def check_sysargs(args):

    """
    given system argument inputs, ensure that they have
    the following characteristics:

    -> args[0] : Is always the name of the python file (count_genome_chars.py)
    -> args[1] : path to the FASTA files (assumes linux/style/filepath)
    -> args[2] : A truthy value.
                 True  -> Slice the last argument of the path, as it is a file (or the path ends in '/')
                 False -> The path is to the folder, not to a file (or the path does not end in '/')
    """
    # Do the easy argument checking.
    assert len(args) == 3, 'Only three system arguments are permitted:\n args[0] == count_genome_chars.py \n args[1] == linux/style/filepath/to/chorm_fastas \n args[2] == true/false'
    assert args[2].lower() == 'true' or args[2].lower() == 'false', "The third system argument must be true or false"

    # Initialize the directory string
    directory=""

    # Split the path on the '/' character. If there is a trailing '/',
    # then the last element will be an empty string
    path_parts = args[1].split('/')

    # Loop over the parts of the folderpath
    for p in path_parts:
        # If the last sysarg is true and the loop is not at the last
        # path part
        if args[2].lower() == 'true' and p != path_parts[-1]:
            # Then build the directory string using p
            directory += f"{p}/"
        # If the last sysarg is set to false
        else:
            # Then just build the directory string as is.
            directory += f"{p}/"

    # Once the directory string is built, check to make sure each
    # fasta file can be opened. Loop over files in the directory
    for file in glob.iglob(f"{directory}*.fasta"):
        # Attempt to open the file
        try:
            with open(file, 'r') as f:
                f.close()
        # If this fails, raise a ValueError
        except ValueError:
            # Tell the user the file is invalid
            print(f"{file} is not a valid file.")
            # and system exit (equivalent of a keyboard interrupt
            sys.exit()

    # If the files can be opened, then return the directory string.
    return directory

def count_nucleotides_fasta(file):

    """
    given a fasta file, return a string in the following format:

    <chromosome>\t<nucleotide_count>\n

    Assumes that the first line of the fasta file has the following format:

    >[chromosome_identifier] [description of the chromosome]
    """

    # Open the file and read it. Assumes file has been
    # pre determined as a valid file.
    with open(file, 'r') as f:

        # Get the chromosome identifier. Read the first line
        chrom = f.readline()
        # Split the line on the spaces, chromosome is in the 0th spot
        chrom = chrom.split(' ')
        # Chromosome is the 0th spot without the carrot (>)
        chrom = chrom[0][1:]

        # Use list comprehension to get the lengths of all remaining lines.
        # Note that the len() method counts the newline character (\n) at the
        # end of each line, so we must subtract one from the number
        count_list = [(len(line) - 1) for line in f]

        # The nucleotide count is the sum of the count list
        count = sum(count_list)

        # Close the file, save some RAM
        f.close()

    # Return the tab separated chromosome count string
    return f"{chrom}\t{count}\n"

def get_count_lines(fasta_dir):

    """
    given a directory that contains chromosome FASTA files,
    return a list of lines to write to a .genome file.

    Assumes that the fasta_dir has format path/to/folder/
    """

    # Use list comprehension to get the lines for writing.
    # depends on the count_nucleotides_fasta() function.
    lines = [count_nucleotides_fasta(file) for file in glob.iglob(f"{fasta_dir}*.fasta")]

    return lines

#
#
##########################################################################################
#
#       main() function

def main():

    # Get the system argument
    args = sys.argv

    # Check that they are valid, assign directory string to directory
    directory = check_sysargs(args)

    # Get the lines list using get_count_lines()
    lines = get_count_lines(directory)

    # Write the length.genome file to the given directory
    with open(f"{directory}length.genome", 'w') as g:
        g.writelines(lines)
        g.close()

    print(f"{directory}length.genome has been written.")

main()

#
#
##########################################################################################


