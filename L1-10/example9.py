import pygame, sys, os, json
from e6s import *
from hallway import *

pygame.init()
clock = pygame.time.Clock()

fname = 'map2.txt'
map=newMap()
mapColors = [(0,0,0),(200,200,200),(255,255,255)]
mapColors2 = [(100,100,200),(100,100,255),(100,255,100),(255,100,100),(255,200,100),(255,100,255),(100,255,255),(200,100,200),(100,100,255),(200,100,200),(255,100,100)]

soldier = pygame.image.load(os.path.join('sprites','soldier_blue.png')).convert_alpha()
s_dest = pygame.image.load(os.path.join('sprites','den_blue.png')).convert_alpha()
pathing_start=(5,5)
pathing_end=(15,15)
h=hallway(map)
pathSprites = [(0,0,0),'0.bmp','2.bmp','4.bmp','6.bmp']

# pygame.font.init()
# font = pygame.font.SysFont('Courier',25,True,False)
# im1=font.render('1',False,(0,0,0))
# im1.set_colorkey((255,255,255))

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
			if event.key==pygame.K_i:h=hallway(map)
			if event.key==pygame.K_n:step=True
			
	#allow user to modify the map
	editMap(pygame.mouse.get_pressed(),pygame.mouse.get_pos(),cellSize,map)
	
	if step:
		h.nextStep()
		step=False
	
	if (not paused)&(time%framesPerUpdate==0):
		h.nextStep()
	
	#render
	screen.fill((100,100,100))
	drawMap(map,mapColors)
	for loc in h.cpts:
		pygame.draw.rect(screen,(255,255,255),[loc.x*cellSize[0],loc.y*cellSize[1],cellSize[0],cellSize[1]],0)
	for loc in h.path:
		pygame.draw.rect(screen,(100,100,255),[loc.x*cellSize[0],loc.y*cellSize[1],cellSize[0],cellSize[1]],0)
	drawMap(h.md,mapColors2)
	drawMap(h.ad,pathSprites)
	
	screen.blit(soldier,(pathing_start[0]*cellSize[0],pathing_start[1]*cellSize[1]))
	screen.blit(s_dest,(pathing_end[0]*cellSize[0],pathing_end[1]*cellSize[1]))
	# screen.blit(im1,[0,0])
	pygame.display.flip()
	
	clock.tick(20)
pygame.quit()