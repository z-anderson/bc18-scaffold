import pygame
from screenObject import *

pygame.init()
clock = pygame.time.Clock()
g = game()

going = True
paused = False
while going:
	for event in pygame.event.get():
		if event.type==pygame.QUIT:
			going=False
		if event.type==pygame.MOUSEBUTTONDOWN:
			keys = pygame.key.get_pressed()
			if keys[pygame.K_LSHIFT]:
				repeats=10
			else:
				repeats=1
			for r in range(repeats):
				g.handleClick(event.pos)
		if event.type==pygame.KEYDOWN:
			if event.key==pygame.K_SPACE:
				paused = not paused;
	if not paused: g.nextMoment()
	if g.battle==0: going=False
	g.render(pygame.mouse.get_pos())
	pygame.display.flip()
	
	clock.tick(20)
pygame.quit()