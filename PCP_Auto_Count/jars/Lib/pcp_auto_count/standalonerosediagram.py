# The workflow for running the Standalone Rose Diagram.
from ij import IJ
from ij.measure import ResultsTable
from pcp_auto_count.settings import settingsFileExists, getProcessingOptionsFromSettingsFile, writeProcessingOptionsToSettingsFile
from pcp_auto_count.rosediagramoptions import RoseDiagramOptionsDialog
from pcp_auto_count.rosediagram import RoseDiagram
from pcp_auto_count.umath import getCircularMeanOfAngles


# The main, high-level workflow of the script.
def main():
	options = None
	optionsDialog = None
	
	IJ.showStatus("Rose Diagram: Options")
		
	# Ask the user for input.	
	try:
		if settingsFileExists():
			options = getProcessingOptionsFromSettingsFile()
	except:
		print "Rose Diagram Warning: could not load existing settings. Normal Run dialog will show default options."
		
	optionsDialog = RoseDiagramOptionsDialog(options)
	optionsDialog.setVisible(True)
		
	# If the user presses cancel, don't do anything else.
	if optionsDialog.userCanceled:
		optionsDialog.dispose()
		IJ.showStatus("Rose Diagram: Canceled")
		return False

	# If we get here, the user didn't cancel, so continue.

	# Store the options which were selected.
	options = optionsDialog.selectedOptions

	# Write the selected options to the settings file.
	try:
		writeProcessingOptionsToSettingsFile(options)
	except:
		print "Rose Diagram Warning: could not write selected settings to file."

	# Write the angles to a cache file for convenience.
	
	
		
	# Generate the Rose Diagram.
        circularMean = getCircularMeanOfAngles(optionsDialog.angles, options.angleAxisScaleZeroTo360)
	barCount = int(360 / options.outputRoseDiagramBarSize)
	RoseDiagram.generate(optionsDialog.angles, options.angleAxisMode, circularMean, barCount, -1, options.outputRoseDiagramAxisSize, options.outputRoseDiagramMarkerIncrement, options.getColorRoseDiagram())

	# Generate the Angle Summary table, if requested.
	if options.outputCellSummary == True:
                IJ.showStatus("Rose Diagram: Angle Summary")
                table = ResultsTable()
                table.addRow()
                table.addValue("RML", circularMean[1])
                table.addValue("Variance", circularMean[2])
                table.addValue("Mean Angle", circularMean[0])
                table.addValue("Standard Deviation", circularMean[3])
                table.show('Angle Summary')
	
	
	# Finally cleanup
	IJ.showProgress(1, 1)
	IJ.showStatus("Rose Diagram: Cleanup")	
	if optionsDialog is not None:
		optionsDialog.dispose()
	
	# All done.
	IJ.showStatus("Rose Diagram: Finished")

# This part only runs if the script is run directly, which should not happen.
if __name__ == "__main__" or __name__ == "__builtin__":
	print "This module is not meant to be run directly."
		
