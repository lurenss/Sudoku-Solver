from time import time
import copy

class SudokuSolver:

    """
    Initializes the Sudoku board's dimensions, expanded cell count,
    cell values, and remaining values given the text in the test file
    """
    def __init__(self, dimension, file):
        self.dimension = dimension
        self.expandedCells = 0

        with open(file) as f:
            text = f.readlines()
            self.board = [list(x.strip()) for x in text]

        self.setBoardRemainingValuesList()

    """
    Prints out the Sudoku game board and number of cells that were expanded
    """
    def __str__(self):
        output = ''
        for row in self.board:
            for x in row:
                output += x + " "
            output += '\n'
        output += "Nodes expanded: {}".format(self.expandedCells)
        return output

    """
    Returns the number of remaining values in a cell's domain
    """
    def getDomainLength(self, list):
        # If there is an 'X' in the cell's remaining values list (meaning the cell has a fixed value) or the list is empty
        if FIXED_CELL in list or list == []:
            return EMPTY_DOMAIN # Return 10 (to make sure this domain length is not mistakenly seen as the MRV)

        # If the cell has remaining values in its domain, return the length of the domain
        else:
            return len(list)

    """
    Returns the [row, col] location of the cell with the next minimum remaining value
    """
    def getNextMRVLocation(self):
        # Make a map of the remaining values in every cell's domain
        remainingValueMap = list(map(self.getDomainLength, self.remainingValues))

        # Find the minimum of the map
        minimum = min(remainingValueMap)

        # If this minimum remaining value is an empty domain,
        # this means there are no further cells to assign values to, so return location [-1,-1]
        if minimum == EMPTY_DOMAIN:
            return (-1,-1)

        # Otherwise return the location of the cell with the minimum remaining value
        else:
            index = remainingValueMap.index(minimum)
            return(index // DOMAIN_SIZE, index % DOMAIN_SIZE)

    """
    Gets the domain of remaining values for a cell, given the constraints that
    no two cells in the same row, column, or box can have the same value
    """
    def getDomainForCell(self, row, col):
        # Sets the initial domain as a list of the eligible values for the cell, i.e. [1,2,3,4,5,6,7,8,9]
        domain = [str(i) for i in range(1, self.dimension + 1)]

        # For each cell in the same row, remove their values from the domain of the cell we are looking at
        for i in range(self.dimension):
            if self.board[row][i] != EMPTY_CELL:
                if self.board[row][i] in domain:
                    domain.remove(self.board[row][i])

        # For each cell in the same column, remove their values from the domain of the cell we are looking at
        for i in range(self.dimension):
            if self.board[i][col] != EMPTY_CELL:
                if self.board[i][col] in domain:
                    domain.remove(self.board[i][col])

        # For each cell in the same 3x3 box, remove their values from the domain of the cell we are looking at
        boxRow = row - row%3
        boxCol = col - col%3
        for i in range(3):
            for j in range(3):
                if self.board[boxRow+i][boxCol+j] != EMPTY_CELL:
                    if self.board[boxRow+i][boxCol+j] in domain:
                        domain.remove(self.board[boxRow+i][boxCol+j])

        # Return the remaining values in the domain of the cell
        return domain

    """
    Updates the board's list of remaining values for each cell in the board
    """
    def setBoardRemainingValuesList(self):
        remainingValues = []

        # For every cell on the board, add their domains of remainingValues to the list
        for row in range(self.dimension):
            for col in range(self.dimension):
                # If the cell is already assigned a value, set its domain in the list to value 'X' (to signal its value has been fixed)
                if self.board[row][col] != '0':
                    remainingValues.append([FIXED_CELL])

                # If the cell is still empty, set its domain in the list to be the list of the cell's remaining values
                else:
                    remainingValues.append(self.getDomainForCell(row,col))

        # Update and set the board's list of remaining values for each cell
        self.remainingValues = remainingValues

    """
    Checks if a cell value assignment produces an empty domain for another cell in the same row, column, or box
    If it does, then we know that cell assignment is not viable
    """
    def isEmptyDomainProduced(self, row, col):
        # Get location of the given cell in the list
        cellLocation = row * DOMAIN_SIZE + col

        # Extract the cell we have just assigned a new value to
        cell = self.remainingValues.pop(cellLocation)

        # If there is an empty domain present now
        if [] in self.remainingValues:
            # Reinsert the given cell and return True
            self.remainingValues.insert(cellLocation, cell)
            return True

        # If no empty domain is produced
        else:
            # Reinsert the given cell and return False
            self.remainingValues.insert(cellLocation, cell)
            return False

    """
    Solves a Sudoku board using constraint propagation with backtracking and forward checking techniques
    """
    def solveConstraintPropagation(self):
        # Gets [row, col] location of the cell with the minimum remaining value
        location = self.getNextMRVLocation()

        # If the location has value -1, this means we are done solving the Sudoku board, so exit algorithm
        if location[0] == -1:
            return True

        # Otherwise, expand the node and attempt to assign a value to a cell
        else:
            self.expandedCells += 1
            row = location[0]
            col = location[1]

            # For each value in that node's list of remaining values
            for value in self.remainingValues[row * DOMAIN_SIZE + col]:
                # Make a copy of the Sudoku board's current remaining values
                currentState = copy.deepcopy(self.remainingValues)

                # Set the cell to the new value
                self.board[row][col] = str(value)

                # Update the Sudoku board's remaining values after the new cell assignment
                self.setBoardRemainingValuesList()

                # If an empty domain is produced, backtrack and return the cell's value back to empty,
                # restore the Sudoku board's previous remaining values, and try another value assignment
                if self.isEmptyDomainProduced(row, col):
                    self.board[row][col] = EMPTY_CELL
                    self.remainingValues = currentState

                # If there is no empty domain produced as a result of this assignment,
                # it is a viable choice, so continue assigning values to other cells
                else:
                    if self.solveConstraintPropagation():
                        return True

            # If we have tried all possible values for a cell and no viable choice is found,
            # return False so show we cannot solve the Sudoku board
            return False

    """
    Solves a Sudoku board using relaxation labeling techniques
    """
    def solveRelaxationLabeling(self):
        return False


"""
Set up and solve the Sudoku boards using 2 techniques: Constraing Propagation & Relaxation Labeling
"""
# The domain of legal values for each cell are the integers [1,9]
DOMAIN_SIZE = 9

# If a cell is empty and does not have a legal value assigned to it yet, it will take value 0
EMPTY_CELL = 0

# If a cell has no remaining values in its domain, the domain will take a value higher than the highest
# legal cell value to ensure the cell won't be chosen as the next MRV location
EMPTY_DOMAIN = DOMAIN_SIZE + 1

# If a cell's value has been assigned and is fixed at that value, it will take value X
FIXED_CELL = 'X'

testFile = 'testFiles/game1.txt'
boardDimension = DOMAIN_SIZE

print("Solving with Constraint Propagation\n-----------------------------------")
sudokuSolver1 = SudokuSolver(boardDimension, testFile.format())
start = time()
isSolved1 = sudokuSolver1.solveConstraintPropagation()
end = time()
print(sudokuSolver1)
print("Time elapsed: {}".format(end - start))
print("Board was solved: {}\n".format(isSolved1))

print("Solving with Relaxation Labeling\n-----------------------------------")
sudokuSolver2 = SudokuSolver(boardDimension, testFile.format())
start = time()
isSolved2 = sudokuSolver2.solveRelaxationLabeling()
end = time()
print(sudokuSolver2)
print("Time elapsed: {}".format(end - start))
print("Board was solved: {}\n".format(isSolved2))