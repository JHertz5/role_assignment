# Role Assignment

This python script reads a grad role preferences and makes use of the [Hungarian Algorithm](http://hungarianalgorithm.com/hungarianalgorithm.php) to generate an optimal matching of grads to roles. The script makes use of the [scipy implementation of the Hungarian Algorithm](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html).

## Use
The script requires no command line input, but does require either /data/table.csv or /data/matrix_in.csv. The formats required are specified in the Table format and Matrix format sections. /data/table.csv is expected to be the output of SharePoint stored as a csv file.

From the data in /data/table.csv, the sript generates a cost matrix as shown in the Matrix format section. Each graduate is assigned three placement preferences, ranked from 0 (highest preference) to 2 (lowest preference). Unspecified preferences are left blank (to be filled with the default value before being processed). 3 is usully used as the default value. Each value denotes the cost assoociated with that pairing, and the algorithm minimises the total cost, so the lower the cost in a cell, the more likely it is that the pairing will be assigned. The matrix is stored as /data/matrix.csv before being processed to produce the output. Due to bias in the assignment algorithm (lower rows are given preferences), the order of the rows in the matrix are randomised. A non-random solution to the bias problem is in development. (TODO)

The results of the assignemnt are stored in a file called /data/grad_assignment.csv. The format of this file is specified in the Result format section. Note that when the algorithm could not assign any of a grad's preference to a grad, it will give the top available role in alphabetically order to them with a cost of 3.

As mentioned previously, the cost matrix is saved as a .csv file before being processed. If the script detects a file called /data/matrix_in.csv, it will skip /data/table.csv and attempt to use the data from the matrix as the cost matrix. The user can edit /data/matrix.csv and save it as /data/matrix_in.csv in order to make adjustments to the input of the assignment.

### Table format: TODO


### Matrix format:

[default value] | role0 | role1 | role2 | role3 | role4
--- | --- | --- | --- | --- | ---
grad0 | 0 | 2 | 1 |   |   |
grad1 |   | 0 | 1 | 2 |   | 
grad2 | 2 |   | 0 | 1 |   |

### Result format:

|Grad  | Cost | Role| | Other Preferences | | |
| ---  | --- | --- | --- | --- | --- | --- |
|grad0 | cost0 | role0 |  |  | 0pref1 | 0pref2 |
|grad1 | cost1 | role1 |  | 1pref0 |  | 1pref2 |
|     |       | unassigned_role0  | | | | |

test.csv is provided as an example input
