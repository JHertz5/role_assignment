""" functions for assign_grads.py """
# Author: Jukka Hertzog

import csv
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
    except FileNotFoundError as e:
        print('Error: {} not found'.format(table_filename))

    table_reader = csv.reader(csvfile)

    roleSet = set()

    # get roles from table
    next(table_reader) # skip first row
    for row in table_reader:
        if row[0] != '':
            for role_column in [1, 3, 5]: # pick from columns with roles listed
                roleSet.add(row[role_column])
    role_list = list(roleSet)
    role_list.sort()

    # reset table_reader to start of file
    csvfile.seek(0)
    table_reader = csv.reader(csvfile)

    next(table_reader) # skip first row
    grad_preferences = {}

    for row in table_reader:
        grad = row[0]
        if grad != '':
            grad_preferences[grad] = {
                    'preference_ids'   : [
                        role_list.index(row[1]),
                        role_list.index(row[3]),
                        role_list.index(row[5])
                    ],
                    'preferences'   : [row[1], row[3], row[5]],
                    'comments'      : [row[2], row[4], row[6]]
                }

    return role_list, grad_preferences

def generate_matrix_csv(role_list, grad_preferences, matrix_filename):
    """
    write grad preference matrix into a csv file
    """
    print('\tgenerating {}'.format(matrix_filename))
    with open(matrix_filename,'w',newline='') as csvfile:
        matrix_writer = csv.writer(csvfile) # open writer
        matrix_writer.writerow(['3'] + role_list)

        gradList = list(grad_preferences.keys())
        # randomise gradlist to eliminate positional bias in assignment
        random.shuffle(gradList)

        for grad in gradList:
            gradRow = [''] * len(role_list)
            for cost in [0,1,2]:
                role_column = grad_preferences[grad]['preference_ids'][cost]
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
    except FileNotFoundError as e:
        print('ERROR: {} not found'.format(matrix_filename))

    matrix_reader = csv.reader(csvfile)

    row = next(matrix_reader) # get first row
    roles = row[1:] # get list of roles from first row
    default_cost = int(row[0]) # cost for unspecified roles
    if default_cost != 3:
        print('\twarning: default cost = {}, not 3'.format(default_cost))
    grads = []

    cost_matrix_raw = []

    for row in matrix_reader:
        grads.append(row[0])
        cost_matrix_raw.append([default_cost if x is '' else int(x) for x in row[1:]])

    cost_matrix = np.array(cost_matrix_raw) # convert cost_matrix into ndarray
    return grads,roles,cost_matrix

def check_cost_matrix_validity(cost_matrix,grads):
    """
    perform checks on cost matrix to provide warnings if:
    - values outside of expected range
    - row duplicates of 0,1,2
    """

    for row_index,row in enumerate(cost_matrix):

       # check for non standard value
        for index,cell in enumerate(row):
            if cell not in (0,1,2,3): # try range(0,4)
               print('WARNING: row {} contains unexpected value {}'.format(grads[row_index],cell))

        unique,counts = np.unique(row,return_counts=True)
        row_count = dict(zip(unique,counts))

        # check for duplicates of 0,1,2 in rows
        for cost in (0,1,2):
            if row_count.get(cost,0) != 1:
                print('WARNING: row {} does not contain exactly 1 {}'.format(grads[row_index],cost))

def process_assignment_results(	cost_matrix,
                                grads, grad_indexes,
                                roles, role_indexes
                                ):
    """
    combine results into list of tuples for easy data access
    also produces list of leftover roles
    """

    # find assigned grad-role pairs and their associated costs
    assigned_roles = {}
    for grad_index,role_index in zip(grad_indexes,role_indexes):
        cost = cost_matrix[grad_index, role_index] # cost of assigned role
        assigned_roles[grads[grad_index]] = (cost,roles[role_index])

    # find unassigned roles
    unassigned_role_indexes = set(range(len(roles))).difference(role_indexes)
    unassigned_roles = [roles[index] for index in list(unassigned_role_indexes)]

    return assigned_roles, unassigned_roles

def generate_result_csv(result_filename, assigned_roles, unassigned_roles, grad_preferences):
    """
    process assignments
    generate results file
    """
    print('\tgenerating {}'.format(result_filename))
    with open(result_filename,'w',newline='') as csvfile:
        result_writer = csv.writer(csvfile) # open writer
        result_writer.writerow(['Grad','Cost','Role','','Other Preferences'])

        cost_count = [0, 0, 0, 0] # counter for each rank

        # write grad and assigned role to line of csv file for each grad
        for grad in sorted(assigned_roles):
            cost,role = assigned_roles[grad]
            other_preferences = grad_preferences[grad]['preferences']
            other_preferences.remove(role)

            result_writer.writerow([grad,cost,role,''] + other_preferences)

            cost_count[cost] += 1

        # write each unassigned role into line with empty grad and cost field
        for role in unassigned_roles:
            result_writer.writerow(['','',role])

        # write stats
        result_writer.writerow([])
        result_writer.writerow(['cost','count'])
        for cost in range(len(cost_count)):
            result_writer.writerow([cost,cost_count[cost]])
