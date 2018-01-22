import battlecode as bc
import random
import sys
import traceback
import os

gc = bc.GameController()
directions = [bc.Direction.North, bc.Direction.Northeast, bc.Direction.East, bc.Direction.Southeast, bc.Direction.South, bc.Direction.Southwest, bc.Direction.West, bc.Direction.Northwest]
tryRotate = [0,-1,1,-2,2]
random.seed(6137)
my_team = gc.team()
enemy_team=bc.Team.Red
if my_team==bc.Team.Red:
	enemy_team=bc.Team.Blue

def invert(loc):#assumes Earth
	newx = earthMap.width-loc.x
	newy = earthMap.height-loc.y
	return bc.MapLocation(bc.Planet.Earth,newx,newy)

def locToStr(loc):
	return '('+str(loc.x)+','+str(loc.y)+')'

class mmap():
	def __init__(self, width, height):
		self.width=width
		self.height=height
		self.arr=[[0]*self.height for i in range(self.width)]
	def get(self, mapLocation):
		if self.is_on_planet(Earth):
			return self.arr[mapLocation.x][mapLocation.y]
	def set(self, mapLocation, val):
		self.arr[mapLocation.x][mapLocation.y]=val
	def printout(self):
		print("printing map: ")
		for y in range(self.height):
			buildstr=''
			for x in range(self.width):
				buildstr+=format(self.arr[x][self.height-1-y], '2d')
				print(buildstr)


def update_kmap(kmap,PlanetMap): #update karbonite map
	for x in range(PlanetMap.width):
		for y in range(PlanetMap.height):
			ml = bc.MapLocation(PlanetMap.planet, x, y)
			if can_sense_location(ml):
				kmap.set(ml,gc.karbonite_at)

if gc.planet() == bc.Planet.Earth:
	gc.queue_research(bc.UnitType.Worker)
	gc.queue_research(bc.UnitType.Worker)
	gc.queue_research(bc.UnitType.Mage)
	oneLoc = gc.my_units()[0].location.map_location()
	earthMap = gc.starting_map(bc.Planet.Earth)
	enemyStart = invert(oneLoc);
	print('worker starts at '+locToStr(oneLoc))
	print('enemy worker presumably at '+locToStr(enemyStart))

	passableMap = mmap(earthMap.width, earthMap.height)
	kMap = mmap(earthMap.width, earthMap.height)
	for x in range(earthMap.width):
		for y in range(earthMap.height):
			m1 = bc.MapLocation(bc.Planet.Earth, x, y)
			passableMap.set(m1, earthMap.is_passable_terrain_at(m1))
			kMap.set(m1, earthMap.initial_karbonite_at(m1))
	passableMap.printout()
	kMap.printout()


def rotate(dir,amount):
	ind = directions.index(dir)
	return directions[(ind+amount)%8]

def goto(unit,dest):
	d = unit.location.map_location().direction_to(dest)
	if gc.can_move(unit.id, d):
		gc.move_robot(unit.id,d)
		
def fuzzygoto(unit,dest):
	toward = unit.location.map_location().direction_to(dest)
	for tilt in tryRotate:
		d = rotate(toward,tilt)
		if gc.can_move(unit.id, d):
			gc.move_robot(unit.id,d)
			break



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
				if numWorkers<5 and gc.can_replicate(unit.id,d):
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
				if blueprintWaiting:
					if gc.is_move_ready(unit.id):
						ml = unit.location.map_location()
						bdist = ml.distance_squared_to(blueprintLocation)
						if bdist>2:
							fuzzygoto(unit,blueprintLocation)
			
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
			
			if unit.unit_type == bc.UnitType.Mage:
				if not unit.location.is_in_garrison:
					attackableEnemies=gc.sense_nearby_units_by_team(unit.location, 30, enemy_team)
					if len(attackableEnemies)>0:
						#there are nearby enemies
						if unit.is_attack_ready(unit.id):
							unit.attack(unit.id, attackableEnemies[0].id)
						if unit.is_move_ready(unit.id):
							nearbyEnemies=gc.sense_nearby_units_by_team(unit.location, 400, enemy_team)
							if len(nearbyEnemies)>0:
								destination=nearbyEnemies[0].location.map_location()
							else:
								destination=enemyStart
							fuzzygoto(unit.id, destination)


			if unit.unit_type == bc.UnitType.Knight:
				if unit.location.is_on_map():#can't move from inside a factory
					if gc.is_move_ready(unit.id):
						if gc.round()>50:
							fuzzygoto(unit,enemyStart)
					
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
