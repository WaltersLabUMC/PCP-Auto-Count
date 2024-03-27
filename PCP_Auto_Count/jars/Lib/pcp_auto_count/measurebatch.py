# A version of umeasure.py that operates on all open images instead of only the active one.
from ij import IJ, ImagePlus, WindowManager
from ij.measure import ResultsTable
from pcp_auto_count.chunkcollection import ChunkCollection
from pcp_auto_count.input import showErrorDialog
from pcp_auto_count.settings import ProcessingOptions, settingsFileExists, getProcessingOptionsFromSettingsFile, writeProcessingOptionsToSettingsFile
from pcp_auto_count.optionsdialog import OptionsDialog
from pcp_auto_count.umath import getCircularMeanOfAngles
from pcp_auto_count.rosediagram import RoseDiagram

degreeSign = u"\N{DEGREE SIGN}"
angleLabel = "Angle" + degreeSign

# The main, high-level workflow of the script.
# Enclosed in a function to make user-initiated cancelling not throw an error.
def main(quickrun=False):
	
	# Before anything, we need to make sure there are one or more open images.
	imageNames = WindowManager.getImageTitles()
	if len(imageNames) == 0:
		IJ.noImage()
		return False
	
	imps = []
	for imageName in imageNames:
		imps.append(WindowManager.getImage(imageName))
		
	options = None
	optionsDialog = None
	
	IJ.showStatus("PCP Auto Count: Options")
	
	if quickrun == True:
	
		# Try to run with the settings used last time.
		
		try:
			if settingsFileExists():
				options = getProcessingOptionsFromSettingsFile()			
		except:
			print "PCP Auto Count Warning: could not load existing settings. Quick Run is continuing with defaults."
			
		if options is None:
			options = ProcessingOptions()
			
	else:
		
		# Ask the user for input on how to run the algorithm.
		
		try:
			if settingsFileExists():
				options = getProcessingOptionsFromSettingsFile()
		except:
			print "PCP Auto Count Warning: could not load existing settings. Normal Run dialog will show default options."
		
		optionsDialog = OptionsDialog(options)
		optionsDialog.setVisible(True)
		
		# If the user presses cancel, don't do anything else.
		if optionsDialog.userCanceled:
			optionsDialog.dispose()
			IJ.showStatus("PCP Auto Count: Canceled")
			return False
			
		options = optionsDialog.selectedOptions
		
		try:
			writeProcessingOptionsToSettingsFile(options)
		except:
			print "PCP Auto Count Warning: could not write selected settings to file."
		
	
	
		
	# If we get here, the user didn't cancel, so continue.
	
	# Process each image individually.
	chunkCollections = []

	# Determine font size for image and overlay labels
	fontSize = 12
	if options.outputImageOverrideFontSize == True:
                fontSize = options.outputImageFontSize
	
	# All measuring, plus image and overlay outputs, can be done completely individually.
	for imp in imps:
	
		chunks = ChunkCollection()	
		chunks.loadChunksFromImage(imp)
		if options.removeNoise == True:
			chunks.removeNoiseChunks(options.noiseMaxSize)
		if options.removeConglomerates == True:
                        chunks.removeConglomerates(options.conglomeratesMinSize)
                if options.excludeOblongCellsW == True or options.excludeOblongCellsH == True:
                        chunks.removeOblongChunks(options.oblongMultiplierW, options.oblongMultiplierH, options.excludeOblongCellsW, options.excludeOblongCellsH)
                if options.splitDoubletsW == True or options.splitDoubletsH == True:
                        chunks.splitDoubletChunks(options.splitDoubletsMultiplierW, options.splitDoubletsMultiplierH, options.splitDoubletsW, options.splitDoubletsH)
		if options.excludeBorderCells == True:
			chunks.removeBorderChunks(options.excludeBorderCellsDistance)
		if options.usePlasticWrap == True:
			chunks.plasticWrapChunks()
		chunks.findCentroids()
		chunks.findCaves(options)
		chunks.removeCavelessChunks()
		chunks.findCentroidDistances()
		chunks.calculateAngles(options)
		chunks.generateChunkLabels()
		
		if options.outputImage == True:
			nimp = chunks.chunksToNewImage(options)			
			if options.outputImageArrows == True:
				chunks.drawArrowsOnImage(nimp, options.getColorArrows())
			if options.outputImageLabels == True or options.outputImageAngles == True:
				chunks.drawAngleLabelsOnImage(nimp, options.outputImageLabels, options.outputImageAngles, options.getColorLabels(), fontSize)
			nimp.show()	
		
		if options.outputOverlay == True:
			oimp = chunks.getOverlayFromChunks(options)
			oimp.show()
			
		chunkCollections.append(chunks)
		
	# However, the results table, chunk summary, and rose diagram should all show combined data.
		
	if options.outputResultsTable == True:
		showAngleResultsTable(chunkCollections, imageNames)	
		
	if options.outputCellSummary == True or options.outputRoseDiagram == True:
		showAngleSummary(chunkCollections, options)	

	
	# Finally cleanup
	IJ.showProgress(1, 1)
	IJ.showStatus("PCP Auto Count: Cleanup")		
	
	if optionsDialog is not None:
		optionsDialog.dispose()
	if chunks is not None:
		chunks.flush()
		chunks = None
	
	# All done.
	IJ.showStatus("PCP Auto Count: Finished")
	
def showAngleResultsTable(chunkCollections, imageNames):
	IJ.showStatus("PCP Auto Count: Generating Results Table...")
	collectionCount = len(chunkCollections)
	IJ.showProgress(0, collectionCount)
	table = ResultsTable()		
	atLeastOneRow = False
	
	for i, collection in enumerate(chunkCollections):
	
		if len(collection.chunks) > 0:
			atLeastOneRow = True
			for c in collection.chunks:
				table.addRow()
				table.addValue("Image", imageNames[i])
				table.addValue("Label", c.label)
				table.addValue("Chunk Centroid X", c.centroid[0])
				table.addValue("Chunk Centroid Y", c.centroid[1])
				table.addValue('Cave Centroid X', c.caveCentroid[0])
				table.addValue('Cave Centroid Y', c.caveCentroid[1])
				table.addValue('Vector Length', c.centroidDistance)
				table.addValue(angleLabel, c.angle)					
		
		IJ.showProgress(i + 1, collectionCount)
		
	if atLeastOneRow == False:
		IJ.showProgress(1, 1)
		table.addRow()
		table.addValue("Image", "No chunks found.")
		table.addValue("Label", "")
		table.addValue("Chunk Centroid X", "")
		table.addValue("Chunk Centroid Y", "")
		table.addValue('Cave Centroid X', "")
		table.addValue('Cave Centroid Y', "")
		table.addValue('Vector Length', "")
		table.addValue(angleLabel, "")
		
	table.show('Angle Results for Chunks - Combined')
	
def showAngleSummary(chunkCollections, options):
		
	# We don't need to do any calculations if neither of the below outputs are desired.
	if options.outputCellSummary == False and options.outputRoseDiagram == False:
		return False
		
	collectionCount = len(chunkCollections)
	
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
	for i, collection in enumerate(chunkCollections):
		IJ.showStatus("PCP Auto Count: Generating Cell Summary...")
		IJ.showProgress(i, collectionCount)
		badCount += len(collection.badChunks)
		for c in collection.chunks:
			angles.append(c.angle)
		
	if len(angles) > 0:
		angles.sort()
		count = len(angles)
		totalCount = count + badCount
		processedPercent = (float(count) / float(totalCount)) * 100.0
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
		
		#table.show('Angle Statistics Summary for Chunks - Combined')
		table.show('Chunk Summary')
		
	if options.outputRoseDiagram == True:
		IJ.showStatus("PCP Auto Count: Generating Rose Diagram...")
		RoseDiagram.generate(angles, options.angleAxisMode, circularMean, 24, -1, options.outputRoseDiagramAxisSize, options.outputRoseDiagramMarkerIncrement)

# This part only runs if the script is run directly, which should not happen.
if __name__ == "__main__" or __name__ == "__builtin__":
	print "This module is not meant to be run directly."
		
