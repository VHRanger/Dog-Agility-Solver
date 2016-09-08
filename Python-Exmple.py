import numpy as np
from numba import jit


##############################
#Example Data
##############################

#Time constraint in seconds
TIME = 30

#Dog land speed in ft/sec
speed = 14.5

#Current location coordinates recorded as a 2 element vector [x,y]
#Initialized to 0 for free start location
location = np.array([0,0])

#Example Final Location (Dog must finish any course at this location)
finalLoc = np.array([25,52])

#Translate obstacle integer-type value to obstacle name
def IntToObs(num):
   return{
    0:'Jump',
    1:'Tunnel',
    2:'Tire',
    3:'Long Jump',
    4:'Spread Jump',
    5:'SeeSaaw',
    6:'Weaves 6 poles',
    7:'Weaves 12 poles',
    8:'A-Frame',
    9:'DogWalk'
}.get(num, 'Error Conversion Obstacle -> Name')

#Example time cost to traverse obstacle type
#index refers to type in "IntToObs"
obstacleTime = np.array([0.3, 1.5, 0.3, 0.3, 0.3, 1.1, 1.9, 3.8, 1.2, 2.3])

#Example points for traversing an obstacle type. Indexed same as in IntToObs()
obstaclePoints = np.array([1, 2, 2, 2, 2, 3, 3, 5, 4, 5])

#Example Data Matrix for obstacles
#Each row represents an obstacle
#First column is obstacle type 0->9. Indexed same as in IntToObs()
#Second and third columns are entry location on map [x,y]
#fourth and fifth is for obstacle exit for long obstacles (else value = [x,y])
#sixth is counter of times the obstacle is allowed to be traversed
obstacles = np.array([
    [0, 40, 10, 40, 10, 2],
    [0, 60, 10, 60, 10, 2],
    [0, 35, 35, 35, 35, 2],
    [0, 55, 30, 50, 30, 2],
    [0, 72, 33, 72, 33, 2],
    [0, 85, 22, 85, 22, 2],
    [0, 68, 48, 68, 48, 2],
    [0, 35, 72, 35, 72, 2],
    [9, 88, 40, 88, 73, 2],
    [1, 93, 40, 85, 47, 2],
    [1, 70, 92, 85, 92, 2],
    [5, 47, 45, 40, 52, 2],
    [0, 20, 10, 20, 10, 2],
    [8, 55, 68, 60, 80, 2]])

##################
#END EXAMPLE DATA
##################

 
@jit 
def SortObs(start, obs):
    """
    Sort obstacles by distance from current position
    input:
        start is current location
        obs is a "obstacles" type np.array
    returns:
        array of indeces of obstacles, sorted
            by distance from start.
        Example: [3,2,4,1] means 3 is closest, 1 furthest    
    """
    #array of distance from current position
    distArr = np.array([])
    for i in range(len(obs)):
        distArr = np.append(distArr,
                    np.sqrt((obs[i, 1] - start[0])**2 + (obs[i, 2] - start[1])**2))
                    
    #add column with distance to from current obs
    obs = np.c_[obs, np.zeros(len(obs))]
    for i in range(len(obs)):
        obs[i, 6] = distArr[i]
        
    #sort by distance
    #obs = obs[np.argsort(obs[:, 6])]
    return obs[:,6].argsort()

@jit
def BnB(start, parentObs, TIME, speed, finalLoc, obsPts, obsTime, solnLst=np.array([]), 
        currentPts=0, startLoc = False, Bound=0.5, SortedObs = np.array([])):
    """
    Divide and conquer + B&B, retains recursive max at each node
    Bound fct is heuristic. 
    Heuristic based on Bound parameter searching only Bound% closest obstacles
    Input:
        start is current location
        parentObs is obs array passed from parent node
        TIME is remaining time, speed land speed in ft/sec
        finalLoc is end location of course
        obsPts and obsTime are np.array of length 10, with points/time 
            for traversing obstacle of respective index (reference: IntToObs fct)
        solnLst and currentPts is used for recursion, do not touch
        startLoc is a heuristic forcing closest obstacle to be chosen first (default off)
        Bound is B&B heuristic parameter. Set it to what you want.
        SortedObs is also used for recursion
    returns: 
        optimal value (float), solution (np.arr)
    """
    #copy parent info to update from child nodes
    obs = np.copy(parentObs)
    CurrentValue = np.copy(currentPts)
    solution = np.copy(solnLst)
    
    #get sorted list of obst index by distance from current location
    #memoize on first pass for every obstacle
    if len(SortedObs) < 1:
        SortedObs = np.zeros((len(obs), len(obs)))
        for i in range(len(obs)):
            SortedObs[i] = SortObs(obs[i, 3:5], obs)
    
    #startLoc heuristic
    #start with closest obstacle if on first pass
    if startLoc == True:
        distArr = np.array([])
        for i in range(len(obs)):
            distArr = np.append(distArr,
                        np.sqrt((obs[i, 1] - start[0])**2 + (obs[i, 2] - start[1])**2))
        closest = int(np.argmin(distArr))
        #update info for now being at closest obstacle
        CurrentValue += obsPts[obs[closest, 0]]
        start[0] = obs[closest, 3]
        start[1] = obs[closest, 4]
        TIME = TIME - (distArr[closest] / speed) - obsTime[obs[closest, 0]]
    
    #get current location in terms of obstacle index
    for i in range(len(obs)):
        if start[0] == obs[i,3] and start[1] == obs[i,4]:
            CurrentLoc = i
    
    #Only search the Bound% closest obstacles
    SL = int(len(SortedObs[CurrentLoc])*Bound)
    #Branch for each obstacle in ascending distance, and stop branching at bound
    for i in SortedObs[CurrentLoc, :SL]:
        #Force prevent obstacle double take and taking obstacles taken twice
        if start[0] == obs[i,3] and start[1] == obs[i,4]: continue
        if obs[i, 5] == 0: continue
        #get distance & remaining time
        obsDistance = np.sqrt((obs[i, 1] - start[0])**2 + (obs[i, 2] - start[1])**2)
        remainTime = TIME - (obsDistance / speed) - obsTime[obs[i, 0]]
        timeToFinal = remainTime - (np.sqrt((obs[i, 1] - finalLoc[0])**2 + (obs[i, 2] - finalLoc[1])**2)
                                    )/speed
        #if solution feasible, compute maximum recursively
        if timeToFinal > 0:
            newObs = obs
            newObs[i,5] -= 1
            newPts = currentPts + obsPts[newObs[i,0]]
            nodeSoln = np.append(solnLst, i)
            nodeValue, nodeSoln = BnB(newObs[i, 3:5], newObs, remainTime, speed, finalLoc, 
                                        obsPts, obsTime, nodeSoln, newPts, startLoc = False, 
                                        Bound = Bound, SortedObs = SortedObs)
            if nodeValue > CurrentValue: 
                CurrentValue = nodeValue
                solution = nodeSoln
    #If at root, append startloc heuristic
    if startLoc == True:
        distArr = np.array([])
        for i in range(len(obs)):
            distArr = np.append(distArr,
                        np.sqrt((obs[i, 1] - start[0])**2 + (obs[i, 2] - start[1])**2))
        closest = int(np.argmin(distArr))
        solution = np.insert(solution, 0, closest)
    return CurrentValue, solution
    
BnB(location, obstacles, TIME, speed, finalLoc, obstaclePoints, obstacleTime, Bound = 0.4)

print (Result[0], Result[1])