Hungarian Algorithm

Each grad connects to 3 placements, edges are ranked 0,1,2 (highest preference to lowest preference). costMatrix is created from edges. 3 is assigned to non existent edges.

.csv input format:

[default value],[placement0],[placement1],[placement2],[placement3],[placement4]
[grad0],0,2,1,,,
[grad1],,0,1,2,,
[grad2],2,,0,,1,

.csv output format:

Grad, Placement:
[grad0],[placement0]
[grad1],[placement1]
[grad2],[placement2]

