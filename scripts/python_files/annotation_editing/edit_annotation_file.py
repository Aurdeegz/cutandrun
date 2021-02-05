"""
Kenneth P. Callahan

23 January 2021

==============================================================================================================
Python 3.8.5

edit_annotation_file.py
==============================================================================================================

** It is assumed here that the annotation files are filtered from an annotation file found
on NCBI. This program was designed using the annotation file for Drosophila melanogaster,
so edits may be required for other organisms (depending on their identifier format)**

This file provides support for cleaning up annotation files. It requires one system argument
from the user:

args[0]    :   edit_annotation_file.py   (This argument always happens, no matter what)
args[1]    :   path/to/annotation_bedfiles (path to folder containing annotation files in bed format)


There are a few organism identifiers that have been manually set in this file:

Drosophila melanogaster    :    dmel
Escherichia coli           :    ecol
Homo sapiens               :    hsap
Mus musculus               :    mmus
Caenorhabditis elegans     :    cele

If your organism is not represented, or if the organism identifier used in your annotation file
is different, then simply edit the organism_identifiers list below (and let me know!!)

If you need to change the column that contains the annotation identifier information, go to the
main function below, and look for the line

edit_lines = get_lines(file, '\t', 4)

and change the integer 4 to the integer for the column you desire.

If this file is run, given a directory containing annotation files in bed format (I would filter them
based on annotation type first, see the cutandrun program for more details), then those files will
be REWRITTEN after formatting of the annotation identifier line. (for bed files, column 4).

"""

##############################################################################################################
#
#           Importables

import sys         # For getting the system argument inputs
import glob        # For iterating over files in a directory

#
#
##############################################################################################################
#
#          Pre defined variables and things

# The annotation files should have extension .bed, and should be in bed format (mostly).
# My annotation files are in a 'bed7' format, where the seventh column is the annotation
# type (gene, exon, etc).
extensions = ["bed",
              "bed6",
              "bed12"]

# These are the "organism identifiers", which are just the first letter of the genus and
# the first three letters of the species. This program was designed around Drosophila
# melanogaster, and there are annotations that have format 'gene-Dmel-CG43201'. The
# organism identifier just lets the program know which portion of the string to take.
organism_identifiers = ["dmel",
                        "ecol",
                        "hsap",
                        "mmus",
                        "cele"]

#
#
##############################################################################################################
#
#        Functions: Checking lines of certain identifiers

def check_rna_line(line,
                   delimiter,
                   column):
    """
    Given a line, a delimiter, and a column number (which has the
    annotation identifier), return a string that is formatted
    based on the qualities below.

    For RNA, possible string types seen:

    rna-|FlyBase|<identifier>-<sub_id>      ->   <identifier>-<sub_id>             (NCBI or Flybase)
    rna-<some_id>_<some_number>.<integer>   ->   <some_id>_<some_number>.<integer> (NCBI identifiers)
    rna-<organism_id>_<identifier>          ->   <identifier>                      (Flybase)
    """
    # Use the global organism_identifiers list
    global organism_identifiers
    # Computer scientists start counting at zero, so subtract 1 from the column number
    # to get the placement in the split line.
    col = column - 1
    # Split the line on the delimiter. Line will be a list.
    line = line.split(delimiter)
    # Check line[col] for the relevant ID types
    #
    # Type 1 as shown in docstring
    if "|" in line[col]:
        # If | is in the ID, then split on | and take the last element
        line[col] = line[col].split('|')[-1]
    # Type 2 as shown in docstring
    # If rna- and N in column
    elif "rna-" in line[col] and "N" in line[col]:
        # Then simply remove the first four characters of the column
        line[col] = line[col][4:]
    # Otherwise, we consult the organism identifiers list
    else:
        # Loop over ids in organism_identifiers
        for id in organism_identifiers:
            # If the id is a substring of the column
            if id in line[col].lower():
                # Then lower the line, split on the id, and take the last element
                # of the split column starting from character 1, uppercase.
                line[col] = line[col].lower().split(id)[-1][1:].upper()
                # and break the loop
                break
    # Initialize the newline
    newline = f"{line[0]}"
    # Delete the 0th element of the split line, as it is in the newline
    del line[0]
    # Loop over the elements of the line
    for colmn in line:
        # Use string formatting to populate the newline string
        newline = f"{newline}{delimiter}{colmn}"
    # Return the newline string
    return newline

def check_cds_line(line,
                   delimiter,
                   column):
    """
    Given a line, a delimiter, and a column number (where the annotation
    identifier lives), return a new string with the identifier cleaned up.

    Possible identifier strings for coding sequences:

    cds-<some_id>_<some_number>.<integer>   ->   <some_id>_<some_number>.<integer> (NCBI identifiers)
    id-<organism_id>_<identifier>          ->    <identifier>                      (Flybase)
    """
    # Computer scientists start counting at zero, so subtract 1 from the column number
    # to get the placement in the split line.
    col = column - 1
    # Split the line on the delimiter, reassigns variable line as a list of strings.
    line = line.split(delimiter)
    # Check line[col] for relevant ID type
    #
    # Type 1: string has substring cds- and N in it
    if "cds-" in line[col] and "N" in line[col]:
        # In which case, just use the string without the first four characters
        line[col] = line[col][4:]
    # If the substring id_N is in the string
    elif "id_N" in line[col]:
        # Then just use the string without the first three characters
        line[col] = line[col][3:]
    # Initialize the newline string
    newline = f"{line[0]}"
    # Delete the 0th element of th eline, as it is in the newline
    del line[0]
    # Loop over the remaining elements of line
    for colmn in line:
        # Use string formatting to populate the newline
        newline = f"{newline}{delimiter}{colmn}"
    # Return the newline
    return newline

def check_exon_line(line,
                    delimiter,
                    column):
    """
    Given a line, a delimiter, and a column (which denotes the column
    containing the identifier string), return a newline with the identifier
    string cleaned up.

    Possible annotation types for exon:

    exon-|FlyBase|<identifier>-<sub_id>      ->   <identifier>-<sub_id>             (NCBI or Flybase)
    exon-<some_id>_<some_number>.<integer>   ->   <some_id>_<some_number>.<integer> (NCBI identifiers)
    exon-<organism_id>_<identifier>          ->   <identifier>                      (Flybase)
    """
    # Use the global organism identifiers list
    # Computer scientists start counting at zero, so subtract 1 from the column number
    # to get the placement in the split line.
    col = column - 1
    # Split the line on the delimiter, reassigns variable line as a list of strings.
    line = line.split(delimiter)
    # Check line[col] for the relevant ID types
    #
    # Type 1 as shown in docstring
    if "|" in line[col]:
        # If | is in the ID, then split on | and take the last element
        line[col] = line[col].split('|')[-1]
    # Or if the substrings exon- and N are in the ID
    elif "exon-" in line[col] and "N" in line[col]:
        # Then take the string without the first five characters
        line[col] = line[col][5:]
    # Or if the substring id-N is in the string
    elif "id-N" in line[col]:
        # Then take the string without the first three characters
        line[col] = line[col][3:]
    # If these fail, then consult the organism identifiers list
    else:
        # loop over IDs in the organism_identifiers list
        for id in organism_identifiers:
            # If the id is in the identfier string
            if id in line[col].lower():
                # Then lower the line, split on the id, and take the last element
                # of the split column starting from character 1, uppercase.
                line[col] = line[col].lower().split(id)[-1][1:].upper()
                # and break the loop
                break
    # Initialize the newline string
    newline = f"{line[0]}"
    # Delete the 0th element of the line, as it is already used
    del line[0]
    # Loop over the remaining elements of the line
    for colmn in line:
        # Populate the newline string using string formatting
        newline = f"{newline}{delimiter}{colmn}"
    # Return the newline
    return newline

def check_gene_line(line,
                    delimiter,
                    column):
    """
    Given a line, a delimiter, and a column (which denotes the column
    containing the identifier string), return a newline with the identifier
    string cleaned up.

    Possible annotation types for gene:

    gene-<some_id>_<some_number>.<integer>   ->   <some_id>_<some_number>.<integer> (NCBI identifiers)
    id-<some_id>_<some_number>.<integer>   ->   <some_id>_<some_number>.<integer> (NCBI identifiers)
    gene-<organism_id>_<identifier>          ->   <identifier>                      (Flybase)
    """
    # Use the global organism identifiers list
    global organism_identifiers
    # Computer scientists start counting at zero, so subtract 1 from the column number
    # to get the placement in the split line.
    col = column - 1
    # Split the line on the delimiter, reassigns variable line as a list of strings.
    line = line.split(delimiter)
    # Check line[col] for the relevant ID types
    #
    # Type 1 as shown in docstring
    # If the substrings gene- and N are in the identifier string
    if "gene-" in line[col] and "N" in line[col]:
        # Then take the string without the first five characters
        line[col] = line[col][5:]
    # Or if the substring id-N is in the string
    elif "id-N" in line[col]:
        # Then take the string without the first three characters
        line[col] = line[col][3:]
    # If these fail, then consult the organism identifiers list
    else:
        # loop over IDs in the organism_identifiers list
        for id in organism_identifiers:
            # If the id is in the identfier string
            if id in line[col].lower():
                # Then lower the line, split on the id, and take the last element
                # of the split column starting from character 1, uppercase.
                line[col] = line[col].lower().split(id)[-1][1:].upper()
                # and break the loop
    # Initialize the newline string
    newline = f"{line[0]}"
    # Delete the 0th element of the line, as it is already in the newline
    del line[0]
    # Loop over the remaining elements of the line list
    for colmn in line:
        # Use string formatting to populate the newline
        newline = f"{newline}{delimiter}{colmn}"
    # Return the newline
    return newline

def check_other_line(line,
                     delimiter,
                     column):
    """
    Given a line, a delimiter, and a column (which denotes the column
    containing the identifier string), return a newline with the identifier
    string cleaned up. This function makes no assumption about the type
    of annotation in the line
    """
    # Computer scientists start counting at zero, so subtract 1 from the column number
    # to get the placement in the split line.
    col = column - 1
    # Split the line on the delimiter, assigns variable splitter as a list of strings
    splitter = line.split(delimiter)
    # Try the RNA line checker.
    newline = check_rna_line(line, delimiter, column)
    # If the newline and line are not equal, then the RNA checker did something
    if line != newline:
        # So return that something
        return newline
    # Try the CDS line checker
    newline = check_cds_line(line, delimiter, column)
    # If the newline and the line are not equal, then the CDS checker did something
    if line != newline:
        # So return that something
        return newline
    # Try the EXON line checker
    newline = check_exon_line(line, delimiter, column)
    # If the newline and the line are not equal, then the EXON checker did something
    if line != newline:
        # So return that something
        return newline
    # Try the GENE line checker
    newline = check_gene_line(line, delimiter, column)
    # If the newline and the line are not equal, then the GENE checker did something
    if line != newline:
        # So return that something
        return newline
    # If none of these worked, the attempt the most basic annotation type: id-N
    else:
        # If id-N is in the identifier column
        if "id-N" in splitter[col]:
            # Then take the string without the first three characters
            splitter[col] = splitter[col][3:]
            # Initialize the newline
            newline = f"{splitter[0]}"
            # Delete the 0th element of splitter, as it is already in the line
            del splitter[0]
            # Loop over the elements of the split line
            for colmn in splitter:
                # Use string formatting to populate the newline
                newline = f"{newline}{delimiter}{colmn}"
            # And returnthe newline
            return newline
        # If all of this fails, then just return the line and give up.
        else:
            return line

#
#
##############################################################################################################
#
#         Function: Checking the system argument inputs

def check_sysargs(args):
    """
    Given the args list (gotten from sys.argv), check that they are in the proper format/valid.

    The arguments should be as follows:
    ================================================================
    args[0]   :   edit_annotation_file.py
    args[1]   :   annotation directory (full of bed files)
    ================================================================
    """
    # Check the number of arguments given. Fail if there are more than two
    assert len(args) == 2, "Only two system arguments should be given"
    # If that passes, then check the directory for bed files that can be opened.
    # Loop over the files in the presumed directory
    for file in glob.iglob(f"{args[1]}/*"):
        # If the file extension is .txt, assume it is fields.txt and pass
        if ".txt" in file:
            pass
        # Otherwise, check for bed files
        else:
            # If the substring .bed is not in the file path, then exit
            assert ".bed" in file, "The directory should contain bed files."
            # If this passes, then attempt to open the file.
            try:
                with open(file, 'r') as f:
                    f.close()
            # IF this fails, then print a value error and exit.
            except ValueError:
                print(f"{file} could not be opened...")
                sys.exit()
    # If these all work, then the user gave a directory of bed files that can be
    # opened, so we attempt to proceed.
    return args[1]


#
#
##############################################################################################################
#
#          Functions: Parsing the file, formatting lines, writing them back to file

def get_lines(file, delimiter, column):
    """
    Given a file, a delimiter, and a column (which contains the identifier of interst),
    return a list of lines with those identifiers reformatted.
    """
    # Initailze the lines list
    lines = []
    # Open the file and read it
    with open(file, 'r') as f:
        # Loop over the lines in the file
        for line in f:
            # If rna is in the line
            if "rna" in str(f).lower():
                # Then check using the RNA checker
                newline = check_rna_line(line, delimiter, column)
            # Or if cds is in the line
            elif "cds" in str(f).lower():
                # Then check using the CDS checker
                newline = check_cds_line(line, delimiter, column)
            # Or if exon is in the line
            elif "exon" in str(f).lower():
                # Then check using the EXON checker
                newline = check_exon_line(line, delimiter, column)
            # Or if gene is in the line
            elif "gene" in str(f).lower():
                # Then check using the GENE checker
                newline = check_gene_line(line, delimiter, column)
            # Or if region is in the line
            elif "region" in str(f).lower():
                # Then this file is a region file, which we do not need.
                # Append the line and continue on
                lines.append(line)
                continue
            # If none of these were found, then use the check_other_line function
            # to just brute force the formatting
            else:
                newline = check_other_line(line, delimiter, column)
            # Add the newline to the lines.
            lines.append(newline)
        # Once you've finished all lines in the file, then close the file
        f.close()
    # and return the lines
    return lines

def write_new_file(file,
                   lines):
    """
    Given a filename and a list of strings (lines),
    Write a file!
    Return a string
    """
    # Open the file signifying write ('w')
    with open(file, 'w') as f:
        # Use the writelines method to write all lines to the file
        f.writelines(lines)
        # And close the file
        f.close()
    # Return the done statement
    return f"{file} has been rewritten!"

#
#
##############################################################################################################
#
#           main() function

def main():
    """
    Main function wraps all of the stuff above together.
    1) Get the system arguments
    2) Check the system arguments
    3) Loop over the files in the directory given
        3a) If it is a text file then pass
        3b) If it is not a text file, then reformat the lines and rewrite the file
    """
    args = sys.argv
    directory = check_sysargs(args)
    for file in glob.iglob(f"{directory}/*"):
        if ".txt" in file:
            pass
        else:
            edited_lines = get_lines(file, '\t', 4)
            statement = write_new_file(file, edited_lines)
            print(statement)
    print(f"All annotation files have been rewritten :) ")


main()

#
#
##############################################################################################################







