from random import randint
import numpy as np

class TrackingState:

    def __init__(self, board):
        self.blockSize = len(board)
        self.count = 0
        self.initial(board)

    def initial(self, board):
        ncel = self.blockSize
        self.cells = []
        for i in range(0, ncel * ncel):
            self.cells.append(['0', [str(i) for i in range(1, ncel + 1)]])

        for i in range(0, self.blockSize):
            for j in range(0, self.blockSize):
                if board[i][j] != '0':
                    value = Supp(str(board[i][j]), i, j)
                    if not self.assign(value):
                        return False
        return True

    # Tries to a assign a value to a cell
    def assign(self, value):
        if self.checkConstr(value):
            self.cells[value.x * self.blockSize + value.y] = [str(value.val), []]
            self.count = self.count + 1
            return True
        else:
            return False

    # Check if the constraints for the assigned value are satisfied
    def checkConstr(self, value):
        return self.checkEmpty(value.x, value.y) and self.checkSquare(value) and self.checkRow(value) and self.checkCol(value)

    # Check if the cell is an empty cell
    def checkEmpty(self, i, j):
        return self.cells[i * self.blockSize + j][0] == '0'

    # Check if the row constraint is satisfied and removing the possible others value in the row
    def checkRow(self, value):
        row = list(range(0, self.blockSize))
        for i in row:
            if not self.delConstrVal(i, value.y, value):
                return False
        return True

    # Checking if the column constraint is satisfied and removing the possible others value in the column
    def checkCol(self, value):
        col = list(range(0, self.blockSize))
        for j in col:
            if not self.delConstrVal(value.x, j, value):
                return False
        return True

    # Check if the square constraint is satisfied and removing the possible others value in the square
    def checkSquare(self, value):
        sx = value.x - value.x%3
        sy = value.y - value.y%3
        for i in range(sx, sx + 3):
            for j in range(sy, sy + 3):
                if not self.delConstrVal(i, j, value):
                    return False
        return True

    # Deletes values during the checking of constraints
    def delConstrVal(self, i, j, value):
        domSet = self.cells[i * self.blockSize + j][1]
        val = self.cells[i * self.blockSize + j][0]
        if val == value.val:
            return False

        if value.val in domSet:
            domSet.remove(value.val)

        if len(domSet) == 1:
            assign = Supp(domSet[0], i, j)

        return True

    # get the possible value that can be assigned
    def getDomSet(self, i, j):
        return self.cells[i * self.blockSize + j][1]

    # get the value that is actually assigned
    def getVal(self, i, j):
        return self.cells[i * self.blockSize + j][0]

class Supp:

    def __init__(self, value, x, y):
        self.x = x
        self.y = y
        self.val = value

class RelaxationLabeling:

    def __init__(self, dimension, file):
        self.totalcel = dimension * dimension
        self.q = np.zeros((self.totalcel, dimension))
        self.p = np.ones((self.totalcel, dimension)) / dimension

        with open(file) as f:
            board = f.read().splitlines()

        board = [list(line) for line in board]
        self.board = TrackingState(board)
        self.ncel = self.board.blockSize

    # Initialization of the board
    def initializeBoard(self):
        for i in range(self.ncel):
            for j in range(self.ncel):
                domainSet = self.board.getDomSet(i, j)
                n = len(domainSet)
                prob = np.zeros((1, self.ncel))[0]

                if not self.board.checkEmpty(i, j):
                    val = int(self.board.getVal(i, j))
                    prob[val-1] = 1
                else:
                    for k in domainSet:
                        prob[int(k)-1] = randint(1,n)

                prob = prob / np.sum(prob)
                self.p[i * self.ncel + j] = prob


    def compatibility(self, i, j, lb, mu):
        if i == j:
            return 0
        if lb != mu:
            return 1
        if self.checkRow(i, j) or self.checkCol(i, j) or self.checkSquare(i, j):
            return 0
        else:
            return 1

    # checking if it is the same row
    def checkRow(self, i, j):
        return (i // self.ncel) == (j // self.ncel)

    # checking if it is the same col
    def checkCol(self, i, j):
        return (i % self.ncel) == (j % self.ncel)

    # checking if is the same square
    def checkSquare(self, i, j):
        six = (i // self.ncel) - (i // self.ncel%3)
        siy = (i % self.ncel) - (i % self.ncel%3)
        sjx = (j // self.ncel) - (j // self.ncel%3)
        sjy = (j % self.ncel) - (j % self.ncel%3)
        return six == sjx and siy == sjy

    # Relaxation labeling core where the board is solved
    def solve(self):
        self.initializeBoard()
        self.refreshProb()

        cells = []

        for i in range(self.totalcel):
            pos = np.argmax(self.p[i])
            cells.append(pos + 1)

        for i in range(self.totalcel):
            if i % self.ncel == 0:
                print("")
            print(cells[i], end=" ")
        print("\n")
        return True

    # updating prob and check of the algorithm end
    def refreshProb(self):
        prev = 0
        diff = 1
        t = 0
        while diff > 0.01:
            self.p = self.newP()
            avg = self.avgCons()
            diff = avg-prev
            print("step: " + str(t) + ", convergency: " + str(diff) + "")
            prev = avg
            t += 1

    # evaluation of average consistency used to stop the algorithm
    def avgCons(self):
        return np.sum(self.p * self.q)

    def newP(self):
        self.computeQ()
        prob = self.p * self.q
        row_sums = prob.sum(axis=1)
        prob = prob / row_sums[:, np.newaxis]
        return prob

    def computeQ(self):
        self.q = np.zeros((self.totalcel, self.ncel))

        for i in range(self.totalcel):
            for lb in range(self.ncel):
                for j in range(self.totalcel):
                    for mu in range(self.ncel):
                        self.q[i][lb] = self.q[i][lb] + self.compatibility(i, j, lb, mu) * self.p[j][mu]