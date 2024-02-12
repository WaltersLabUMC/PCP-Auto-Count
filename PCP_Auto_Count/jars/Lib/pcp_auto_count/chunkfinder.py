# This file contains the chunk-finding algorithm.
from ij import IJ
from ij.process import ByteProcessor
from pcp_auto_count.chunk import Chunk

class ChunkFinder:

	# This function takes an ImagePlus and finds all the potential chunks inside of it.
	# The chunks are added to the provided (empty) list of chunks.
	@staticmethod
	def FindChunks(imp, chunks):
	
		width = imp.width
		height = imp.height
		ipmain = imp.getProcessor()
		whitePixel = 255
		if ipmain.isInvertedLut() == True:
			whitePixel = 0
		bp = ByteProcessor(ipmain, True)
		
		oldestPossibleChunkIndex = 0
		skewerMultiple = 25
		skewerIncrement = 25
		
		for x in range(width):
		
			IJ.showStatus("PCP Auto Count: Finding Chunks...")
			IJ.showProgress(x, width)
		
			roundSpans = []
		
			currentSpanYs = []
			
			for y in range(height):
			
				if bp.getPixel(x, y) == whitePixel:
				
					if len(currentSpanYs) == 0:
						currentSpanYs.append(y)
					elif currentSpanYs[-1] == (y - 1):
						currentSpanYs.append(y)
					else:
						# Next chunk in the same column...
						roundSpans.append([currentSpanYs[0], currentSpanYs[-1]])
						currentSpanYs = [y]
						
			if not len(currentSpanYs) == 0:			
				roundSpans.append([currentSpanYs[0], currentSpanYs[-1]])
				currentSpanYs = []
			
			if x == 0:
				if len(roundSpans) > 0:
					for span in roundSpans:
						chunk = Chunk()
						chunk.addSpan(0, span[0], span[1])
						chunks.append(chunk)
						oldestPossibleChunkIndex = 0
			else:
				# For all but the first column, we need to see if the discovered pieces touch one or more existing chunks to the left.
				# If so, this piece (and possibly other chunks if touching more than one) must be consolidated into it, instead of added new.
				
				if len(roundSpans) > 0:
				
					for span in roundSpans:
					
						# Let's get the indexes of chunks this span touches.					
						touching = []
						
						for i in range(oldestPossibleChunkIndex, len(chunks)):
							if chunks[i].touchesSpan(x, span[0], span[1]) == True:
								touching.append(i)
								
						# If this span touches no existing chunks, it becomes a new one.
						if len(touching) == 0:					
							chunk = Chunk()
							chunk.addSpan(x, span[0], span[1])
							chunks.append(chunk)
						
						# If this span touches at least one chunk, add the span to the existing chunk (first one if multiple).
						elif len(touching) > 0:
						
							chunks[touching[0]].addSpan(x, span[0], span[1])
						
							# If the span touched more than one chunk, the latter chunks are absorbed into the first one.
							if len(touching) > 1:
							
								# Add the pixels from the other chunks to the first one
								for i in range(1, len(touching)):
									for s in chunks[touching[i]].spans:
										chunks[touching[0]].addSpan(s.x, s.minY, s.maxY)
										
								# Then remove the absorbed chunks from the list
								touching.pop(0)
								touching.sort()
								touching.reverse()
								
								oldestIsBiggerThan = 0
								for i in touching:
									chunks.pop(i)
									if oldestPossibleChunkIndex > i:
										oldestIsBiggerThan += 1
								
								if oldestIsBiggerThan > 0:
									oldestPossibleChunkIndex = oldestPossibleChunkIndex - oldestIsBiggerThan
									
					# Skewering helps reduce processing time for large images.
					# Do this every multiple of 50 chunks before moving on...
					
					if len(chunks) >= skewerMultiple:
						count = len(chunks)
						newOldestIndex = count
						for i in range(count - 1, oldestPossibleChunkIndex - 1, -1):
							if chunks[i].maxX >= x:
								if i < newOldestIndex:
									newOldestIndex = i
						oldestPossibleChunkIndex = newOldestIndex
						skewerMultiple = skewerMultiple + skewerIncrement								
				
								
		IJ.showProgress(1, 1)
								
		for chunk in chunks:
			IJ.showStatus("PCP Auto Count: Calculating Chunk Sizes...")
			chunk.getSize()
								
# This part only runs if the script is run directly, which should not happen.
if __name__ == "__main__" or __name__ == "__builtin__":
	print "This module is not meant to be run directly."
		
		
