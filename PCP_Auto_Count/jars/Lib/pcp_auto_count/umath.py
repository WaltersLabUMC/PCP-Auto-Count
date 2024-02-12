# Utility math functions.
# Placed into their own file so multiple processes can use them generically.
import math

def angleFlipX(angle):
	return 360.0 - angle

def angleFlipY(angle):
	if angle == 0.0:
		return 180.0
	elif angle <= 180.0:
		return 180.0 - angle
	else:
		return 180.0 + (360.0 - angle)

# Gets angle using the slope formula. Transforms it based on the axisMode.	
def getAngleM(x1, x2, y1, y2, optionsObj = None):

	options = {
		"angleAxisZeroDirection": "east",
		"angleAxisDirectionClockwise": False,
		"angleAxisScaleZeroTo360" : True
	}

	if optionsObj is not None:
		options = {
			"angleAxisZeroDirection": optionsObj.angleAxisZeroDirection,
			"angleAxisDirectionClockwise": optionsObj.angleAxisDirectionClockwise,
			"angleAxisScaleZeroTo360" : optionsObj.angleAxisScaleZeroTo360
		}
		

	angle = -1.0
	
	# Transform coordinates due to computer images not being cartesian
	if y1 > y2:
		y2 = y2 + (2 * (y1 - y2))
	elif y1 < y2:
		y2 = y2 - (2 * (y2 - y1))
		
	# Check for undefined slope
	if x1 == x2:
		if y2 > y1:
			angle = 90.0
		elif y2 < y1:
			angle = 270.0
			
	else:	
		
		if y1 == y2:
			if x2 > x1:
				angle = 0.0
			elif x2 < x1:
				angle = 180.0
		else:
		
			slope = (y2 - y1) / (x2 - x1)
			angle = math.degrees(math.atan(slope))
			quadrant = 1
			
			if y2 > y1:
				if x2 > x1:
					quadrant = 1
				else:
					quadrant = 2
			else:
				if x2 > x1:
					quadrant = 4
				else:
					quadrant = 3
			
			if quadrant == 2 or quadrant == 3:
				angle = 180.0 + angle
			elif quadrant == 4:
				angle = 360.0 + angle
				
        cangle = angle
	
	if options["angleAxisZeroDirection"] == "north":
		cangle = angle - 90.0
	elif options["angleAxisZeroDirection"] == "west":
		cangle = angle - 180.0
	elif options["angleAxisZeroDirection"] == "south":
		cangle = angle - 270.0
		
	if cangle < 0.0:
		cangle = cangle + 360.0
	
	if options["angleAxisDirectionClockwise"] == True:
		cangle = 360.0 - cangle

	if options["angleAxisScaleZeroTo360"] == False:
		if cangle > 180.0:
			cangle = cangle - 360.0
			
	return (angle, cangle)



# A function to get the circular mean and angular dispersion of the angles in an array.
# Angles should be in degrees, and be 0 to (not including) 360.
def getCircularMeanOfAngles(angles, zeroTo360=True):
	
	n = float(len(angles))
	s = 0.0
	c = 0.0
	for a in angles:
		angle = a
		if angle < 0.0:
			angle = angle + 360.0
		s = s + math.sin(math.radians(angle))
		c = c + math.cos(math.radians(angle))
		
	s = s / n
	c = c / n
	
	r = math.sqrt(pow(s, 2) + pow(c, 2))
	v = 1 - r
	
	sdv = math.degrees(math.sqrt(math.log(1 / pow(r, 2))))
	
	sina = s / r
	cosa = c / r
	
	avg = -1.0
	#m = -1.0
	
	if s > 0.0 and c > 0.0:
		avg = math.degrees(math.atan(s / c))
		#m = math.degrees(math.atan( sina / cosa ))
	elif s < 0.0 and c > 0.0:
		avg = math.degrees(math.atan(s / c)) + 360.0
		#m = math.degrees(math.atan( sina / cosa )) + 360.0
	else:
		avg = math.degrees(math.atan(s / c)) + 180.0
		#m = math.degrees(math.atan( sina / cosa )) + 180.0
		
	if zeroTo360 == False:
		if avg > 180.0:
			avg = avg - 360.0
		
	return [avg, r, v, sdv]

# Gets the distance between two points.
def getDistance(startX, startY, endX, endY):
        return math.sqrt(pow(endX - startX, 2) + pow(endY - startY, 2))

# Gets the endpoint of a line segment given the starting point, angle (degrees), and distance.
def getEndpoint(startX, startY, angle, distance):
	rangle = math.radians(angle)
	x = distance * math.cos(rangle)
	x = float(startX) + x
	x = int(round(x, 0))
	y = distance * math.sin(rangle)
	y = float(startY) + y
	y = int(round(y, 0))
	# Don't forget the y axis is flipped in computer images...
	if y > startY:
		y = y - (2 * (y - startY))
	elif y < startY:
		y = y + (2 * (startY - y))
	return [x, y]

# Gets the endpoint of a line segment given the starting point, angle (degrees), and distance.
def getEndpointFloat(startX, startY, angle, distance):
	rangle = math.radians(angle)
	x = distance * math.cos(rangle)
	x = float(startX) + x
	y = distance * math.sin(rangle)
	y = float(startY) + y
	# Don't forget the y axis is flipped in computer images...
	if y > startY:
		y = y - (2.0 * (y - startY))
	elif y < startY:
		y = y + (2.0 * (startY - y))
	return (x, y)	


# Returns the slope of a line with the provided point coordinates.		
def getSlope(x1, x2, y1, y2):
	return float(y2 - y1) / float(x2 - x1)

# Find the missing x coordinate of a point on described line.
def findX(x1, y1, y2, m):	
	x2 = float(((y2 - y1) / m) + x1)
	return int(x2)

# Used for sorting coordinates in a line
def coordinateSortByX(coord):
	return float(coord[0]) + (float(coord[1]) * 0.0000000001)
	
def coordinateSortByY(coord):
	return float(coord[1]) + (float(coord[0]) * 0.0000000001)

# Finds the center of mass for pixels passed in.
# The columns list should be in the format used by Chunk.columns.
def findCenterOfMass(columns):

	centroid = [-1, -1]
		
	sumX = 0
	sumY = 0
	tally = 0
	
	for column in columns:
		sumX = sumX + (column[0]*len(column[1]))
		for y in column[1]:
			sumY = sumY + y
			tally = tally + 1
	
	avgX = float(sumX) / float(tally)
	avgY = float(sumY) / float(tally)
	
	return [avgX, avgY]

# Finds the center of mass for pixels passed in.
# The columns list should be in the format used by Cave.columns.
def findCenterOfMassB(columns):

	centroid = [-1, -1]
		
	sumX = 0
	sumY = 0
	tally = 0
	
	for column in columns:
		sumX = sumX + (column.x*len(column.ys))
		for y in column.ys:
			sumY = sumY + y
			tally = tally + 1
	
	avgX = float(sumX) / float(tally)
	avgY = float(sumY) / float(tally)
	
	return [avgX, avgY]


# Get all the points (rounded to integers) on the described line segments.	
def getPointsOnLineSegment(x1, x2, y1, y2):

	rise = y2 - y1
	run = x2 - x1
	
	pointsInLine = []
	
	# The line segment is just a single point, no math needed
	if rise == 0 and run == 0:
		pointsInLine.append([x1, y1])
		return pointsInLine
		
	startX = x1
	xincr = 1
	endX = x2 + 1
	if x1 > x2:
		xincr = -1
		endX = x2 - 1
	
	startY = y1
	yincr = 1
	endY = y2 + 1
	if y1 > y2:
		yincr = -1
		endY = y2 - 1	
	
	# Calculation for line with undefined slope
	if run == 0:
		for y in range(startY, endY, yincr):
			pointsInLine.append([x1, y])	
		return pointsInLine
		
	# Calculation for line with 0 slope
	if rise == 0:
		for x in range(startX, endX, xincr):
			pointsInLine.append([x, y1])			
		return pointsInLine
	
	# Calculation for any other line
	slope = float(rise) / float(run)
	intercept = float(y1) - (float(slope) * float(x1))
	
	p2 = []
	
	for x in range(startX, endX, xincr):
		floatY = (float(slope) * float(x)) + float(intercept)
		y = int(round(floatY))
		pointsInLine.append([x, y])
				
	for y in range(startY, endY, yincr):
		floatX = (float(y) - float(intercept)) / float(slope)
		x = int(round(floatX))
		p2.append([x, y])
	
	for p in p2:
		duplicate = False
		for op in pointsInLine:
			if p[0] == op[0] and p[1] == op[1]:
				duplicate = True
				break
		if duplicate == False:
			pointsInLine.append([p[0], p[1]])
	
	if abs(rise) > abs(run):
		pointsInLine.sort(key=coordinateSortByY)
	else:
		pointsInLine.sort(key=coordinateSortByX)
				
	if pointsInLine[0][0] != x1:
		pointsInLine.reverse()
	
	return pointsInLine
	

# This part only runs if the script is run directly, which should not happen.
if __name__ == "__main__" or __name__ == "__builtin__":
	print "This module is not meant to be run directly."
