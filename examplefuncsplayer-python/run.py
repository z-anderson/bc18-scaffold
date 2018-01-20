# TIME TO COPY AND PASTE!!! LECTURE PLAYER 7

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
	def get(self,mapLocation):
		if not onEarth(mapLocation):return -1
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
if gc.planet() == bc.Planet.Earth:
	gc.queue_research(bc.UnitType.Worker)
	gc.queue_research(bc.UnitType.Knight)
	gc.queue_research(bc.UnitType.Knight)
	gc.queue_research(bc.UnitType.Knight)
	gc.queue_research(bc.UnitType.Knight)
	oneLoc = gc.my_units()[0].location.map_location()
	loadStart = time.time()
	earthMap = gc.starting_map(bc.Planet.Earth)
	loadEnd = time.time()
	print('loading the map took '+str(loadEnd-loadStart)+'s')
	enemyStart = invert(oneLoc);
	print('worker starts at '+locToStr(oneLoc))
	print('enemy worker presumably at '+locToStr(enemyStart))

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

while True:
	try:
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
				if numWorkers<10 and gc.can_replicate(unit.id,d):
					gc.replicate(unit.id,d)
					continue
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
				elif gc.can_produce_robot(unit.id, bc.UnitType.Knight):#produce Knights
					gc.produce_robot(unit.id, bc.UnitType.Knight)
					continue

			if unit.unit_type == bc.UnitType.Knight:
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


'''

import battlecode as bc
import random
import sys
import traceback
import time

import os
print(os.getcwd())

print("pystarting")

# A GameController is the main type that you talk to the game with.
# Its constructor will connect to a running game.
gc = bc.GameController()
directions = list(bc.Direction)

print("pystarted")

# It's a good idea to try to keep your bots deterministic, to make debugging easier.
# determinism isn't required, but it means that the same things will happen in every thing you run,
# aside from turns taking slightly different amounts of time due to noise.
random.seed(6137)

# let's start off with some research!
# we can queue as much as we want.
gc.queue_research(bc.UnitType.Rocket)
gc.queue_research(bc.UnitType.Worker)
gc.queue_research(bc.UnitType.Knight)

my_team = gc.team()

'''
'''
def launch_rocket(rocket_id, destination):
    if gc.can_launch_rocket(self, rocket_id, destination) == True:
        #destination: read in Jordan's map, maybe loop through, find good places to land,land there
        #load rocket

        for rob in robots:
                if can_load(self, structure_id, robot_id):
                    load(self, structure_id, robot_id))

                gc.launch_rocket(self, rocket_id, location) #same fo rlocation :(
'''
'''

while True:
    # We only support Python 3, which means brackets around print()
    print('pyround:', gc.round(), 'time left:', gc.get_time_left_ms(), 'ms')

    # frequent try/catches are a good idea
    try:
        # walk through our units:
        d = random.choice(directions)
        numWorkers = 0
        for unit in gc.my_units():

            # worker replication

            if unit.unit_type == bc.UnitType.Worker:
                if numWorkers < 10 and gc.can_replicate(unit.id,d):
                    gc.replicate(unit.id,d)
                    numWorkers += 1
                    continue


            # first, factory logic
            if unit.unit_type == bc.UnitType.Factory:
                garrison = unit.structure_garrison()
                if len(garrison) > 0:
                    d = random.choice(directions)
                    if gc.can_unload(unit.id, d):
                        print('unloaded a knight!')
                        gc.unload(unit.id, d)
                        continue
                elif gc.can_produce_robot(unit.id, bc.UnitType.Knight):
                    gc.produce_robot(unit.id, bc.UnitType.Knight)
                    print('produced a knight!')
                    continue

            # first, let's look for nearby blueprints to work on
            location = unit.location
            if location.is_on_map():
                nearby = gc.sense_nearby_units(location.map_location(), 2)
                for other in nearby:
                    if unit.unit_type == bc.UnitType.Worker and gc.can_build(unit.id, other.id):
                        gc.build(unit.id, other.id)
                        print('built a factory!')
                        # move onto the next unit
                        continue
                    if other.team != my_team and gc.is_attack_ready(unit.id) and gc.can_attack(unit.id, other.id):
                        print('attacked a thing!')
                        gc.attack(unit.id, other.id)
                        continue

            # okay, there weren't any dudes around

            # or, try to build a factory:
            if gc.karbonite() > bc.UnitType.Factory.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
                gc.blueprint(unit.id, bc.UnitType.Factory, d)
            elif gc.karbonite() > bc.UnitType.Rocket.blueprint_cost() and gc.can_blueprint(unit.id, bc.UnitType.Rocket, d):
                #or, try to build a rocket ZOE 1/19
                gc.blueprint(unit.id, bc.UnitType.Rocket, d)
                adjacentUnits = gc.sense_nearby_units(unit.location.map_location(), 2)
                for adjacent in adjacentUnits:#build
                    if gc.can_build(unit.id,adjacent.id):
                        gc.build(unit.id,adjacent.id)
                        continue
            # and if that fails, try to move
            elif gc.is_move_ready(unit.id) and gc.can_move(unit.id, d):
                gc.move_robot(unit.id, d)

            #TODO: ATTACK

            # TODO: launch rocket


    except Exception as e:
        print('Error:', e)
        # use this to show where the error was
        traceback.print_exc()

    # send the actions we've performed, and wait for our next turn.
    gc.next_turn()

    # these lines are not strictly necessary, but it helps make the logs make more sense.
    # it forces everything we've written this turn to be written to the manager.
    sys.stdout.flush()
    sys.stderr.flush()
'''
