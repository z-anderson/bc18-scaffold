import pygame
import math
#define gameObject
class gameObject:
	def __init__(self,coords,vel,orbits,size,color):
		self.startCoords=[coords[0],coords[1]]
		self.coords=coords
		self.vel=vel
		self.orbits=orbits
		self.size=size
		self.color=color
	def update(self):
		if len(self.orbits)==0:#controlled by keyboard
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
		else: #orbits the target object
			vector = [self.coords[0]-self.orbits[0],self.coords[1]-self.orbits[1]]
			radius = math.sqrt(vector[0]**2+vector[1]**2)
			if radius<1:radius=1#avoid divide-by-zero
			fact = -1000
			acc = [fact*vector[0]/radius**3,fact*vector[1]/radius**3]
		self.vel[0]+=acc[0]
		self.vel[1]+=acc[1]
		self.coords[0]+=self.vel[0]
		self.coords[1]+=self.vel[1]
		return pygame.Rect(self.coords[0],self.coords[1],self.size[0],self.size[1])
	def reset(self):
		if len(self.orbits)!=0:#only reset the location of the satellites
			self.coords[0]=self.startCoords[0]
			self.coords[1]=self.startCoords[1]
			self.vel=[0,0]