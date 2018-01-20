		
class vector:
	def __init__(self,x,y=None):
		if isinstance(x,int):
			self.x=x
			self.y=y
		else:
			self.x=x[0]
			self.y=x[1]
	def __add__(self,v2):
		return vector(self.x+v2.x,self.y+v2.y)
	def __sub__(self,v2):
		return vector(self.x-v2.x,self.y-v2.y)
	def __mul__(self,v2):
		if isinstance(v2,int)==1:
			return vector(self.x*v2,self.y*v2)
		else:
			return vector(self.x*v2.x,self.y*v2.y)
	def dist2(self,v2):
		return (v2.x-self.x)**2+(v2.y-self.y)**2
	def dirTo(self,v2):
		closestDist=100000000
		for i in range(len(direction.getVs())):
			testDir = direction(i)
			testLoc = self + testDir
			testDist = testLoc.dist2(v2)
			if testDist<closestDist:
				closestDist=testDist
				closestDir=testDir
		return closestDir
	def of(self,arr):
		return arr[self.x][self.y]
	def set(self,arr,val):
		arr[self.x][self.y]=val
	def __str__(self):
		return 'vector('+str(self.x)+','+str(self.y)+')'
	def __eq__(self,v2):
		return (self.x==v2.x)&(self.y==v2.y)
	def cross(self,v2):
		return -self.y*v2.x+self.x*v2.y
class direction(vector):
	vs = (vector(0,-1),vector(1,0),vector(0,1),vector(-1,0))
	def __init__(self,d):
		if isinstance(d,int):
			self.index=d
		else:
			self.index=direction.getVs().index(d)
		self.update()
	def update(self):
		self.v=direction.getVs()[self.index]
		self.x=self.v.x
		self.y=self.v.y
	def rotateRight(self):
		self.rotateAmount(1)
	def rotateLeft(self):
		self.rotateAmount(-1)
	def rotateAmount(self,n):
		self.index=(self.index+n)%len(direction.getVs())
		self.update()
	@classmethod
	def getVs(cls):
		return cls.vs
	@classmethod
	def getDs(cls):
		return [direction(i) for i in range(len(direction.getVs()))]
		
def dist2(start,end):
	return (end[0]-start[0])**2+(end[1]-start[1])**2