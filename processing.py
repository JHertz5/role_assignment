""" functions for assign_grads.py """
# Author: Jukka Hertzog

import csv
import sys
import random
import numpy as np

# TODO make try excepts into functions, returning csv.reader

def extract_table_csv_data(table_filename):
    """
    read table csv file
    extract role list and role preference information for each grad
    """
    print('\treading {}'.format(table_filename))
    try:
        csvfile = open(table_filename,newline='')
    except FileNotFoundError:
        print('Error: {} not found'.format(table_filename))
        sys.exit()

    table_reader = csv.reader(csvfile)

    role_set = set()

    # get roles from table
    next(table_reader) # skip first row
    for row in table_reader:
        if row[0] != '':
            for role_column in [1, 3, 5]: # pick from columns with roles listed
                role_set.add(row[role_column])
    role_list = list(role_set)
    role_list.sort()

    # reset table_reader to start of file
    csvfile.seek(0)
    table_reader = csv.reader(csvfile)

    next(table_reader) # skip first row
    grad_preference_form_data = {}

    for row in table_reader:
        grad = row[0]
        if grad != '':
            grad_preference_form_data[grad] = {
                    'preference_ids'   : [
                        role_list.index(row[1]),
                        role_list.index(row[3]),
                        role_list.index(row[5])
                    ],
                    'preferences'   : [row[1], row[3], row[5]],
                    'comments'      : [row[2], row[4], row[6]]
                }

    return role_list, grad_preference_form_data


def process_clone(clone_title, clone_titles):
    """
    add clone role to clone list and return clone id
    """
    if clone_title not in clone_titles:
        print(clone_title)
        clone_titles.append(clone_title)
        
    clone_id = clone_titles.index(clone_title)
    return clone_id,clone_titles

def extract_role_csv_data(roles_filename):
    """
    read role titles from csv file
    """
    print('\treading {}'.format(roles_filename))
    try:
        csvfile = open(roles_filename,newline='')
    except FileNotFoundError:
        print('Error: {} not found'.format(roles_filename))
        sys.exit()

    role_reader = csv.reader(csvfile)

    clone_str = ' - Placement '
    clone_str_idx1 = -(len(clone_str)+1)

    role_data = {}
    clone_titles = []

    for row_id,row in enumerate(role_reader):
        if row[0] != '':
            role_title = row[0]

            # detect and process ' - Placement n' clones
            if (role_title[clone_str_idx1:-1] == clone_str and 
                                        role_title[-1].isdigit()):
                clone_title = role_title[:clone_str_idx1]
                clone_id,clone_titles = process_clone(clone_title,clone_titles)

            # detect and process '(n)' clones
            elif (role_title[-3] == '(' and role_title[-2].isdigit() and 
                                                    role_title[-1] == ')'):
                clone_title = role_title[:-3]
                clone_id,clone_titles = process_clone(clone_title,clone_titles)

            else:
                clone_id = None
            
            role_data[role_title] = {
                'id' : row_id,
                'clone' : clone_id
            }

    return role_data

def generate_matrix_csv(role_list, grad_preference_form_data, matrix_filename):
    """
    write grad preference matrix into a csv file
    """
    print('\tgenerating {}'.format(matrix_filename))
    try:
        csvfile = open(matrix_filename,'w',newline='')
    except PermissionError:
        print('ERROR: {} could not be edited\n\tcheck that it is not open in another application'.
            format(matrix_filename))
        sys.exit()

    matrix_writer = csv.writer(csvfile) # open writer
    matrix_writer.writerow(['3'] + role_list)

    gradList = list(grad_preference_form_data.keys())
    # randomise gradlist to eliminate positional bias in assignment
    random.shuffle(gradList)

    for grad in gradList:
        gradRow = [''] * len(role_list)
        for cost in [0,1,2]:
            role_column = grad_preference_form_data[grad]['preference_ids'][cost]
            gradRow[role_column] = cost
        matrix_writer.writerow([grad] + gradRow)

def extract_matrix_csv_data(matrix_filename):
    """
    read matrix csv file
    split data into grads (column1[1:]), roles (row1[1:]) and cost_matrix
    """
    print('\treading {}'.format(matrix_filename))
    try:
        csvfile = open(matrix_filename,newline='')
    except FileNotFoundError:
        print('ERROR: {} not found'.format(matrix_filename))
        sys.exit()

    matrix_reader = csv.reader(csvfile)

    row = next(matrix_reader) # get first row
    role_list = row[1:] # get list of roles from first row
    default_cost = int(row[0]) # cost for unspecified roles
    if default_cost != 3:
        print('\twarning: default cost = {}, not 3'.format(default_cost))
    grad_list = []

    cost_matrix_raw = []

    grad_preferences = {}

    for row in matrix_reader:
        #TODO get preference data
        grad = row[0]
        grad_preferences[grad] = ['','','']
        for cost in [0,1,2]:
            cost_column = row.index(str(cost))
            grad_preferences[grad][cost] = role_list[cost_column-1] # role_list skips first column

        grad_list.append(grad)
        cost_matrix_raw.append([default_cost if x is '' else int(x) for x in row[1:]])

    cost_matrix = np.array(cost_matrix_raw) # convert cost_matrix into ndarray
    return grad_list, role_list, cost_matrix, grad_preferences

def check_cost_matrix_validity(cost_matrix,grad_list):
    """
    perform checks on cost matrix to provide warnings if:
    - values outside of expected range
    - row duplicates of 0,1,2
    """

    for row_index,row in enumerate(cost_matrix):

       # check for non standard value
        for cell in enumerate(row):
            if cell not in (0,1,2,3): # try range(0,4)
               print('WARNING: row {} contains unexpected value {}'.format(grad_list[row_index],cell))

        unique,counts = np.unique(row,return_counts=True)
        row_count = dict(zip(unique,counts))

        # check for duplicates of 0,1,2 in rows
        for cost in (0,1,2):
            if row_count.get(cost,0) != 1:
                print('WARNING: row {} does not contain exactly 1 {}'.format(grad_list[row_index],cost))

def process_assignment_results(	cost_matrix,
                                grad_list, grad_indexes,
                                role_list, role_indexes
                                ):
    """
    combine results into list of tuples for easy data access
    also produces list of leftover roles
    """

    # find assigned grad-role pairs and their associated costs
    assignments = {}

    for grad_index,role_index in zip(grad_indexes,role_indexes):
        cost = cost_matrix[grad_index, role_index] # cost of assigned role
        assignments[grad_list[grad_index]] = (cost,role_list[role_index])

    return assignments

def generate_result_csv(result_filename, assignments, role_list, grad_preferences):
    """
    process assignments
    generate results file
    """
    print('\tgenerating {}'.format(result_filename))
    try:
        csvfile = open(result_filename,'w',newline='')
    except PermissionError:
        print('ERROR: {} could not be edited\n\tcheck that it is not open in another application'.
            format(result_filename))
        sys.exit()

    result_writer = csv.writer(csvfile) # open writer
    result_writer.writerow(['Grad','Cost','Role','','Other Preferences'])

    cost_count = [0, 0, 0, 0] # counter for each rank

    assigned_roles = set()

    # write grad and assigned role to line of csv file for each grad
    for grad in sorted(assignments):
        cost,role = assignments[grad]

        assigned_roles.add(role) # keep track of which roles have been assigned

        other_preferences = [ x if x != role else ' ' for x in grad_preferences[grad]]
        result_writer.writerow([grad,cost,role,' '] + other_preferences)

        cost_count[cost] += 1

    # capture which roles haven't been assigned
    unassigned_roles = set(role_list).difference(assigned_roles)
    for role in unassigned_roles:
        result_writer.writerow(['','',role])

    # write stats
    result_writer.writerow([])
    result_writer.writerow(['cost','count'])
    for cost in range(len(cost_count)):
        result_writer.writerow([cost,cost_count[cost]])

print(extract_role_csv_data('./data/role_titles.csv'))
