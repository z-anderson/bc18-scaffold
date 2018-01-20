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
def launch_rocket(rocket_id, destination):
    if gc.can_launch_rocket(self, rocket_id, destination) == True:
        #destination: read in Jordan's map, maybe loop through, find good places to land,land there
        #load rocket

        for rob in robots:
                if can_load(self, structure_id, robot_id):
                    load(self, structure_id, robot_id))

                gc.launch_rocket(self, rocket_id, location) #same fo rlocation :(
'''

while True:
    # We only support Python 3, which means brackets around print()
    print('pyround:', gc.round(), 'time left:', gc.get_time_left_ms(), 'ms')

    # frequent try/catches are a good idea
    try:
        # walk through our units:
        d = random.choice(directions)
        #numWorkers = 0
        for unit in gc.my_units():

            #Can anyone figure this out?

            #if unit.unit_type == bc.UnitType.Worker:
                #if numWorkers < 10 and gc.can_replicate(unit.id,d):
                    #gc.replicate(unit.id,d)
                    #numWorkers += 1
					#continue

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
            # pick a random direction:
            d = random.choice(directions)

            #this might be a really bad strategy
            for d in directions:
                if gc.can_replicate(unit.id,d):
                    gc.replicate(unit.id,d)
                    replicated=True
                    break

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

            #launch a rocket ZOE 1/19


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
