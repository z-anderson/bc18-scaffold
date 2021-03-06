import battlecode as bc
import random
import sys
import traceback
import os
import time


gc = bc.GameController()
directions = [bc.Direction.North, bc.Direction.Northeast, bc.Direction.East, bc.Direction.Southeast, bc.Direction.South, bc.Direction.Southwest, bc.Direction.West, bc.Direction.Northwest]
allDirections = list(bc.Direction)#includes center, and is weirdly ordered
tryRotate = [0,-1,1,-2,2]
random.seed(6137)
my_team = gc.team()
if my_team==bc.Team.Red:enemy_team = bc.Team.Blue
else: enemy_team = bc.Team.Red


class mmap():
    def __init__(self,width,height):
        self.width=width
        self.height=height
        self.arr=[[0]*self.height for i in range(self.width)];
    def onMap(self,loc):
        if (loc.x<0) or (loc.y<0) or (loc.x>=self.width) or (loc.y>=self.height): return False
        return True
    def get(self,mapLocation):
        if not self.onMap(mapLocation):return -1
        return self.arr[mapLocation.x][mapLocation.y]
    def set(self,mapLocation,val):
        self.arr[mapLocation.x][mapLocation.y]=val
    def printout(self):
        print('printing map:')
        for y in range(self.height):
            buildstr=''
            for x in range(self.width):
                buildstr+=format(self.arr[x][self.height-1-y],'2d')
            print(buildstr)
    def addDisk(self,mapLocation,r2,val):
        locs = gc.all_locations_within(mapLocation,r2)
        for loc in locs:
            if self.onMap(loc):
                self.set(loc,self.get(loc)+val)
    def multiply(self,mmap2):
        for x in range(self.width):
            for y in range(self.height):
                ml = bc.MapLocation(bc.Planet.Earth,x,y);
                self.set(ml,self.get(ml)*mmap2.get(ml))
    def findBest(self,mapLocation,r2):
        locs = gc.all_locations_within(mapLocation,r2)
        bestAmt = 0
        bestLoc = None
        for loc in locs:
            amt = self.get(loc)
            if amt>bestAmt:
                bestAmt=amt
                bestLoc=loc
        return bestAmt, bestLoc


class vector:
    def __init__(self, x, y=None):
        if isinstance(x, int):
            self.x = x
            self.y = y
        else:
            self.x = x[0]
            self.y = x[1]

    def __add__(self, v2):
        return vector(self.x + v2.x, self.y + v2.y)

    def __sub__(self, v2):
        return vector(self.x - v2.x, self.y - v2.y)

    def __mul__(self, v2):
        if isinstance(v2, int) == 1:
            return vector(self.x * v2, self.y * v2)
        else:
            return vector(self.x * v2.x, self.y * v2.y)

    def dist2(self, v2):
        return (v2.x - self.x) ** 2 + (v2.y - self.y) ** 2

    def dirTo(self, v2):
        closestDist = 100000000
        for i in range(len(direction.getVs())):
            testDir = direction(i)
            testLoc = self + testDir
            testDist = testLoc.dist2(v2)
            if testDist < closestDist:
                closestDist = testDist
                closestDir = testDir
            return closestDir

    def of(self, arr):
        return arr[self.x][self.y]

    def set(self, arr, val):
        arr[self.x][self.y] = val

    def __str__(self):
        return 'vector(' + str(self.x) + ',' + str(self.y) + ')'

    def __eq__(self, v2):
        return (self.x == v2.x) & (self.y == v2.y)

    def cross(self, v2):
        return -self.y * v2.x + self.x * v2.y

#also for pathfinding
class direction(vector):
    vs = (vector(0, -1), vector(1,-1), vector(1, 0), vector(1,1), \
          vector(0, 1), vector(-1,1), vector(-1, 0), vector(-1,-1))

    def __init__(self, d):
        if isinstance(d, int):
            self.index = d
        else:
            self.index = direction.getVs().index(d)
        self.update()

    def update(self):
        self.v = direction.getVs()[self.index]
        self.x = self.v.x
        self.y = self.v.y

    def rotateRight(self):
        self.rotateAmount(1)

    def rotateLeft(self):
        self.rotateAmount(-1)

    def rotateAmount(self, n):
        self.index = (self.index + n) % len(direction.getVs())
        self.update()

    @classmethod
    def getVs(cls):
        return cls.vs

    @classmethod
    def getDs(cls):
        return [direction(i) for i in range(len(direction.getVs()))]

#
# #tile in map for pathfinding
# class tile:
#     def __init__(self, loc, dist):
#         self.loc = loc
#         self.dist = dist
#         self.dirs = [0, 0, 0, 0, 0, 0, 0, 0]
#         self.width = 0
#
#     def getDirs(self):
#         dirs = []
#         for i in range(len(self.dirs)):
#             if self.dirs[i] == 1: dirs.append(direction(i))
#         return dirs
#
#     def addDir(self, dir, dist):
#         if dist < self.dist: self.dist = dist
#         self.dirs[dir.index] = 1
#
#     def __str__(self):
#         return 'tile(dist=' + str(self.dist) + ',dirs=' + str(self.dirs) + ',width=' + str(self.width)
#


def invert(loc):#assumes Earth
    newx = earthMap.width-loc.x
    newy = earthMap.height-loc.y
    return bc.MapLocation(bc.Planet.Earth,newx,newy)

def locToStr(loc):
    return '('+str(loc.x)+','+str(loc.y)+')'

def onEarth(loc):
    if (loc.x<0) or (loc.y<0) or (loc.x>=earthMap.width) or (loc.y>=earthMap.height): return False
    return True


#for pathfinding
class pathing:

    def __init__(self, map, start, end):
        self.map = map
        self.w = len(self.map)
        self.h = len(self.map[0])
        self.md = [[0] * self.h for i in range(self.w)]
        for i in range(self.w):
            for j in range(self.h):
                self.md[i][j] = [[0,0,0,0,0,0,0,0],1000]
        self.start = vector(start)
        self.md[self.start.x][self.start.y][1] = 0
        self.end = vector(end)
        self.cpts = []
        self.cpts.append(self.start)
        self.dist = 0
        self.state = 'spread'
        self.path = []
        self.return_dist = 0
        self.vdirs = (vector(0, -1), vector(1, -1), vector(1, 0), vector(1, 1), \
                     vector(0, 1), vector(-1, 1), vector(-1, 0), vector(-1, -1))

    def isOpen(self, loc, dist):
        onMap = (loc.x >= 0) & (loc.x < self.w) & (loc.y >= 0) & (loc.y < self.h)
        if not onMap: return False
        traversable = self.map[loc.x][loc.y] == 0
        acceptablePathLength = dist <= self.md[loc.x][loc.y][1]
        return traversable & acceptablePathLength

    def nextStep(self):
        if self.state == 'spread':
            nextPoints = []
            for p in self.cpts:
                for d in range(8):
                    ahead = p + self.vdirs[d]
                    if self.isOpen(ahead,self.dist):
                        self.md[ahead.x][ahead.y][0][d] = 1
                        self.md[ahead.x][ahead.y][1] = self.dist
                        if not ahead in nextPoints: nextPoints.append(ahead)
            if len(nextPoints) == 0:
                self.state = 'return'
                self.cpts = [self.end]
            else:
                self.cpts = nextPoints
            self.dist += 1
        elif self.state == 'return':
            nextPoints = []
            for p in self.cpts:
                temp_dirs = self.md[p.x][p.y][0]
                for ind in range(len(temp_dirs)):
                    if temp_dirs[ind] == 1:
                        newdir = (ind+4)%8  # flip backwards ------------------------------
                        behind = p + self.vdirs[newdir]
                        # behind.of(self.md).width = len(self.cpts)
                        if not behind in nextPoints: nextPoints.append(behind)
            self.path.extend(self.cpts)
            self.cpts = nextPoints
            if len(nextPoints) == 0:
                self.state = 'arrived'
                self.return_dist -= 1 # to account for extra step
            self.return_dist += 1




class pathMap:
    def __init__(self, planet): #bc.Planet.... (delete?)
        self.p = planet
        self.pMap = gc.starting_map(self.p)
        self.w = self.pMap.width
        self.h = self.pMap.height
        self.pathMap = [[0]*self.h for i in range(self.w)] # array[x,y]
        self.dirdict = [bc.Direction.North, bc.Direction.Northwest, \
                        bc.Direction.West, bc.Direction.Southwest, \
                        bc.Direction.South, bc.Direction.Southeast,\
                        bc.Direction.East, bc.Direction.Northeast]
        # map for pathfinding/next_move
        for x in range(self.w):
            for y in range(self.h):
                mapLoc = bc.MapLocation(self.p, x, y)
                if not self.pMap.is_passable_terrain_at(mapLoc):
                    self.pathMap[x][y] = 2  # 2 representing not passable terrain

    def update_pathmap_units(self,Unit = None): # updates the pathfinding map with current units. use update before using next move!
        for x in range(self.w):
            for y in range(self.h):
                maploc = bc.MapLocation(self.p,x,y)
                if gc.can_sense_location(maploc):
                    if self.pathMap[x][y] != 2:
                        if gc.has_unit_at_location(maploc):
                            if gc.sense_unit_at_location(maploc):
                                self.pathMap[x][y] = 1
                        else:
                            self.pathMap[x][y] = 0
        if Unit: self.pathMap[Unit.location.map_location().x][Unit.location.map_location().y] = 0

    # input like (x,y); map should be 2D array; '0' on the map means not traversable, returns Direction
    def next_move(self, start_maploc, end_maploc):
        end_loc = (start_maploc.x,start_maploc.y)
        start_loc = (end_maploc.x,end_maploc.y)
        mypath = pathing(self.pathMap, start_loc, end_loc)
        while mypath.state == 'spread':
            mypath.nextStep()

        dirs = mypath.md[mypath.end.x][mypath.end.y][0]
        print(dirs)
        print(dirs.index(1))
        next_mo = self.dirdict[dirs.index(1)] # since there are many options for going back, I default to the first... this can change

        while mypath.state == 'return':
            mypath.nextStep()

        return next_mo, mypath.return_dist



class Kmap:
    def __init__(self, planet):
        self.p = planet
        self.pMap = gc.starting_map(self.p)
        self.w = self.pMap.width
        self.h = self.pMap.height
        self.Kmap = [[0]*self.h for i in range(self.w)] # array[x,y]
        for x in range(self.w):
            for y in range(self.h):
                ml = bc.MapLocation(self.p,x,y)
                self.Kmap[x][y] = self.pMap.initial_karbonite_at(ml)

    def update_kmap(self): #update karbonite map
        for x in range(self.w):
            for y in range(self.h):
                ml = bc.MapLocation(self.p, x, y)
                if gc.can_sense_location(ml):
                    self.Kmap[x][y] = gc.karbonite_at(ml)

    def closest_K(self,unit): # by radius?
        minDist = 1000
        closestk = None
        myLoc = unit.location.map_location()
        for x in range(self.w):
            for y in range(self.h):
                if self.Kmap[x][y] != 0:
                    d2 = (x-myLoc.x)**2 + (y-myLoc.y)**2
                    if d2 < minDist:
                        minDist = d2
                        closestk = bc.MapLocation(self.p, x, y)

        if closestk:
            return minDist, closestk
        else:
            return None #no karbonite

if gc.planet() == bc.Planet.Mars:
    marsPathMap = pathMap(bc.Planet.Mars)
    rocket_locations = []

if gc.planet() == bc.Planet.Earth:
    gc.queue_research(bc.UnitType.Worker)
    gc.queue_research(bc.UnitType.Ranger)
    gc.queue_research(bc.UnitType.Rocket)
    gc.queue_research(bc.UnitType.Mage)
    gc.queue_research(bc.UnitType.Ranger)
    gc.queue_research(bc.UnitType.Ranger)
    gc.queue_research(bc.UnitType.Mage)

    oneLoc = gc.my_units()[0].location.map_location()
    loadStart = time.time()
    earthMap = gc.starting_map(bc.Planet.Earth)

    path_map = pathMap(bc.Planet.Earth)
    print(path_map.pathMap)
    path_map.update_pathmap_units()
    k_map = Kmap(bc.Planet.Earth)

    loadEnd = time.time()
    print('loading the map took '+str(loadEnd-loadStart)+'s')
    enemyStart = invert(oneLoc);
    print('worker starts at '+locToStr(oneLoc))
    print('enemy worker presumably at '+locToStr(enemyStart))

    #test out addDisk function
    tmap = mmap(earthMap.width,earthMap.height)
    tmap.addDisk(bc.MapLocation(bc.Planet.Earth,1,5),30,1)
    tmap.addDisk(bc.MapLocation(bc.Planet.Earth,3,10),30,1)
    tmap.printout()

    #store the map locally
    storageStart=time.time()
    passableMap = mmap(earthMap.width,earthMap.height);
    kMap = mmap(earthMap.width,earthMap.height);
    for x in range(earthMap.width):
        for y in range(earthMap.height):
            ml = bc.MapLocation(bc.Planet.Earth,x,y);
            passableMap.set(ml,earthMap.is_passable_terrain_at(ml))
            kMap.set(ml,earthMap.initial_karbonite_at(ml))
    storageEnd=time.time()
    print('storing the maps took '+str(storageEnd-storageStart)+'s')
    passableMap.printout()
    kMap.printout()
    print('printing the maps took '+str(time.time()-storageEnd)+'s')
    accessLocation = bc.MapLocation(bc.Planet.Earth,10,10)
    accessStart=time.time()
    for x in range(10000):
        locData = gc.starting_map(bc.Planet.Earth).is_passable_terrain_at(accessLocation)
    accessEnd=time.time()
    print('accessing (x10,000) the gc map took '+str(accessEnd-accessStart)+'s')
    accessStart=time.time()
    for x in range(10000):
        locData = passableMap.get(accessLocation)
    accessEnd=time.time()
    print('accessing (x10,000) the local map took '+str(accessEnd-accessStart)+'s')

    # #generate an ordered list of karbonite locations, sorted by distance to start
    # tOrderStart=time.time()
    # kLocs = []
    # currentLocs = []
    # evalMap = mmap(earthMap.width,earthMap.height)
    # for unit in gc.my_units():
    #     currentLocs.append(unit.location.map_location())
    # while(len(currentLocs)>0):
    #     nextLocs = []
    #     for loc in currentLocs:
    #         for dir in directions:
    #             newPlace = loc.add(dir)
    #             if evalMap.get(newPlace)==0:
    #                 evalMap.set(newPlace,1)
    #                 nextLocs.append(newPlace)
    #                 if kMap.get(newPlace)>0:
    #                     kLocs.append(loc)
    #     currentLocs=nextLocs
    # print('generating kLocs took '+str(time.time()-tOrderStart)+'s')

def rotate(dir,amount):
    ind = directions.index(dir)
    return directions[(ind+amount)%8]

def goto(unit,dest):
    d = unit.location.map_location().direction_to(dest)
    if gc.can_move(unit.id, d):
        gc.move_robot(unit.id,d)

def fuzzygoto(unit,dest):
    if unit.location.map_location()==dest:return
    toward = unit.location.map_location().direction_to(dest)
    for tilt in tryRotate:
        d = rotate(toward,tilt)
        newLoc = unit.location.map_location().add(d)
        if dmap.get(newLoc)==0:
            if gc.can_move(unit.id, d):
                gc.move_robot(unit.id,d)
                break
def myfuzzygoto(unit,dest):
    if unit.location.map_location()==dest:return
    toward = unit.location.map_location().direction_to(dest)
    for tilt in tryRotate:
        d = rotate(toward,tilt)
        if gc.can_move(unit.id, d):
            gc.move_robot(unit.id,d)
            return True
    return False


def checkK(loc):
    if not onEarth(loc): return 0
    return gc.karbonite_at(loc)

def bestKarboniteDirection(loc):
    mostK = 0
    bestDir = None
    for dir in allDirections:
        newK = checkK(loc.add(dir))
        if newK>mostK:
            mostK=newK
            bestDir=dir
    return mostK, bestDir

if gc.planet() == bc.Planet.Earth:
    w=earthMap.width
    h=earthMap.height
else:
    marsMap=gc.starting_map(bc.Planet.Mars)
    w=marsMap.width
    h=marsMap.height

while True:
    try:
        #prepare danger zone map
        dmap = mmap(w,h)
        for unit in gc.units():
            if not unit.location.is_in_garrison():
                if unit.team!=my_team:
                    dmap.addDisk(unit.location.map_location(),70,1) #changed to 70 bc Rangers vision range is 70
        if gc.round()==45:
            print("Printing the danger zone map\n")
            dmap.printout()
        umap = mmap(w,h)
        fmap = mmap(w,h)
        for unit in gc.units():
            if not unit.location.is_in_garrison():
                if unit.team==my_team: amt=-1
                else: amt=1
                fmap.addDisk(unit.location.map_location(),30,amt)
                umap.set(unit.location.map_location(),1)
        fmap.multiply(umap)
        if gc.round()==45:
            print("Printing the fmap\n")
            fmap.printout()


        #count things: unfinished buildings, workers, mages, Rangers
        numWorkers = 0
        workerJob = {"k":0,"r":0,"f":0,"b":0}
        numMages = 0
        numRangers = 0
        numFactories = 0
        numRockets = 0
        blueprintLocation = []


        for unit in gc.my_units():
            if unit.unit_type== bc.UnitType.Factory:
                if not unit.structure_is_built():
                    ml = unit.location.map_location()
                    blueprintLocation.append(ml)
                    numFactories += 1
            if unit.unit_type== bc.UnitType.Rocket:
                if not unit.structure_is_built():
                    ml = unit.location.map_location()
                    blueprintLocation.append((ml))
                    numRockets += 1
            if unit.unit_type== bc.UnitType.Worker:
                numWorkers+=1
                numWorkers += 1
            if unit.unit_type == bc.UnitType.Ranger:
                numRangers+=1
            if unit.unit_type == bc.UnitType.Mage:
                numMages += 1


        workersLeft = numWorkers
        if gc.round() > 300 and gc.karbonite() < bc.UnitType.Rocket.blueprint_cost() and numRockets < 1:
            rocketmode = True
        else:
            rocketmode = False



        for unit in gc.my_units():
            if unit.unit_type == bc.UnitType.Worker:
                d = random.choice(directions)
                if numWorkers<10: # up from 10
                    replicated=False
                    for d in directions:
                        if gc.can_replicate(unit.id,d):
                            gc.replicate(unit.id,d)
                            print("Replicated Worker\n")
                            replicated=True
                            break
                    if replicated:
                        continue

                if rocketmode:
                    if gc.karbonite() > bc.UnitType.Rocket.blueprint_cost():
                        bpRocket = False
                        for d in directions:
                            if gc.can_blueprint(unit.id, bc.UnitType.Rocket, d):
                                gc.blueprint(unit.id, bc.UnitType.Rocket, d)
                                workerJob["r"] += 1
                                workersLeft -= 1
                                bpRocket = True
                                continue
                        if bp: continue


                print("amt karbonite: ", gc.karbonite())

                #build
                if workerJob.get("b") < numWorkers//3:
                    adjacentUnits = gc.sense_nearby_units(unit.location.map_location(), 2)
                    for adjacent in adjacentUnits:  # build
                        if gc.can_build(unit.id, adjacent.id):
                            gc.build(unit.id, adjacent.id)
                            workerJob["b"] += 1
                            workersLeft -= 1
                            print("Building blueprint\n")
                            break
                    if gc.can_build(unit.id,adjacent.id):
                        continue

                #build factory
                if not rocketmode:
                    if workerJob.get("f") < numWorkers // 3:
                        if numFactories < 6 and gc.karbonite() > bc.UnitType.Factory.blueprint_cost():#blueprint
                            if gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
                                gc.blueprint(unit.id, bc.UnitType.Factory, d)
                                workerJob["f"] += 1
                                print("Made blueprint\n")
                                workersLeft -= 1
                                continue

                # harvest Karbonite
                if workerJob.get("k") < numWorkers//3:
                    harvested = False
                    for d in directions:
                        if gc.can_harvest(unit.id,d):
                            harvested = True
                            gc.harvest(unit.id,d)
                            workerJob["k"] += 1
                            workersLeft -= 1
                            print("Worker harvested karbonite\n")
                            break
                    if harvested: continue

                #build or move to blueprint
                if workerJob.get("b") < len(blueprintLocation)*2:
                    didHarvestOrBuild = False
                    adjacentUnits = gc.sense_nearby_units(unit.location.map_location(), 2)
                    for adjacent in adjacentUnits:  # build
                        if gc.can_build(unit.id, adjacent.id):
                            didHarvestOrBuild = True
                            gc.build(unit.id, adjacent.id)
                            print("Building blueprint\n")
                            break
                    if didHarvestOrBuild: continue
                    elif gc.is_move_ready(unit.id):
                        minBP = 1000
                        for bp in blueprintLocation:
                            distBP = unit.location.map_location().distance_squared_to(bp)
                            if distBP <= minBP:
                                minBP = distBP
                                bestBP = bp
                        if myfuzzygoto(unit,bestBP):
                            workersLeft -= 1
                            workerJob["b"] += 1
                            continue

                #harvest or move to karbonite
                if workersLeft < numWorkers // 3 - workerJob.get("k"):
                    didHarvestOrBuild = False
                    for d in directions:
                        if gc.can_harvest(unit.id, d):
                            didHarvestOrBuild = True
                            gc.harvest(unit.id, d)
                            workerJob["k"] += 1
                            workersLeft -= 1
                            print("Worker harvested karbonite\n")
                            continue
                    if didHarvestOrBuild: continue
                    elif gc.is_move_ready(unit.id):
                        k_map.update_kmap()
                        distK, kML = k_map.closest_K(unit)
                        if myfuzzygoto(unit, kML):
                            workerJob["k"] += 1
                            workersLeft -= 1
                            continue

                if gc.karbonite() > bc.UnitType.Rocket.blueprint_cost():
                    bpRocket = False
                    for d in directions:
                        if gc.can_blueprint(unit.id, bc.UnitType.Rocket, d):
                            gc.blueprint(unit.id, bc.UnitType.Rocket, d)
                            workerJob["r"] += 1
                            workersLeft -= 1
                            bpRocket = True
                            break
                    if bpRocket: continue

                didHarvestOrBuild = False
                for d in directions:
                    if gc.can_harvest(unit.id, d):
                        didHarvestOrBuild = True
                        gc.harvest(unit.id, d)
                        workerJob["k"] += 1
                        workersLeft -= 1
                        print("Worker harvested karbonite\n")
                        break
                if didHarvestOrBuild: continue

                adjacentUnits = gc.sense_nearby_units(unit.location.map_location(), 2)
                for adjacent in adjacentUnits:  # build
                    if gc.can_build(unit.id, adjacent.id):
                        didHarvestOrBuild = True
                        gc.build(unit.id, adjacent.id)
                        workerJob["b"] += 1
                        workersLeft -= 1
                        print("Building blueprint\n")
                        break
                if didHarvestOrBuild: continue

                if gc.is_move_ready(unit.id) and len(blueprintLocation) > 0:
                    k_map.update_kmap()
                    distK, kML = k_map.closest_K(unit)
                    for bp in blueprintLocation:
                        distBP = unit.location.map_location().distance_squared_to(bp)
                        if distBP <= distK:
                            distK = distBP
                            bestBP = bp
                            workerJob["k"] += 1
                            workersLeft -= 1
                    myfuzzygoto(unit,bestBP)
                    continue





                # #build rockets
                #
                # if numRockets < 5 and gc.karbonite() > bc.UnitType.Rocket.blueprint_cost():
                #
                # if gc.karbonite() > bc.UnitType.Rocket.blueprint_cost(): # try build rockets in general # gc.round() > 500 and
                #
                #     if gc.can_blueprint(unit.id, bc.UnitType.Rocket, d):
                #         gc.blueprint(unit.id, bc.UnitType.Rocket, d)
                #         continue
                #
                #
                #
                # adjacentUnits = gc.sense_nearby_units(unit.location.map_location(), 2) #comment this out? -Zoe
                #
                # # adjacentUnits = gc.sense_nearby_units(unit.location.map_location(), 50)
                #
                # for adjacent in adjacentUnits:#build
                #     if gc.can_build(unit.id,adjacent.id):
                #         gc.build(unit.id,adjacent.id)
                #         print("Building blueprint\n")
                #         continue
                #
                # #head toward blueprint location
                # if gc.is_move_ready(unit.id):
                #     if blueprintWaiting:
                #         ml = unit.location.map_location()
                #         bdist = ml.distance_squared_to(blueprintLocation)
                #         if bdist>2:
                #             fuzzygoto(unit,blueprintLocation)
                #             print("Worker moved\n")
                #             continue
                # #harvest karbonite from nearby
                # mostK, bestDir = bestKarboniteDirection(unit.location.map_location())
                # if mostK>0:#found some karbonite to harvest
                #     if gc.can_harvest(unit.id,bestDir):
                #         gc.harvest(unit.id,bestDir)
                #         print("Worker harvested karbonite\n")
                #         continue
                #
                # if gc.is_move_ready(unit.id):
                #     if blueprintWaiting:
                #         ml = unit.location.map_location()
                #         bdist = ml.distance_squared_to(blueprintLocation)
                #         if bdist>2:
                #             fuzzygoto(unit,blueprintLocation)
                #             print("Worker moved")
                #             continue
                # if gc.is_move_ready(unit.id):#need to go looking for karbonite
                #     ml = unit.location.map_location()
                #     ml2 = k_map.closest_K(unit)
                #     if ml2 and (ml2 != ml or ml2.y != ml.y):# 0 indicates no karbonite left
                #         fuzzygoto(unit.ml2)













            if unit.unit_type == bc.UnitType.Factory:
                garrison = unit.structure_garrison()
                if len(garrison) > 0:#ungarrison
                    d = random.choice(directions)
                    if gc.can_unload(unit.id, d):
                        gc.unload(unit.id, d)
                        print("Unloaded Garrison\n")
                        continue

                # if numRangers <= 8: #produce Rangers up to 8, then produce Mages up to 8, then keep on producing Rangers.

                # TODO: make this not random and stuff (Zoe)

                if gc.can_produce_robot(unit.id, bc.UnitType.Ranger):#produce Ranger
                    if numRangers and numMages != 0:
                        if numRangers/(numRangers + numMages) < 0.90:

                            gc.produce_robot(unit.id, bc.UnitType.Ranger)
                            print("Produced Ranger\n")
                            continue
                    else:
                        gc.produce_robot(unit.id, bc.UnitType.Ranger)
                        print("Produced Ranger\n")
                        continue
                    # yeah, that was pretty unpythonic :/

                elif gc.can_produce_robot(unit.id, bc.UnitType.Mage):#produce Mage
                        gc.produce_robot(unit.id, bc.UnitType.Mage)
                        print("Produced Mage\n")
                        continue
                #seems redundant
                '''
                elif gc.can_produce_robot(unit.id, bc.UnitType.Ranger):#produce Ranger
                        gc.produce_robot(unit.id, bc.UnitType.Ranger)
                        print("Produced Ranger\n")
                        continue
                '''

                '''
                if gc.can_produce_robot(unit.id, bc.UnitType.Ranger):#produce Ranger
                        gc.produce_robot(unit.id, bc.UnitType.Ranger)
                        print("Produced Ranger\n")
                        continue
                elif numMages <= 8 and gc.can_produce_robot(unit.id, bc.UnitType.Mage):#produce Mage
                        gc.produce_robot(unit.id, bc.UnitType.Mage)
                        print("Produced Mage\n")
                        continue
                #seems redundant

                elif gc.can_produce_robot(unit.id, bc.UnitType.Ranger):#produce Ranger
                        gc.produce_robot(unit.id, bc.UnitType.Ranger)
                        print("Produced Ranger\n")
                        continue
                '''
            #LAUNCH ROCKET

            if unit.unit_type == bc.UnitType.Rocket:
                # get locations on Mars to land on
                marsPathMap.update_pathmap_units()
                for x in marsPathMap.w:
                    for y in marsPathMap.h:
                        ml = bc.MapLocation(bc.Planet.Mars,x,y)
                        if not ml in rocket_locations:
                            if can_launch_rocket(unit.id, ml):
                                launch_rocket(unit.id, ml)



            if unit.unit_type == bc.UnitType.Mage:
                if not unit.location.is_in_garrison():#can't move from inside a factory
                    bestAmt, bestLoc = fmap.findBest(unit.location.map_location(),unit.attack_range()) # bestLoc undefined Line 500
                    if bestAmt>0:#found something to shoot
                        attackableEnemies = gc.sense_nearby_units_by_team(unit.location.map_location(),unit.attack_range(),enemy_team)
                        if len(attackableEnemies)>0:
                            if gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, attackableEnemies[0].id):
                                if bestLoc:
                                    if gc.has_unit_at_location(bestLoc):
                                        targetUnit = gc.sense_unit_at_location(bestLoc)
                                        gc.attack(unit.id, targetUnit.id)
                                        print("Mage attacked\n")
                        if gc.is_move_ready(unit.id): #attacked, now move
                            nearbyEnemies = gc.sense_nearby_units_by_team(unit.location.map_location(),unit.vision_range,enemy_team)
                            if len(nearbyEnemies)>0:
                                destination=nearbyEnemies[0].location.map_location()
                            else:
                                destination=enemyStart
                            fuzzygoto(unit,destination)
                            print("Mage moved\n")
                    elif gc.is_move_ready(unit.id):
                        nearbyEnemies = gc.sense_nearby_units_by_team(unit.location.map_location(),unit.vision_range,enemy_team)
                        if len(nearbyEnemies)>0:
                            destination=nearbyEnemies[0].location.map_location()
                        else:
                            destination=enemyStart
                        fuzzygoto(unit,destination)
                        print("Mage moved\n")
                        if bestAmt>0:#found something to shoot. #moved, now attack
                            attackableEnemies = gc.sense_nearby_units_by_team(unit.location.map_location(),unit.attack_range(),enemy_team)
                            if len(attackableEnemies)>0:
                                if gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, attackableEnemies[0].id):
                                    if bestLoc:
                                        if gc.has_unit_at_location(bestLoc):
                                            targetUnit = gc.sense_unit_at_location(bestLoc)
                                            gc.attack(unit.id, targetUnit.id)
                                            print("Mage attacked\n")

            if unit.unit_type == bc.UnitType.Ranger:
                if not unit.location.is_in_garrison():#can't move from inside a factory
                    attackableEnemies = gc.sense_nearby_units_by_team(unit.location.map_location(),unit.attack_range(),enemy_team)
                    if len(attackableEnemies)>0: #attack, then move? SHOULD WE MOVE???
                        if gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, attackableEnemies[0].id):
                            gc.attack(unit.id, attackableEnemies[0].id)
                            print("Ranger attacked\n")
                        if gc.is_move_ready(unit.id): #attacked, now move
                            nearbyEnemies = gc.sense_nearby_units_by_team(unit.location.map_location(),unit.vision_range,enemy_team)
                            if len(nearbyEnemies)>0:
                                destination=nearbyEnemies[0].location.map_location()
                            else:
                                destination=enemyStart
                            fuzzygoto(unit,destination)
                            print("Ranger moved\n")
                    elif gc.is_move_ready(unit.id): #move, then attack
                        nearbyEnemies = gc.sense_nearby_units_by_team(unit.location.map_location(),unit.vision_range,enemy_team)
                        if len(nearbyEnemies)>0:
                            destination=nearbyEnemies[0].location.map_location()
                        else:
                            destination=enemyStart
                        fuzzygoto(unit,destination)
                        print("Ranger moved\n")
                        if len(attackableEnemies)>0:
                            if gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, attackableEnemies[0].id):
                                gc.attack(unit.id, attackableEnemies[0].id)
                                print("Ranger attacked\n")

            # attack
            # if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                # gc.attack(unit.id, other.id)

            # movement
            # elif gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
                # gc.move_robot(unit.id, d)

    except Exception as e:
        print('Error:', e)
        traceback.print_exc()

    # send the actions we've performed, and wait for our next turn.
    gc.next_turn()

    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
    sys.stdout.flush()
    sys.stderr.flush()
