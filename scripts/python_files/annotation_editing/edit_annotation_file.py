"""
Kenneth P. Callahan

23 January 2021

==============================================================================================================
Python 3.8.5

edit_annotation_file.py
==============================================================================================================

Doc string area

"""

import sys
import glob

extensions = ["bed", "bed6", "bed12"]

organism_identifiers = ["dmel", "ecol", "hsap", "mmus"]


def check_rna_line(line,
                   delimiter,
                   column):
    """
    assumes that RNA substring is in the file name

    possible types of ids:

    rna-<some_id>_<some_number>.<integer>
    rna-|FlyBase|<identifier>-<sub_id>
    rna-<organism_id>_<identifier>

    in every case, we want the identifiers

    """
    col = column - 1
    line = line.split(delimiter)
    # Check line[3] for id types
    if "|" in line[col]:
        line[col] = line[col].split('|')[-1]
    elif "rna-" in line[col] and "N" in line[col]:
        line[col] = line[col][4:]
    else:
        for id in organism_identifiers:
            if id in line[col].lower():
                line[col] = line[col].lower().split(id)[-1][1:].upper()
                break
    newline = f"{line[0]}"
    del line[0]
    for colmn in line:
        newline = f"{newline}{delimiter}{colmn}"
    return newline

def check_cds_line(line,
                   delimiter,
                   column):
    """
    assumes that exon substring is in the file name
    """
    col = column - 1
    line = line.split(delimiter)
    if "cds-" in line[col] and "N" in line[col]:
        line[col] = line[col][4:]
    elif "id_N" in line[col]:
        line[col] = line[col][3:]
    newline = f"{line[0]}"
    del line[0]
    for colmn in line:
        newline = f"{newline}{delimiter}{colmn}"
    return newline

def check_exon_line(line,
                    delimiter,
                    column):
    """
    assumes that cds substring is in the file name
    """
    col = column - 1
    line = line.split(delimiter)
    if "exon-" in line[col] and "N" in line[col]:
        line[col] = line[col][5:]
    elif "id-N" in line[col]:
        line[col] = line[col][3:]
    else:
        for id in organism_identifiers:
            if id in line[col].lower():
                line[col] = line[col].lower().split(id)[-1][1:].upper()
                break
    newline = f"{line[0]}"
    del line[0]
    for colmn in line:
        newline = f"{newline}{delimiter}{colmn}"
    return newline

def check_gene_line(line,
                    delimiter,
                    column):
    """

    """
    col = column - 1
    line = line.split(delimiter)
    if "gene-" in line[col] and "N" in line[col]:
        line[col] = line[col][5:]
    elif "id-N" in line[col]:
        line[col] = line[col][3:]
    else:
        for id in organism_identifiers:
            if id in line[col].lower():
                line[col] = line[col].lower().split(id)[-1][1:].upper()
    newline = f"{line[0]}"
    del line[0]
    for colmn in line:
        newline = f"{newline}{delimiter}{colmn}"
    return newline

def check_other_line(line,
                     delimiter,
                     column):
    """
    makes no assumptions about the identitiy of the file.
    """
    col = column - 1
    splitter = line.split(delimiter)
    newline = check_rna_line(line, delimiter, column)
    if line != newline:
        return newline
    newline = check_cds_line(line, delimiter, column)
    if line != newline:
        return newline
    newline = check_exon_line(line, delimiter, column)
    if line != newline:
        return newline
    newline = check_gene_line(line, delimiter, column)
    if line != newline:
        return newline
    else:
        if "id-N" in splitter[col]:
            splitter[col] = splitter[col][3:]
            newline = f"{splitter[0]}"
            del splitter[0]
            for colmn in splitter:
                newline = f"{newline}{delimiter}{colmn}"
            return newline
        else:
            return line


def check_sysargs(args):
    """
    args[0]   :   edit_annotation_file.py
    args[1]   :   annotation directory

    rna: split on -, unless |FlyBase| is in the line. If Dmel also in line, then split on _
    cds: split on -
    exon: if exon in line, remove first five characters. If Dmel in line, split on _
    gene: split on _
    region: pass
    """
    assert len(args) == 2, "Only two system arguments should be given"

    for file in glob.iglob(f"{args[1]}/*"):
        if ".txt" in file:
            pass
        else:
            assert ".bed" in file, "The directory should contain bed files."
            try:
                with open(file, 'r') as f:
                    f.close()
            except ValueError:
                print(f"{file} could not be opened...")
                sys.exit()
    return args[1]



def get_lines(file, delimiter, column):
    """

    """
    lines = []
    with open(file, 'r') as f:
        for line in f:
            if "rna" in str(f).lower():
                newline = check_rna_line(line, delimiter, column)
            elif "cds" in str(f).lower():
                newline = check_cds_line(line, delimiter, column)
            elif "exon" in str(f).lower():
                newline = check_exon_line(line, delimiter, column)
            elif "gene" in str(f).lower():
                newline = check_gene_line(line, delimiter, column)
            elif "region" in str(f).lower():
                lines.append(line)
                continue
            else:
                newline = check_other_line(line, delimiter, column)
            lines.append(newline)
        f.close()
    return lines

def write_new_file(file,
                   lines):
    """

    """
    with open(file, 'w') as f:
        f.writelines(lines)
        f.close()

def main():
    """
    """
    #
    args = sys.argv
    #
    directory = check_sysargs(args)
    #
    for file in glob.iglob(f"{directory}/*"):
        #
        if ".txt" in file:
            pass
        else:
            edited_lines = get_lines(file, '\t', 4)
            #
            write_new_file(file, edited_lines)
    print("done")


main()









