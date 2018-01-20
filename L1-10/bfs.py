from vd import *
#one of several pathing modules
#bug pathing evaluates only nearby tiles
#then there is a refinement step available
# map1=[
# [1,1,1,1,1],
# [1,1,0,1,1],
# [1,0,0,1,1],
# [1,1,1,1,1],
# [1,1,1,1,1]]
# p=pathing(map1,(0,0),(4,4))

class pathing:
	def __init__(self,map,start,end):
		self.map=map
		self.md=[[0]*len(map[0]) for i in range(len(map))]
		self.start=vector(start)
		self.end=vector(end)
		self.cpts=[self.start]#points being evaluated
		self.state = 'spread'
		self.path=[self.end]
	def isOpen(self,loc):
		#notVisited = loc.of(self.md)==0
		onMap = (loc.x>=0)&(loc.x<len(self.map))&(loc.y>=0)&(loc.y<len(self.map[0]))
		if not onMap: return False
		traversable = loc.of(self.map)!=0
		newGround = loc.of(self.md)==0#check to see if the tile was reached already
		return traversable&newGround
	def nextStep(self):
		nextPoints = []
		for p in self.cpts:
			for d in direction.getDs():
				ahead = p+d
				if self.isOpen(ahead):
					nextPoints.append(ahead)
					ahead.set(self.md,d.index+1)
			if p==self.end: self.state='return'
		self.cpts=nextPoints
		if self.state=='return':
			currentPt = self.path[-1]
			tileDir = direction(self.path[-1].of(self.md)-1)
			tileDir.rotateAmount(2)#flip backwards
			behind = self.path[-1]+tileDir
			self.path.append(behind)
			if behind==self.start:self.state='arrived'