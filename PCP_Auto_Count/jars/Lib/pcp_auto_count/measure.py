# A more complex algorithm that builds off of the original one, but accounts for issues like noise.
# Intended to work on mostly black-and-white images.
from ij import IJ, ImagePlus
from pcp_auto_count.chunkcollection import ChunkCollection
from pcp_auto_count.settings import ProcessingOptions, settingsFileExists, getProcessingOptionsFromSettingsFile, writeProcessingOptionsToSettingsFile
from pcp_auto_count.optionsdialog import OptionsDialog


# The main, high-level workflow of the script.
# Enclosed in a function to make user-initiated cancelling not throw an error.
def main(quickrun=False):
	
	# Before anything, we need to make sure there is an active image.
	imp = None
	try:
		imp = IJ.getImage()
	except:
		return False
		
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
	chunks.calculateAngles(options)
	chunks.generateChunkLabels()
	
	if options.outputImage == True:
		nimp = chunks.chunksToNewImage(options)			
		if options.outputImageArrows == True:
			chunks.drawArrowsOnImage(nimp, options.getColorArrows())
		if options.outputImageLabels == True or options.outputImageAngles == True:
                        fontSize = 12
                        if options.outputImageOverrideFontSize == True:
                                fontSize = options.outputImageFontSize
			chunks.drawAngleLabelsOnImage(nimp, options.outputImageLabels, options.outputImageAngles, options.getColorLabels(), fontSize)
		nimp.show()	
	
	if options.outputResultsTable == True:
		chunks.showAngleResultsTable()
	if options.outputCellSummary == True or options.outputRoseDiagram == True:
		chunks.showAngleSummary(options)	
	
	if options.outputOverlay == True:
		oimp = chunks.getOverlayFromChunks(options)
		oimp.show()
	
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

# This part only runs if the script is run directly, which should not happen.
if __name__ == "__main__" or __name__ == "__builtin__":
	print "This module is not meant to be run directly."
		
