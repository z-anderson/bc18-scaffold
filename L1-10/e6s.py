import pygame, sys, os, json

mapSize = (20,20)
cellSize = (25,25)
screenSize = (mapSize[0]*cellSize[0],mapSize[1]*cellSize[1])
screen = pygame.display.set_mode(screenSize)


arimg={}#dictionary stores arrow sprites
for i in range(8):
	fname=str(i)+'.bmp'
	im=pygame.image.load(os.path.join('sprites',fname)).convert()
	im.set_colorkey((255,255,255))
	arimg[fname]=im

def newMap():
	global mapSize
	return [[1]*mapSize[1] for i in range(mapSize[0])]
def saveMap(map,fname):
	if os.path.isfile(fname):os.remove(fname)
	sf = open(fname,'w+')
	sf.write(json.dumps(map))
	sf.close()
def loadMap(fname):
	if os.path.isfile(fname):
		sf = open(fname,'r')
		str=sf.read();
		map = json.loads(str)
		sf.close()
	return map
def getIndices(pt,offset,cellSize):
	return ((pt[0]-offset[0])//cellSize[0],(pt[1]-offset[1])//cellSize[1])
def lineInd(start,end):
	currentPoint=start
	ptlist=[currentPoint]
	while(currentPoint!=end):
		closestDist=1000000
		for n in orthoNeighbors(currentPoint):
			ndist2=dist2(n,end)
			if ndist2<closestDist:
				closestDist=ndist2
				closestn=n
		currentPoint=closestn
		ptlist.append(currentPoint)
	return ptlist			
def dist2(start,end):
	return (end[0]-start[0])**2+(end[1]-start[1])**2
def orthoNeighbors(pt):
	return [(pt[0]-1,pt[1]),(pt[0]+1,pt[1]),(pt[0],pt[1]-1),(pt[0],pt[1]+1)]
prevPress=None
def editMap(mouseButtons,mousePos,cellSize,map):#pygame.mouse.get_pressed(),pygame.mouse.get_pos()
	global prevPress
	lmb = mouseButtons[0]
	rmb = mouseButtons[2]
	if lmb | rmb:#left or right mouse button pressed
		if lmb:wn=0#"write"
		else:wn=1#"erase"
		ind = getIndices(mousePos,(0,0),cellSize)
		if prevPress==None:
			map[ind[0]][ind[1]]=wn
		else:
			inds=lineInd(prevPress,ind)
			for ind in inds: map[ind[0]][ind[1]]=wn
		prevPress=ind
	else:
		prevPress=None
def drawMap(map, mapColors):
	global cellSize, screen
	for i in range(len(map)):
		for j in range(len(map[0])):
			val=map[i][j]
			if val>0:
				if val>=len(mapColors):val=val%len(mapColors)
				rcolor = mapColors[val]
				if isinstance(rcolor,tuple):
					pygame.draw.rect(screen,rcolor,[i*cellSize[0],j*cellSize[1],cellSize[0],cellSize[1]],0)
				else:
					screen.blit(arimg[rcolor],[i*cellSize[0],j*cellSize[1]])
		
	