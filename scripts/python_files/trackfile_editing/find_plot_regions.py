"""
Kenny P. Callahan

9 January 2020

find_plot_regions.py

Python 3.8.5



Docstring
"""

###########################################################################################
#
#    Importables

import sys

#
#
###########################################################################################
#
#     Functions

def check_sysargs(args):
    
    assert type(args) == list, "args should have type 'list'"
    assert len(args) == 4, "only three system arguments should be given"
    assert ".bg" in args[1], "the first system argument should be a comma separated list of bedgraph files"
    assert ".genome" in args[2], "the second system argument should be a .genome file"
    
    files = args[1].strip().split(',')
    
    for file in files:
        try:
            with open(file, 'r') as f:
                f.close()
        except ValueError:
            print(f"{file} is not a valid file.")
            sys.exit()
    
    try:
        with open(args[2], 'r') as f:
            f.close()
    except ValueError:
        [print(f"{args[2]} is not a valid file.")]
        sys.exit()
        
    if ".txt" not in args[3]:
        outfile = f"{args[3]}.txt"
    else:
        outfile = args[3]
        
    return files, args[2], outfile

def update_dictionary(dictionary,
                      line, 
                      key = 0, 
                      removal = -1):
    
    assert type(dictionary) == dict, "dictionary should be of type 'dictionary'"
    assert type(line) == list, "line should be of type 'list'"
    assert type(key) == int and key >= 0, "the key position should be a positive integer"
    assert type(removal) == int and removal < 0, "removal should be a negative integer describing \n the number of rightmost coloumns to be removed"
        
    if line[key] in dictionary.keys():
        
        newkey = line[key]
        
        del line[key]
        
        dictionary[newkey].append(tuple(line[:removal]))
    
    else:
        
        newkey = line[key]
        
        del line[key]
        
        dictionary[newkey] = [line[:removal]]
        
def get_peaks(file_list,
              delimiter):
    
    
    file_dictionary = {}
    
    for file in file_list:
        
        file_dictionary[file] = {}
        
        with open(file, 'r') as f:
            
            for line in f:
                
                line = line.strip().split(delimiter)
                
                update_dictionary(file_dictionary[file],
                                  line)
                
            f.close()
    return file_dictionary

def format_numbers(file_dictionary):
    
    for file in file_dictionary.keys():
        
        for key, value in file_dictionary[file].items():
            
            file_dictionary[file][key] = [tuple([int(item) for item in value[i]])
                                           for i in range(len(value))]

def compare_regions(region_1,
                    region_2,
                    end_distance,
                    max_length):

    if  region_1[0] >= region_2[0] and region_1[0] <= region_2[1] and region_1[1] >= region_2[0] and region_1[1] <= region_2[1]:
        return 'pass'
                        
    elif region_1[0] >= region_2[0] and region_1[0] <= region_2[1] and region_1[1] > region_2[1]:
        beginning = region_2[0]
        ending = region_1[1] + end_distance
        if beginning < 0:
            beginning = 0
        if ending > max_length:
            ending = max_length
        return (beginning, ending)
                            
    elif region_1[0] < region_2[0] and region_1[1] >= region_2[0] and region_1[1] <= region_2[1]:
        beginning = region_1[0] - end_distance
        ending = region_2[1]
        if beginning < 0:
            beginning = 0
        if ending > max_length:
            ending = max_length
        return (beginning, ending)
                            
    elif region_1[0] < region_2[0] and region_1[0] < region_2[1] and region_1[1] > region_2[0] and region_1[1] > region_2[1]:
        beginning = region_1[0] - end_distance
        ending = region_1[1] + end_distance
        if beginning < 0:
            beginning = 0
        if ending > max_length:
            ending = max_length
        return (beginning, ending)
    
    else:
        return 'break'
    
def find_regions(file_dictionary,
                 end_distances,
                 max_lengths):
    
    regions_list = []
    
    files = list(file_dictionary.keys())
    
    for file_1 in files:
        
        regions = {}
    
        for key, value in file_dictionary[file_1].items():

            regions[key] = []

            for reg in value:

                holder = (reg[0] - end_distances[key], reg[1] + end_distances[key])

                if holder[0] < 0:
                    holder = (0, holder[1])

                for file in files:

                    if file != file_1:
                        try:
                            for item in file_dictionary[file][key]:
                                next_reg = compare_regions(item, 
                                                           holder, 
                                                           end_distances[key],
                                                           max_lengths[key])

                                if next_reg == 'pass':
                                    pass
                                elif next_reg == 'break':
                                    break
                                else:
                                    holder = next_reg
                        except:
                            pass
                if len(regions[key]) == 0:

                    regions[key].append(holder)
                else:
                    next_reg = compare_regions(holder,
                                               regions[key][-1],
                                               end_distances[key],
                                               max_lengths[key])
                    if next_reg == 'pass':
                        pass
                    elif next_reg == 'break':
                        regions[key].append(holder)
                    else:
                        regions[key][-1] = next_reg
        regions_list.append(regions)
    return regions_list

def get_chrom_lengths(length_genome,
                      delimiter):
    
    dictionary = {}
    
    with open(length_genome, 'r') as f:
        
        for line in f:
            
            line = line.strip().split(delimiter)
            
            dictionary[line[0]] = int(line[1])

    return dictionary



def make_end_distances(chrom_length_dist,
                      factor = 0.01):
    
    factors = {'100000'  : 0.1,
               '1000000' : 0.05,
               '10000000': 0.01,
               '100000000' : 0.005,
               '1000000000' : 0.001}

    end_distances = {}
    
    for key, value in chrom_length_dist.items():
        
        facts = factors.keys()

        facts = [int(f) for f in facts]
        count=0
        for f in facts:
            if value < f and count == 0:
                print(value)
                factor = factors[str(f)]
                print(factor)
                count+=1

        end_distances[key] = value * factor
    
    return end_distances

def merge_all_regions(regions_list):
    
    lengths = [(len(region), region) for region in regions_list]
    
    lengths.sort(key=lambda l: l[0])
    
    lengths = lengths[::-1]
    
    lengths = [lengths[i][1] for i in range(len(lengths))]
    
    regions = lengths[0]
    
    del lengths[0]
    
    for key in regions.keys():
        
        for reg in lengths:
            
            try:
                regions[key] += reg[key]
            except:
                pass
            
        regions[key].sort(key=lambda s: s[0])
        
    return regions

def clean_merged_regions(merged_dictionary, 
                         max_lengths):
    
    cleaned_regions = {}
    
    for key, value in merged_dictionary.items():
        
        count = 0
        holder = (0,0)
        cleaned_regions[key] = []
        for reg in value:
            if count == 0:
                cleaned_regions[key].append(reg)
                count+=1
            else:
                next_reg = compare_regions(cleaned_regions[key][-1],
                                           reg,
                                           0,
                                           max_lengths[key])
                
                if next_reg == "pass":
                    pass
                elif next_reg == "break":
                    cleaned_regions[key].append(reg)
                else:
                    if next_reg != cleaned_regions[key][-1]:
                        next_c = compare_regions(reg,
                                                 cleaned_regions[key][-1],
                                                 0,
                                                 max_lengths[key])
                        if next_c == "pass":
                            pass
                        else:
                            cleaned_regions[key][-1] = next_c
    return cleaned_regions

def get_lines(cleaned_regions):
    
    lines = []
    
    for key, value in cleaned_regions.items():
        
        for reg in value:
            line = f"{key}\t{int(reg[0])}\t{int(reg[1])}\n"
            lines.append(line)
            
    return lines

def write_regions_file(lines, outfilename):
    
    with open(outfilename, 'w') as f:
        f.writelines(lines)
        f.close()
        
#
#
###########################################################################################
#
#        main() function


def main():
    
    args = sys.argv
    
    file_list, chromfile, outfile = check_sysargs(args)
    
    chrom_lengths = get_chrom_lengths(chromfile, '\t')
    
    end_distance = make_end_distances(chrom_lengths)
    
    peaks_dictionary = get_peaks(file_list, '\t')
    
    format_numbers(peaks_dictionary)
    
    regions_by_file = find_regions(peaks_dictionary,
                                   end_distance,
                                   chrom_lengths)
    
    merged_regions_dict = merge_all_regions(regions_by_file)
    
    cleaned_regions_merged = clean_merged_regions(merged_regions_dict,
                                                  chrom_lengths)
    
    lines_to_write = get_lines(cleaned_regions_merged)
    
    write_regions_file(lines_to_write, outfile)

main()
    
#
#
###########################################################################################
#
#
