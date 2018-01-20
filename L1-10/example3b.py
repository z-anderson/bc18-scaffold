import pygame
from support import *

#pygame setup
pygame.init()
clock = pygame.time.Clock()
screenSize = (500,500)
screen = pygame.display.set_mode(screenSize)

gameObjects=[]
#player data
player = gameObject([250,250],[0,0],[],[50,50],(200,180,120))
gameObjects.append(player)
#satellites
for i in range(50):
	for j in range(50):
		coords = [i*10,j*10]
		vel = [0,0]
		satellite = gameObject(coords,vel,player.coords,[5,5],(255,255,255))
		gameObjects.append(satellite)

#main game loop
going = True
while going:
	#check if window was closed
	for event in pygame.event.get():
		if event.type==pygame.QUIT:
			going=False
		if event.type==pygame.KEYDOWN:
			if event.key==pygame.K_r:
				for g in gameObjects:
					g.reset()
			
	#update and draw
	screen.fill((0,0,0))
	for g in gameObjects:
		pygame.draw.rect(screen,g.color,g.update(),0)
	
	# hazardRect = pygame.Rect(hazardCoords[0],hazardCoords[1],50,50)
	# if playerRect.colliderect(hazardRect):
		# going=False
	
	pygame.display.flip()
	clock.tick(30)
pygame.quit()