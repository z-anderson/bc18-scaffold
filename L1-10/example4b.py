import pygame
import sys

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
iterno = 0
dist=1
map[middle[0]][middle[1]]=1

while going:
	for event in pygame.event.get():
		if event.type==pygame.QUIT:
			going=False
	
	screen.fill((255,255,255))
	# if iterno<50:
	# iterno+=1
	
	
	for i in range(dist,mapSize[0]-dist):
		for j in range(dist,mapSize[1]-dist):
			neighbors = [map[i-1][j],map[i+1][j],map[i][j+1],map[i][j-1],map[i][j]]
			map2[i][j] = liverule[sum(neighbors)]#sum(neighbors)%2
	
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