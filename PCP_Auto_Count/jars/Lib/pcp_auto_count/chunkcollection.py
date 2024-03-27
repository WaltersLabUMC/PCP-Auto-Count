# This class holds a list of chunks, and provides methods to process them.
from ij import IJ, ImagePlus
from ij.measure import ResultsTable
from java.awt import Color
from pcp_auto_count.chunkfinder import ChunkFinder
from pcp_auto_count.umath import getCircularMeanOfAngles
from pcp_auto_count.drawing import drawArrow, drawText
from pcp_auto_count.rosediagram import RoseDiagram
from pcp_auto_count.plasticwrap import PlasticWrap

imageTypes = { ImagePlus.COLOR_RGB : "RGB", ImagePlus.GRAY8 : "8-bit", ImagePlus.GRAY16 : "16-bit", ImagePlus.GRAY32 : "32-bit", ImagePlus.COLOR_256 : "8-bit color"}
blackColor = Color(0, 0, 0)
whiteColor = Color(255, 255, 255)
magentaColor = Color(255, 0, 255)
redColor = Color(255, 0, 0)
purpleColor = Color(80, 16, 208)
yellowColor = Color(255, 255, 0)
cyanColor = Color(0, 255, 255)
grayColor = Color(66, 66, 66)
blueColor = Color(100, 149, 237)
transparentColor = Color(0, 0, 0, 0)


degreeSign = u"\N{DEGREE SIGN}"
angleLabel = "Angle" + degreeSign

class ChunkCollection:

	# Constructor
	def __init__(self):
		self.chunks = []
		self.noiseChunks = []
		self.conglomerates = []
		self.tooWideChunks = []
		self.tooTallChunks = []
		self.doubletBothAxisChunks = []
		self.removedBorderChunks = []
		self.badChunks = []

		self.imageWidth = 0
		self.imageHeight = 0
		self.imageDepth = 1
		self.imageType = "RGB"
		self.imageTitle = "untitled"

	# Returns how many chunks currently exist.
	def count(self):
		return len(self.chunks)

	# Adds a chunk to the collection
	def append(self, chunk):
		self.chunks.append(chunk)

	# Scans an ImagePlus for chunks, noise included.
	def loadChunksFromImage(self, imp):
		self.imageWidth = imp.width
		self.imageHeight = imp.height
		self.imageDepth = imp.getNSlices()
		self.imageType = imageTypes[imp.type]
		self.imageTitle = imp.title
		ChunkFinder.FindChunks(imp, self.chunks)

	# Removes tiny chunks from the list to be processed.
	def removeNoiseChunks(self, size):
		count = len(self.chunks)
		for i in range(count - 1, -1, -1):
			IJ.showStatus("PCP Auto Count: Removing Noise...")
			IJ.showProgress(count - i, count)
			if self.chunks[i].size <= size:
				self.noiseChunks.append(self.chunks.pop(i))
		IJ.showProgress(1, 1)

	# Remove chunks which are too large to be processed.
	def removeConglomerates(self, size):
                count = len(self.chunks)
                for i in range(count - 1, -1, -1):
                        IJ.showStatus("PCP Auto Count: Removing Conglomerates...")
                        IJ.showProgress(count - i, count)
                        if self.chunks[i].size >= size:
                                self.conglomerates.append(self.chunks.pop(i))
                IJ.showProgress(1, 1)

	# Remove chunks which are too wide or too tall.
	def removeOblongChunks(self, tooWideMultiplier = 0.0, tooTallMultiplier = 0.0, checkTooWide = True, checkTooTall = True):
		if tooWideMultiplier <= 0.0:
			checkTooWide = False
		if tooTallMultiplier <= 0.0:
			checkTooTall = False
		if checkTooWide == False and checkTooTall == False:
			return False
		count = self.count()
		for i in range(count - 1, -1, -1):
			IJ.showStatus("PCP Auto Count: Removing oblong chunks...")
			IJ.showProgress(count - i, count + 1)
			c = self.chunks[i]
			w = float(c.getBoundingBoxWidth())
			h = float(c.getBoundingBoxHeight())
			if checkTooWide:
				if w >= h * tooWideMultiplier:
					self.tooWideChunks.append(self.chunks.pop(i))
					continue
			if checkTooTall:
				if h >= w * tooTallMultiplier:
					self.tooTallChunks.append(self.chunks.pop(i))

        IJ.showProgress(1, 1)

	# Split chunks which are too wide or too tall into two separate ones.
	def splitDoubletChunks(self, tooWideMultiplier = 0.0, tooTallMultiplier = 0.0, checkTooWide = True, checkTooTall = True):
		if tooWideMultiplier <= 0.0:
			checkTooWide = False
		if tooTallMultiplier <= 0.0:
			checkTooTall = False
		if checkTooWide == False and checkTooTall == False:
			return False

		count = self.count()

		for i in range(count - 1, -1, -1):
			IJ.showStatus("PCP Auto Count: Finding Doublets...")
			IJ.showProgress(count - i, count + 1)
			c = self.chunks[i]
			w = float(c.getBoundingBoxWidth())
			h = float(c.getBoundingBoxHeight())
			isTooWide = False
			isTooTall = False
			if checkTooWide:
				if w >= h * tooWideMultiplier:
					isTooWide = True

			if checkTooTall:
				if h >= w * tooTallMultiplier:
					isTooTall = True

			if isTooWide and isTooTall:
				self.doubletBothAxisChunks.append(self.chunks.pop(i))
			elif isTooWide:
				splitChunks = c.divide()
				self.chunks.pop(i)
				self.chunks.insert(i, splitChunks[1])
				self.chunks.insert(i, splitChunks[0])
			elif isTooTall:
				splitChunks = c.divideHorizontally()
				self.chunks.pop(i)
				self.chunks.insert(i, splitChunks[1])
				self.chunks.insert(i, splitChunks[0])

		IJ.showProgress(1, 1)

	# Removes chunk at the image border.
	def removeBorderChunks(self, offset = 0):
		count = self.count()
		adjustedOffset = 1 + offset
		for i in range(count - 1, -1, -1):
			IJ.showStatus("PCP Auto Count: Removing Border Chunks...")
			IJ.showProgress(count - i, count)
			if self.chunks[i].minX < adjustedOffset or self.chunks[i].minY < adjustedOffset:
				self.removedBorderChunks.append(self.chunks.pop(i))
			elif self.chunks[i].maxX >= self.imageWidth - adjustedOffset:
				self.removedBorderChunks.append(self.chunks.pop(i))
			elif self.chunks[i].maxY >= self.imageHeight - adjustedOffset:
				self.removedBorderChunks.append(self.chunks.pop(i))
		IJ.showProgress(1, 1)

	# Uses vector math to find new borders as though you were plastic wrapping them.
	# Mostly useful for chunks with true caves that aren't fully enclosed in the chunk.
	def plasticWrapChunks(self, expandBoundsBy = 0):
		PlasticWrap.plasticWrapChunks(self)

	# Finds the true cave of each chunk in the collection.
	# The cavefinder also finds the cave centroid when a cave is detected.
	def findCaves(self, options=None):
		count = self.count()
		for i, c in enumerate(self.chunks):
			IJ.showStatus("PCP Auto Count: Finding Caves...")
			IJ.showProgress(i, count)
			c.findCave(options)

	# Removes any chunk that has no cave.
	def removeCavelessChunks(self):
		count = self.count()
		for i in range(len(self.chunks) - 1, -1, -1):
			IJ.showStatus("PCP Auto Count: Marking Bad Chunks...")
			IJ.showProgress(count - i, count)
			if self.chunks[i].cave is None:
				self.badChunks.append(self.chunks.pop(i))
			# Also remove any chunk where the chunk centroid is the same point as the cave centroid.
			elif self.chunks[i].centroidInt[0] == self.chunks[i].caveCentroidInt[0] and self.chunks[i].centroidInt[1] == self.chunks[i].caveCentroidInt[1]:
                                self.badChunks.append(self.chunks.pop(i))

	# Finds the centroids of each chunk.
	def findCentroids(self):
		count = self.count()
		for i, c in enumerate(self.chunks):
			IJ.showStatus("PCP Auto Count: Calculating chunk centroids...")
			IJ.showProgress(i, count)
			c.findCentroid()

	# Calculates the cell-PCP angle for each chunk.
	def calculateAngles(self, options):
		count = self.count()
		for i, c in enumerate(self.chunks):
			IJ.showStatus("PCP Auto Count: Taking angle measurements...")
			IJ.showProgress(i, count)
			c.calculateAngle(options)
			c.findAngleOrientation()

	# Generates a unique numeric label for each chunk for identification on the image and/or results table.
	def generateChunkLabels(self):
		count = self.count()
		for i, chunk in enumerate(self.chunks):
			IJ.showStatus("PCP Auto Count: Generating Chunk Labels...")
			IJ.showProgress(i, count)
			chunk.label = str(i + 1)
		count = len(self.badChunks)
		for i, badChunk in enumerate(self.badChunks):
			IJ.showStatus("PCP Auto Count: Generating Bad Chunk Labels...")
			IJ.showProgress(i, count)
			badChunk.label = "BAD_" + str(i + 1)
		count = len(self.removedBorderChunks)
		for i, removedBorderChunk in enumerate(self.removedBorderChunks):
			IJ.showStatus("PCP Auto Count: Generating Removed Border Chunk Labels...")
			IJ.showProgress(i, count)
			removedBorderChunk.label = "REM_" + str(i + 1)
		IJ.showProgress(1, 1)

	# Gets an overlay image containing only the arrows.
	# Users can put this over the original for comparison.
	def getOverlayFromChunks(self, options):
		if self.imageWidth < 1 or self.imageHeight < 1:
			return None

		IJ.showStatus("PCP Auto Count: Creating Overlay...")
		IJ.showProgress(0, 1)

		IJ.newImage("Overlay - " + self.imageTitle, "RGB", self.imageWidth, self.imageHeight, self.imageDepth)
		imp = IJ.getImage()
		ip = imp.getProcessor()

		ip.setColor(transparentColor)
		ip.fill()

		if options.outputOverlayArrows == True:
			self.drawArrowsOnImage(imp, options.getColorArrows())

		if options.outputOverlayLabels == True or options.outputOverlayAngles == True:
                        fontSize = 12
                        if options.outputOverlayOverrideFontSize == True:
                                fontSize = options.outputOverlayFontSize
			self.drawAngleLabelsOnImage(imp, options.outputOverlayLabels, options.outputOverlayAngles, options.getColorLabels(), fontSize)

		imp.updateAndRepaintWindow()

		return imp

	# A sanity check that draws the detected pixels of each chunk on a new image.
	# We can compare this to the original to get an idea if everything desirable is being detected.
	# Returns None if there is no image to process (shouldn't happen), or a reference to the new image.
	def chunksToNewImage(self, options):
		if self.imageWidth < 1 or self.imageHeight < 1:
			return None

		IJ.showStatus("PCP Auto Count: Drawing Output Image...")
		IJ.showProgress(0, 1)

		IJ.newImage("Detected chunks - " + self.imageTitle, "RGB", self.imageWidth + options.outputImageMarginPixels, self.imageHeight, self.imageDepth)
		imp = IJ.getImage()
		ip = imp.getProcessor()

		ip.setColor(blackColor)
		ip.fill()

		# If the user wants the gray margin, we color it in here.
		if options.outputImageMarginPixels > 0:
			ip.setColor(grayColor)
			ip.fillRect(self.imageWidth, 0, options.outputImageMarginPixels, self.imageHeight)

		ip.setColor(whiteColor)
		count = self.count()
		for i, c in enumerate(self.chunks):
			IJ.showStatus("PCP Auto Count: Drawing Successful Chunks...")
			IJ.showProgress(i, count)
			for col in c.columns:
				for y in col.ys:
					ip.drawPixel(col.x, y)

		# We only care about plastic wrap drawing options if it was actually used
		if options.usePlasticWrap == True:

			# Plastic wrap was used if we get here.

			if options.outputImagePlasticWrapBorder == True:
				# If we get here, the user wants to draw the plastic wrap pixels.
				# In either mode, drawing all such pixels in yellow is fine to start.
				ip.setColor(options.getColorPlasticWrap())
				#ip.setColor(yellowColor)
				for i, c in enumerate(self.chunks):
					IJ.showStatus("PCP Auto Count: Drawing Plastic Wrap Pixels...")
					IJ.showProgress(i, count)
					if len(c.plasticWrapBorder) > 1:
						for p in c.plasticWrapBorder:
							ip.drawPixel(p[0], p[1])

				if options.outputImagePlasticWrapAddedWeight == True:
					# If the second mode was used, unique plastic wrap pixels should be in cyan instead of yellow.
					ip.setColor(options.getColorPlasticWrapNew())
					#ip.setColor(cyanColor)
					for i, c in enumerate(self.chunks):
						IJ.showStatus("PCP Auto Count: Drawing Plastic Wrap Added Weight...")
						IJ.showProgress(i, count)
						if len(c.plasticWrapUniquePixels) > 0:
							for p in c.plasticWrapUniquePixels:
								ip.drawPixel(p[0], p[1])

			else:
				# If plastic wrap was used but the user doesn't want those pixels highlighted, we actually need to draw any unique pixels in black.
				# This is because they were technically added to the original chunk pixels, which were already drawn in white.
				for i, c in enumerate(self.chunks):
					IJ.showStatus("PCP Auto Count: Hiding Plastic Wrap Added Weight...")
					IJ.showProgress(i, count)
					if len(c.plasticWrapUniquePixels) > 0:
						ip.setColor(blackColor)
						for p in c.plasticWrapUniquePixels:
							ip.drawPixel(p[0], p[1])

		if options.outputImageNoise == True and len(self.noiseChunks) > 0:
			count = len(self.noiseChunks)
			ip.setColor(options.getColorNoise())
			#ip.setColor(magentaColor)
			for i, n in enumerate(self.noiseChunks):
				IJ.showStatus("PCP Auto Count: Drawing removed noise...")
				IJ.showProgress(i, count)
				for col in n.columns:
					for y in col.ys:
						ip.drawPixel(col.x, y)

		if options.outputImageConglomerates == True and len(self.conglomerates) > 0:
                        count = len(self.conglomerates)
                        ip.setColor(options.getColorConglomerates())
                        for i, n in enumerate(self.conglomerates):
                                IJ.showStatus("PCP Auto Count: Drawing removed conglomerates...")
                                IJ.showProgress(i, count)
                                for col in n.columns:
                                        for y in col.ys:
                                                ip.drawPixel(col.x, y)

		if options.outputImageBadCells == True and len(self.badChunks) > 0:
			count = len(self.badChunks)
			ip.setColor(options.getColorBadChunks())
			#ip.setColor(redColor)
			for i, b in enumerate(self.badChunks):
				IJ.showStatus("PCP Auto Count: Drawing bad chunks...")
				IJ.showProgress(i, count)
				for col in b.columns:
					for y in col.ys:
						ip.drawPixel(col.x, y)

		if options.outputImageRemovedBorderCells == True and len(self.removedBorderChunks) > 0:
			count = len(self.removedBorderChunks)
			ip.setColor(options.getColorBorderChunks())
			#ip.setColor(purpleColor)
			for i, r in enumerate(self.removedBorderChunks):
				IJ.showStatus("PCP Auto Count: Drawing removed border chunks...")
				IJ.showProgress(i, count)
				for col in r.columns:
					for y in col.ys:
						ip.drawPixel(col.x, y)

		if options.outputImageRemovedOblongCells == True:
                        IJ.showStatus("PCP Auto Count: Drawing removed border chunks...")
                        ip.setColor(options.getColorOblongChunks())
                        #ip.setColor(blueColor)
                        if len(self.tooWideChunks) > 0:
                                for tw in self.tooWideChunks:
                                        for col in tw.columns:
                                                for y in col.ys:
                                                        ip.drawPixel(col.x, y)
                        if len(self.tooTallChunks) > 0:
                                for tt in self.tooTallChunks:
                                        for col in tt.columns:
                                                for y in col.ys:
                                                        ip.drawPixel(col.x, y)

		imp.updateAndRepaintWindow()

		# Cleanup
		ip = None

		IJ.showProgress(1, 1)

		return imp

	# Draws arrows representing all chunk angles on an image.
	def drawArrowsOnImage(self, imp, arrowColor):
		count = self.count()
		for i, c in enumerate(self.chunks):
			IJ.showStatus("PCP Auto Count: Drawing arrows for angle measurements...")
			IJ.showProgress(i, count)
			coords = c.getArrowCoords()
			drawArrow(imp, arrowColor, coords[0], coords[1], coords[2], coords[3])

	# Draws angle labels and/or angle measures at each chunk centroid.
	def drawAngleLabelsOnImage(self, imp, outputImageLabels, outputImageAngles, textColor, fontSize = 12):
		if outputImageLabels == True or outputImageAngles == True:
			count = self.count()
			for i, c in enumerate(self.chunks):
				IJ.showStatus("PCP Auto Count: Drawing chunk labels...")
				IJ.showProgress(i, count)
				text = ""
				if outputImageLabels == True and outputImageAngles == False:
					text = "[" + c.label + "]"
				elif outputImageLabels == False and outputImageAngles == True:
					text = str(round(c.angle, 3)) + degreeSign
				else:
					text = "[" + c.label + "]   " + str(round(c.angle, 3)) + degreeSign
				drawText(imp, text, c.centroidInt[0], c.centroidInt[1], textColor, fontSize)


	# Generates a table showing the angle of each detected cell, and other metrics.
	def showAngleResultsTable(self):
		IJ.showStatus("PCP Auto Count: Generating Results Table...")
		table = ResultsTable()
		if len(self.chunks) > 0:
			count = self.count()
			for i, c in enumerate(self.chunks):
				IJ.showProgress(i, count)
				table.addRow()
				table.addValue("Label", c.label)
				table.addValue("Chunk Centroid X", c.centroid[0])
				table.addValue("Chunk Centroid Y", c.centroid[1])
				table.addValue('Cave Centroid X', c.caveCentroid[0])
				table.addValue('Cave Centroid Y', c.caveCentroid[1])
				table.addValue('Vector Length', c.centroidDistance)
				table.addValue(angleLabel, c.angle)
		else:
			IJ.showProgress(1, 1)
			table.addRow()
			table.addValue("Label", "No chunks found.")
			table.addValue("Chunk Centroid X", "")
			table.addValue("Chunk Centroid Y", "")
			table.addValue('Cave Centroid X', "")
			table.addValue('Cave Centroid Y', "")
			table.addValue('Vector Length', "")
			table.addValue(angleLabel, "")

		table.show('Angle Results for Chunks - ' + self.imageTitle)

	# Shows a window with aggregate statistics about the angle data.
	def showAngleSummary(self, options):

		# We don't need to do any calculations if neither of the below outputs are desired.
		if options.outputCellSummary == False and options.outputRoseDiagram == False:
			return False

		chCount = self.count()

		count = 0
		badCount = 0
		totalCount = 0
		processedPercent = "N/A"
		minAngle = "N/A"
		maxAngle = "N/A"
		average = "N/A"
		stdDeviation = "N/A"
		med = "N/A"
		circularMean = ["N/A", "N/A", "N/A", "N/A"]

		angles = []
		for i, c in enumerate(self.chunks):
			IJ.showStatus("PCP Auto Count: Generating Cell Summary...")
			IJ.showProgress(i, chCount)
			angles.append(c.angle)

		if len(angles) > 0:
			angles.sort()
			count = len(angles)
			badCount = len(self.badChunks)
			totalCount = count + badCount
			processedPercent = (float(count) / float(totalCount)) * 100
			minAngle = angles[0]
			maxAngle = angles[-1]
			circularMean = getCircularMeanOfAngles(angles, options.angleAxisScaleZeroTo360)

		if options.outputCellSummary == True:

			table = ResultsTable()
			table.addRow()
			table.addValue("Processed Count", count)
			table.addValue("Bad Count", badCount)
			table.addValue("Total Count", totalCount)
			table.addValue("Processed %", processedPercent)
			table.addValue("RML", circularMean[1])
			table.addValue("Variance", circularMean[2])
			table.addValue("Mean Angle", circularMean[0])
			table.addValue("Standard Deviation", circularMean[3])

			#table.show('Angle Statistics Summary for Chunks - Calculations Circular Where Applicable - ' + self.imageTitle)
			table.show('Chunk Summary')

		if options.outputRoseDiagram == True:
			IJ.showStatus("PCP Auto Count: Generating Rose Diagram...")
			# Need to translate bar size to bar count first...
			barCount = int(360 / options.outputRoseDiagramBarSize)
			RoseDiagram.generate(angles, options.angleAxisMode, circularMean, barCount, -1, options.outputRoseDiagramAxisSize, options.outputRoseDiagramMarkerIncrement, options.getColorRoseDiagram())

		IJ.showProgress(1, 1)

	def flush(self):
		# A function to cleanup memory when an instance of ChunkCollection will no longer be needed.
		del self.chunks
		del self.noiseChunks
		del self.removedBorderChunks
		del self.badChunks

# This part only runs if the script is run directly, which should not happen.
if __name__ == "__main__" or __name__ == "__builtin__":
	print "This module is not meant to be run directly."
