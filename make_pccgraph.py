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
import xlrd
from xlrd.sheet import ctype_text
import xlwt

keyword_files = ['Placeholder List.txt']
# keyword_files = ['Load 5.0 FMM Output Report.txt','Placeholder List.txt']
signal_file = 'master_signals.xls'
signal_file_out = 'master_signals_out.xls'
params_file = 'master_params.xls'
params_file_out = 'master_params_out.xls'

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

book = xlrd.open_workbook(signal_file)
sheet = book.sheet_by_name('HAM Signal')
nrows = sheet.nrows
ncols = sheet.ncols

signals_sheet = [] # An arrary of all signals filtered for fm_keywords
signals_sheet_new = [] # An arrary of all signals remaining after flattenging
llr_signals = {} # A dictionary of rows each signal exists in { signal: [llr_rows]}

# Read signals spreadsheet and keep rows that have legit FM keywords, capture defines in dictionary llr_signals
new_row = 0
header = sheet.row_values(0)
for row in range(1,nrows):
    fm_keyword = sheet.cell(row,1).value
    llr_signal = sheet.cell(row,0).value
    if fm_keyword in fm_keywords:
        signals_sheet.append(sheet.row_values(row))
        if llr_signal in llr_signals:
            llr_signals[llr_signal].append(new_row)
        else:
            llr_signals[llr_signal] = [new_row]
        new_row += 1

# For every llr_signal, look for multiples.  For those whose defined is Input, combine rows.  Write to new_data
for signal in llr_signals:
    row_numbers = llr_signals[signal]
    if len(row_numbers) == 1:
        new_data = signals_sheet[row_numbers[0]]  # Target data exists in row_data[0], only row for this signal
    else:
        new_data = []  # New list to hold cell values we will write to a new row
        used_functions = []  # List to hold the names of all functions that use this signal
        row_data_list = []  # List to hold spreadsheet data for each of the rows being flattened
        for row_number in row_numbers: # Store each of the rows to be flattened in this dictionary
            row_data_list.append(signals_sheet[row_number])

        for row_data in row_data_list:  # Build new combined signal info from each signal based on rules
            for function in row_data[3].split():
                used_functions.append(function) # Collect all the functions that use the signal
            if len(new_data) == 0: # This is first row being processed
                new_data = row_data
            else:
                save_defined = new_data[2] # Preserve previous value of 'defined', even if Input
                if row_data[2].find('Input') > -1:
                    new_data = row_data  # If it is an Input row, we want to use it
                    new_data[2] = save_defined # Restore previous value of 'defined'
                else:
                    new_data[2] = row_data[2] # This is not input row so we want to use its 'defined'

        new_data[3] = ' '.join(used_functions) # Build combined list of defined

    signals_sheet_new.append(new_data)

# Write new Excel workbook for signals
book2 = xlwt.Workbook()
sheet1 = book2.add_sheet('HAM Signal')

for col, heading in enumerate(header):
    sheet1.write(0, col, heading)

for row, data in enumerate(signals_sheet_new):
    for col, cell in enumerate(data):
        sheet1.write(row + 1, col, cell)

book2.save(signal_file_out)

######################################################
fm_keywords = ['SV Turbo Fan Fuel Cooled']

book = xlrd.open_workbook(params_file)
sheet = book.sheet_by_name('HAM Parameter')
nrows = sheet.nrows
ncols = sheet.ncols

params_sheet = [] # An arrary of all parameters filtered for fm_keywords
params_sheet_new = [] # An arrary of all parameters remaining after flattenging
llr_params = {} # A dictionary of rows each parameters exists in { signal: [llr_rows]}

# Read params spreadsheet and keep rows that have legit FM keywords

new_row = 0
header = sheet.row_values(0)
for row in range(1,nrows):
    fm_keyword = sheet.cell(row,1).value
    llr_param = sheet.cell(row,0).value
    if fm_keyword in fm_keywords:
        params_sheet.append(sheet.row_values(row))
        if llr_param in llr_params:
            llr_params[llr_param].append(new_row)
        else:
            llr_params[llr_param] = [new_row]
        new_row += 1

# For every llr_param, look for multiples.  Combine rows.  Write to new_data
for param in llr_params:
    row_numbers = llr_params[param]
    if len(row_numbers) == 1:
        new_data = params_sheet[row_numbers[0]]  # Target data exists in row_data[0], only row for this signal
    else:
        pass # Flattening ignored for now because requirements changed
        new_data = []  # New list to hold cell values we will write to a new row
        used_functions = []  # List to hold the names of all functions that use this signal
        row_data_list = []  # List to hold spreadsheet data for each of the rows being flattened
        for row_number in row_numbers: # Store each of the rows to be flattened in this dictionary
            row_data_list.append(params_sheet[row_number])
        for row_data in row_data_list:  # Build new combined parameter info from each parameter based on rules
            for function in row_data[2].split():
                used_functions.append(function) # Collect all the functions that use the signal
            new_data = row_data
            new_data[2] = ' '.join(used_functions) # Build combined list of defined

    params_sheet_new.append(new_data)

# Write new Excel workbook for parameters
book2 = xlwt.Workbook()
sheet1 = book2.add_sheet('HAM Parameter')

for col, heading in enumerate(header):
    sheet1.write(0, col, heading)

for row, data in enumerate(params_sheet_new):
    for col, cell in enumerate(data):
        sheet1.write(row + 1, col, cell)

book2.save(params_file_out)
