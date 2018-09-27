"""
program for assigning graduates to roles using the Hungarian algorithm
"""
# Author: Jukka Hertzog

import sys # for reading CLI arguments
import numpy as np # for ndarray type
import processing

# csv filename input required as command line argument 1
if len(sys.argv) < 2:
    infile_name = '' # FILL IN FILENAME BETWEEN ""!!!
    if infile_name == '':
        print('ERROR: no input file provided\n\t(set filename either in code or give as command line argument)')
        sys.exit()
else:
    infile_name = sys.argv[1]

if infile_name[-4:] != '.csv':
    print('ERROR: input must be .csv file')
    sys.exit()

print('\treading {}'.format(infile_name))

#extract, process and check csv data
grads, roles, cost_matrix = processing.extract_csv_data(infile_name)
# processing.check_cost_matrix_validity(cost_matrix,grads) # raises error if problem discovered

# perform assignment
# print(cost_matrix)
from scipy.optimize import linear_sum_assignment
grad_idx,role_idx = linear_sum_assignment(cost_matrix)

assigned_roles,unassigned_roles = processing.process_assignment_results(
    cost_matrix,
    grads,grad_idx,
    roles,role_idx)

# generate output file
outfile_name = 'grad_assignments.csv'
processing.generate_result_csv(outfile_name, assigned_roles,unassigned_roles)
print('{} generated'.format(outfile_name))
