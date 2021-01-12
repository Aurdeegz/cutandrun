"""
Kenny P. Callahan
22 December 2020

A little helper to create a .genome file for bedtools.
"""

import glob
import sys

args = sys.argv
print(args)
# Get the directory string from the input argument
directory=""

try:
    splitter = args[1].index('/')
    paths = args[1].split('/')
    if args[2] == "True":
        for p in range(len(paths)-1):
            directory+=f"{paths[p]}/"
    else:
        for p in range(len(paths)):
            directory+=f"{paths[p]}/"
except:
    directory+=f"{args[1]}/"

#cd teprint(directory)

# Open and write the length.genome file, which will hold
# the chromosomes and their lengths.
with open(f"{directory}length.genome", 'w') as g:

    # Lines list, will be used to write chromosome lengths
    # to the output file
    lines = []

    # Loop over the FASTA files in the directory
    for fast in glob.iglob(f"{directory}/*.fasta"):

        # Count variable initialized for this file
        count = 0

        # OPen and read the FASTA file
        with open(fast,'r') as f:

            # The chromosome name is in the first line
            chrom = f.readline()
            # In the first position
            chrom = chrom.split(' ')[0]
            # And preceededd by the character >
            chrom = chrom[1:]

            # The number of nucleotides in the line is
            # one less than the length of the line
            for line in f:
                count+=(len(line)-1)

            # Append the chromosome, count to the lines,
            # tab separated with a newline character
            lines.append(f"{chrom}\t{count}\n")
            # Close the file
            f.close()
    # When all of the chromsomes are counted, write
    # the lines of the file.
    g.writelines(lines)
