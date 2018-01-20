import random

numList = []
for i in range(16):
	numList.append(i)

going = True
while going:
	rind = random.randrange(len(numList))
	rnum = numList.pop(rind)
	print(str(rnum))
	usrInput = input()
	if usrInput=='q':
		going = False
	else :
		print(format(rnum,'04b'))
	if len(numList)==0:
		going = False