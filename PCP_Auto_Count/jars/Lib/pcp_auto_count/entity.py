# "entity" is a class that chunk and cave both inherit from.
# This is because, while they are different, they both share
# the same functionality in having spans and columns of pixels.

class Column:
	def __init__(self):
		self.x = -1
		self.ys = []
		
class Span:
	def __init__(self):
		self.x = -1
		self.minY = -1
		self.maxY = -1
		
	def __eq__(self, other):
		return self.x == other.x and self.minY == other.minY
		
	def __gt__(self, other):
		if self.x > other.x:
			return True
		if self.x == other.x:
			if self.minY > other.minY:
				return True
		return False
			
	def __lt__(self, other):
		if self.x < other.x:
			return True
		if self.x == other.x:
			if self.minY < other.minY:
				return True
		return False
		
class Entity():

	def __init__(self):
		self.columns = []
		self.spans = []
		self.minX = -1
		self.maxX = -1
		self.minY = -1
		self.maxY = -1
		self.size = 0
		
	def addSpan(self, x, ystart, yend):
		
		# We add the span as a new column or to an existing one, and update metadata.
		
		# First, add the span
		span = Span()
		span.x = x
		span.minY = ystart
		span.maxY = yend
		
		self.spans.append(span)
		
		self.spans.sort() # Make sure to keep the correct order. Extremely important for absorbing other entities.
		
		# Second, the column.
		ys = range(ystart, yend + 1)
		
		# If a column is already on the books which would contain coordinates in this span, add it there.
		if len(self.columns) > 0:
			for col in self.columns:
				if col.x == x:
					for y in ys:
						col.ys.append(y)
					col.ys.sort()
					self.recalculateBoundaries(x, ystart, yend)
					return True
					
		# Otherwise, add the span's coordinates to a new column.		
		col = Column()
		col.x = x
		for y in ys:
			col.ys.append(y)
		self.columns.append(col)
		
		# Finally, we see if adding the pixels in this span changes the entity's bounding box.
		self.recalculateBoundaries(x, ystart, yend)
			
	def recalculateBoundaries(self, x, ystart, yend):
		if self.minX == -1 or x < self.minX:
			self.minX = x
		if self.maxX == -1 or x > self.maxX:
			self.maxX = x
		if self.minY == -1 or ystart < self.minY:
			self.minY = ystart
		if self.maxY == -1 or yend > self.maxY:
			self.maxY = yend
	
	def touchesSpan(self, x, ystart, yend):
	
		# Tests whether the described span of pixels touches an pixels in this entity.
		
		# Let's check our entity's spans backwards. This is typically how we'd check algorithmically.
		for i in range(len(self.spans) - 1, -1, -1):
			span = self.spans[i]
			if span.x < (x - 1):
				# At this point, we're checking spans too far to the left of our span to touch.
				return False
			elif span.x == (x - 1):
				# This is a span that may be touching.
				# They touch if the y ranges of the spans overlap.
				if ((yend >= span.minY) and (span.maxY >= ystart)) == True:
					return True
				
		# If we go through all the spans and none of them passed the test, the described span doesn't touch.
		return False
		
	def getSize(self):
		# Returns the number of pixels that make up this entity.
		size = 0
		if len(self.columns) > 0:
			for col in self.columns:
				size += len(col.ys)
		self.size = size
		return size

	def getBoundingBoxWidth(self):
                return (self.maxX - self.minX) + 1

        def getBoundingBoxHeight(self):
                return (self.maxY - self.minY) + 1
		
# This part only runs if the script is run directly, which should not happen.
if __name__ == "__main__" or __name__ == "__builtin__":
	print "This module is not meant to be run directly."
