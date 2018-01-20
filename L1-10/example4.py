import pygame
import sys

pygame.init()
clock = pygame.time.Clock()
mapSize = (int(sys.argv[1]),int(sys.argv[2]))
middle = (mapSize[0]//2,mapSize[1]//2)
map = [[0]*mapSize[1] for i in range(mapSize[0])]
map2 = [[0]*mapSize[1] for i in range(mapSize[0])]
cellSize = (10,10)
screenSize = (mapSize[0]*cellSize[0],mapSize[1]*cellSize[1])
screen = pygame.display.set_mode(screenSize)
mapColors = [(100,100,255),(200,200,200)]

going = True
while going:
	for event in pygame.event.get():
		if event.type==pygame.QUIT:
			going=False
	
	screen.fill((255,255,255))
	
	map[middle[0]][middle[1]]=1
	for i in range(1,mapSize[0]-1):
		for j in range(1,mapSize[1]-1):
			neighbors = [map[i][j-1],map[i][j+1],map[i-1][j],map[i+1][j]]
			map2[i][j] = sum(neighbors)%2
	
	for i in range(mapSize[0]):
		for j in range(mapSize[1]):
			map[i][j] = map2[i][j]
			rcolor = mapColors[map2[i][j]]
			pygame.draw.rect(screen,rcolor,[i*cellSize[0],j*cellSize[1],cellSize[0],cellSize[1]],0)
	pygame.display.flip()
	
	clock.tick(10)
pygame.quit()