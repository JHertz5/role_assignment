"""
program for assigning graduates to roles using the Hungarian algorithm
"""
# Author: Jukka Hertzog

#TODO alternate randomness solution - test coparison of one normal and one reversed

import processing
from scipy.optimize import linear_sum_assignment
from os import path # for file exists checking

table_filename = './data/table.csv'
roles_filename = './data/role_titles.csv'
matrix_filename = './data/matrix.csv'
matrix_in_filename = './data/matrix_in.csv'
result_filename = './data/grad_assignments.csv'

if path.exists(matrix_in_filename):
    # if matrix input file exists, skip sharepoint data
    matrix_filename = matrix_in_filename
    print('skipping table input and using {} as matrix input'.format(matrix_in_filename))
else:
    # process raw input data and generate matrix file
    role_list, grad_preference_form_data = processing.extract_table_csv_data(table_filename)
    role_ids = processing.extract_role_csv_data(roles_filename)
    processing.generate_matrix_csv(role_list, role_ids, grad_preference_form_data, matrix_filename)

# process matrix file and extract data
grad_list, role_list, cost_matrix, grad_preferences = processing.extract_matrix_csv_data(matrix_filename)

# perform assignment
grad_idx,role_idx = linear_sum_assignment(cost_matrix)

assignments = processing.process_assignment_results(
    cost_matrix, grad_list, grad_idx,
    role_list,
    role_idx
)

# generate output file
processing.generate_result_csv(
    result_filename,
    assignments,
    role_list,
    grad_preferences
    )
print('{} generated'.format(result_filename))
