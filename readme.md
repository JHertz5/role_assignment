# Role Assignment

This python script reads a matrix of grad role preferences and makes use of the [Hungarian Algorithm](http://hungarianalgorithm.com/hungarianalgorithm.php) to generate an optimal matching of grads to roles. The script makes use of the [scipy implementation of the Hungarian Algorithm](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html).

## Use
The script requires one command line input, the filename of the input .csv file. Each graduate should be assigned three placement preferences, ranked from 0 (highest preference) to 2 (lowest preference). Any spaces left blank will be filled with the default value (typically 3 should be chosen as the default value, so that the cost is higher than the preferences). Each value denotes the cost assoociated with that pairing, and the algorithm minimises the total cost, so the lower the cost, the more likely it is that the pairing will be assigned.

This script can be used flexibly with no change to the code. By changing the cost values, the user can adjust the functionality of the script to suit their needs. For example:
* If the user does not want to rank the preferences, they can give each preference the same cost as opposed to 0,1,2. 
* If they want to give certain graduates priority over others, they can assign higher costs for each of the lower priority's choices. 
* If they would like to prevent graduates from being assigned certain placements, those pairings can be given a cost higher than the default. 


### Input format:

[default value] | role0 | role1 | role2 | role3 | role4
--- | --- | --- | --- | --- | ---
grad0 | 0 | 2 | 1 |   |   |
grad1 |   | 0 | 1 | 2 |   | 
grad2 | 2 |   | 0 | 1 |   |

### Output format:

Grad | Cost | Role
-----|------|-----
grad0 | cost0 | role0
grad1 | cost1 | role1

test.csv is provided as an example input
