import pygame
import sys
import os
import json

pygame.init()
clock = pygame.time.Clock()
mapSize = (int(sys.argv[1]),int(sys.argv[2]))
middle = (mapSize[0]//2,mapSize[1]//2)
map = [[0]*mapSize[1] for i in range(mapSize[0])]
map2 = [[0]*mapSize[1] for i in range(mapSize[0])]
cellSize = (7,7)
screenSize = (mapSize[0]*cellSize[0],mapSize[1]*cellSize[1])
screen = pygame.display.set_mode(screenSize)
mapColors = [(100,100,255),(200,200,200),(255,255,255)]
liverule = (0,1,2,1,1,1,0,0,0,0,0)#(0,1,0,2,0,0,0,1,0)

going = True
paused = False
map[middle[0]][middle[1]]=1

while going:
	for event in pygame.event.get():
		if event.type==pygame.QUIT:
			going=False
		if event.type==pygame.KEYDOWN:
			if event.key==pygame.K_SPACE:
				paused = not paused;
			if event.key==pygame.K_s:#save map
				fname = 'map.txt'
				if os.path.isfile(fname):os.remove(fname)
				sf = open(fname,'w+')
				sf.write(json.dumps(map))
				sf.close()
			if event.key==pygame.K_l:#load map
				fname = 'map.txt'
				if os.path.isfile(fname):
					sf = open(fname,'r')
					str=sf.read();
					map2 = json.loads(str)
					map = json.loads(str)
					sf.close()
				
	if not paused:
		#run cellular simulation
		for i in range(1,mapSize[0]-1):
			for j in range(1,mapSize[1]-1):
				neighbors = [map[i-1][j],map[i+1][j],map[i][j+1],map[i][j-1],map[i][j]]
				map2[i][j] = liverule[sum(neighbors)]
	#render
	screen.fill((255,255,255))
	for i in range(mapSize[0]):
		for j in range(mapSize[1]):
			map[i][j] = map2[i][j]
			rcolor = mapColors[map2[i][j]]
			pygame.draw.rect(screen,rcolor,[i*cellSize[0],j*cellSize[1],cellSize[0],cellSize[1]],0)
	pygame.display.flip()
	
	clock.tick(5)
pygame.quit()

#nice ones:
#(1,1,1,2,1,1,0,0,0) with ortho and no seed, 67x67
#(1,2,1,2,1,1,0,0,0) '' '' ''
#(0,1,2,1,1,1,0,0,0,0,0) with ortho+self and seed once, 67x67
#(0,1,2,1,1,1,0,0,0,0,0) with ortho+self and seed once, 53x53 actually stops after a while