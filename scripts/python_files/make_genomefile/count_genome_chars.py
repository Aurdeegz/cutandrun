"""
Kenny P. Callahan
22 December 2020

===========================================================================================
Python 3.8.5

count_genome_chars.py
===========================================================================================

A little helper to create a .genome file for bedtools.

The file format is:

<chrom>\t<number_of_nucleotides>

Since this program is tested using the NCBI FASTA genome files, the chrom will be an
NCBI identifier for that sequence, and the number will be the count.

"""
###########################################################################################
#
#        Imports

import glob    # Used to iterate over the files in a directory
import sys     # Used to get command line inputs (system arguments)

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
    allowed_extensions = ["fasta", "fa", "fna", "ffn", "faa", "frn"]

    # Do the easy argument checking. Number of argument
    assert len(args) == 4, 'Only three system arguments are permitted:\n args[0] == count_genome_chars.py \n args[1] == linux/style/filepath/to/chorm_fastas \n args[2] == true/false'
    # The second argument is a boolean
    assert args[2].lower() == 'true' or args[2].lower() == 'false', "The third system argument must be true or false"
    # The third system argument is a valid fasta file
    assert args[3] in allowed_extensions, "The given file extension is not a fasta file."

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
    return directory, args[3]

def count_nucleotides_fasta(file):

    """
    given a fasta file, return a string in the following format:

    <chromosome>\t<nucleotide_count>\n

    Assumes that the first line of the fasta file has the following format:

    >[chromosome_identifier] [description of the chromosome]
    """
    # Initialize the list to hold the lines
    lines = []

    # Open the file and read it. Assumes file has been
    # pre determined as a valid file.
    with open(file, 'r') as f:
        # Initialize a string for the last seen chromosome identifier
        current_chrom_id = ""
        # Inititalize a variable to hold the organism initials
        org_initials = ""
        # Initialize the count!
        count = 0
        # Set the variable go to False, used to tell the function to count later on
        go = False
        # Loop over the lines in the file
        for line in f:
            # If the line begins with a > character, then you've hit a new annotated region
            if line[0] == ">":
                # Check to see if the annotated region line includes the following substrings:
                # "chromosome" and not "sequence" means that you've found the entire chromosome
                # "complete genome" means that you've found a mitochondrial genome (at least for drosophila)
                if "chromosome" in line and "sequence" not in line or "complete genome" in line:
                    # Then check to see if this is the first chromosome sequence you've found
                    if len(lines) == 0 and current_chrom_id == "" and count == 0:
                        # If it is, then set go to True
                        go = True
                        # Split the line on the spaces
                        line = line.split(' ')
                        # The chromosome ID is the zeroeth element of the list without the > character
                        current_chrom_id = f"{line[0][1:]}"
                        # The organism initials are the first characters of the first and second strings in the list
                        org_initials = f"{line[1][0].lower()}{line[2][0].lower()}"
                    # Or if the number of lines is zero but we have seen a chromosome already
                    elif len(lines) == 0 and current_chrom_id != "":
                        # Then we should tell the program to continue counting (new chromosome)
                        go = True
                        # Add the count from the old chromosome to the list of lines formatted as in the docstring
                        lines.append(f"{current_chrom_id}\t{count}\n")
                        # Split this new line on spaces
                        line = line.split(' ')
                        # The chromosome ID is the zeroeth element of the line without the leading > character
                        current_chrom_id = f"{line[0][1:]}"
                        # And reset the count to zero to continue the counting of this next chromosome
                        count = 0
                    # Or if there are already lines found
                    elif len(lines) > 0:
                        # Then we should tell the program to continue counting (new chromosome)
                        go = True
                        # Add the count from the old chromosome to the list of lines formatted as in the docstring
                        lines.append(f"{current_chrom_id}\t{count}\n")
                        # Split this new line on spaces
                        line = line.split(' ')
                        # The chromosome ID is the zeroeth element of the line without the leading > character
                        current_chrom_id = f"{line[0][1:]}"
                        # And reset the count to zero to continue the counting of this next chromosome
                        count = 0
                # If we are not at a chromosome or the mitochondrial genome sequence, then we don't want to count
                else:
                    # So set the go variable to False
                    go = False
            # Or if the line does not start with > and the go variable is True
            elif go == True:
                # Then count the characters in the line, minus 1 for the newline character
                count += len(line)-1
        # At the end of the loop, add the last chrom and count to the liens list
        lines.append(f"{current_chrom_id}\t{count}\n")
        # Close the file when done
        f.close()

    # Return the tab separated chromosome count string
    return lines, org_initials

def get_count_lines(fasta_dir, extension):

    """
    given a directory that contains chromosome FASTA files,
    return a list of lines to write to a .genome file.

    Assumes that the fasta_dir has format path/to/folder/
    """

    # Initialize the lines variable
    lines= []
    # Use generator iglob to iterate over the files in the given directory
    for file in glob.iglob(f"{fasta_dir}/*.{extension}"):
        # Use the count_nucleotides_fasta() function to count the chromosomes/nucleotides.
        # This returns a list of strings and a organism ID
        new_lines, org_initials = count_nucleotides_fasta(file)
        # Add the lines found to the lines list
        lines += new_lines
    # Return the lines list and the orgnaims ID
    return lines, org_initials

#
#
##########################################################################################
#
#       main() function

def main():

    # Get the system argument
    args = sys.argv

    # Check that they are valid, assign directory string to directory
    directory, extension = check_sysargs(args)

    # Get the lines list using get_count_lines()
    lines, org_initials = get_count_lines(directory, extension)

    # Write the length.genome file to the given directory
    with open(f"{directory}length.genome", 'w') as g:
        g.writelines(lines)
        g.close()
    # Print the organims initials. If you run a bash script, this can be captured by
    # id=$(python3 count_genome_chars.py "directory/to/fasta/files")
    print(f"{org_initials}")

main()

#
#
##########################################################################################


