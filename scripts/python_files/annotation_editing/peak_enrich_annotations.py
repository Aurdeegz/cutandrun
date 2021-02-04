"""
Kenneth P. Callahan

26 January 2021

==============================================================================================================
Python 3.8.5

peak_enrich_annotations.py
==============================================================================================================

A docstring goes here.

"""

import sys
import os
import subprocess
import glob


filetype_formatting={"narrowPeak" : {'0' : 'chrom',
                                     '1' : 'chromStart',
                                     '2' : 'chromEnd',
                                     '6' : 'signalValue',
                                     '7' : 'pValue (-log base 10)',
                                     '8' : 'qValue (-log base 10)',
                                     '9' : 'peak'},
                     "xls" : {'0' : 'chrom',
                              '1' : 'chromStart',
                              '2' : 'chromEnd',
                              '5' : 'peak_position',
                              '6' : 'pValue (-log base 10)',
                              '7' : 'fold_enrichment',
                              '8' : 'qValue (-log base 10)'},
                     "bed" : {'0' : 'chrom',
                               '1' : 'chromStart',
                               '2' : 'chromEnd',
                               '3' : 'identifier',
                               '5' : 'strandedness',
                               '6' : 'annotation_type'} }

title_folder_formats = ["_exp_", "_exper_", "_experiment_", "_rep_", "_replicate_", "_enrich_", "_enrichment_"]

def get_exper_title(directory,
                    title_format_list):
    """

    """
    split_dirpath = directory.split('/')
    for t in title_format_list:
        for fold in split_dirpath:
            if t in fold:
                return fold
    return "No title folder found"

def get_bound_keys(formatting_dictionary,
                   file_type):
    """

    """
    for key, value in formatting_dictionary[file_type].items():
        if value == "chrom":
            chrom_key = int(key)
        elif value == "chromStart":
            start_key = int(key)
        elif value == "chromEnd":
            end_key = int(key)
    return chrom_key, start_key, end_key

def compare_regions(peak_chrom,
                    peak_start,
                    peak_end,
                    region_chrom,
                    region_start,
                    region_end):
    """
    CONDITIONS TO TAKE:
    peak end and region start overlap
    peak start and region end overlap
    peak start and peak end between region start and region end
    region start and region end between peak start and peak end

    Conditions to throw:
    peak start and peak end outside region_start and region_end
    """
    if peak_chrom != region_chrom:
        return 'continue'
    elif peak_start <= region_end and peak_end >= region_end:
        return True
    elif peak_start <= region_start and peak_end >= region_start:
        return True
    elif peak_start >= region_start and peak_end <= region_end:
        return True
    elif peak_start <= region_start and peak_end >= region_end:
        return True
    elif peak_start <= region_start and peak_end <= region_end:
        return 'break'
    else:
        return False


def check_line_annotes(annot_file,
                       annot_extension,
                       peak_chrom,
                       peak_start,
                       peak_end,
                       delimiter,
                       formatting_dictionary,
                       region_wiggle = 100):
    """

    """

    #
    true_compared = []
    #
    reg_chrom_key, reg_start_key, reg_end_key = get_bound_keys(formatting_dictionary,
                                                               annot_extension)
    #
    with open(annot_file, 'r') as a:
        #
        for line in a:
            #
            split_line = line.strip().split(delimiter)
            #
            region_chrom = split_line[reg_chrom_key]
            region_start = int(split_line[reg_start_key]) - region_wiggle
            region_end = int(split_line[reg_end_key]) + region_wiggle
            #
            compare = compare_regions(peak_chrom, peak_start, peak_end,
                                      region_chrom, region_start, region_end)
            #
            if compare == True:
                newline = format_line(formatting_dictionary, annot_extension,
                                      split_line, delimiter)
                print(newline)
                true_compared.append(newline)
            #
            elif compare == 'continue':
                continue
            #
            elif compare == 'break':
                break
        #
        a.close()
    #
    return true_compared

def make_compared_lines(true_compared_lines,
                        title,
                        peak_file_line):
    """

    """
    return [(line, title, peak_file_line) for line in true_compared_lines]

def format_line(formatting_dictionary,
                file_extension,
                a_split_line,
                delimiter):
    """

    """
    #
    new_line =""
    #
    initializer = True
    #
    indice = [int(key) for key in formatting_dictionary[file_extension].keys() ]
    indice = sorted(indice)
    #
    newline = f"{a_split_line[indice[0]]}"
    #
    for index in indice:
        if index == 0:
            continue
        else:
            newline = f"{newline}{delimiter}{a_split_line[index]}"
    #
    newline = f"{newline}\n"
    #
    return newline

def make_header(formatting_dictionary,
                file_type,
                delimiter):
    """

    """
    positions = [int(key) for key in formatting_dictionary[file_type].keys()]
    positions = sorted(positions)
    newline = f"{formatting_dictionary[file_type][str(positions[0])]}"
    del positions[0]
    for position in positions:
        newline = f"{newline}{delimiter}{formatting_dictionary[file_type][str(position)]}"
    newline = f"{newline}\n"
    return newline

def get_enrich_annote_lines(filtered_file_dir,
                            annot_dir,
                            formatting_dictionary,
                            title_format_list,
                            delimiter,
                            file_type = "xls"):
    #
    title = get_exper_title(filtered_file_dir, title_format_list)
    #
    if title == "No title folder found":
        raise ValueError(f"Unable to extract a title from the folderpath.")
    #
    header = make_header(formatting_dictionary, file_type, delimiter)
    #
    annot_header = ""
    #
    comp_holder = []
    #
    comparisons = {}
    #
    for file in glob.iglob(f"{filtered_file_dir}/*.{file_type}"):
        #
        print(f"Finding annoted regions that overlap with peaks from {file}\n")
        peak_chrom_key, peak_start_key, peak_end_key = get_bound_keys(formatting_dictionary, file_type)
        #
        file_comparisons = []
        with open(file, 'r') as f:
            #
            for l in f:
                #
                splitted = l.strip().split(delimiter)
                #
                reformed_line = format_line(formatting_dictionary, file_type,
                                            splitted, delimiter)
                #
                peak_chrom = splitted[peak_chrom_key]
                peak_start = int(splitted[peak_start_key])
                peak_end = int(splitted[peak_end_key])
                #
                for annot_file in glob.iglob(f"{annot_dir}/*"):
                    #
                    annot_extension = annot_file.split('.')[-1]
                    #
                    if annot_header == "":
                        annot_header = make_header(formatting_dictionary, annot_extension, delimiter)
                    #
                    if annot_extension == 'txt' or "region" in annot_file:
                        continue
                    #
                    new_comparisons = check_line_annotes(annot_file,
                                                         annot_extension,
                                                         peak_chrom,
                                                         peak_start,
                                                         peak_end,
                                                         delimiter,
                                                         formatting_dictionary)
                    #
                    new_comparisons = make_compared_lines(new_comparisons,
                                                          title,
                                                          reformed_line)
                    #
                    file_comparisons += new_comparisons
            #
            f.close()
        headers = (annot_header, "exp_title", header)
        comparisons[file] = headers, file_comparisons
    return comparisons

def make_empty(formatting_dictionary,
               file_type,
               delimiter):
    """

    """
    delim_num = len(list(formatting_dictionary[file_type].keys())) - 1
    newline = f"-"
    for _ in range(delim_num):
        newline = f"{newline}{delimiter}-"
    newline = f"{newline}\n"
    return newline

def merge_comparison_lists(comparisons_list,
                           extensions_list,
                           formatting_dictionary,
                           delimiter):
    """
    """
    outstrs = []
    seen = []
    #
    listcount_1 = 0
    for list_1 in comparisons_list:
        #
        for sublist_1 in list_1:
            #
            l1_outstr = []
            #
            if sublist_1[0] not in seen:
                seen.append(sublist_1[0])
                l1_outstr.append(sublist_1[0])
                l1_outstr.append([list(sublist_1)[1:]])
            #
            elif sublist_1[0] in seen:
                continue
            #
            listcount_2 = 0
            for list_2 in comparisons_list:
                #
                if list_1 == list_2:
                    continue
                #
                else:
                    #
                    found = False
                    for sublist_2 in list_2:
                        if sublist_1[0] == sublist_2[0]:
                            found = True
                            l1_outstr[1].append(list(sublist_2)[1:])
                            break
                    if found == False:
                        title = list_2[0][1]
                        newline = make_empty(formatting_dictionary,
                                             extensions_list[listcount_2],
                                             delimiter)
                        l1_outstr[1].append([title, newline])
                listcount_2 += 1
            outstrs += l1_outstr
        listcount_1 += 1
    del seen
    return outstrs


def merge_headers_lists(headers_list, delimiter):
    """
    """
    outstr = []
    for head in headers_list:
        if head[0].strip() in outstr:
            for i in range(1,len(head)):
                outstr.append(head[i].strip())
        else:
            for i in range(len(head)):
                outstr.append(head[i].strip())
    newline = f"{outstr[0]}"
    del outstr[0]
    for string in outstr:
        newline = f"{newline}{delimiter}{string}"
    del outstr
    newline = f"{newline}\n"
    return newline

def make_a_line(an_annote,
                lines_lists,
                delimiter):
    """

    """
    newline = an_annote.strip()
    newline = f"{newline}"
    ordlist = sorted(lines_lists, key = lambda x: x[0][-1])
    #
    for l in ordlist:
        for string in l:
            st = string.strip()
            newline = f"{newline}{delimiter}{st}"
    newline = f"{newline}\n"
    return newline


def format_comparison_lines(comparison_list,
                            delimiter):
    """

    """
    loop_len = len(comparison_list) // 2
    newlines = [make_a_line(comparison_list[2*i], comparison_list[2*i+1], delimiter) for i in range(loop_len)]
    return newlines


def merge_comparison_dicts(formatting_dictionary,
                           delimiter,
                           *args):
    """

    """
    for arg in args:
        assert type(arg) == dict, f"all arguments should be dictionaries"
    headers = []
    comparisons = []
    extensions = []
    for arg in args:
        for key, value in arg.items():
            headers.append(value[0])
            comparisons.append(value[1])
            extensions.append(key.split('.')[-1])
    headers = merge_headers_lists(headers, delimiter)
    merged_comps = merge_comparison_lists(comparisons,
                                          extensions,
                                          formatting_dictionary,
                                          delimiter)
    merged_comps = format_comparison_lines(merged_comps, delimiter)
    lines = [headers] + merged_comps
    return lines

def get_all_dictionaries(directory,
                         annot_dir,
                         formatting_dictionary,
                         title_format_list,
                         delimiter,
                         file_type = 'xls'):
    """

    """
    dict_list = []
    for folder in glob.iglob(f"{directory}/*"):
        subdirs = glob.glob(f"{folder}/*")
        if f"{folder}/macs3_out" not in subdirs:
            continue
        else:
            subsubdirs = glob.glob(f"{folder}/macs3_out/*")
            if f"{folder}/macs3_out/modified_peakfiles" not in subsubdirs:
                continue
            else:
                new_dict = get_enrich_annote_lines(f"{folder}/macs3_out/modified_peakfiles",
                                                   annot_dir,
                                                   formatting_dictionary,
                                                   title_format_list,
                                                   delimiter,
                                                   file_type = file_type)
                dict_list.append(new_dict)
    if dict_list == []:
        raise ValueError(f"Modified macs3 output files could not be found in {directory} with extension {file_type}")
    else:
        return dict_list

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
    args[0]   :   peak_enrich_annotations.py
    args[1]   :   directory to the experimental files.
    args[2]   :   directory to annotation files
    OPTIONAL
    args[3]   :   delimiter  default \t
    args[4]   :   file type, default xls
    """
    #
    assert 3 <= len(args) <= 5, "Three or four system arguments should be given"
    #
    is_dir1_good = check_dir(args[1])
    is_dir2_good = check_dir(args[2])
    if is_dir1_good == None or is_dir1_good == False:
        raise ValueError(f"{args[1]} has empty folders. Please delete them and try again.")
    if is_dir2_good == None or is_dir2_good == False:
        raise ValueError(f"{args[2]} has empty folders. Please delete them and try again.")
    if len(args) == 4:
        assert arg[3] in ['\t', ':', ",", ';', '|','-']
        return args[1], args[2], args[3]
    elif len(args) == 5:
        assert arg[3] in ['\t', ':', ",", ';', '|','-']
        assert arg[4] in filetype_formatting.keys(), "Invalid filetype given"
        return args[1], args[2], '\t', arg[4]
    else:
        return args[1], args[2], '\t'

def get_fields_list(annot_dir):
    """

    """
    annot_dir_files = glob.glob(f"{annot_dir}/*")
    if f"{annot_dir}/fields.txt" not in annot_dir_files:
        return False
    else:
        with open(f"{annot_dir}/fields.txt", 'r') as f:
            field_list = [line.strip() for line in f]
            f.close()
    return field_list

def filter_by_annot(annot_dir,
                    peak_dir,
                    lines_to_write):
    """

    """
    os.mkdir(f"{peak_dir}")
    with open(f"{peak_dir}/temp.txt", 'w') as f:
        f.writelines(lines_to_write[1:])
        f.close()
    header = lines_to_write[0]

    subprocess.call(f"sort -k 1,1 -k 2,2n {peak_dir}/temp.txt > {peak_dir}/temp_sorted.txt", shell=True)
    subprocess.call(f'echo "{header}" > {peak_dir}/all_annotes_by_peak.txt', shell = True)
    subprocess.call(f"cat {peak_dir}/all_annotes_by_peak.txt {peak_dir}/temp_sorted.txt > {peak_dir}/all_annotes_by_peak_sorted.xls", shell = True)
    subprocess.call(f"rm {peak_dir}/temp.txt",shell = True)
#    subprocess.call(f"rm {peak_dir}/temp_sorted.txt",shell = True)
#    subprocess.call(f"rm {peak_dir}/all_annotes_by_peak.txt",shell = True)

    field_list = get_fields_list(annot_dir)
    if field_list == False:
        subprocess.call(f"rm {peak_dir}/temp_sorted.txt",shell = True)
        subprocess.call(f"rm {peak_dir}/all_annotes_by_peak.txt",shell = True)
        return f"Filtered peak regions and their annotations are written in {peak_dir}/all_annotes_by_peak_sorted.xls"
    else:
        for field in field_list:
            subprocess.call(f"""awk 'BEGIN{{OFS="\t"}}{{if ($6 == "{field}") {{ print }} }}' {peak_dir}/temp_sorted.txt > {peak_dir}/temp_{field}_sorted.txt""", shell = True)
            subprocess.call(f"cat {peak_dir}/all_annotes_by_peak.txt {peak_dir}/temp_{field}_sorted.txt > {peak_dir}/field_{field}_by_peak_sorted.xls", shell = True)
            subprocess.call(f"rm {peak_dir}/temp_{field}_sorted.txt", shell = True)
        subprocess.call(f"rm {peak_dir}/temp_sorted.txt",shell = True)
        subprocess.call(f"rm {peak_dir}/all_annotes_by_peak.txt",shell = True)
        return f"Filtered peak regions and their annotations are written in {peak_dir} as .xls files"


def main():
    """
    """
    #
    args = sys.argv
    #
    if len(args) == 4 or len(args) == 3:
        exp_dir, annot_dir, delim = check_sysargs(args)
        dict_list = get_all_dictionaries(exp_dir,
                                         annot_dir,
                                         filetype_formatting,
                                         title_folder_formats,
                                         delim)
        newlines = merge_comparison_dicts(filetype_formatting,
                                          delim, *dict_list)

    elif len(args) == 5:
        exp_dir, annot_dir, delim, f_type = check_sysargs(args)
        dict_list = get_all_dictionaries(directory,
                                         annot_dir,
                                         filetype_formatting,
                                         title_folder_formats,
                                         delim,
                                         file_type = f_type)

        newlines = merge_comparison_dicts(filetype_formatting,
                                          delim,
                                          *dict_list)


    printer = filter_by_annot(annot_dir, f"{exp_dir}/peak_annotations", newlines)
    print(printer)
#    os.mkdir(f"{exp_dir}/peak_annotations")
#    with open(f"{exp_dir}/peak_annotations/temp.txt", 'w') as f:
#        f.writelines(newlines[1:])
#        f.close()

#    subprocess.call(f"sort -k 1,1 -k 2,2n {exp_dir}/peak_annotations/temp.txt > {exp_dir}/peak_annotations/temp_sorted.txt", shell=True)
#    subprocess.call(f'echo "{newlines[0]}" > {exp_dir}/peak_annotations/all_annotes_by_peak.txt', shell = True)
#    subprocess.call(f"cat {exp_dir}/peak_annotations/all_annotes_by_peak.txt {exp_dir}/peak_annotations/temp_sorted.txt > {exp_dir}/peak_annotations/all_annotes_by_peak_sorted.xls", shell = True)
#    subprocess.call(f"rm {exp_dir}/peak_annotations/temp.txt",shell = True)
#    subprocess.call(f"rm {exp_dir}/peak_annotations/temp_sorted.txt",shell = True)
#    subprocess.call(f"rm {exp_dir}/peak_annotations/all_annotes_by_peak.txt",shell = True)
#    print('done')

main()

