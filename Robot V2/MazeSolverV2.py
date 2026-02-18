global cellSize
global mazeInfo
global currentPosition
global movementStack
global endPosition
global InvisibleWallFix
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
# this is the website that i got this information from - https://api.vex.com/vr/home/playgrounds/dynamic_wall_maze.html
cellSize = 250

# this is a variable that deturmines weather the bugged maze has been fixed or not.
# i put this on a toggle so that i demonstrait that the robot chooses the shortest path
InvisibleWallFix = True 

# I will be storing the maze info as a dictionary with the key being the coodinates in relation to the origin,
# this will mean that the robot should be able to work for any size maze. The robot can also quickly check if
# it has been to a cell before by checking if it exists in the dictionary. The contents of each entry will be a list of
# the robot can access from that cell
mazeInfo = {}

# this is just a variable to track where the robot is in relation to the start of the maze.
currentPosition = (0, 0)
endPosition = ()

# a stack which will store the movements the robot has made, once it has reached a dead end, it can then pop off 
# of this stack until it reaches a point that it can start exploring the maze again
movementStack = []

# this method assumes that the entrence is at the bottom of the maze
# and that the end of the maze is at the top because the robot can leave the maze at these places
def SearchCell():
    global movementStack
    global endPosition
    global mazeInfo
    mazeInfo[currentPosition] = []
    exploredCells = list(mazeInfo.keys())
    isEnd = down_eye.detect(RED)

    if isEnd:
        endPosition = (currentPosition[0], currentPosition[1])
    
    # this bit of code gets the last move the robot made so that it wont look behind its self,
    # i initally set lastMove as "n" because it simulates the robot entering the maze.
    # this also stop a null error from occuring if the stack is empty.
    lastMove = "n"
    if len(movementStack) != 0:
        lastMove = movementStack[len(movementStack) - 1]
    
    currentX = currentPosition[0]
    currentY = currentPosition[1]

    # this will add the cell the robot just came from to the list of available cells for the robot to move to from
    # its current cell
    # the second check here makes sure that the robot doesnt think that there is a cell south of the start.
    if lastMove == "n" and currentPosition != (0, 0):
        mazeInfo[currentPosition].append((currentX, currentY - 1))
    elif lastMove == "e":
        mazeInfo[currentPosition].append((currentX - 1, currentY))
    elif lastMove == "s":
        mazeInfo[currentPosition].append((currentX, currentY + 1))
    elif lastMove == "w":
        mazeInfo[currentPosition].append((currentX + 1, currentY))
    
    # each direction has 2 checks. the first check makes sure that the direction hasnt been looked at before, 
    # the second check makes sure that the robot doesnt look in the direction that it just came from
    
    # checking north
    # the third check here makes sure that the robot doesnt leave the maze after finding the end
    if not (currentX, currentY + 1) in exploredCells and lastMove != "s" and not isEnd:
        drivetrain.turn_to_heading(0, DEGREES)
        isWallInfront = front_eye.detect(RED)
        if not isWallInfront:
            mazeInfo[currentPosition].append((currentX, currentY + 1))
    #checking east
    if not (currentX + 1, currentY) in exploredCells and lastMove != "w":
        drivetrain.turn_to_heading(90, DEGREES)
        isWallInfront = front_eye.detect(RED)
        if not isWallInfront:
            mazeInfo[currentPosition].append((currentX + 1, currentY))
    #checking south
    #the third check here makes sure that the robot doesnt leave the maze from the entrence
    if not (currentX, currentY - 1) in exploredCells and lastMove != "n" and currentPosition != (0, 0):
        drivetrain.turn_to_heading(180, DEGREES)
        isWallInfront = front_eye.detect(RED)
        if not isWallInfront:
            mazeInfo[currentPosition].append((currentX, currentY - 1))
    #checking west
    # I also need to have a check here so that on one of the mazes, 
    # the robot doesnt think there isnt a wall where there is one
    overide = False
    if InvisibleWallFix == True:
        # I can do this with the movement stack as i have checked all of the mazes and
        # the movement leading to this wall on both sides are unique
        lastMoveIndex = len(movementStack) - 1
        # the right side of the wall
        if currentPosition == (-3, 6):
            if movementStack[lastMoveIndex] == "w" and movementStack[lastMoveIndex - 1] == "w" and movementStack[lastMoveIndex - 2] == "n":
                overide = True
        if currentPosition == (-4, 6):
            if (-3,6) in list(mazeInfo.keys()):
                if not (-4, 6) in mazeInfo[(-3, 6)]:
                    overide = True

    if not (currentX - 1, currentY) in exploredCells and lastMove != "e" and overide == False:
        drivetrain.turn_to_heading(270, DEGREES)
        isWallInfront = front_eye.detect(RED)
        if not isWallInfront:
            mazeInfo[currentPosition].append((currentX - 1, currentY))

# just a method to move the robot
def MoveRobot(direction):
    global currentPosition
    global movementStack
    movementStack.append(direction)
    if direction == "n":
        drivetrain.turn_to_heading(0, DEGREES)
        drivetrain.drive_for(FORWARD, cellSize, MM)
        currentPosition = (currentPosition[0], currentPosition[1] + 1)
    if direction == "e":
        drivetrain.turn_to_heading(90, DEGREES)
        drivetrain.drive_for(FORWARD, cellSize, MM)
        currentPosition = (currentPosition[0] + 1, currentPosition[1])
    if direction == "s":
        drivetrain.turn_to_heading(180, DEGREES)
        drivetrain.drive_for(FORWARD, cellSize, MM)
        currentPosition = (currentPosition[0], currentPosition[1] - 1)
    if direction == "w":
        drivetrain.turn_to_heading(270, DEGREES)
        drivetrain.drive_for(FORWARD, cellSize, MM)
        currentPosition = (currentPosition[0] - 1, currentPosition[1])

# this method will make the robot backtrack by looking at the top of the movementStack and doing the oposite and
# then popping the top of the stack off.
def Backtrack():
    global movementStack
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
        if not currentPosition in searchedCells:
            SearchCell()
        # bot decides which way to go next by checking which cells around it it has not gone yet
        # the bot will check up, then left, then down and finally right
        #currentCellInfo = mazeInfo[currentPosition]
        possibleCells = mazeInfo[currentPosition]
        # the first check here makes sure that the cell hasnt been explored yet, the secnd check makes sure that
        # the robot can move into that cell
        if not (currentPosition[0], currentPosition[1] + 1) in searchedCells and (currentPosition[0], currentPosition[1] + 1) in possibleCells:
            MoveRobot("n")
        elif not (currentPosition[0] + 1, currentPosition[1]) in searchedCells and (currentPosition[0] + 1, currentPosition[1]) in possibleCells:
            MoveRobot("e")
        elif not (currentPosition[0], currentPosition[1] - 1) in searchedCells and (currentPosition[0], currentPosition[1] - 1) in possibleCells:
            MoveRobot("s")
        elif not (currentPosition[0] - 1, currentPosition[1]) in searchedCells and (currentPosition[0] - 1, currentPosition[1]) in possibleCells:
            MoveRobot("w")
        else:
            # when logic gets to this point, it means that all of the available cells around the robot have been searched
            # if the stack is empty, this means that the maze has been completely searched.
            # if it isnt empty, it means that the robot is at a dead end.
            if len(movementStack) == 0:
                return
            else:
                Backtrack()

# this method is just used to help me debug, all it does is print out the dictionarry containing the maze info
# it will output the letters of the direction where there are walls.
def PrintMazeInfo():
    searchedCells = list(mazeInfo.keys())
    brain.new_line()
    brain.print("NEW INFO")
    for i in range (0, len(searchedCells)):
        brain.new_line()
        brain.print(f"{searchedCells[i]} : {mazeInfo[searchedCells[i]]}")

# this method will handle searching for the shortest path from the entrence to the exit
# with this method, i have tried to implement dijkstra algorithm.
# i used this video as a guide to implement thiis algorithm - https://www.youtube.com/watch?v=LGiRB_lByh0
def FindShortestPathToExit():
    start = (0, 0)
    unvisitedCells = {cell : float("inf") for cell in mazeInfo}
    unvisitedCells[(0, 0)] = 0
    visitedCells = {}
    reversePath = {}

    while len(unvisitedCells) != 0:
        currentCell = min(unvisitedCells, key = unvisitedCells.get)
        visitedCells[currentCell] = unvisitedCells[currentCell]
        
        if currentCell == endPosition:
            break

        cellNeighbors = mazeInfo[currentCell]
        for i in range(0, len(cellNeighbors)):
            if cellNeighbors[i] in visitedCells:
                continue
            tempDistance = unvisitedCells[currentCell] + 1

            if tempDistance < unvisitedCells[cellNeighbors[i]]:
                unvisitedCells[cellNeighbors[i]] = tempDistance
                reversePath[cellNeighbors[i]] = currentCell
        
        unvisitedCells.pop(currentCell)

    # now that we have a list of cells that will lead to the end, i need to reverse engineer it into a list
    # of directions that will lead to the exit
    path = []
    visitedCoordinates = list(reversePath.keys())
    currentCell = endPosition
    while currentCell != (0, 0):
        previousCell = reversePath[currentCell]
        #check if the robot needs to move north
        if currentCell[1] == previousCell[1] + 1:
            path.append("n")
        #check if the robot needs to move east
        elif currentCell[0] == previousCell[0] + 1:
            path.append("e")
        #check if the robot needs to move south
        elif currentCell[1] == previousCell[1] - 1:
            path.append("s")
        #check if the robot needs to move west
        elif currentCell[0] == previousCell[0] - 1:
            path.append("w")
        currentCell = previousCell
    path.reverse()
    return path

# this function just makes the robot follow a list of directions and draw a line behind its self
def FollowPath(path):
    pen.move(DOWN)
    for i in range (0, len(path)):
        MoveRobot(path[i])
    pen.move(UP)

# this function will return the bot to the start
def BackToStart():
    while len(movementStack) != 0:
        Backtrack()

#this function outputs the information the robot has gathered about the maze in a visual format
def PrintMappedMaze():
    topRightCell = max(mazeInfo.keys())
    bottomLeftCell = min(mazeInfo.keys())
    mazeWidth = abs(bottomLeftCell[0] - topRightCell[0])
    mazeHieght = abs(bottomLeftCell[1] - topRightCell[1])
    printList = [["-"]*((mazeWidth * 2) + 3)]*((mazeHieght * 2) + 3)

    for y in range(topRightCell[1], bottomLeftCell[1] - 1, -1):
        line1 = ["#"]
        line2 = ["#"]
        for x in range(bottomLeftCell[0], topRightCell[0] + 1):
            cellInfo = mazeInfo[x, y]
            wallNorth = not (x, y + 1) in cellInfo
            wallEast = not (x + 1, y) in cellInfo
            if (x, y) == endPosition:
                line2.append("E")
            elif(x,y) == (0, 0):
                line2.append("S")
            else:
                line2.append(" ")
                
            if wallNorth:
                line1.append("#")
            else:
                line1.append(" ")
            if wallEast:
                line2.append("#")
            else:
                line2.append(" ")
            line1.append("#")
        brain.new_line()
        for i in range(0, len(line1)):
            brain.print(line1[i])
        brain.new_line()
        for i in range(0, len(line2)):
            brain.print(line2[i])
    brain.new_line()
    brain.print("#"* ((mazeWidth * 2) + 3))

def when_started1():
    brain.clear()
    SearchMaze()
    PrintMappedMaze()
    searchMazeTime = brain.timer_time(SECONDS)
    brain.new_line()
    brain.print(f"Time taken to search maze: {searchMazeTime} seconds")
    shortestPath = FindShortestPathToExit()
    brain.timer_reset()
    FollowPath(shortestPath)
    completeTime = brain.timer_time(SECONDS)
    brain.new_line()
    brain.print(f"Time taken to complete maze: {completeTime} seconds")
    brain.new_line()
    brain.print(f"Total time taken: {completeTime + searchMazeTime} seconds")
    brain.new_line()
    brain.print("Directions for the fastest route to the exit: ")
    for i in range(0,len(shortestPath)):
        brain.print(f"{shortestPath[i]}, ")
    BackToStart()
    stop_project()
    pass

vr_thread(when_started1)