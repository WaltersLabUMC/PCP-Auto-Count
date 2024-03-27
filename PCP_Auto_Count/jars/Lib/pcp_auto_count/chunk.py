# Represents a chunk found in an image, and functions related directly to them.
from pcp_auto_count.umath import getAngleM, getSlope, findX, findCenterOfMassB, getDistance, getEndpointFloat
from pcp_auto_count.cavefinder import CaveFinder
from pcp_auto_count.entity import Entity

class Chunk(Entity):

	def __init__(self):
		Entity.__init__(self)
		self.plasticWrapBorder = []
		self.centroidDistance = -1.0

	@staticmethod
	def getEntityType():
		return "chunk"

	def containsPixel(self, x, y):
		for col in self.columns:
			if col.x == x:
				for yy in col.ys:
					if yy == y:
						return True
		return False

	def divide(self):
		# This is called when the chunk is detected to be a doublet.
		# It splits itself down the middle vertically, and returns the resulting chunks.

		centerX = int(self.minX + (self.getBoundingBoxWidth() / 2.0))

		leftChunk = Chunk()
		rightChunk = Chunk()

		for span in self.spans:
			if span.x < centerX:
				leftChunk.addSpan(span.x, span.minY, span.maxY)
			else:
				rightChunk.addSpan(span.x, span.minY, span.maxY)

		return (leftChunk, rightChunk)

	def divideHorizontally(self):
		# This is called when the chunk is detected to be a doublet.
		# It splits itself across the center horizontally, and returns the resulting chunks.

		centerY = int(self.minY + (self.getBoundingBoxHeight() / 2.0))

		topChunk = Chunk()
		bottomChunk = Chunk()

		for span in self.spans:
			if span.minY < centerY and span.maxY < centerY: # Top chunk
				topChunk.addSpan(span.x, span.minY, span.maxY)
			elif span.minY >= centerY and span.maxY >= centerY: # Bottom chunk
				bottomChunk.addSpan(span.x, span.minY, span.maxY)
			else: # Split the difference
				topChunk.addSpan(span.x, span.minY, centerY - 1)
				bottomChunk.addSpan(span.x, centerY, span.maxY)

		return (topChunk, bottomChunk)

	def findCave(self, options):
		CaveFinder.FindCave(self, options)

	def findCentroid(self):
		self.centroid = findCenterOfMassB(self.columns)
		self.centroidInt = [int(round(self.centroid[0])), int(round(self.centroid[1]))]

	def findCaveCentroid(self):
		self.caveCentroid = findCenterOfMassB(self.cave.columns)
		self.caveCentroidInt = [int(round(self.caveCentroid[0])), int(round(self.caveCentroid[1]))]

        def findCentroidDistance(self):
                self.centroidDistance = getDistance(self.centroid[0], self.centroid[1], self.caveCentroid[0], self.caveCentroid[1])

	def getArrowCoords(self):
                startX = self.centroid[0]
                startY = self.centroid[1]

                distance = self.centroidDistance * 1.5
                if distance < 10.0:
                        distance = 10.0

                endpoint = getEndpointFloat(startX, startY, self.imageAngle, distance) 

                return(startX, startY, endpoint[0], endpoint[1])

	def calculateAngle(self, options):

		#----
		x1 = float(self.centroid[0])
		y1 = float(self.centroid[1])
		x2 = float(self.caveCentroid[0])
		y2 = float(self.caveCentroid[1])

                angleCalcs = getAngleM(x1, x2, y1, y2, options)
                self.imageAngle = angleCalcs[0]
		self.angle = angleCalcs[1]

	def findAngleOrientation(self):

		if self.centroid[0] > self.caveCentroid[0]:
			self.angleHorizontalDirection = "W"
		elif self.centroid[0] < self.caveCentroid[0]:
			self.angleHorizontalDirection = "E"
		else:
			self.angleHorizontalDirection = "="

		if self.centroid[1] > self.caveCentroid[1]:
			self.angleVerticalDirection = "N"
		elif self.centroid[1] < self.caveCentroid[1]:
			self.angleVerticalDirection = "S"
		else:
			self.angleVerticalDirection = "="

# This part only runs if the script is run directly, which should not happen.
if __name__ == "__main__" or __name__ == "__builtin__":
	print "This module is not meant to be run directly."
