# This class contains the "plastic wrap" algorithm
# Use the method "plasticWrapChunks" to apply plastic wrap to each chunk in the collection.
from ij import IJ
from pcp_auto_count.umath import getPointsOnLineSegment

class PlasticWrap:

	# This is the main plastic wrap algorithm.
	@staticmethod
	def plasticWrapChunks(chunkCollection, expandBoundsBy = 0):
	
		chunkCount = len(chunkCollection.chunks)

		# Analyze each chunk.
		for i, c in enumerate(chunkCollection.chunks):
		
			IJ.showStatus("PCP Auto Count: Plastic Wrapping Chunks...")
			IJ.showProgress(i, chunkCount)
		
			# Expand the bounding box by a set amount for context.			
			if expandBoundsBy < 0:
				expandBoundsBy = 0
									
			bbMinX = c.minX - expandBoundsBy
			bbMaxX = c.maxX + expandBoundsBy
			bbMinY = c.minY - expandBoundsBy
			bbMaxY = c.maxY + expandBoundsBy
			
			if bbMinX < 0:
				bbMinX = 0
			if bbMinY < 0:
				bbMinY = 0
			if bbMaxX >= chunkCollection.imageWidth:
				bbMaxX = chunkCollection.imageWidth - 1
			if bbMaxY >= chunkCollection.imageHeight:
				bbMaxY = chunkCollection.imageHeight - 1
				
			# We are looking for "border pixels". Store their coordinates here.
			borderPoints = []
			
			# Any pixels in the border that were not originally part of the chunk will be noted here.
			borderChunkAdditions = []
			
			# FIRST SCAN: STRAIGHT DOWN SCAN
			# First scan for border points: Run a horizontal line from top to bottom of the box.
			
			for y in range(bbMinY, bbMaxY + 1):
				scanline = getPointsOnLineSegment(bbMinX, bbMaxX, y, y)
				closestWhitePixelX = -1
				furthestWhitePixelX = -1
				for p in scanline:
					if c.containsPixel(p[0], p[1]) == True:
						if closestWhitePixelX < 0:
							closestWhitePixelX = p[0]
						furthestWhitePixelX = p[0]
				if furthestWhitePixelX > 0:
					borderPoints.append([closestWhitePixelX, y])
					if furthestWhitePixelX > closestWhitePixelX + 1:
						for i in range(closestWhitePixelX + 1, furthestWhitePixelX + 1):
							borderPoints.append([i, y])
							if c.containsPixel(i, y) == False:
								borderChunkAdditions.append([i, y])
					elif furthestWhitePixelX == closestWhitePixelX + 1:
						borderPoints.append([furthestWhitePixelX, y])
					break # We stop scanning as soon as we had a scanline find one or more white pixels.
			
					
			# SECOND SCAN: FROM POINT DOWN THE RIGHT BORDER
			# Second scan: starting at the rightmost pixel found with coordinates (x, y):
			# Draw a line from (x, y) to (bbMaxX, y + 1).
			# Repeat, increasing destination y by 1 each time.
			# When a white pixel is found, you continue the scan, but startX moves to the x coord of the right-most white pixel found.
			
			# So, the starting pixel to draw our scanlines for this phase is the rightmost white pixel.			
			startX = borderPoints[-1][0]
			startY = borderPoints[-1][1]
			
			# If the first scanline would be vertical, we're on the edge of what we'd scan. We can skip this phase.
			run = bbMaxX - startX
			if run != 0:
			
				for endY in range(startY + 1, bbMaxY + 1):
				
					scanline = getPointsOnLineSegment(startX, bbMaxX, startY, endY)
					furthestWhitePixelIndex = 0
					for index, p in enumerate(scanline):
						if c.containsPixel(p[0], p[1]) == True:
							furthestWhitePixelIndex = index
								
					if furthestWhitePixelIndex > 0: # Notice we don't care about the point at the first index, since it was already added previously
						for i in range(1, furthestWhitePixelIndex + 1):
							borderPoints.append([scanline[i][0], scanline[i][1]])
							if c.containsPixel(scanline[i][0], scanline[i][1]) == False:
								borderChunkAdditions.append([scanline[i][0], scanline[i][1]])
						startX = borderPoints[-1][0]
						startY = borderPoints[-1][1]
						
						# If we are now starting at the rightmost border of the image, we can go to the next scan.
						if startX == bbMaxX:
							break
			
			# THIRD SCAN: FROM POINT TO THE LEFT ACROSS THE BOTTOM BORDER
			# Third scan. Starting at the most recent border pixel found with coordinates (x, y):
			# Draw a line from (x, y) to (bbMax - 1, bbMaxY).
			# Repeat, decreasing destination x by 1 each time.
			
			startX = borderPoints[-1][0]
			startY = borderPoints[-1][1]
			
			endX1 = bbMaxX
			
			for endX in range(endX1, bbMinX - 1, -1):
			
				scanline = getPointsOnLineSegment(startX, endX, startY, bbMaxY)
				furthestWhitePixelIndex = 0
				for index, p in enumerate(scanline):
					if c.containsPixel(p[0], p[1]) == True:
						furthestWhitePixelIndex = index
				
				if furthestWhitePixelIndex > 0:
					for i in range(1, furthestWhitePixelIndex + 1):
						borderPoints.append([scanline[i][0], scanline[i][1]])
						if c.containsPixel(scanline[i][0], scanline[i][1]) == False:
							borderChunkAdditions.append([scanline[i][0], scanline[i][1]])
					startX = borderPoints[-1][0]
					startY = borderPoints[-1][1]
					
					# If we are now starting at the bottom border of the image, we can go to the next scan.
					if startY == bbMaxY:
						break
			
			# FOURTH SCAN: FROM POINT UP THE LEFT BORDER
			# Fourth scan. We are now drawing points from the last border point to the bottom-left corner, incrementing up the left-most of the image.
			
			startX = borderPoints[-1][0]
			startY = borderPoints[-1][1]
			
			endY1 = bbMaxY
			
			for endY in range(endY1, bbMinY - 1, -1):
			
				scanline = getPointsOnLineSegment(startX, bbMinX, startY, endY)
				furthestWhitePixelIndex = 0
				for index, p in enumerate(scanline):
					if c.containsPixel(p[0], p[1]) == True:
						furthestWhitePixelIndex = index
				
				if furthestWhitePixelIndex > 0:
					for i in range(1, furthestWhitePixelIndex + 1):
						borderPoints.append([scanline[i][0], scanline[i][1]])
						if c.containsPixel(scanline[i][0], scanline[i][1]) == False:
							borderChunkAdditions.append([scanline[i][0], scanline[i][1]])
					startX = borderPoints[-1][0]
					startY = borderPoints[-1][1]
					
					# If we're now at the leftmost border of the image, we can go to the last scan.
					if startX == bbMinX:
						break
						
					
			# FIFTH (FINAL) SCAN: FROM POINT TO THE RIGHT ACROSS THE TOP BORDER
			# Fifth scan. This one is special because we need to end up back at the very first border point we found.
			# There should be no border points to find above it or at its level, nor any new border points to the right of it.
			# This does narrow the scope a bit.
			
			startX = borderPoints[-1][0]
			startY = borderPoints[-1][1]
			
			endX1 = bbMinX
			
			for endX in range(endX1, bbMaxX + 1):
				
				scanline = getPointsOnLineSegment(startX, endX, startY, bbMinY)
				furthestWhitePixelIndex = 0
				for index, p in enumerate(scanline):
					if c.containsPixel(p[0], p[1]) == True:
						furthestWhitePixelIndex = index
						
				if furthestWhitePixelIndex > 0:
					for i in range(1, furthestWhitePixelIndex + 1):
						if scanline[i] not in borderPoints:
							borderPoints.append([scanline[i][0], scanline[i][1]])
							if c.containsPixel(scanline[i][0], scanline[i][1]) == False:
								borderChunkAdditions.append([scanline[i][0], scanline[i][1]])
					
					startX = borderPoints[-1][0]
					startY = borderPoints[-1][1]
			
			# Recording plastic wrap pixels for specialized image output	
			c.plasticWrapBorder = borderPoints
			c.plasticWrapUniquePixels = borderChunkAdditions
			
			# Actually add the plastic pixels to the chunk
			for b in borderChunkAdditions:
				for col in c.columns:
					if b[0] == col.x:
						col.ys.append(b[1])
						break
			
			for col in c.columns:
				col.ys.sort()
				
			# Update stale size information
			c.getSize()

		IJ.showProgress(1, 1)
		
# This part only runs if the script is run directly, which should not happen.
if __name__ == "__main__" or __name__ == "__builtin__":
	print "This module is not meant to be run directly."
	
	
