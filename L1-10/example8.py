import pygame, sys, os, json
from e6s import *
from bfs2 import *

pygame.init()
clock = pygame.time.Clock()

fname = 'map2.txt'
map=newMap()
mapColors = [(0,0,0),(200,200,200),(255,255,255)]

soldier = pygame.image.load(os.path.join('sprites','soldier_blue.png')).convert_alpha()
s_dest = pygame.image.load(os.path.join('sprites','den_blue.png')).convert_alpha()
pathing_start=(5,5)
pathing_end=(15,15)
p=pathing(map,pathing_start,pathing_end)
pathSprites = [(0,0,0),'0.bmp','2.bmp','4.bmp','6.bmp']

going = True
paused = True
time = 0
framesPerUpdate=1
step = False
while going:
	time+=1
	for event in pygame.event.get():
		if event.type==pygame.QUIT:
			going=False
		if event.type==pygame.KEYDOWN:
			if event.key==pygame.K_SPACE:paused = not paused;
			if event.key==pygame.K_c:map=newMap()
			if event.key==pygame.K_s:saveMap(map,fname)
			if event.key==pygame.K_l:map=loadMap(fname)
			if event.key==pygame.K_i:p=pathing(map,pathing_start,pathing_end)
			if event.key==pygame.K_n:step=True
			
	#allow user to modify the map
	editMap(pygame.mouse.get_pressed(),pygame.mouse.get_pos(),cellSize,map)
	
	if step:
		p.nextStep()
		step=False
	
	if (not paused)&(time%framesPerUpdate==0):
		p.nextStep()
	
	#render
	screen.fill((100,100,100))
	drawMap(map,mapColors)
	for loc in p.cpts:
		pygame.draw.rect(screen,(255,255,255),[loc.x*cellSize[0],loc.y*cellSize[1],cellSize[0],cellSize[1]],0)
	for loc in p.path:
		pygame.draw.rect(screen,(100,100,255),[loc.x*cellSize[0],loc.y*cellSize[1],cellSize[0],cellSize[1]],0)
	
	# drawMap(p.md,pathSprites)
	
	screen.blit(soldier,(pathing_start[0]*cellSize[0],pathing_start[1]*cellSize[1]))
	screen.blit(s_dest,(pathing_end[0]*cellSize[0],pathing_end[1]*cellSize[1]))
	pygame.display.flip()
	
	clock.tick(20)
pygame.quit()