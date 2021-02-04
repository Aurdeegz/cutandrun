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

allowed_extensions = ["narrowPeak", "xls"]

#
#
##########################################################################################################
#
#           Functions

def filter_line_np(line,
                   value_column,
                   delimiter,
                   qvalue = 0.01,
                   pvalue = None):
    """

    """
    if line[0] == "#" or line == "\n":
        return None
    #
    line = line.split(delimiter)
    #
    col = int(value_column - 1)
    #
    if "pvalue" in line[col] or "qvalue" in line[col]:
        return None

    if pvalue != None:
        log_trans = -math.log(pvalue)
    #
    else:
        log_trans = -math.log(qvalue)
    #
    if float(line[col]) >= log_trans:
        #
        newline = f"{line[0]}"
        del line[0]
        #
        for column in line:
            newline = f"{newline}\t{column}"
        return newline
    #
    else:
        return None

def filter_line_xls(line,
                    value_column,
                    delimiter,
                    qvalue = 0.01,
                    pvalue = None):
    """

    """
    if line[0] == "#" or line == "\n":
        return None
    #
    line = line.split(delimiter)
    #
    col = value_column - 1
    #
    if "pvalue" in line[col] or "qvalue" in line[col]:
        return None

    if pvalue != None:
        log_trans = -math.log(pvalue)
    #
    else:
        log_trans = -math.log(qvalue)
    #
    if float(line[col]) >= log_trans:
        #
        newline = f"{line[0]}"
        del line[0]
        #
        for column in line:
            newline = f"{newline}\t{column}"
        return newline
    #
    else:
        return None


def filter_all_lines(file,
                     delimiter,
                     qvalue = 0.01,
                     pvalue = None,
                     ext = "narrowPeak"):
    """

    """
    #
    with open(file, 'r') as f:
        #
        if ext == "narrowPeak" and pvalue == None:
            #
            newlines = [filter_line_np(line,
                                       9,
                                       delimiter,
                                       qvalue = qvalue,
                                       pvalue = pvalue) for line in f if line != "\n"]
            #
            newlines = [l for l in newlines if l != None]
        #
        elif ext == "narrowPeak" and pvalue != None:
            #
            newlines = [filter_line_np(line,
                                       8,
                                       delimiter,
                                       qvalue = qvalue,
                                       pvalue = pvalue) for line in f if line != "\n"]
            #
            newlines = [l for l in newlines if l != None]
        #
        elif ext == "xls" and pvalue == None:
            #
            newlines = [filter_line_xls(line,
                                        9,
                                        delimiter,
                                        qvalue = qvalue,
                                        pvalue = pvalue) for line in f if line[0] != "#" or line != "\n"]
            #
            newlines = [l for l in newlines if l != None]
            #
            newlines = newlines[1:]
        #
        elif ext == "xls" and pvalue != None:
            newlines = [filter_line_xls(line,
                                        7,
                                        qvalue = qvalue,
                                        pvalue = pvalue) for line in f if line[0] != "#" or line != "\n"]
            #
            newlines = [l for l in newlines if l != None]
            #
            newlines = newlines[1:]
        #
        else:
            raise ValueError(f"{ext} and {pvalue} together are invalid.")
        #
        f.close()
    #
    return newlines

def filter_macs3_outputs(macs3_dir,
                         desired_extensions,
                         delimiter,
                         qvalue = 0.01,
                         pvalue = None):
    """

    """
    #
    os.mkdir(f"{macs3_dir}/unmodified_outfiles")
    os.mkdir(f"{macs3_dir}/modified_peakfiles")
    #
    for file in glob.iglob(f"{macs3_dir}/*"):
        #
        if f"{file}" == f"{macs3_dir}/unmodified_outfiles" or f"{file}" == f"{macs3_dir}/modified_peakfiles":
            continue
        #
        file_extension = file.split(".")[-1]
        #
        file_name = file.split('.')[0].split('/')[-1]
        #
        if file_extension in desired_extensions:
            #
            new_lines = filter_all_lines(file,
                                         delimiter,
                                         qvalue = qvalue,
                                         pvalue = pvalue,
                                         ext = file_extension)
            # Write the new file
            if qvalue != None and pvalue == None:
                #
                with open(f"{macs3_dir}/modified_peakfiles/q_filtered_peaks.{file_extension}", 'w') as f:
                    f.writelines(new_lines)
                    f.close()
            #
            elif qvalue == None and pvalue != None:
                #
                with open(f"{macs3_dir}/modified_peakfiles/p_filtered_peaks.{file_extension}", 'w') as f:
                    f.writelines(new_lines)
                    f.close()
            # Move the file using os.rename()
            os.rename(f"{file}", f"{macs3_dir}/unmodified_outfiles/{file_name}.{file_extension}")
        else:
            # Move the file, not intersting to us.
            os.rename(f"{file}", f"{macs3_dir}/unmodified_outfiles/{file_name}.{file_extension}")



def filter_all_files(directory,
                     desired_extensions,
                     delimiter,
                     qvalue = 0.01,
                     pvalue = None):
    """

    """
    #
    for folder in glob.iglob(f"{directory}/*"):
        #
        for subfold in glob.iglob(f"{folder}/*"):
            #
            if "macs3" in subfold.lower():
                #
                filter_macs3_outputs(subfold,
                                     allowed_extensions,
                                     delimiter,
                                     qvalue = qvalue,
                                     pvalue = pvalue)
                continue

#
#
##########################################################################################################
#
#      System Argument Checking Functions

def check_dir(directory):
    """

    """
    #
    if len(directory.split('.')) == 1:
        #
        dirlist = glob.glob(f"{directory}/*")
        #
        if len(dirlist) == 0:
            #
            return False
        #
        else:
            #
            for fold in dirlist:
                #
                checker = check_dir(fold)
                #
                if checker == None:
                    continue
                #
                elif checker == False:
                    return False
        #
        return True

def check_sysargs(args):
    """
    args[0]   :    filter_narrowpeak_qvalue.py
    args[1]   :    directory


    OPTIONAL

    args[2]   : qvalue; float, None or default (if using pvalue, default is q = 0.01)
    args[3]   : pvalue; float, None or default (if using qvalue, default is p = None)
    args[4]   : delimiter; default is '\t'

    """
    #
    assert len(args) <= 5, f"a maximum of five system arguments are allowed."
    #
    if len(args) == 2:
        #
        is_directory_good = check_dir(args[1])
        #
        if is_directory_good == None or is_directory_good == False:
            raise ValueError(f"{args[1]} has empty folders. Please delete them and try again.")
        #
        else:
            return args[1], 0.01, None, '\t'

    #
    elif len(args) == 3:
        #
        is_directory_good = check_dir(args[1])
        #
        if is_directory_good == None or is_directory_good == False:
             raise ValueError(f"{args[1]} has empty folders. Please delete them and try again.")
        #
        try:
            qvalue = float(args[2])
        #
        except:
            raise ValueError(f"{args[2]} (qvalue) should be a floating point number.")
        #
        return args[1], qvalue, None, '\t'

    #
    elif len(args) == 4:
        #
        is_directory_good = check_dir(args[1])
        #
        if is_directory_good == None or is_directory_good == False:
            raise ValueError(f"{args[1]} has empty folders. Please delete them and try again.")
        #
        try:
            pvalue = float(args[3])
        #
        except:
            #
            if pvalue.lower() == 'none':
                pvalue = None
            #
            else:
                raise ValueError(f"{args[3]} (pvalue) should be a floating point number.")
        #
        if args[2].lower() != 'none' and pvalue != None:
            print(f"A valid pvalue was given, but the qvalue was not set to None... Setting qvalue = None")
            qvalue = None
        #
        elif args[1].lower() != 'none' and pvalue == None:
            #
            try:
                qvalue = float(args[2])
            #
            except:
                raise ValueError(f"{args[2]} (qvalue) should be a floating point number.")
        #
        else:
            qvalue = None
        #
        return args[1], qvalue, pvalue, '\t'

    #
    elif len(args) == 5:
        #
        is_directory_good = check_dir(args[1])
        #
        if is_directory_good == None or is_directory_good == False:
            raise ValueError(f"{args[1]} has empty folders. Please delete them and try again.")
        #
        try:
            pvalue = float(args[3])
        #
        except:
            #
            if pvalue.lower() == 'none':
                pvalue = None
            #
            else:
                raise ValueError(f"{args[3]} (pvalue) should be a floating point number.")
        #
        if args[2].lower() != 'none' and pvalue != None:
            print(f"A valid pvalue was given, but the qvalue was not set to None... Setting qvalue = None")
            qvalue = None
        #
        elif args[1].lower() != 'none' and pvalue == None:
            #
            try:
                qvalue = float(args[2])
            #
            except:
                raise ValueError(f"{args[2]} (qvalue) should be a floating point number.")
        #
        else:
            qvalue = None
        #
        assert args[4] in [",", ".", "\t", ";", ":", "|", "-", "_"], f"invalid delimiter given: {args[4]}"
        #
        return args[1], qvalue, pvalue, args[4]

#
#
##########################################################################################################
#
#        main() function

def main():
    """

    """
    #
    args = sys.argv
    #
    directory, qvalue, pvalue, delimiter = check_sysargs(args)
    #
    filter_all_files(directory,
                     allowed_extensions,
                     delimiter,
                     qvalue = qvalue,
                     pvalue = pvalue)
    #
    print("done")

main()

#
#
##########################################################################################################
