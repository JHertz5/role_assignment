""" functions for assign_grads.py """
# Author: Jukka Hertzog

import csv
import sys
import random
import numpy as np

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

    # reset table_reader to start of file
    csvfile.seek(0)
    table_reader = csv.reader(csvfile)

    next(table_reader) # skip first row
    grad_preference_form_data = {}

    for row in table_reader:
        grad = row[0]
        if grad != '':
            grad_preference_form_data[grad] = {
                    'preferences'   : [row[1], row[3], row[5]],
                    'comments'      : [row[2], row[4], row[6]]
                }

    return grad_preference_form_data

def process_clone(clone_title, role_id, clone_data):
    """
    add clone role to clone list and return clone id
    """
    if clone_title not in clone_data:
        clone_data[clone_title] = []

    clone_data[clone_title].append(role_id)
    return clone_data

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

    role_ids = {}
    role_titles = []
    clone_data = {}

    next(role_reader) # skip header row

    for row in role_reader:
        if row[0] != '':
            role_titles.append(row[0])

    role_titles.sort()

    for role_id, role_title in enumerate(sorted(role_titles)):
        # detect and process ' - Placement n' clones
        if len(role_title) > clone_str_idx1:
            if (role_title[clone_str_idx1:-1] == clone_str and 
                                    role_title[-1].isdigit()):
                clone_title = role_title[:clone_str_idx1]
                clone_data = process_clone(clone_title, role_id, clone_data)

        # detect and process '(n)' clones
        elif (role_title[-3] == '(' and role_title[-2].isdigit() and 
                                                role_title[-1] == ')'):
            clone_title = role_title[:-3]
            clone_data = process_clone(clone_title, role_id, clone_data)

        # role_id stored as list to accommodate clones
        role_ids[role_title] = [role_id] 

    # link clones to fellow clones
    for clone_title in clone_data:
        for role_id in clone_data[clone_title]:
            role_title = role_titles[role_id]
            role_ids[role_title] = clone_data[clone_title]

    return role_ids

def generate_matrix_csv(role_ids, grad_preference_form_data, matrix_filename):
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

    default_cost = '5'
    role_list = sorted(role_ids.keys())
    
    matrix_writer = csv.writer(csvfile) # open writer
    matrix_writer.writerow([default_cost] + role_list)

    gradList = list(grad_preference_form_data.keys())
    # randomise gradlist to eliminate positional bias in assignment
    random.shuffle(gradList)

    # write grad choice rows
    for grad in gradList:
        gradRow = [''] * len(role_list)
        for cost in [0,1,2]:
            role_title = grad_preference_form_data[grad]['preferences'][cost]
            role_id_list = role_ids[role_title]
            for role_column in role_id_list: 
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

    normal_default_cost = 5

    matrix_reader = csv.reader(csvfile)

    row = next(matrix_reader) # get first row
    role_list = row[1:] # get list of roles from first row
    default_cost = int(row[0]) # cost for unspecified roles
    if default_cost != normal_default_cost:
        print('\tnote: default cost set {}, not {}'.format(default_cost,normal_default_cost))
    
    grad_list = []
    cost_matrix_raw = []
    grad_preferences = {}

    # extract grad preferences from matrix
    for row in matrix_reader:
        grad = row[0]
        grad_preferences[grad] = ['','','']
        for cost in [0,1,2]:
            cost_column = row.index(str(cost))
            grad_preferences[grad][cost] = role_list[cost_column-1] # role_list skips first column

        grad_list.append(grad)
        cost_matrix_raw.append([default_cost if x is '' else int(x) for x in row[1:]])

    cost_matrix = np.array(cost_matrix_raw) # convert cost_matrix into ndarray
    return grad_list, role_list, cost_matrix, grad_preferences

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
        print('cost {} - {}'.format(cost,cost_count[cost]))
