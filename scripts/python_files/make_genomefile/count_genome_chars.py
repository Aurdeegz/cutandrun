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
    allowed_extensions = ["fasta", "fa", "fna", "ffn", "faa", "frn"]

    # Do the easy argument checking.
    assert len(args) == 4, 'Only three system arguments are permitted:\n args[0] == count_genome_chars.py \n args[1] == linux/style/filepath/to/chorm_fastas \n args[2] == true/false'
    assert args[2].lower() == 'true' or args[2].lower() == 'false', "The third system argument must be true or false"
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

    lines = []

    # Open the file and read it. Assumes file has been
    # pre determined as a valid file.
    with open(file, 'r') as f:

        current_chrom_id = ""
        org_initials = ""
        count = 0
        go = False
        for line in f:

            if line[0] == ">":
                if "chromosome" in line and "sequence" not in line or "complete genome" in line:
                    if len(lines) == 0 and current_chrom_id == "" and count == 0:
                        go = True
                        line = line.split(' ')
                        current_chrom_id = f"{line[0][1:]}"
                        org_initials = f"{line[1][0].lower()}{line[2][0].lower()}"

                    elif len(lines) == 0 and current_chrom_id != "":
                        go = True
                        lines.append(f"{current_chrom_id}\t{count}\n")
                        line = line.split(' ')
                        current_chrom_id = f"{line[0][1:]}"
                        count = 0
                    elif len(lines) > 0:
                        go = True
                        lines.append(f"{current_chrom_id}\t{count}\n")
                        line = line.split(' ')
                        current_chrom_id = f"{line[0][1:]}"
                        count = 0
                else:
                    go = False
            elif go == True:
                count += len(line)-1

        lines.append(f"{current_chrom_id}\t{count}\n")

        f.close()

    # Return the tab separated chromosome count string
    return lines, org_initials

def get_count_lines(fasta_dir, extension):

    """
    given a directory that contains chromosome FASTA files,
    return a list of lines to write to a .genome file.

    Assumes that the fasta_dir has format path/to/folder/
    """

    # Use list comprehension to get the lines for writing.
    # depends on the count_nucleotides_fasta() function.

    lines= []

    for file in glob.iglob(f"{fasta_dir}/*.{extension}"):
        new_lines, org_initials = count_nucleotides_fasta(file)
        lines += new_lines

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

    print(f"{org_initials}")

main()

#
#
##########################################################################################


