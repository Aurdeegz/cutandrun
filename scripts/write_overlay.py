"""
Kenneth P. Callahan
7 January 2020

Writing the ini file.

"""

##########################################################################
#
#           Imports

import sys

#
#
##########################################################################
#
#           Formatting for Bedgraphs and bed files

bedgraph_formatting = {'file' : '',
                       'color' : '',
                       'file_type' : '',
                       'height' : '7',
                       'overlay_previous' : 'default',
                       'min_value' : 'default',
                       'max_value' : 'default',
                       'alpha' : 'default'}

bed_formatting = {'file' : '',
                  'color' : 'default',
                  'filetype' : '',
                  'style' : 'default',
                  'height' : '7',
                  'arrow_interval' : 'default',
                  'all_labels_inside' : 'default',
                  'file_type' : '',
                  'fontsize' : 'default'}

#
#
##########################################################################
#
#           Defaults: colour list and dictionaries

colours = ['red', 'orange', 'green', 'blue', 'indigo', 'violet']

extensions = {'bg' : 'bedgraph',
              'bedgraph' : 'bedgraph',
              'bw' : 'bigwig',
              'bigwig' : 'bigwig',
              'bed' : 'bed'}

bed_keys = {'file' : '',
            'title' : '',
            'height' : '4',
            'overlay_previous' : 'no',
            'fontsize' : '8',
            'orientation' : '',
            'line_width' : '0.5',
            'color' : 'cyan',
            'max_value' : 'auto',
            'min_value' : '0',
            'border_color' : 'black',
            'preferred_name' : 'transcript_name',
            'merge_transcripts' : 'false',
            'labels' : 'true',
            'style' : 'UCSC',
            'display' : 'stacked',
            'max_labels' : '60',
            'global_max_row' : 'false',
            'gene_rows' : '',
            'arrow_interval' : '2',
            'arrowhead_included' : 'false',
            'color_utr' : 'grey',
            'height_utr' : '1',
            'arrow_length' : '',
            'all_labels_inside' : 'true',
            'labels_in_margin': 'false',
            'file_type' : ''}

bgr_keys = {'file' : '',
            'title' : '',
            'height' : '4',
            'overlay_previous' : 'no',
            'orientation' : '',
            'color' : 'purple',
            'alpha' : '1',
            'max_value' : 'auto',
            'min_value' : '0',
            'use_middle' : 'false',
            'show_data_range' : 'true',
            'type' : 'fill',
            'negative_color' : '',
            'nans_to_zero' : 'false',
            'summary_method' : '',
            'number_of_bins' : '700',
            'transform' : 'no',
            'log_pseudocount' : '0',
            'y_axis_values' : 'transformed',
            'second_file' : '',
            'operation' : 'file',
            'grid' : 'false',
            'rastersize' : 'false',
            'file_type' : ''}

#
#
##########################################################################
#
#       Functions

def check_sysargs(args):
    
    """
    Given sys.argsv (arguments passed in from the command line),
    determine whether or not:
    
    -> 
    -> 
    
    The zeroeth value of sys.argv is the file name, thus the program
    evaluates the first and second arguments for a tracksfile and
    an output file, respectively.
    """
    assert type(args) == list, "args must have type 'list'"
    assert len(args) >= 5, "less than five system arguments were given"
    
    #print('\n', args)
    
    args = args[1:]    # First argument is the filename
    
    #print(str(args[-1].lower() != 'false'))
    

    args[-1] = args[-1].split(',')
    for i in range(len(args[-1])):
        try:
            arg[-1][i] = float(arg[-1][i])
        except ValueError:
            print(f"The last system argument should be a comma separated string of max heights, \n\
corresponding to the max heights of the bedgraph file lists to plot.")

    if args[-2].lower() != 'true' and args[-1].lower() != 'false':
        raise ValueError(f"The second to last system argument was neither True nor False")
        sys.exit()
        
    else:
        if args[-2].lower() == 'true':
            args[-2] = True
        else:
            args[-1] = False
        
    if ".ini" not in args[-3]:
        raise ValueError(f"The third to last system argument not a .ini file")
        sys.exit()
        
    for arg in args[:-3]:
        files = arg.split(',')
        for file in files:
            try:
                with open(file, 'r') as f:
                    f.close()
            except ValueError:
                print(f"{file} is not a valid file")
                sys.exit()
    return args[:-3], args[-3], args[-2], args[-1]
        

def get_lines(option_dictionary,
              **kwargs):
    
#    assert type(lines) == list, "lines should be of type 'list'"
    assert type(option_dictionary) == dict, "option_dictionary should be of type 'dict'"
    assert 'file' in kwargs.keys(), "no file is given"
    
    newlines = []
    
    field = kwargs['file'].split('/')
    if len(field) == 1:
        field = f"[{field[0].split('.')[0]}]\n"
    else:
        field = f"[{field[-1].split('.')[0]}]\n"
        
    newlines.append(field)
        
    proposed = kwargs.keys()
    
    for key, value in option_dictionary.items():    
        if key in proposed:
            
            if kwargs[key] == 'default':
                newlines.append(f"{key} = {value}\n")
            else:
                newlines.append(f"{key} = {kwargs[key]}\n")
        else:
            newlines.append(f"#{key} = {value}\n")
    
    newlines.append(f"\n")
    
    return newlines

def get_spacer(height = 0.5):
    
    newlines = [f"[spacer]\n",
                f"# height of space in cm (optional)\n",
                f"height = {height}\n",
                f"\n"]
    
    return newlines

def get_xaxis(fontsize = 10,
              where = ''):
    
    newlines = [f"[x-axis]\n",
                f"fontsize = {fontsize}\n",
                f"#where = {where}\n"
               f"\n"]
    
    return newlines

def make_all_lines(colors,
                   overlay,
                   heights,
                   *args):
    
    assert type(heights) == list, "heights should be of type 'list'"
    assert type(colors) == list, "colors should be of type 'list'"
    for arg in args:
        assert type(arg) == list, "args should be lists of files"
        
    lines = []
    
    lines += get_spacer()
    
    blockcount = 0
    for arg in args:
        divisor = len(arg)
        count = 0
        for file in arg:
            ext = file.split('.')[-1]
            if ext in extensions.keys():
                if extensions[ext] == 'bedgraph' or extensions[ext] == 'bigwig':
                    lines.append(f"\n")
                    
                    bedgraph_formatting['file'] = file
                    bedgraph_formatting['color'] = colors[count]
                    bedgraph_formatting['file_type'] = extensions[ext]
                    
                    if overlay == True and count == 0:
                        
                        bedgraph_formatting['overlay_previous'] = 'default'
                        bedgraph_formatting['alpha'] = 1
                        bedgraph_formatting['max_value'] = heights[blockcount]
                        blockcount += 1
                        
                        lines += get_lines(bgr_keys,
                                           **bedgraph_formatting)
                    elif overlay == True:
                        
                        bedgraph_formatting['overlay_previous'] = 'share-y'
                        bedgraph_formatting['alpha'] = 1- count*(1/divisor)
                        
                        lines += get_lines(bgr_keys,
                                           **bedgraph_formatting)
                    else:
                        lines += get_lines(bgr_keys,
                                           **bedgraph_formatting)
                        
                    count += 1
                elif extensions[ext] == 'bed':
                    
                    bed_formatting['file'] = file
                    bed_formatting['file_type'] = extensions[ext] 
                    
                    lines += get_spacer()
                    
                    lines.append(f"\n")
                    lines += get_lines(bed_keys,
                                       **bed_formatting)
            else:
                print(f"{file} is not recognized file.")
        lines += get_spacer()
    
    lines += get_xaxis()
    
    return lines

#
#
##########################################################################
#
#      main()

def main():
    
    args = sys.argv
    
    filestrings, outfiles, overlay, heights = check_sysargs(args)
    
    file_lists = [files.split(',') for files in filestrings]
    
    lines = make_all_lines(colours,
                           overlay,
                           heights,
                           *file_lists)
    
    with open(outfiles, 'w') as f:
        f.writelines(lines)
        f.close()
    print("")
    print(f"{outfiles} has been written")
    print("")
main()
#
#
##########################################################################
#
#
