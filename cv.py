
import imp
from sqlite3 import sqlite_version_info
from time import sleep
from warnings import catch_warnings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException

import random
import numpy as np

driver = webdriver.Chrome('./chromedriver.exe')
action = ActionChains(driver)


height = 800
width = 1200
driver.set_window_size(width, height)
driver.get("https://minesweeperonline.com/#150")
game = driver.find_element(by=By.ID, value="game")

boardWidth = 30
boardHeight = 16

board = np.full((boardHeight, boardWidth), 99, dtype=np.uint8) # For an expert board

deathCount = [0]
pastLocs = [] # bad practice but lets roll with it for now

def main():
    playGame()

def clickSquare(x,y):
    identifier = str(y) + "_" + str(x)
    squareLink = game.find_element(by=By.ID, value=identifier)
    squareLink.click()

    try:
        alert = driver.switch_to.alert
        # alert.send_keys("ttv/trbarron")
        # action.send_keys("ttv/trbarron").perform()
        sleep(5039)
        # alert.accept()
        print("Alert switched to")
    except:
        linkClass = squareLink.get_attribute('class')

        # If the linkclass is a square_open0 then we've gotta update the whole picture
        if linkClass == "square open0":
            # for item in pastLocs:
            #     pastLocs.remove(item)
            # expandZeroFind(x-1, y-1)
            getBoardState()
        else: #Otherwise the only square that changed was the square we clicked, so we
                    # update that square only
            val = lookupVal(linkClass)
            board[y - 1][x - 1] = val
            if val == 58: return False
    return True

def clickRestart():
    game.find_element(by=By.CLASS_NAME, value="facedead").click()

def lookupVal(className):
    lookupTable={
        "blank": 99,
        "square blank": 99,
        "open0": 0,
        "square open0": 0,
        "open1": 1,
        "square open1": 1,
        "open2": 2,
        "square open2": 2,
        "open3": 3,
        "square open3": 3,
        "open4": 4,
        "square open4": 4,
        "open5": 5,
        "square open5": 5,
        "open6": 6,
        "square open6": 6,
        "open7": 7,
        "square open7": 7,
        "open8": 8,
        "square open8": 8,
        "bombflagged": 68,
        "square bombflagged": 68,
        "bombrevealed": 70,
        "square bombrevealed": 70,
        "square bombmrevealed": 70,
        "bombdeath": 58,
        "square bombdeath": 58,
    }

    return lookupTable[className]

def getBoardState():
    def updateBoardBasedOnClass(className):
        squares = game.find_elements(by=By.CLASS_NAME, value=className)
        for sq in squares:
            loc = sq.get_attribute('id')
            [y, x] = loc.split("_")
            y = int(y)
            x = int(x)

            if x > boardWidth or y > boardHeight or x <= 0 or y <= 0:
                continue
            else:
                board[y - 1][x - 1] = lookupVal(className)
        return
    
    # updateBoardBasedOnClass("blank")
    updateBoardBasedOnClass("open0")
    updateBoardBasedOnClass("open1")
    updateBoardBasedOnClass("open2")
    updateBoardBasedOnClass("open3")
    updateBoardBasedOnClass("open4")
    updateBoardBasedOnClass("open5")
    updateBoardBasedOnClass("open6")
    # updateBoardBasedOnClass("open7") #Should be included but omitting for SPEED
    # updateBoardBasedOnClass("open8") #Should be included but omitting for SPEED
    # updateBoardBasedOnClass("bombflagged")
    # updateBoardBasedOnClass("bombrevealed")

    #We've updated for each square type... now the board variable is correct

    return


def expandZeroFind(x,y):
    # X and Y are zero indexed
    identifier = str(y+1) + "_" + str(x+1)
    sq = game.find_element(by=By.ID, value=identifier)
    className = sq.get_attribute('class')
    board[y - 1][x - 1] = lookupVal(className)

    # Look left
    if ((x-1) >= 0) and (not [x-1, y] in pastLocs):
        pastLocs.append([x-1,y])
        expandZeroFind(x-1,y)
    
    # Look right
    if ((x+1) < boardWidth) and (not [x+1, y] in pastLocs):
        pastLocs.append([x+1,y])
        expandZeroFind(x+1,y)

    # Look up
    if ((y+1) < boardHeight) and (not [x, y+1] in pastLocs):
        pastLocs.append([x,y+1])
        expandZeroFind(x,y+1)
    
        # Look up
    if ((y-1) >= 0) and (not [x, y-1] in pastLocs):
        pastLocs.append([x,y-1])
        expandZeroFind(x,y-1)




def printBoardState():
    print("------------")
    for row in board:
        rowString = "| "
        for col in row:
            if len(str(col)) == 1:
                col = str(col) + " "
            rowString = rowString + "|" + str(col)
        rowString = rowString + " |"
        print(rowString)
    print("------------")




def playGame():
    while True:
        alive = True
        clickSquare(15,8)
        getBoardState()
        # printBoardState()
        while alive:
            findClearcutBombs()
            alive = clickRandomSquare()
        
        if not alive:
            deathCount[0] = deathCount[0] + 1
            print("Aww died: ", deathCount)
            # printBoardState()
            sleep(1)
            clickRestart()
            for x in range(boardWidth):
                for y in range(boardHeight):
                    board[y][x] = 99
            playGame()


def clickRandomSquare():
    foundSquare = False

    while not foundSquare:
        # print("random called")
        x = random.randint(0,boardWidth - 1)
        y = random.randint(0,boardHeight - 1)
        if board[y][x] == 99:
            onTopBoundary = False
            onBottomBoundary = False
            onLeftBoundary = False
            onRightBoundary = False

            #look left, right, up, down, diagonal
            # check to see if we're on a boundary
            if y == 0: onTopBoundary = True
            elif y == boardHeight - 1: onBottomBoundary = True

            if x == 0: onLeftBoundary = True
            elif x == boardWidth - 1: onRightBoundary = True

            #check up
            if not onTopBoundary:
                if not onLeftBoundary and board[y - 1][x - 1] != 99:
                    foundSquare = True
                elif board[y - 1][x] != 99: 
                    foundSquare = True
                elif not onRightBoundary and board[y - 1][x + 1] != 99:
                    foundSquare = True
            
            # check middle
            if not onLeftBoundary and board[y][x - 1] != 99:
                foundSquare = True
            if not onRightBoundary and board[y][x + 1] != 99:
                foundSquare = True
            
            #check down
            if not onBottomBoundary and not foundSquare:
                if not onLeftBoundary and board[y + 1][x - 1] != 99:
                    foundSquare = True
                elif board[y + 1][x] != 99: 
                    foundSquare = True
                elif not onRightBoundary and board[y + 1][x + 1] != 99:
                    foundSquare = True

    alive = clickSquare(x + 1, y + 1)
    return alive


def findClearcutBombs():

    def checkSq(x,y, neighboringEmptySquares, valSqOfInt):
        if board[y][x] == 99:
            neighboringEmptySquares.append([x,y])
        elif board[y][x] == 68:
            valSqOfInt -= 1
        return neighboringEmptySquares, valSqOfInt
    
    def incPtOfInt(ptOfInt):
        newPtOfInt = ptOfInt[0]
        newPtOfInt[1] += 1
        if newPtOfInt[1] == boardHeight:
            newPtOfInt[0] += 1
            newPtOfInt[1] = 0
        if newPtOfInt[0] == boardWidth:
            newPtOfInt[0] = 0
        return newPtOfInt


    lastPtOfInt = [[0,0]]
    ptOfInt = [[0,1]]
    livesLeft = [1]

    while not (ptOfInt[0] == lastPtOfInt[0] and livesLeft[0] == 0):
        x = ptOfInt[0][0]
        y = ptOfInt[0][1]
        sqOfInterest = board[y][x]

        if ptOfInt[0] == lastPtOfInt[0]:
            livesLeft[0] = 0

        # If its a 0, 68, 99 (empty0, bombflagged or blank) then we skip
        if sqOfInterest == 0 or sqOfInterest == 68 or sqOfInterest == 99:
            ptOfInt[0] = incPtOfInt(ptOfInt)
            continue

        # its a number so see if the empty squares around it have to be bombs
        neighboringEmptySquares = []
        onTopBoundary = False
        onBottomBoundary = False
        onLeftBoundary = False
        onRightBoundary = False

        valSqOfInt = sqOfInterest

        #look left, right, up, down, diagonal
        # check to see if we're on a boundary
        if y == 0: onTopBoundary = True
        elif y == boardHeight - 1: onBottomBoundary = True

        if x == 0: onLeftBoundary = True
        elif x == boardWidth - 1: onRightBoundary = True

        #check up
        if not onTopBoundary:
            if not onLeftBoundary: neighboringEmptySquares, valSqOfInt = checkSq(x-1, y - 1, neighboringEmptySquares, valSqOfInt)
            neighboringEmptySquares, valSqOfInt = checkSq(x, y - 1, neighboringEmptySquares, valSqOfInt)
            if not onRightBoundary: neighboringEmptySquares, valSqOfInt = checkSq(x + 1, y - 1, neighboringEmptySquares, valSqOfInt)
        
        # check middle
        if not onLeftBoundary: neighboringEmptySquares, valSqOfInt = checkSq(x-1, y, neighboringEmptySquares, valSqOfInt)
        if not onRightBoundary: neighboringEmptySquares, valSqOfInt = checkSq(x + 1, y, neighboringEmptySquares, valSqOfInt)
        
        #check down
        if not onBottomBoundary:
            if not onLeftBoundary: neighboringEmptySquares, valSqOfInt = checkSq(x-1, y + 1, neighboringEmptySquares, valSqOfInt)
            neighboringEmptySquares, valSqOfInt = checkSq(x, y + 1, neighboringEmptySquares, valSqOfInt)
            if not onRightBoundary: neighboringEmptySquares, valSqOfInt = checkSq(x + 1, y + 1, neighboringEmptySquares, valSqOfInt)

        if len(neighboringEmptySquares) == valSqOfInt:
            for sq in neighboringEmptySquares:
                identifier = str(sq[1] + 1) + "_" + str(sq[0] + 1)
                squareLink = game.find_element(by=By.ID, value=identifier)
                action.move_to_element(squareLink).context_click().perform()
                board[sq[1]][sq[0]] = 68
                lastPtOfInt[0] = sq
                livesLeft[0] = 1

        if valSqOfInt == 0:
            boardMax = board.max()
            if boardMax != 99:
                print("DONE")

            for sq in neighboringEmptySquares:
                clickSquare(sq[0] + 1,sq[1] + 1)  
                lastPtOfInt[0] = sq  
                livesLeft[0] = 1

        # add one to our point of interest and make sure to loop it appropriately
        ptOfInt[0] = incPtOfInt(ptOfInt)


if __name__ == "__main__":
    main()
