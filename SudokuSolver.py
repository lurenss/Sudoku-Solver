from time import time
from ConstraintPropagation import ConstraintPropagation
from RelaxationLabeling import RelaxationLabeling

"""
Set up and solve the Sudoku boards using 2 techniques: Constraint Propagation with Backtracking & Relaxation Labeling
"""

testFile = 'testFiles/game1.txt'

# The domain of legal values for each cell are the integers [1,9]
boardDimension = 9

print("Solving with Constraint Propagation\n-----------------------------------")
constrainPropagationSolver = ConstraintPropagation(boardDimension, testFile.format())
start = time()
isSolved1 = constrainPropagationSolver.solve()
end = time()
print(constrainPropagationSolver)
print("Time elapsed: {}".format(end - start))
print("Board was solved: {}\n".format(isSolved1))

print("Solving with Relaxation Labeling\n-----------------------------------")
relaxationLabelingSolver = RelaxationLabeling(boardDimension, testFile.format())
start = time()
isSolved2 = relaxationLabelingSolver.solve()
end = time()
print("Time elapsed: {}".format(end - start))
print("Board was solved: {}\n".format(isSolved2))