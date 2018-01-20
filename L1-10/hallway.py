from vd import *

class hallway:
	def __init__(self,mapIn):
		self.padMap(mapIn)
		self.md=[[0]*len(self.map[0]) for i in range(len(self.map))]
		self.ad=[[0]*len(self.map[0]) for i in range(len(self.map))]
		self.cpts=[]
		self.id=1
		for j in range(len(self.map[0])):
			for i in range(len(self.map)):
				v=vector(i,j)
				if (v.of(self.map)==0)&(v.of(self.md)==0):
					self.fill(v)#points being evaluated #|(i==0)|(j==0)|(i==len(map[0])-1)|(j==len(map)-1)
		self.path=[]
		self.dist=0
	def padMap(self, mapIn):
		#add a boundary around the map to accommodate the map edge condition
		self.map=[[0]*(len(mapIn[0])+2) for i in range(len(mapIn)+2)]
		for j in range(1,len(self.map[0])-3):
			for i in range(1,len(self.map)-3):
				self.map[i][j]=mapIn[i][j]
	def contiguousNeighbors(self,loc):
		vs=[[0,-1],[1,-1],[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1]]
		return [vector(v)+loc for v in vs]
	def fill(self,loc):
		#assign the same ID number to contiguous obstacles
		loc.set(self.md,self.id)
		pts=[loc]
		self.cpts.append(loc)
		while len(pts)>0:
			newpts=[]
			for p in pts:
				for n in self.contiguousNeighbors(p):
					if self.onMap(n):
						if n.of(self.map)==0:#obstacle
							if n.of(self.md)==0:#not yet labeled
								n.set(self.md,self.id)
								newpts.append(n)
			pts=newpts
			self.cpts.extend(newpts)
		self.id+=1
	def onMap(self,loc):
		return (loc.x>=0)&(loc.x<len(self.map))&(loc.y>=0)&(loc.y<len(self.map[0]))
	def isOpen(self,loc):
		#notVisited = loc.of(self.md)==0
		if not self.onMap(loc): return False
		traversable = loc.of(self.map)!=0
		newGround = loc.of(self.md)==0#check to see if the tile was reached already
		return traversable&newGround
	def nextStep(self):
		nextPoints = []
		for p in self.cpts:
			pID = p.of(self.md)
			for d in direction.getDs():
				ahead = p+d
				if self.isOpen(ahead):
					ahead.set(self.ad,d.index+1)
					ahead.set(self.md,pID)
					nextPoints.append(ahead)
		self.cpts=nextPoints
		self.dist+=1#could be used to record hallway width
map1=[
[1,1,1,1,1],
[1,1,0,1,1],
[1,0,1,1,1],
[1,1,1,1,0],
[0,0,1,1,0]]
h=hallway(map1)