import pygame

#pygame setup
pygame.init()
clock = pygame.time.Clock()
screenSize = (500,500)
screen = pygame.display.set_mode(screenSize)

#player data
coords = [250,0]
vel = [0,3]
acc = [0,0]

#hazard zone
hazardCoords = [250,250]

#main game loop
going = True
while going:
	#check if window was closed
	for event in pygame.event.get():
		if event.type==pygame.QUIT:
			going=False
	#use arrow keys to accelerate
	acc = [0,0];
	keys = pygame.key.get_pressed()
	if keys[pygame.K_DOWN]:
		acc[1]+=1
	if keys[pygame.K_UP]:
		acc[1]-=1
	if keys[pygame.K_RIGHT]:
		acc[0]+=1
	if keys[pygame.K_LEFT]:
		acc[0]-=1
	vel = [vel[0]+acc[0],vel[1]+acc[1]]
	coords = [coords[0]+vel[0],coords[1]+vel[1]]
	playerRect = pygame.Rect(coords[0],coords[1],50,50)
	hazardRect = pygame.Rect(hazardCoords[0],hazardCoords[1],50,50)
	if playerRect.colliderect(hazardRect):
		going=False
	
	#draw graphics to screen
	screen.fill((0,0,0))
	pygame.draw.rect(screen,(200,180,120),playerRect,0)
	pygame.draw.rect(screen,(255,0,0),hazardRect,0)
	pygame.display.flip()
	clock.tick(30)
pygame.quit()