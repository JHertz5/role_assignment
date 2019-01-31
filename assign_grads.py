"""
program for assigning graduates to roles using the Hungarian algorithm
"""
# Author: Jukka Hertzog

import processing
from scipy.optimize import linear_sum_assignment
from os import path # for file exists checking

table_filename = './data/table.csv'
matrix_filename = './data/matrix.csv'
matrix_in_filename = './data/matrix_in.csv'
result_filename = './data/grad_assignments.csv'

if path.exists(matrix_in_filename):
    # if matrix input file exists, skip sharepoint
    matrix_filename = matrix_in_filename
    print('skipping table input and using {} as matrix input'.format(matrix_in_filename))
else:
    # process raw input data and generate matrix file
    role_list, grad_preferences = processing.extract_table_csv_data(table_filename)
    processing.generate_matrix_csv(role_list, grad_preferences, matrix_filename)

# process matrix file and extract data
grads, roles, cost_matrix = processing.extract_matrix_csv_data(matrix_filename)

processing.check_cost_matrix_validity(cost_matrix,grads)

# perform assignment
grad_idx,role_idx = linear_sum_assignment(cost_matrix)

assigned_roles,unassigned_roles = processing.process_assignment_results(
    cost_matrix,
    grads,grad_idx,
    roles,role_idx
    )

# generate output file
processing.generate_result_csv(
    result_filename,
    assigned_roles,
    unassigned_roles,
    grad_preferences
    )
print('{} generated'.format(result_filename))
