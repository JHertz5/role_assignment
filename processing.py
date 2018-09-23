""" functions for assign_grads.py """
# Author: Jukka Hertzog

import csv
import numpy as np

def extract_csv_data(infile_name):
    """
    read input csv file
    Split data into grads (column1[1:]), roles (row1[1:]) and cost_matrix
    Return grads, roles, cost_matrix

    :param infile_name: filename of input csv file
    """

    with open(infile_name,newline='') as csvfile:
        infile_reader = csv.reader(csvfile)

        row = next(infile_reader)
        roles = row[1:] # get list of roles from first row
        default_cost = int(row[0]) # cost for unspecified roles
        print('\tdefault cost = {}'.format(default_cost))
        grads = []

        cost_matrix_raw = []

        for row in infile_reader:
            grads.append(row[0])
            cost_matrix_raw.append([default_cost if x is '' else int(x) for x in row[1:]])

        cost_matrix = np.array(cost_matrix_raw) # convert cost_matrix into ndarray
    return grads,roles,cost_matrix

def check_cost_matrix_validity(cost_matrix,grads):
    """
    perform checks on cost matrix to provide warnings if:
    - values outside of expected range
    - row duplicates of 0,1,2

    :param cost_matrix:		array of costs for grad/role combinations
    """

    for row_index,row in enumerate(cost_matrix):

#        # check for non standard value
#        for index,cell in enumerate(row):
#            if cell not in (0,1,2,3): # try range(0,4)
#                print('WARNING: row {} contains unexpected value {}'.format(grads[row_index],cell))
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

    :param cost_matrix:		array of costs for grad/role combinations
    :param grads:			list of grad names
    :param grad_indexes:	array containing grad indexes
                                                    corresponding to role_idx
    :param roles:			list of role names
    :param role_indexes:	array containing role assignment indexes
                                                    corresponding to grad_idx
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

def generate_result_csv(outfile_name, assigned_roles,unassigned_roles):
    """
    process assignments
    generate results file

    :param outfile_name:	filename of output csv file
    :param assigned_roles:	dict containing assignment results
                                    - assigned_roles[grad] = (cost, role)
    """

    with open(outfile_name,'w',newline='') as csvfile:
        outfile_writer = csv.writer(csvfile) # open writer
        outfile_writer.writerow(['Grad','Cost','Role'])

        # write grad and assigned role to line of csv file for each grad
        for grad in sorted(assigned_roles):
            cost,role = assigned_roles[grad]
            outfile_writer.writerow([grad,cost,role])

        # write each unassigned role into line with empty grad and cost field
        for role in unassigned_roles:
            outfile_writer.writerow(['','',role])

