"""
program for assigning graduates to roles using the Hungarian algorithm
"""
# Author: Jukka Hertzog

#TODO Randomise input order
#TODO handle error with file open
#TODO list how many of each choice were selected
#TODO change input path to fixed and in folder
#TODO list other choices and comments
#TODO possible to get unselected roles as well?
#TODO check matrix validity

import sys # for reading CLI arguments
import processing
from scipy.optimize import linear_sum_assignment

table_filename = 'input.csv'
matrix_filename = 'matrix.csv'
result_filename = 'grad_assignments.csv'

# process raw input data and generate matrix file
roleList, gradPreferences = processing.extract_table_csv_data('test_raw.csv')
processing.generate_matrix_csv(roleList, gradPreferences, matrix_filename)

# process matrix file and extract data
grads, roles, cost_matrix = processing.extract_matrix_csv_data(matrix_filename)

# perform assignment
# print(cost_matrix)

grad_idx,role_idx = linear_sum_assignment(cost_matrix)

assigned_roles,unassigned_roles = processing.process_assignment_results(
    cost_matrix,
    grads,grad_idx,
    roles,role_idx)

# generate output file
processing.generate_result_csv(result_filename, assigned_roles,unassigned_roles)
print('{} generated'.format(result_filename))
