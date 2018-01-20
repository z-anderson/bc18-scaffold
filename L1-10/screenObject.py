import pygame
import json
import os
import math

pygame.font.init()
font = pygame.font.SysFont('Courier',20,True,False)

class button:
	def __init__(self,rect,color,text,fn=None):
		self.rect=rect
		self.color=color
		self.text=text
		self.fn=fn
	def check(self,pt):
		#if clicked, execute fn
		if self.fn != None:
			if self.rect.collidepoint(pt):
				self.fn(pt)
	def render(self,screen):
		#render on screen
		if self.text!='':
			pygame.draw.rect(screen,self.color,self.rect,2)
			screen.blit(font.render(self.text,False,(255,255,255)),[self.rect.x+4,self.rect.y])
		else:
			pygame.draw.rect(screen,self.color,self.rect,0)
			
class screenMap:
	def __init__(self,coords,mapSize,cellSpace,cellSize,colors,fname,fn):
		self.coords = coords
		self.mapSize = mapSize
		self.cellSpace = cellSpace
		self.cellSize = cellSize
		self.colors = colors
		self.map=loadmap(fname,mapSize)
		self.rect = pygame.Rect(coords[0],coords[1],mapSize[0]*cellSpace[0],mapSize[1]*cellSpace[1])
		self.fn=fn
		self.indices=[]
	def check(self,pt):
		#if clicked, execute fn
		if self.fn != None:
			if self.rect.collidepoint(pt):
				#determine the (i,j) indices of the tile that was clicked
				self.fn(self.getIndices(pt))
	def render(self,screen):
		#render on screen
		for i in range(self.mapSize[0]):#draw tiles
			for j in range(self.mapSize[1]):
				if self.map[i][j]>0 :
					rcolor = self.colors[self.map[i][j]]
					pygame.draw.rect(screen,rcolor,[i*self.cellSpace[0],j*self.cellSpace[1],self.cellSize[0],self.cellSize[1]],0)
		for ind in self.indices:#draw any highlighted tiles during mouseover
			pygame.draw.rect(screen,(255,255,0),[ind[0]*self.cellSpace[0],ind[1]*self.cellSpace[1],self.cellSize[0]-4,self.cellSize[1]-4],0)
	def getIndices(self,pt):
		return ((pt[0]-self.coords[0])//self.cellSpace[0],(pt[1]-self.coords[1])//self.cellSpace[1])
	def nearEdge(self,loc):
		return ((loc[0]<game.EDGE) | (loc[0]>self.mapSize[0]-game.EDGE-1)|(loc[1]<game.EDGE) | (loc[1]>self.mapSize[1]-game.EDGE-1))
	def getDiskIndices(self,c):
		# if not self.rect.collidepoint(pt): return []
		# c=self.getIndices(pt)
		if self.map[c[0]][c[1]]==0: return []
		if self.nearEdge(c): return []
		indices=[]
		rad2 = 15
		rad = math.ceil(math.sqrt(rad2))
		for i in range(max(c[0]-rad,0),min(c[0]+rad+1,self.mapSize[0])):
			for j in range(max(c[1]-rad,0),min(c[1]+rad+1,self.mapSize[1])):
				if (self.map[i][j]!=0)&(not self.nearEdge((i,j))):
					dist2 = (i-c[0])**2+(j-c[1])**2
					if dist2<rad2-3:
						indices.append([i,j])
		return indices
	def setDiskIndices(self,pt):
		self.indices=self.getDiskIndices(pt)
class game:
	def __init__(self):
		#determine map size before opening game window
		tmap=loadmap('map.txt',(50,50))#50 by 50 default map size
		self.mapSize = (len(tmap),len(tmap[0]))
		self.cellSpace = (12,12)
		self.yos=self.mapSize[1]*self.cellSpace[1]#y offset for text fields
		self.screenSize = (self.mapSize[0]*self.cellSpace[0],self.yos+250)
		self.screen = pygame.display.set_mode(self.screenSize)
		subSize = (8,8)
		tColors = [(50,50,50),(200,200,200),(0,150,0)]
		self.terrain = screenMap([0,0],self.mapSize,self.cellSpace,self.cellSpace,tColors,'map.txt',self.tryExpand)
		subColors = [(0,0,0),(255,255,255),(150,150,255)]
		self.territory = screenMap([0,0],self.mapSize,self.cellSpace,subSize,subColors,'',None)
		bs=(45,24)
		self.b1 = button(pygame.Rect([12,self.yos+36,bs[0],bs[1]]),(200,200,200),'Buy',self.tryHouse)
		self.b2 = button(pygame.Rect([12,self.yos+60,bs[0],bs[1]]),(200,200,200),'Buy',self.tryFood)
		self.b3 = button(pygame.Rect([12,self.yos+84,bs[0],bs[1]]),(200,200,200),'Buy',self.tryFarm)
		self.b4 = button(pygame.Rect([12,self.yos+108,bs[0],bs[1]]),(200,200,200),'Buy',self.tryMilitary)
		self.screenObjects=[self.terrain,self.territory,self.b1,self.b2,self.b3,self.b4]
		#setup player resources
		self.money=350
		self.house=0
		self.food=0
		self.farm=0
		self.military=5
		self.space=0
		self.soil=0
		self.perimeter=0
		self.notice=''
		self.noticeAge=0
		self.battle=100
		self.time=0
	def updateLand(self):
		self.perimeter=0
		self.space=0
		self.soil=0
		for i in range(1,self.mapSize[0]-1):
			for j in range(1,self.mapSize[1]-1):
				if self.territory.map[i][j]>0:
					if self.terrain.map[i][j]==1: self.space+=1
					if self.terrain.map[i][j]==2: self.soil+=1
					neighbors = [(i+1,j),(i-1,j),(i,j+1),(i,j-1)]
					safe=True
					for n in neighbors:
						if not self.safeLocation(n):
							safe=False
							break
					if safe:
						self.territory.map[i][j]=1
					else:
						self.territory.map[i][j]=2
						self.perimeter+=1
	def safeLocation(self,ind):
		return (self.territory.map[ind[0]][ind[1]]>0)|(self.terrain.map[ind[0]][ind[1]]==0)
	def setNotice(self,text):
		self.notice=text
		self.noticeAge=0
	EDGE = 3 #clearance around map edge
	def tryExpand(self,loc):
		if self.battle<50:
			self.setNotice('Need 50 battle to expand')
			return
		if ((loc[0]<game.EDGE) | (loc[0]>self.territory.mapSize[0]-game.EDGE-1)|(loc[1]<game.EDGE) | (loc[1]>self.territory.mapSize[1]-game.EDGE-1)):
			self.setNotice('Can\'t build so close to edge')
			return
		if self.money<60:
			self.setNotice('Need 60 money to expand')
			return
		if (self.space>0) | (self.soil>0):
			if self.territory.map[loc[0]][loc[1]]==0:
				self.setNotice('Must expand from your base')
				return
		self.battle-=50
		self.money-=60
		indices = self.terrain.getDiskIndices(loc)
		for ind in indices:
			self.territory.map[ind[0]][ind[1]]=1
		self.updateLand()
	def tryHouse(self,pt):
		if self.space<=self.house:
			self.setNotice('Insufficient space for more houses')
			return
		if self.money<5:
			self.setNotice('Insufficient money for more houses')
			return
		self.house+=1
		self.money-=5
		self.setNotice('Built a house.')
	def tryFood(self,pt):
		if self.money<20:
			self.setNotice('Need 20 money to buy 10 food')
			return
		self.setNotice('Bought 10 food')
		self.food+=10
		self.money-=20
	def tryFarm(self,pt):
		if self.soil<=self.farm:
			self.setNotice('Insufficient soil for more farms')
			return
		if self.money<10:
			self.setNotice('Need 10 money for more farms')
			return
		self.farm+=1
		self.money-=10
		self.setNotice('Built a farm.')
	def tryMilitary(self,pt):
		if self.money<10:
			self.setNotice('Need 10 money for more military')
			return
		self.setNotice('Built more military.')
		self.military+=1
		self.money-=10
	def handleClick(self,pt):
		for s in self.screenObjects:
			s.check(pt)
	HRDAY=100#frames per day
	FF=5#food per farm
	BF=.02#battle factor
	def nextMoment(self):
		self.time+=1
		if self.time%game.HRDAY==0:#income
			self.money+=self.house
			self.money-=self.military
			if self.money<0:
				self.military+=self.money#unpaid military loss
				self.money=0
			self.food+=self.farm*game.FF
			self.food-=self.house
			if self.food<0:
				self.house+=self.food#unfed house loss
				self.food=0
		self.battle+=(self.military-self.perimeter)*game.BF
		if self.battle<0: self.battle=0 #lose condition
	def rbar(self,rect,c1,c2,frac):
		#render a bar graph at location rect, display fraction from 0 to 1
		prog=min(max(0,frac),1)*rect[2]//1;
		pygame.draw.rect(self.screen,c1,[rect[0],rect[1],prog,rect[3]],0)
		pygame.draw.rect(self.screen,c2,[rect[0]+prog,rect[1],rect[2]-prog,rect[3]],0)
	def render(self,mousepos):
		#highlight tiles when building:
		if self.terrain.rect.collidepoint(mousepos):
			self.terrain.setDiskIndices(self.terrain.getIndices(mousepos))
		else:
			self.terrain.indices=[]
		#game map
		self.screen.fill((0,0,0))
		for s in self.screenObjects:
			s.render(self.screen)
		#info text
		self.screen.blit(font.render('Money    '+format(self.money,' 4d')+format(self.house-self.military,'+4d'),False,(255,255,255)),[80,self.yos+12])
		self.screen.blit(font.render('Houses   '+format(self.house,' 4d')+'/'+format(self.space,' 4d')+' Space',False,(255,255,255)),[80,self.yos+36])
		self.screen.blit(font.render('Food     '+format(self.food,' 4d')+format(-self.house+game.FF*self.farm,'+4d'),False,(255,255,255)),[80,self.yos+60])
		self.screen.blit(font.render('Farms    '+format(self.farm,' 4d')+'/'+format(self.soil,' 4d')+' Soil',False,(255,255,255)),[80,self.yos+84])
		self.screen.blit(font.render('Military '+format(self.military,' 4d')+' occupying'+format(self.perimeter,' 4d')+' perimeter tiles',False,(255,255,255)),[80,self.yos+108])
		self.screen.blit(font.render('Battle   '+format(self.battle,' 4.0f')+format(game.HRDAY*(-self.perimeter+self.military)*game.BF,'+4.0f'),False,(255,255,255)),[80,self.yos+132])
		#self.rbar([260,self.yos+132,200,24],(150,150,255),(255,50,50),self.battle/200)
		self.screen.blit(font.render('         '+self.notice,False,(255,200,0)),[80,self.yos+156])
		self.screen.blit(font.render('Time     '+format(self.time//game.HRDAY,' 2d')+'d '+format(self.time%game.HRDAY,' 2d')+'h',False,(255,255,255)),[80,self.yos+180])
		self.screen.blit(font.render('Goal: Have 8 military per perimeter by day 100',False,(255,255,255)),[80,self.yos+204])
def loadmap(fname,mapSize):#uses mapSize as a default
	if os.path.isfile(fname):#load a map from file
		sf = open(fname,'r')
		str=sf.read();
		map = json.loads(str)
		sf.close()
	elif fname=='':#seed map with zeros
		map = [[0]*mapSize[1] for i in range(mapSize[0])]
	else:#generate a blank map
		print('Could not find map \''+fname+'\'. Using blank map instead.')
		map = [[1]*mapSize[1] for i in range(mapSize[0])]
	return map