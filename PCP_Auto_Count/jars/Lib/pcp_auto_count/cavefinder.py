# This file contains the cave-finding algorithm.
from pcp_auto_count.cave import Cave
from pcp_auto_count.umath import findCenterOfMassB, getAngleM

class CaveFinder:

	# This function takes a prospective chunk and finds its cave, if it has one.
	@staticmethod
	def FindCave(chunk, options=None):

                selectionMethod = "largest"
                smallCaveLimit = 0
                largeCaveLimit = 0

                if options is not None:
                        selectionMethod = options.trueCaveMode
                        if options.ignoreSmallCaves == True:
                                smallCaveLimit = options.smallCaveMaxSize
                        if options.ignoreLargeCaves == True:
                                largeCaveLimit = options.largeCaveMinSize
		
		caves = []
		
		for col in chunk.columns:
		
			roundSpans = []
		
			currentSpanYs = []
			
			for y in range(chunk.minY, chunk.maxY + 1):
			
				if y not in col.ys:
				
					if len(currentSpanYs) == 0:
						currentSpanYs.append(y)
					elif currentSpanYs[-1] == (y - 1):
						currentSpanYs.append(y)
					else:
						# Next cave in the same column...
						roundSpans.append([currentSpanYs[0], currentSpanYs[-1]])
						currentSpanYs = [y]
						
			if not len(currentSpanYs) == 0:			
				roundSpans.append([currentSpanYs[0], currentSpanYs[-1]])
				currentSpanYs = []
			
			if col.x == chunk.minX:
				for span in roundSpans:
					cave = Cave()
					cave.addSpan(col.x, span[0], span[1])
					caves.append(cave)
			else:
				# For all but the first column, we need to see if the discovered pieces touch one or more existing caves to the left.
				# If so, this piece (and possibly other caves if touching more than one) must be consolidated into it, instead of added new.
				
				for span in roundSpans:
				
					# Let's get the indexes of caves this span touches.					
					touching = []
					
					for i, cave in enumerate(caves):
						if cave.touchesSpan(col.x, span[0], span[1]) == True:
							touching.append(i)
							
					# If this span touches no existing caves, it becomes a new one.
					if len(touching) == 0:					
						cave = Cave()
						cave.addSpan(col.x, span[0], span[1])
						caves.append(cave)
					
					# If this span touches at least one cave, add the span to the existing cave (first one if multiple).
					elif len(touching) > 0:
					
						caves[touching[0]].addSpan(col.x, span[0], span[1])
					
						# If the span touched more than one cave, the latter caves are absorbed into the first one.
						if len(touching) > 1:
						
							# Add this pixels from the other caves to the first one
							for i in range(1, len(touching)):
								for s in caves[touching[i]].spans:
									caves[touching[0]].addSpan(s.x, s.minY, s.maxY)
									
							# Then remove the absorbed caves from the list
							touching.pop(0)
							touching.sort()
							touching.reverse()
							
							for i in touching:
								caves.pop(i)
		
		
		chunk.cave = None
		
		if len(caves) == 0:
			return False
		
		# Any prospective caves that are actually outside the chunk are invalid.
		for i in range(len(caves) - 1, -1, -1):
			if caves[i].minX == chunk.minX or caves[i].maxX == chunk.maxX or caves[i].minY == chunk.minY or caves[i].maxY == chunk.maxY:
				caves.pop(i)
				
		if len(caves) == 0:
			return False
				
		# Any cave that doesn't have more pixels than smallCaveLimit is disqualified.
		if smallCaveLimit > 0:
			for i in range(len(caves) -1, -1, -1):
				if caves[i].getSize() <= smallCaveLimit:
					caves.pop(i)
		
		if len(caves) == 0:
			return False

		if largeCaveLimit > 0:
                        for i in range(len(caves) -1, -1, -1):
                                if caves[i].getSize() >= largeCaveLimit:
                                        caves.pop(i)

                if len(caves) == 0:
                        return False
		
		# Use the provided criteria to determine the true cave.
		
		# If there's only one potential cave at this point, it's the true cave.
		if len(caves) == 1:
			chunk.cave = caves[0]
			chunk.findCaveCentroid()
			return True
		
		trueCave = None
		trueCaveCentroid = None
		
		if selectionMethod == "largest":
			largestSize = 0
			for cave in caves:
				size = cave.getSize()
				if size > largestSize:
					trueCave = cave
					largestSize = size
		
		elif selectionMethod == "highest":
			smallestY = -1
			for cave in caves:
				if (cave.minY < smallestY) or (smallestY < 0):
					smallestY = cave.minY
					trueCave = cave
		
		elif selectionMethod == "lowest":
			largestY = -1
			for cave in caves:
				if (cave.maxY > largestY):
					largestY = cave.maxY
					trueCave = cave
		
		elif selectionMethod == "leftmost":
			smallestX = -1
			for cave in caves:
				if (cave.minX < smallestX) or (smallestX < 0):
					smallestX = cave.minX
					trueCave = cave
		
		elif selectionMethod == "rightmost":
			largestX = -1
			for cave in caves:
				if (cave.maxX > largestX):
					largestX = cave.maxX
					trueCave = cave
					
		elif selectionMethod in ["northmost", "southmost", "eastmost", "westmost"]:
			
			trueCaveAngle = None
			trueCaveDiff = None
			
			targetAngle = 0.0
			if selectionMethod == "northmost":
				targetAngle = 90.0
			elif selectionMethod == "westmost":
				targetAngle = 180.0
			elif selectionMethod == "southmost":
				targetAngle = 270.0
			
			for i, cave in enumerate(caves):
			
				pCentroid = findCenterOfMassB(cave.columns)				
				pAngle = None
				if chunk.centroid[0] == pCentroid[0]:
					if chunk.centroid[1] > pCentroid[1]:
						pAngle = 90.0
					elif chunk.centroid[1] < pCentroid[1]:
						pAngle = 270.0
				else:
					pxAngle = getAngleM(chunk.centroid[0], pCentroid[0], chunk.centroid[1], pCentroid[1])
					pAngle = pxAngle[1]
			
				if trueCaveAngle is None and pAngle is not None: # First valid cave in the list, so automatic front-runner
				
					trueCaveCentroid = pCentroid
					trueCaveAngle = pAngle
					trueCaveDiff = abs(targetAngle - pAngle)
					if trueCaveDiff > 180.0:
						trueCaveDiff = trueCaveDiff - (2.0 * (trueCaveDiff - 180.0))
					trueCave = cave
					
				else:
				
					curDiff = abs(targetAngle - pAngle)
					if curDiff > 180.0:
						curDiff = curDiff - (2.0 * (curDiff - 180.0))
							
					if curDiff == trueCaveDiff:
						if cave.getSize() > trueCave.getSize():
							trueCaveAngle = pAngle
							trueCaveDiff = curDiff
							trueCaveCentroid = pCentroid
							trueCave = cave 
					elif curDiff < trueCaveDiff:
						trueCaveDiff = curDiff
						trueCaveAngle = pAngle
						trueCaveCentroid = pCentroid
						trueCave = cave			
			
		
		if trueCave is not None:
			chunk.cave = trueCave
			if trueCaveCentroid is not None:
				chunk.caveCentroid = trueCaveCentroid
				chunk.caveCentroidInt = [int(round(trueCaveCentroid[0])), int(round(trueCaveCentroid[1]))]
			else:
				chunk.findCaveCentroid()			
		
		return True

# This part only runs if the script is run directly, which should not happen.
if __name__ == "__main__" or __name__ == "__builtin__":
	print "This module is not meant to be run directly."
			
			
				
		
			
	
