global cellSize
global mazeInfo
global currentPosition
global movementStack
global endPosition
#region VEXcode Generated Robot Configuration
import math
import random
from vexcode_vr import *

# Brain should be defined by default
brain=Brain()

drivetrain = Drivetrain("drivetrain", 0)
pen = Pen("pen", 8)
pen.set_pen_width(THIN)
left_bumper = Bumper("leftBumper", 2)
right_bumper = Bumper("rightBumper", 3)
front_eye = EyeSensor("frontEye", 4)
down_eye = EyeSensor("downEye", 5)
front_distance = Distance("frontdistance", 6)
distance = front_distance
magnet = Electromagnet("magnet", 7)
location = Location("location", 9)

#endregion VEXcode Generated Robot Configuration
# just settiing the speed of the robot to the maximum value
drivetrain.set_drive_velocity(100, PERCENT)
drivetrain.set_turn_velocity(100, PERCENT)

# I found documentation that the maze is 2000mm by 2000mm, the maze is 8 by 8 cells,
# meaning that each cell is 250mm by 250mm
cellSize = 250

# I will be storing the maze info as a dictionary with the key being the coodinates in relation to the origin,
# this will mean that the robot should be able to work for any size maze. The robot can also quickly check if
# it has been to a cell before by checking if it exists in the dictionary
mazeInfo = {}

# this is just a variable to track where the robot is in relation to the start of the maze.
currentPosition = [0, 0]
endPosition = []

# a stack which will store the movements the robot has made, once it has reached a dead end, it can then pop off 
# of this stack until it reaches a point that it can start exploring the maze again
movementStack = []

# this class will store info about tbe cell
# it stores wether a direction has a wall and if a cell is the end cell
class CellInfo:
    north = False
    east = False
    south = False
    west = False
    isEnd = False

fullySearched = False

# this method assumes that the entrence is at the bottom of the maze
# and that the end of the maze is at the top because the robot can leave the maze at these places
def SearchCell():
    global endPosition
    global mazeInfo
    posistionString = f"{currentPosition[0]}, {currentPosition[1]}"
    mazeInfo[posistionString] = CellInfo()
    isEnd = down_eye.detect(RED)

    if isEnd:
        endPosition = [currentPosition[0], currentPosition[1]]
        mazeInfo[posistionString].north = True

    if currentPosition[0] == 0 and currentPosition[1] == 0:
        mazeInfo[posistionString].south = True
    
    # this bit of code gets the last move the robot made so that it wont look behind its self,
    # i initally set lastMove as "n" because it simulates the robot entering the maze.
    # this also stop a null error from occuring if the stack is empty.
    lastMove = "n"
    if len(movementStack) != 0:
        lastMove = movementStack[len(movementStack) - 1]

    # each direction has 2 checks. the first check makes sure that the direction hasnt been looked at before, 
    # the second check makes sure that the robot doesnt look in the direction that it just came from
    if not mazeInfo[posistionString].north and lastMove != "s":
        drivetrain.turn_to_heading(0, DEGREES)
        mazeInfo[posistionString].north = front_eye.detect(RED)

    if not mazeInfo[posistionString].east and lastMove != "w":
        drivetrain.turn_to_heading(90, DEGREES)
        mazeInfo[posistionString].east = front_eye.detect(RED)

    if not mazeInfo[posistionString].south and lastMove != "n":
        drivetrain.turn_to_heading(180, DEGREES)
        mazeInfo[posistionString].south = front_eye.detect(RED)

    if not mazeInfo[posistionString].west and lastMove != "e":
        drivetrain.turn_to_heading(270, DEGREES)
        mazeInfo[posistionString].west = front_eye.detect(RED)

# just a method to move the robot
def MoveRobot(direction):
    movementStack.append(direction)
    if direction == "n":
        drivetrain.turn_to_heading(0, DEGREES)
        drivetrain.drive_for(FORWARD, cellSize, MM)
        currentPosition[1] += 1
    if direction == "e":
        drivetrain.turn_to_heading(90, DEGREES)
        drivetrain.drive_for(FORWARD, cellSize, MM)
        currentPosition[0] += 1
    if direction == "s":
        drivetrain.turn_to_heading(180, DEGREES)
        drivetrain.drive_for(FORWARD, cellSize, MM)
        currentPosition[1] -= 1
    if direction == "w":
        drivetrain.turn_to_heading(270, DEGREES)
        drivetrain.drive_for(FORWARD, cellSize, MM)
        currentPosition[0] -= 1

# this method will make the robot backtrack by looking at the top of the movementStack and doing the oposite and
# then popping the top of the stack off.
def BackTrack():
    topOfStack = movementStack.pop()
    if topOfStack == "n":
        MoveRobot("s")
    if topOfStack == "e":
        MoveRobot("w")
    if topOfStack == "s":
        MoveRobot("n")
    if topOfStack == "w":
        MoveRobot("e")
    # i need to pop the top of the stack off again because the moveRobot method adds the last movement to the stack
    # and i did not feel like it was worth it to make a new movement method without this functionality
    movementStack.pop()

# this is the method that will handle all of the logic for when the robot is mapping out the maze
def SearchMaze():
    searching = True
    while searching:
        searchedCells = list(mazeInfo.keys())
        if not f"{currentPosition[0]}, {currentPosition[1]}" in searchedCells:
            SearchCell()
        # bot decides which way to go next by checking which cells around it it has not gone yet
        # the bot will check up, then left, then down and finally right
        currentCellInfo = mazeInfo[f"{currentPosition[0]}, {currentPosition[1]}"]
        if not f"{currentPosition[0]}, {currentPosition[1] + 1}" in searchedCells and currentCellInfo.north == False:
            MoveRobot("n")
        elif not f"{currentPosition[0] + 1}, {currentPosition[1]}" in searchedCells and currentCellInfo.east == False:
            MoveRobot("e")
        elif not f"{currentPosition[0]}, {currentPosition[1] - 1}" in searchedCells and currentCellInfo.south == False:
            MoveRobot("s")
        elif not f"{currentPosition[0] - 1}, {currentPosition[1]}" in searchedCells and currentCellInfo.west == False:
            MoveRobot("w")
        else:
            # when logic gets to this point, it means that all of the available cells around the robot have been searched
            # if the stack is empty, this means that the maze has been completely searched.
            # if it isnt empty, it means that the robot is at a dead end.
            if len(movementStack) == 0:
                searching = False
            else:
                BackTrack()
        #PrintMazeInfo()

# this method is just used to help me debug, all it does is print out the dictionarry containing the maze info
# it will output the letters of the direction where there are walls.
def PrintMazeInfo():
    searchedCells = list(mazeInfo.keys())
    brain.new_line()
    brain.print("NEW INFO")
    for i in range (0, len(searchedCells)):
        outputString = ""
        cellInfo = mazeInfo[searchedCells[i]]
        if cellInfo.north == True:
            outputString += "n"
        if cellInfo.east == True:
            outputString += "e"
        if cellInfo.south == True:
            outputString += "s"
        if cellInfo.west == True:
            outputString += "w"
        brain.new_line()
        brain.print(f"{searchedCells[i]} : {outputString}")

# this method will be used by the shortest path algithm to get the cells that neighbor the inputted cell
def getNeighbors(cell):
    neighbors = []
    #cellInfo = mazeInfo[f"{cell[0]}, {cell[1]}"]
    cellInfo = mazeInfo[cell]

    # just processing the input string 
    coordinates = cell.split(", ")

    if not cellInfo.north:
        neighbors.append([cell[0], cell[1] + 1])
    if not cellInfo.east:
        neighbors.append([cell[0] + 1, cell[1]])
    if not cellInfo.south:
        neighbors.append([cell[0], cell[1] - 1])
    if not cellInfo.west:
        neighbors.append([cell[0] - 1, cell[1]])
     
    return neighbors

# this method will handle searching for the shortest path from the entrence to the exit
# with this method, i have tried to implement dijkstra algorithm.
def FindShortestPathToExit():
    path = []
    
    distanceFromStart = {cell : float("inf") for cell in mazeInfo}
    distanceFromStart["0, 0"] = 0

    previousCells = {}
    unvisitedCells = list(mazeInfo.keys())

    while len(unvisitedCells) != 0:
        # this bit of code just gets the cell that is closest to the start and has not been visited. 
        currentCell = min(unvisitedCells, key = lambda cell : distanceFromStart[cell])

        posistionString = f"{currentCell[0]}, {currentCell[1]}"

        #this just ends the search when it reaches the end of the maze
        if currentCell == endPosition:
            break

        unvisitedCells.remove(currentCell)

        neighboringCells = getNeighbors(posistionString)
        for i in range (0, len(neighboringCells)):
            if neighboringCells[i] in unvisitedCells:
                currentDistence = distanceFromStart[posistionString] + 1
                neighborCellPositionString = f"{neighboringCells[i][0]}, {neighboringCells[i][1]}"
                if currentDistance < distanceFromStart[neighborCellPositionString]:
                    distanceFromStart[neighborCellPositionString] = currentDistence
                    previousCells[neighborCellPositionString] = posistionString

    brain.print(previousCells)
    return path

def when_started1():
    #map maze - done
    #find shorest path to end of maze
    #turn on pen
    #get to end of maze
    #fix the bug of the robot moving though the wall between -3, 6 and -4, 6 on that buggy maze
    #maybe output a visual output of the maze? 
    SearchMaze()
    shortestPath = FindShortestPathToExit()
    stop_project()
    pass

vr_thread(when_started1)
