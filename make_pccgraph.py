# make_pccgraph.phy
#
# This program will take as inputs two text files and two spreadsheets.  It will produce
#   modified versions of the spreadsheets that are in turn inputs for another downstream process.
#   - The downstream process creates map files for PCCGraph to display.
#   - The input text files are a list of FM Keywords.  They will be used to filter rows of the spreadsheets.
#   - One of the input spreadsheets contains system signals.  This program must select rows that contain
#     FM Keywords.  These rows often contain pairs (defined, used), and the program must also
#     combine (flatten) those rows.
#   - The new list of signals will contain the functions that consume the signals.  The list of functions
#     from this will be used to filter the parameters spreadsheet.

# Approach:
# 1) Build list of selected (SET) FM Keywords, by reading FMM Output report and Placeholder list.
# 2) Read, filter and flatten master_signals spreadsheet, collect functions.
# 3) Read and filter master_paramters spreadsheet.

import sys
import os

keyword_files = ['Load 5.0 FMM Output Report.txt','Placeholder List.txt']
fm_keywords = []
fm_set_flag = False
fm_set_string = 'FM SELECTION (SET)'
fm_unset_string = 'FM SELECTION (NOT SET)'

for keyword_file_name in keyword_files:
    try:
        keyword_file = open(keyword_file_name)
    except IOError:
        exit(status_file_name + " does not exist.")

    lines = keyword_file.readlines()

    for line in lines:
        line = line.strip()
        if len(line) == 0:
            continue
        if line.find(fm_set_string) > -1:
            fm_set_flag = True
            continue
        if line.find(fm_unset_string) > -1:
            fm_set_flag = False
            continue
        if fm_set_flag:
            fm_keywords.append(line)





