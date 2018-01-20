from vd import *
#one of several pathing modules
#bug pathing evaluates only nearby tiles
#then there is a refinement step available

# class arrow:
	# def __init__(self,loc,dist,dir):
		# self.loc=loc
		# self.dist=dist
		# self.dir=dir
	# def __str__(self):
		# return 'arrow(loc='+str(self.loc)+',dist='+str(self.dist)+',dirIndex='+str(self.dir.index)
class tile:
	def __init__(self,loc,dist):
		self.loc=loc
		self.dist=dist
		self.dirs=[0,0,0,0]
		self.width=0
	def getDirs(self):
		dirs=[]
		for i in range(len(self.dirs)):
			if self.dirs[i]==1: dirs.append(direction(i))
		return dirs
	def addDir(self,dir,dist):
		if dist<self.dist: self.dist=dist
		self.dirs[dir.index]=1
	def __str__(self):
		return 'tile(dist='+str(self.dist)+',dirs='+str(self.dirs)+',width='+str(self.width)
class pathing:
	def __init__(self,map,start,end):
		self.map=map
		self.md=[[0]*len(self.map[0]) for i in range(len(self.map))]
		for i in range(len(self.map)):
			for j in range(len(self.map[0])):
				self.md[i][j]=tile(vector(i,j),10000)
		self.start=vector(start)
		self.start.of(self.md).dist=0
		self.end=vector(end)
		self.cpts=[]
		self.cpts.append(self.start)
		self.dist=0
		self.state = 'spread'
		self.path=[]
	def isOpen(self,loc,dist):
		onMap = (loc.x>=0)&(loc.x<len(self.map))&(loc.y>=0)&(loc.y<len(self.map[0]))
		if not onMap: return False
		traversable = loc.of(self.map)!=0
		acceptablePathLength = dist<=loc.of(self.md).dist
		return traversable&acceptablePathLength
	def nextStep(self):
		if self.state=='spread':
			nextPoints = []
			for p in self.cpts:
				for d in direction.getDs():
					ahead = p+d
					if self.isOpen(ahead,self.dist):
						ahead.of(self.md).addDir(d,self.dist)
						if not ahead in nextPoints: nextPoints.append(ahead)
			if len(nextPoints)==0: 
				self.state='return'
				self.cpts=[self.end]
			else:
				self.cpts=nextPoints
			self.dist+=1
		elif self.state=='return':
			nextPoints = []
			for p in self.cpts:
				for d in p.of(self.md).getDirs():
					d.rotateAmount(2)#flip backwards
					behind = p+d
					behind.of(self.md).width=len(self.cpts)
					if not behind in nextPoints: nextPoints.append(behind)
			self.path.extend(self.cpts)
			self.cpts=nextPoints
			if len(nextPoints)==0:self.state='arrived'
		
# map1=[
# [1,1,1,1,1],
# [1,1,0,1,1],
# [1,0,0,1,1],
# [1,1,1,1,1],
# [1,1,1,1,1]]
# p=pathing(map1,(0,0),(4,4))
def prm():
	global p
	for j in range(len(p.map[0])):
		for i in range(len(p.map)):
			print(vector(i,j).of(p.md))
		print('---')