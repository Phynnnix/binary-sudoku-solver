import tkinter as tk
from tkinter import ttk
import time
from copy import deepcopy

canvas = None
posdict = {}
sdk = None
saveState = None

def cellFilled(cell):
    return (True if (cell == 0 or cell == 1) else False)


def checkFilled(sudoku):
    for col in sudoku:
        for cell in col:
            if not cellFilled(cell): return False
    return True


def testTwo(sudoku, x1, y1, x2, y2):
    cell1 = sudoku[x1][y1]
    cell2 = sudoku[x2][y2]
    if cellFilled(cell1) and cellFilled(cell2) and cell1 == cell2:
        return True
    return False


def countTypeCellsIn(sudoku, mode, typ, num):
    count = 0
    if (mode == "col"):
        for cell in sudoku[num]:
            if (typ == -1 and not cellFilled(cell)) or cell == typ:
                count += 1
    elif (mode == "row"):
        for x in range(len(sudoku)):
            cell = sudoku[x][num]
            if (typ == -1 and not cellFilled(cell)) or cell == typ:
                count += 1
    else:
        for col in sudoku:
            for cell in col:
                if (typ == -1 and not cellFilled(cell)) or cell == typ:
                    count += 1
    return count


def solveDoubleClue(sudoku):
    change = False
    for x in range(len(sudoku)):
        for y in range(len(sudoku[0])):
            cell = (sudoku[x])[y]
            if not cellFilled(cell):
                if x >= 2 and testTwo(sudoku, x - 2, y, x - 1, y):
                    sudoku[x][y] = 1 - sudoku[x - 1][y]
                    change = True
                elif x < len(sudoku) - 2 and testTwo(sudoku, x + 2, y, x + 1, y):
                    sudoku[x][y] = 1 - sudoku[x + 1][y]
                    change = True
                elif y >= 2 and testTwo(sudoku, x, y - 2, x, y - 1):
                    sudoku[x][y] = 1 - sudoku[x][y - 1]
                    change = True
                elif y < len(sudoku[0]) - 2 and testTwo(sudoku, x, y + 2, x, y + 1):
                    sudoku[x][y] = 1 - sudoku[x][y + 1]
                    change = True
                elif x >= 1 and x < len(sudoku) - 1 and testTwo(sudoku, x - 1, y, x + 1, y):
                    sudoku[x][y] = 1 - sudoku[x - 1][y]
                    change = True
                elif y >= 1 and y < len(sudoku[0]) - 1 and testTwo(sudoku, x, y - 1, x, y + 1):
                    sudoku[x][y] = 1 - sudoku[x][y - 1]
                    change = True
    return change


def fillColor(sudoku):
    change = False
    for x in range(len(sudoku)):
        # print("x#{}-x:{}".format(x, countTypeCellsIn(sudoku, "col", -1, x)))
        # print("x#{}-0:{}".format(x, countTypeCellsIn(sudoku, "col", 0, x)))
        # print("x#{}-1:{}".format(x, countTypeCellsIn(sudoku, "col", 1, x)))
        # print(len(sudoku[x])//2)
        if not countTypeCellsIn(sudoku, "col", -1, x) == 0:
            if ((len(sudoku[x]) // 2) == countTypeCellsIn(sudoku, "col", 1, x)):
                change = True
                for y in range(len(sudoku[x])):
                    if not cellFilled(sudoku[x][y]):
                        sudoku[x][y] = 0
            if (len(sudoku[x]) // 2 == countTypeCellsIn(sudoku, "col", 0, x)):
                change = True
                for y in range(len(sudoku[x])):
                    if not cellFilled(sudoku[x][y]):
                        sudoku[x][y] = 1
    for ry in range(len(sudoku[0])):
        # print("ry#{}-x:{}".format(ry, countTypeCellsIn(sudoku, "row", -1, ry)))
        # print("ry#{}-0:{}".format(ry, countTypeCellsIn(sudoku, "row", 0, ry)))
        # print("ry#{}-1:{}".format(ry, countTypeCellsIn(sudoku, "row", 1, ry)))
        # print()
        if not countTypeCellsIn(sudoku, "row", -1, ry) == 0:
            if (len(sudoku) // 2 == countTypeCellsIn(sudoku, "row", 1, ry)):
                change = True
                for rx in range(len(sudoku)):
                    if not cellFilled(sudoku[rx][ry]):
                        sudoku[rx][ry] = 0
            if (len(sudoku) // 2 == countTypeCellsIn(sudoku, "row", 0, ry)):
                change = True
                for rx in range(len(sudoku)):
                    if not cellFilled(sudoku[rx][ry]):
                        sudoku[rx][ry] = 1
    return change


def existsInSudoku(line, rowcol, sudoku):
    lines = list(range(len(sudoku)))
    newLines = []
    for u in range(len(line)):
        if (rowcol == "row"):
            for r in lines:
                if line[u] == sudoku[u][r]:
                    newLines.append(r)
        if (rowcol == "col"):
            for c in lines:
                if line[u] == sudoku[c][u]:
                    newLines.append(c)
        lines = newLines
        newLines = []
        if len(lines) == 0: return False
    return True


def hasSomeError(line):
    cOne, cZero = 0, 0
    for i in range(len(line)):
        if line[i] == 0:
            cZero += 1
        if line[i] == 1:
            cOne += 1
        if cOne > len(line) // 2 or cZero > len(line) // 2:
            return True
        if (i < len(line) - 2):
            if line[i] == line[i + 1] and line[i + 1] == line[i + 2]:
                return True
    return False


def getVariantsRec(ones, zeroes, branch):
    if zeroes == 0:
        branch.extend([1] * ones)
        return [branch]
    if ones == 0:
        branch.extend([0] * zeroes)
        return [branch]
    variants = []
    if ones > 0:
        br1 = branch.copy()
        br1.append(1)
        variants += getVariantsRec(ones - 1, zeroes, br1)
    if zeroes > 0:
        br0 = branch.copy()
        br0.append(0)
        variants += getVariantsRec(ones, zeroes - 1, br0)
    return variants


VARIANTS = {}


def getVariants(zeroes, ones):
    global VARIANTS
    if not zeroes in VARIANTS:
        VARIANTS[zeroes] = {}
        VARIANTS[zeroes][ones] = getVariantsRec(ones, zeroes, [])
    elif not ones in VARIANTS[zeroes]:
        VARIANTS[zeroes][ones] = getVariantsRec(ones, zeroes, [])
    return VARIANTS[zeroes][ones]


def fitValuesFromAcceptables(acceptables):
    if len(acceptables) == 0: return []
    fit = []
    for i in range(len(acceptables[0])):
        fit.append(acceptables[0][i])
        for acc in acceptables:
            if not acc[i] == fit[i]:
                fit[i] = -1
                break
    return fit


def insertIntoLine(insertPos, insertVals, line):
    if len(insertPos) != len(insertVals): return False
    for i in range(len(insertPos)):
        line[insertPos[i]] = insertVals[i]


def tryAndFindEquals(sudoku):
    length = 2
    change = False
    emptyPos = []
    variants = []
    acceptable = []
    fitValues = []
    line = []
    while length < len(sudoku) // 2 and not change:
        for x in range(len(sudoku)):
            if countTypeCellsIn(sudoku, "col", -1, x) == length:
                missingOnes = len(sudoku[x]) // 2 - countTypeCellsIn(sudoku, "col", 1, x)
                missingZeroes = length - missingOnes
                variants = getVariants(missingZeroes, missingOnes)
                acceptable = []
                emptyPos = []
                line = []
                for y in range(len(sudoku[x])):
                    line.append(sudoku[x][y])
                    if not cellFilled(sudoku[x][y]):
                        emptyPos.append(y)
                # print("x:{},y:{}".format(x,y))
                # print(displaySudoku(sudoku))
                # print(line)
                # print(countTypeCellsIn(sudoku, "col", 1, x))
                for vrt in variants:
                    insertIntoLine(emptyPos, vrt, line)
                    if (not hasSomeError(line)) and (not existsInSudoku(line, "col", sudoku)):
                        acceptable.append(vrt)
                fitValues = fitValuesFromAcceptables(acceptable)
                # print("0: {}, 1: {}".format(missingZeroes, missingOnes))
                # print(emptyPos)
                # print(acceptable)
                # print(fitValues)
                for i in range(len(fitValues)):
                    if fitValues[i] == 0 or fitValues[i] == 1:
                        sudoku[x][emptyPos[i]] = fitValues[i]
                        change = True
        for ry in range(len(sudoku[0])):
            if countTypeCellsIn(sudoku, "row", -1, ry) == length:
                missingOnes = len(sudoku) // 2 - countTypeCellsIn(sudoku, "row", 1, ry)
                missingZeroes = length - missingOnes
                variants = getVariants(missingZeroes, missingOnes)
                emptyPos = []
                acceptable = []
                line = []
                for rx in range(len(sudoku)):
                    line.append(sudoku[rx][ry])
                    if not cellFilled(sudoku[rx][ry]):
                        emptyPos.append(rx)
                for vrt in variants:
                    insertIntoLine(emptyPos, vrt, line)
                    if (not hasSomeError(line)) and (not existsInSudoku(line, "row", sudoku)):
                        acceptable.append(vrt)
                fitValues = fitValuesFromAcceptables(acceptable)
                for i in range(len(fitValues)):
                    if fitValues[i] == 0 or fitValues[i] == 1:
                        sudoku[emptyPos[i]][ry] = fitValues[i]
                        change = True
        length += 1
    return change


def solveBinarySudoku(sudoku, showStats=False, showState=False, showSteps=False):
    # safety = 10000
    global canvas
    change = True
    while (not checkFilled(sudoku)) and change:  # safety > 0:
        change = False
        cntSDC, cntFC, cntTAFE = 0, 0, 0
        while solveDoubleClue(sudoku):
            change = True
            if showSteps:
                printSudokuOnCanvas(sudoku, canvas, canvas.winfo_width(), canvas.winfo_height())
                canvas.update()
                time.sleep(.1)
            cntSDC += 1
        while fillColor(sudoku):
            change = True
            if showSteps:
                printSudokuOnCanvas(sudoku, canvas, canvas.winfo_width(), canvas.winfo_height())
                canvas.update()
                time.sleep(.1)
            cntFC += 1
        if not change:
            change = tryAndFindEquals(sudoku)
            if change:
                if showSteps:
                    printSudokuOnCanvas(sudoku, canvas, canvas.winfo_width(), canvas.winfo_height())
                    canvas.update()
                    time.sleep(.1)
                cntTAFE = 1
        # safety -= 1
        if showStats:
            print("SDC: {}, FC: {}, TAFE: {}".format(cntSDC, cntFC, cntTAFE))
        if showState:
            print(displaySudoku(sudoku))
    return sudoku


def emptySudoku(size):
    sudoku = []
    e = 5
    for x in range(size):
        sudoku.append([])
        for y in range(size):
            sudoku[x].append(e)
    return sudoku


def setCells(sudoku, xy0s, xy1s):
    for x0 in range(len(xy0s)):
        for y0 in xy0s[x0]:
            sudoku[x0][y0] = 0
    for x1 in range(len(xy1s)):
        for y1 in xy1s[x1]:
            sudoku[x1][y1] = 1


def displaySudoku(sudoku):
    pr = ""
    for y in range(len(sudoku[0])):
        for x in range(len(sudoku)):
            cell = sudoku[x][y]
            if cellFilled(cell):
                cell = str(cell)
            else:
                cell = " "
            pr += cell + " "
        pr += '\n'
    return pr


def clickPos(ev, sudoku):
    global posdict
    print(ev)
    print(posdict)
    pos = posdict[ev.widget.find_withtag('current')[0]]
    cellVal = sudoku[pos[0]][pos[1]]
    newVal = 0
    if cellVal == 0:
        newVal = 1
    if cellVal == 1:
        newVal = 5
    print(pos)
    print(displaySudoku(sudoku))
    sudoku[pos[0]][pos[1]] = newVal
    print(displaySudoku(sudoku))

def evalClickAndPrint(ev, sudoku, canvas, cw, ch):
    clickPos(ev, sudoku)
    printSudokuOnCanvas(sudoku, canvas, cw, ch)

def printSudokuOnCanvas(sudoku, canvas, cw, ch):
    global posdict
    rectWidth = cw // len(sudoku)
    rectHeight = ch // len(sudoku)
    canvas.delete("all")
    posdict = {}
    for x in range(len(sudoku)):
        for y in range(len(sudoku[x])):
            x1 = rectWidth * x + 5
            y1 = rectHeight * y + 5
            x2 = x1 + rectWidth - 10
            y2 = y1 + rectHeight - 10
            rectFill = "black"
            if sudoku[x][y] == 0:
                rectFill = "yellow"
            if sudoku[x][y] == 1:
                rectFill = "blue"
            cn = canvas.create_rectangle(x1, y1, x2, y2, fill=rectFill, tags=('cell'))
            posdict[cn] = [x, y]
    canvas.tag_bind('cell', "<Button-1>", lambda ev: evalClickAndPrint(ev, sudoku, canvas, cw, ch))
    print(posdict)

def solveAndShow(sudoku):
    global canvas
    solveBinarySudoku(sudoku, showSteps=True)
    canvas.update()
    printSudokuOnCanvas(sudoku, canvas, canvas.winfo_width(), canvas.winfo_height())

def setNewSize(sz):
    global sdk, canvas
    sdk = emptySudoku(sz)
    canvas.update()
    printSudokuOnCanvas(sdk, canvas, canvas.winfo_width(), canvas.winfo_height())

def save():
    global saveState, sdk
    saveState = deepcopy(sdk)

def load():
    global saveState, sdk, canvas
    sdk = deepcopy(saveState)
    canvas.update()
    printSudokuOnCanvas(sdk, canvas, canvas.winfo_width(), canvas.winfo_height())

if __name__ == '__main__':
    sdk = emptySudoku(8)
    saveState = deepcopy(sdk)
    #zeros = [[5, 6], [1], [1, 6, 9], [2, 7], [], [4], [1], [], [3, 6], [4], [6, 7, 9], [0]]
    #ones = [[], [], [], [11], [5, 6, 11], [9, 10], [5], [2, 11], [], [2, 11], [], [3, 8]]
    #setCells(sdk, zeros, ones)

    window = tk.Tk()
    canvasWidth = 500
    canvasHeight = 500
    #s = ttk.Style()
    #s.configure("ClickBox", foreground="black")
    #s.configure("ClickBox.one", foreground="yellow")
    #s.configure("ClickBox.zero", foreground="blue")
    canvas = tk.Canvas(window, width=canvasWidth, height=canvasHeight, background='gray75')
    printSudokuOnCanvas(sdk, canvas, canvasWidth, canvasHeight)
    canvas.pack()

    buttonS = tk.Button(window, text="Save", command=save)
    buttonS.pack(side="left")
    buttonL = tk.Button(window, text="Load", command=load)
    buttonL.pack(side="right")

    button = tk.Button(window, text="Solve", command=lambda: solveAndShow(sdk))
    button.pack()

    button4 = tk.Button(window, text="4", width=5, command=lambda: setNewSize(4))
    button4.pack(side='left', padx=5)
    button6 = tk.Button(window, text="6", width=5, command=lambda: setNewSize(6))
    button6.pack(side='left', padx=5)
    button8 = tk.Button(window, text="8", width=5, command=lambda: setNewSize(8))
    button8.pack(side='left', padx=5)
    button10 = tk.Button(window, text="10", width=5, command=lambda: setNewSize(10))
    button10.pack(side='left', padx=5)

    button18 = tk.Button(window, text="18", width=5, command=lambda: setNewSize(18))
    button18.pack(side='right', padx=5)
    button16 = tk.Button(window, text="16", width=5, command=lambda: setNewSize(16))
    button16.pack(side='right', padx=5)
    button14 = tk.Button(window, text="14", width=5, command=lambda: setNewSize(14))
    button14.pack(side='right', padx=5)
    button12 = tk.Button(window, text="12", width=5, command=lambda: setNewSize(12))
    button12.pack(side='right', padx=5)

    window.mainloop()

    #solved = solveBinarySudoku(sdk, True, True)
    # print(displaySudoku(solved))
    # print(existsInSudoku([0,1,1,0,1,0,0,1,1,0,1,0],"row",solved))
    # print(existsInSudoku([0,0,1,1,0,0,1,1,0,0,1,1],"col",solved))
    # print(existsInSudoku([0,0,1,0,0,1,1,0,1,0,1,1],"row",solved))
    # print(existsInSudoku([1,1,0,1,1,0,0,1,0,0,1,0],"col",solved))
    # print(getVariants(1, 2))
    # print(fitValuesFromAccaptables([[0,0,1,0,1],[0,0,1,1,1],[0,0,0,0,1],[1,0,1,0,1]]))
    # lne = [1,1,0,1,5,1,0,1,0,5,1,1,0,5,5,0]
    # ps = [0,4,9,14]
    # vl = [5,1,1,0]
    # insertIntoLine(ps,vl,lne)
    # print(lne)

