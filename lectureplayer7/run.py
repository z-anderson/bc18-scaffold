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
    vs = (vector(0, -1), vector(1,-1), vector(1, 0), vector(1,1), vector(0, 1), vector(-1,1), vector(-1, 0))

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


#tile in map for pathfinding
class tile:
    def __init__(self, loc, dist):
        self.loc = loc
        self.dist = dist
        self.dirs = [0, 0, 0, 0, 0, 0, 0, 0]
        self.width = 0

    def getDirs(self):
        dirs = []
        for i in range(len(self.dirs)):
            if self.dirs[i] == 1: dirs.append(direction(i))
        return dirs

    def addDir(self, dir, dist):
        if dist < self.dist: self.dist = dist
        self.dirs[dir.index] = 1

    def __str__(self):
        return 'tile(dist=' + str(self.dist) + ',dirs=' + str(self.dirs) + ',width=' + str(self.width)

#for pathfinding
class pathing:
    def __init__(self, map, start, end):
        self.map = map
        self.md = [[0] * len(self.map[0]) for i in range(len(self.map))]
        for i in range(len(self.map)):
            for j in range(len(self.map[0])):
                self.md[i][j] = tile(vector(i, j), 10000)
        self.start = vector(start)
        self.start.of(self.md).dist = 0
        self.end = vector(end)
        self.cpts = []
        self.cpts.append(self.start)
        self.dist = 0
        self.state = 'spread'
        self.path = []

    def isOpen(self, loc, dist):
        onMap = (loc.x >= 0) & (loc.x < len(self.map)) & (loc.y >= 0) & (loc.y < len(self.map[0]))
        if not onMap: return False
        traversable = loc.of(self.map) != 0
        acceptablePathLength = dist <= loc.of(self.md).dist
        return traversable & acceptablePathLength

    def nextStep(self):
        if self.state == 'spread':
            nextPoints = []
            for p in self.cpts:
                for d in direction.getDs():
                    ahead = p + d
                    if self.isOpen(ahead, self.dist):
                        ahead.of(self.md).addDir(d, self.dist)
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
                for d in p.of(self.md).getDirs():
                    d.rotateAmount(4)  # flip backwards
                    behind = p + d
                    behind.of(self.md).width = len(self.cpts)
                    if not behind in nextPoints: nextPoints.append(behind)
            self.path.extend(self.cpts)
            self.cpts = nextPoints
            if len(nextPoints) == 0: self.state = 'arrived'

# input like (x,y); map should be 2D array; '0' on the map means not traversable, returns Direction
def next_move(map,start_loc,end_loc):
    dirdict = {(1, 0): 'East', (1, 1): 'NorthEast', (0, 1): 'North', (-1, 1): 'Northwest',\
               (-1, 0): 'East',(-1, -1): 'Southwest', (0, -1): 'South', (1, -1): 'Southeast'}

    mypath = pathing(map,start_loc,end_loc)
    while True:
        if mypath.state == 'return':
            break
        mypath.nextStep()
    mypath.nextStep()
    # since there are many options for going back, I default to the first... this can change
    mydir = (mypath.cpts[0].x - end_loc[0], end_loc[1] - mypath.cpts[0].y)
    return dirdict.get(mydir)





def invert(loc):#assumes Earth
	newx = earthMap.width-loc.x
	newy = earthMap.height-loc.y
	return bc.MapLocation(bc.Planet.Earth,newx,newy)

def locToStr(loc):
	return '('+str(loc.x)+','+str(loc.y)+')'

def onEarth(loc):
	if (loc.x<0) or (loc.y<0) or (loc.x>=earthMap.width) or (loc.y>=earthMap.height): return False
	return True
	
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

if gc.planet() == bc.Planet.Earth:
	gc.queue_research(bc.UnitType.Worker)
	gc.queue_research(bc.UnitType.Ranger)
	gc.queue_research(bc.UnitType.Ranger)
	oneLoc = gc.my_units()[0].location.map_location()
	loadStart = time.time()
	earthMap = gc.starting_map(bc.Planet.Earth)
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
	
	#generate an ordered list of karbonite locations, sorted by distance to start
	tOrderStart=time.time()
	kLocs = []
	currentLocs = []
	evalMap = mmap(earthMap.width,earthMap.height)
	for unit in gc.my_units():
		currentLocs.append(unit.location.map_location())
	while(len(currentLocs)>0):
		nextLocs = []
		for loc in currentLocs:
			for dir in directions:
				newPlace = loc.add(dir)
				if evalMap.get(newPlace)==0:
					evalMap.set(newPlace,1)
					nextLocs.append(newPlace)
					if kMap.get(newPlace)>0:
						kLocs.append(loc)
		currentLocs=nextLocs
	print('generating kLocs took '+str(time.time()-tOrderStart)+'s')	
	
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
					dmap.addDisk(unit.location.map_location(),50,1)
		if gc.round()==45:
			dmap.printout()
		
		#count things: unfinished buildings, workers
		numWorkers = 0
		blueprintLocation = None
		blueprintWaiting = False
		for unit in gc.my_units():
			if unit.unit_type== bc.UnitType.Factory:
				if not unit.structure_is_built():
					ml = unit.location.map_location()
					blueprintLocation = ml
					blueprintWaiting = True
			if unit.unit_type== bc.UnitType.Worker:
				numWorkers+=1
		
		for unit in gc.my_units():
			if unit.unit_type == bc.UnitType.Worker:
				d = random.choice(directions)
				if numWorkers<10:
					replicated=False
					for d in directions:
						if gc.can_replicate(unit.id,d):
							gc.replicate(unit.id,d)
							replicated=True
							break
					if replicated:continue
				if gc.karbonite() > bc.UnitType.Factory.blueprint_cost():#blueprint
					if gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
						gc.blueprint(unit.id, bc.UnitType.Factory, d)
						continue
				adjacentUnits = gc.sense_nearby_units(unit.location.map_location(), 2)
				for adjacent in adjacentUnits:#build
					if gc.can_build(unit.id,adjacent.id):
						gc.build(unit.id,adjacent.id)
						continue
				#head toward blueprint location
				if gc.is_move_ready(unit.id):
					if blueprintWaiting:
						ml = unit.location.map_location()
						bdist = ml.distance_squared_to(blueprintLocation)
						if bdist>2:
							fuzzygoto(unit,blueprintLocation)
							continue
				#harvest karbonite from nearby
				mostK, bestDir = bestKarboniteDirection(unit.location.map_location())
				if mostK>0:#found some karbonite to harvest
					if gc.can_harvest(unit.id,bestDir):
						gc.harvest(unit.id,bestDir)
						continue
				elif gc.is_move_ready(unit.id):#need to go looking for karbonite
					if len(kLocs)>0:
						dest=kLocs[0]
						if gc.can_sense_location(dest):
							kAmt = gc.karbonite_at(dest)
							if kAmt==0:
								kLocs.pop(0)
							else:
								fuzzygoto(unit,dest)
			
			if unit.unit_type == bc.UnitType.Factory:
				garrison = unit.structure_garrison()
				if len(garrison) > 0:#ungarrison
					d = random.choice(directions)
					if gc.can_unload(unit.id, d):
						gc.unload(unit.id, d)
						continue
				elif gc.can_produce_robot(unit.id, bc.UnitType.Ranger):#produce Mages
					gc.produce_robot(unit.id, bc.UnitType.Ranger)
					continue
			
			if unit.unit_type == bc.UnitType.Ranger:
				if not unit.location.is_in_garrison():#can't move from inside a factory
					attackableEnemies = gc.sense_nearby_units_by_team(unit.location.map_location(),unit.attack_range(),enemy_team)
					if len(attackableEnemies)>0:
						if gc.is_attack_ready(unit.id):
							gc.attack(unit.id, attackableEnemies[0].id)
					elif gc.is_move_ready(unit.id):
						nearbyEnemies = gc.sense_nearby_units_by_team(unit.location.map_location(),unit.vision_range,enemy_team)
						if len(nearbyEnemies)>0:
							destination=nearbyEnemies[0].location.map_location()
						else:
							destination=enemyStart
						fuzzygoto(unit,destination)
			
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
