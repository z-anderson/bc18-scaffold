import pdb, traceback
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
		self.cpt=self.start#current point
		self.state='free'#free walking mode
		self.closest=self.cpt.dist2(self.end)
		self.path=[]
	def isOpen(self,loc):
		#notVisited = loc.of(self.md)==0
		onMap = (loc.x>=0)&(loc.x<len(self.map))&(loc.y>=0)&(loc.y<len(self.map[0]))
		if not onMap: return False
		traversable = loc.of(self.map)!=0
		return traversable
	def nextStep(self):
		if self.state=='free':#free to move in open terrain
			self.dir=self.cpt.dirTo(self.end)#head toward the goal
			ahead = self.cpt + self.dir
			if self.isOpen(ahead):
				self.moveAhead()
			else:
				self.closest=self.cpt.dist2(self.end)#record closest position
				self.state='follow'
		if self.state=='follow':#following a wall
			#continue turning to the right until the way is clear.
			for i in range(len(direction.getVs())):
				if self.isOpen(self.cpt+self.dir): break
				self.dir.rotateRight()
			#make a move, then turn the moving direction to the left
			self.moveAhead()
			self.dir.rotateLeft()
			#if you have reached a position closer than ever before, exit follow mode
			if self.cpt.dist2(self.end)<self.closest:
				self.state='free'
		if self.cpt==self.end:
			self.state='arrived'
		# self.printArr()
	def printArr(self):
		print('')
		for j in range(len(self.md[0])):
			s=''
			for i in range(len(self.md)):
				s+=str(self.md[i][j])
			print(s)
		print(self.dir)
		print(self.state)
	def moveAhead(self):
		self.cpt.set(self.md,self.dir.index+1)#record tile visit
		self.cpt=self.cpt+self.dir
		self.path.append(self.cpt)
	def refine(self):
		#tries to improve the path
		if len(self.path)<=2:return
		# pdb.set_trace()
		i=0
		while i<len(self.path)-2:
			try:
				v1=self.path[i+1]-self.path[i]
				v2=self.path[i+2]-self.path[i+1]
				crossProduct=v1.cross(v2)
				d1=direction(v1)
				d1.rotateAmount(crossProduct)
				alt=self.path[i]+d1
				if self.isOpen(alt):
					self.path[i+1]=alt
				repeats=0
				for j in range(i+2,len(self.path)):
					if self.path[j]==self.path[i+1]:repeats=j-(i+1)
				for r in range(repeats):
					del self.path[i+1]
			except:
				pdb.set_trace()
				traceback.print_exc()
			i+=1
