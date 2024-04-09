# Improved version of the dialog window where a user sets options for running PCP Auto Count.
from ij.gui import GenericDialog
from javax.swing import JDialog, JLabel, JButton, JPanel, JTabbedPane, JCheckBox, JSpinner, SpinnerNumberModel, JRadioButton, ButtonGroup, JComboBox, SwingConstants, BoxLayout, Box, JColorChooser
from javax.swing.border import TitledBorder
from java.awt import FlowLayout, GridBagLayout, GridBagConstraints, Insets, Color, Component, Dimension, Font
from java.awt.event import ActionListener
import copy
from java.lang.System import getProperty
from pcp_auto_count.settings import ProcessingOptions, DefaultDrawingColors

class ControlTarget():
	SELF = 0,
	DIALOG_BUTTONS = 1,
	CHUNK_EXCLUSION = 2,
	CAVE_DETECTION = 3,
	ANGLE_MEASUREMENT = 4,
	ANGLE_MEASUREMENT_PREVIEW = 5,
	OUTPUT = 6,
	IMAGE_OPTIONS = 7,
	PROCESSED_IMAGE_OPTIONS = 8,
	DISQUALIFIED_IMAGE_OPTIONS = 9,
	ROSEDIAGRAM_OPTIONS = 10,
	OVERLAY_OPTIONS = 11,
	BASIC_CHUNK_EXCLUSIONS = 12,
	DOUBLETS = 13,
	COLORS = 14,
	DRAWING = 15,
	ANNOTATION = 16
	
class ControlPositioningOptions():
	def __init__(self):
		self.startX = 0
		self.startY = 0
		self.width = 1
		self.height = 1
		self.weightX = 1
		self.weightY = 1
		self.paddingTop = 0
		self.paddingLeft = 0
		self.paddingBottom = 0
		self.paddingRight = 0
		self.anchor = GridBagConstraints.CENTER
		self.dock = False
		self.horizontalFill = False
		self.verticalFill = False
	def setPaddingAll(self, padding):
		self.paddingTop = padding
		self.paddingLeft = padding
		self.paddingRight = padding
		self.paddingBottom = padding
	def setWeightAll(self, weight):
		self.weightX = weight
		self.weightY = weight

class OptionsDialog(JDialog):

	def __init__(self, startingOptions=None):
		
		# Get the main PCP Auto Count window	
		gd = GenericDialog("PCP Auto Count Options")
		fijiWindow = gd.getOwner()
		gd.dispose()
		
		# Initialize the dialog		
		JDialog.__init__(self, fijiWindow, "PCP Auto Count Options", True)
		self.setDefaultCloseOperation(JDialog.HIDE_ON_CLOSE)
		self.contentLayout = GridBagLayout()	
		self.setLayout(self.contentLayout)
		self.setResizable(False)
		
		# Boolean describing whether the user cancelled (Closed) or continued (pressed OK)
		self.userCanceled = True
		
		# Set starting options
		self.startingOptions = startingOptions
		if startingOptions is None:
			self.startingOptions = ProcessingOptions()
			
		# Initialize result items
		self.selectedOptions = copy.deepcopy(self.startingOptions)

		# We'll need this to assist in reverting to default colors
		self.defaultColors = DefaultDrawingColors()
			
		# Create the OK and Cancel Buttons and display them
		self.initializeDialogButtons()
		
		# The following is needed to display images
		self.htmlPathToImages = getProperty('fiji.dir').replace('\\', '/') + '/lib/pcp_auto_count'
		
		# Create each of the tab panels
		self.initializeChunkExclusionsTab()
		self.initializeCaveDetectionTab()
		self.initializeAngleMeasurementTab()
		self.initializeOutputTab()
		self.initializeColorsTab()
		
		# Create the tabbed pane, put the tab panels inside, and display it
		self.initializeTabs()

		# Fix sizes of components.
		self.fixSize()
		self.setLocationRelativeTo(None)
	
	def initializeDialogButtons(self):
	
		# Configures the OK and Cancel buttons.
	
		self.dialogButtonLayout = GridBagLayout()
		self.dialogButtonPanel = JPanel(self.dialogButtonLayout)	
		
		# Create the buttons
		self.OKButton = JButton("OK", actionPerformed = self.eventOkClicked)
		self.CancelButton = JButton("Cancel", actionPerformed = self.eventCancelClicked)
		
		# Position and place Cancel button
		opts = ControlPositioningOptions()
		opts.setPaddingAll(10)
		opts.paddingRight = 5		
		self.addControl(self.CancelButton, ControlTarget.DIALOG_BUTTONS, opts)
		
		# Position and place OK Button
		opts.paddingRight = 10
		opts.paddingLeft = 5
		opts.startX = 1		
		self.addControl(self.OKButton, ControlTarget.DIALOG_BUTTONS, opts)
		
		# Position and place the panel for these buttons onto the dialog
		opts = ControlPositioningOptions()
		opts.startY = 1
		opts.setWeightAll(0)
		opts.anchor = GridBagConstraints.LAST_LINE_END
		self.addControl(self.dialogButtonPanel, ControlTarget.SELF, opts)
		
	def initializeChunkExclusionsTab(self):
	
		# Builds the panel for the Chunk Exclusions tab.
		self.chunkExclusionsLayout = GridBagLayout()
		self.chunkExclusionsTab = JPanel(self.chunkExclusionsLayout)

		# A subpanel for very basic exclusions
		self.basicChunkExclusionsPanel = JPanel(GridBagLayout())
		bceBorder = TitledBorder("Exclusions")
		self.basicChunkExclusionsPanel.setBorder(bceBorder)
		
		# Create and position the Remove Noise checkbox
		opts = ControlPositioningOptions()
		opts.setPaddingAll(10)
		opts.paddingBottom = 0
		opts.setWeightAll(0)
		opts.anchor = GridBagConstraints.FIRST_LINE_START		
		self.removeNoiseCheckbox = JCheckBox("Remove noise of this many pixels or fewer:", self.startingOptions.removeNoise, actionPerformed = self.removeNoiseCheckboxCheckedChanged)
		self.addControl(self.removeNoiseCheckbox, ControlTarget.BASIC_CHUNK_EXCLUSIONS, opts)
		
		# Create and position the Max Noise spinner
		opts.startX = 1		
		self.maxNoiseSpinner = JSpinner(SpinnerNumberModel(self.startingOptions.noiseMaxSize, 1, 1000000, 1))
		self.maxNoiseSpinner.setEnabled(self.startingOptions.removeNoise)
		self.addControl(self.maxNoiseSpinner, ControlTarget.BASIC_CHUNK_EXCLUSIONS, opts)

		# Create and position the Min Conglomerate checkbox
		opts.startX = 0
		opts.startY += 1
		self.removeConglomeratesCheckbox = JCheckBox('Remove "conglomerates" of this many pixels or more:', self.startingOptions.removeConglomerates, actionPerformed = self.removeConglomeratesCheckboxCheckedChanged)
		self.addControl(self.removeConglomeratesCheckbox, ControlTarget.BASIC_CHUNK_EXCLUSIONS, opts)

		# Create and position the Min Conglomerate spinner
		opts.startX = 1
		self.minConglomerateSpinner = JSpinner(SpinnerNumberModel(self.startingOptions.conglomeratesMinSize, 1, 1000000, 1))
		self.minConglomerateSpinner.setEnabled(self.startingOptions.removeConglomerates)
		self.addControl(self.minConglomerateSpinner, ControlTarget.BASIC_CHUNK_EXCLUSIONS, opts)
		
		# Create and position the Exclude Border Chunks checkbox
		opts.startX = 0
		opts.startY += 1
		opts.setWeightAll(1)
		opts.paddingBottom = 10
		self.excludeBorderCellsCheckbox = JCheckBox("Exclude chunks this many pixels from the image border:", self.startingOptions.excludeBorderCells, actionPerformed = self.excludeBorderCellsCheckboxCheckedChanged)
		self.addControl(self.excludeBorderCellsCheckbox, ControlTarget.BASIC_CHUNK_EXCLUSIONS, opts)

		# Create and position the Exclude Border Chunks spinner
		opts.startX = 1
		self.excludeBorderCellsDistanceSpinner = JSpinner(SpinnerNumberModel(self.startingOptions.excludeBorderCellsDistance, 0, 1000000, 1))
		self.excludeBorderCellsDistanceSpinner.setEnabled(self.startingOptions.excludeBorderCells)
		self.addControl(self.excludeBorderCellsDistanceSpinner, ControlTarget.BASIC_CHUNK_EXCLUSIONS, opts)

		

		# A subpanel for dealing with doublets...
		self.doubletsPanel = JPanel(GridBagLayout())
		dblBorder = TitledBorder("Doublets")
		self.doubletsPanel.setBorder(dblBorder)

		opts = ControlPositioningOptions()
		opts.setPaddingAll(10)
		opts.paddingBottom = 0
		opts.anchor = GridBagConstraints.FIRST_LINE_START

		
                # A label for when chunks are too wide.
                opts.width = 2
                self.doubletWideLabel = JLabel("<html><body>When chunks are <b>wider</b> than they are tall...</body></html>")
                self.addControl(self.doubletWideLabel, ControlTarget.DOUBLETS, opts)

                opts.width = 1
                opts.startY += 1
                opts.paddingLeft = 20

		# Create and position the Split Doublets W checkbox
		self.splitDoubletsWCheckbox = JCheckBox("<html><body><b>Split</b> chunks that are this many times as wide:</body></html>", self.startingOptions.splitDoubletsW, actionPerformed = self.splitDoubletsWCheckboxCheckedChanged)
		self.addControl(self.splitDoubletsWCheckbox, ControlTarget.DOUBLETS, opts)

		# Create and position the Split Doublets W Multiplier spinner
		opts.startX = 1
		opts.paddingLeft = 10
		self.splitDoubletsWMultiplierSpinner = JSpinner(SpinnerNumberModel(self.startingOptions.splitDoubletsMultiplierW, 0.1, 1000000.0, 0.1))
                self.splitDoubletsWMultiplierSpinner.setEnabled(self.startingOptions.splitDoubletsW)
                self.addControl(self.splitDoubletsWMultiplierSpinner, ControlTarget.DOUBLETS, opts)

                opts.width = 2
                opts.startX = 0
                opts.startY += 1
                opts.paddingBottom = 10
                opts.paddingLeft = 20
                opts.setWeightAll(1)

                # Create and position the Exclude Doublets W checkbox
		self.excludeDoubletsWCheckbox = JCheckBox("<html><body><b>Exclude</b> chunks that are this many times as wide:</body></html>", self.startingOptions.excludeOblongCellsW, actionPerformed = self.excludeDoubletsWCheckboxCheckedChanged)
		self.addControl(self.excludeDoubletsWCheckbox, ControlTarget.DOUBLETS, opts)

		# Create and position the Exclude Doublets W Multiplier spinner
		opts.startX = 1
		opts.paddingLeft = 10
		opts.setWeightAll(0)
		self.excludeDoubletsWMultiplierSpinner = JSpinner(SpinnerNumberModel(self.startingOptions.oblongMultiplierW, 0.1, 1000000.0, 0.1))
                self.excludeDoubletsWMultiplierSpinner.setEnabled(self.startingOptions.excludeOblongCellsW)
                self.addControl(self.excludeDoubletsWMultiplierSpinner, ControlTarget.DOUBLETS, opts)

                #########

                # A label for when chunks are too tall.
                opts.startX = 0
                opts.startY += 1
                opts.width = 2
                opts.paddingBottom = 0
                self.doubletTallLabel = JLabel("<html><body>When chunks are <b>taller</b> than they are wide...</body></html>")
                self.addControl(self.doubletTallLabel, ControlTarget.DOUBLETS, opts)

                opts.width = 1
                opts.startY += 1
                opts.paddingLeft = 20

		# Create and position the Split Doublets H checkbox
		self.splitDoubletsHCheckbox = JCheckBox("<html><body><b>Split</b> chunks that are this many times as tall:</body></html>", self.startingOptions.splitDoubletsH, actionPerformed = self.splitDoubletsHCheckboxCheckedChanged)
		self.addControl(self.splitDoubletsHCheckbox, ControlTarget.DOUBLETS, opts)

		# Create and position the Split Doublets H Multiplier spinner
		opts.startX = 1
		opts.paddingLeft = 10
		self.splitDoubletsHMultiplierSpinner = JSpinner(SpinnerNumberModel(self.startingOptions.splitDoubletsMultiplierH, 0.1, 1000000.0, 0.1))
                self.splitDoubletsHMultiplierSpinner.setEnabled(self.startingOptions.splitDoubletsH)
                self.addControl(self.splitDoubletsHMultiplierSpinner, ControlTarget.DOUBLETS, opts)

                opts.width = 2
                opts.startX = 0
                opts.startY += 1
                opts.paddingBottom = 10
                opts.paddingLeft = 20
                opts.setWeightAll(1)

                # Create and position the Exclude Doublets H checkbox
		self.excludeDoubletsHCheckbox = JCheckBox("<html><body><b>Exclude</b> chunks that are this many times as tall:</body></html>", self.startingOptions.excludeOblongCellsH, actionPerformed = self.excludeDoubletsHCheckboxCheckedChanged)
		self.addControl(self.excludeDoubletsHCheckbox, ControlTarget.DOUBLETS, opts)

		# Create and position the Exclude Doublets H Multiplier spinner
		opts.startX = 1
		opts.paddingLeft = 10
		opts.setWeightAll(0)
		self.excludeDoubletsHMultiplierSpinner = JSpinner(SpinnerNumberModel(self.startingOptions.oblongMultiplierH, 0.1, 1000000.0, 0.1))
                self.excludeDoubletsHMultiplierSpinner.setEnabled(self.startingOptions.excludeOblongCellsH)
                self.addControl(self.excludeDoubletsHMultiplierSpinner, ControlTarget.DOUBLETS, opts)

                ########

                # Add the subpanels
                opts = ControlPositioningOptions()
                opts.setWeightAll(0)
                opts.setPaddingAll(10)
		opts.anchor = GridBagConstraints.FIRST_LINE_START
		opts.horizontalFill = True
		self.addControl(self.basicChunkExclusionsPanel, ControlTarget.CHUNK_EXCLUSION, opts)
		opts.startY += 1
		opts.setWeightAll(1)
		self.addControl(self.doubletsPanel, ControlTarget.CHUNK_EXCLUSION, opts)
		
	def initializeCaveDetectionTab(self):
	
		# Builds the panel for the Cave Detection tab.
		self.caveDetectionLayout = GridBagLayout()
		self.caveDetectionTab = JPanel(self.caveDetectionLayout)
		
		# Create and position the Apply Plastic Wrap checkbox
		opts = ControlPositioningOptions()
		opts.setPaddingAll(10)
		opts.paddingBottom = 0
		opts.setWeightAll(0)
		opts.width = 2
		opts.anchor = GridBagConstraints.FIRST_LINE_START		
		self.applyPlasticWrapCheckbox = JCheckBox("Apply Plastic Wrap to chunks before cave detection", self.startingOptions.usePlasticWrap)
		self.addControl(self.applyPlasticWrapCheckbox, ControlTarget.CAVE_DETECTION, opts)
		
		# Create and position the Ignore Small Caves checkbox
		opts.startY += 1
		opts.width = 1
		self.ignoreSmallCavesCheckbox = JCheckBox("Ignore caves of this many pixels or fewer:", self.startingOptions.ignoreSmallCaves, actionPerformed = self.ignoreSmallCavesCheckboxCheckedChanged)
		self.addControl(self.ignoreSmallCavesCheckbox, ControlTarget.CAVE_DETECTION, opts)
		
		# Create and position the Small Cave Max Size spinner
		opts.startX = 1
		self.maxSmallCaveSpinner = JSpinner(SpinnerNumberModel(self.startingOptions.smallCaveMaxSize, 1, 1000000, 1))
		self.maxSmallCaveSpinner.setEnabled(self.startingOptions.ignoreSmallCaves)
		self.addControl(self.maxSmallCaveSpinner, ControlTarget.CAVE_DETECTION, opts)		

		# Create and position the Ignore Large Caves checkbox
		opts.startX = 0
		opts.startY += 1
		opts.width = 1
		self.ignoreLargeCavesCheckbox = JCheckBox("Ignore caves of this many pixels or greater:", self.startingOptions.ignoreLargeCaves, actionPerformed = self.ignoreLargeCavesCheckboxCheckedChanged)
		self.addControl(self.ignoreLargeCavesCheckbox, ControlTarget.CAVE_DETECTION, opts)
		
		# Create and position the Large Cave Min Size spinner
		opts.startX = 1
		self.minLargeCaveSpinner = JSpinner(SpinnerNumberModel(self.startingOptions.largeCaveMinSize, 1, 1000000, 1))
		self.minLargeCaveSpinner.setEnabled(self.startingOptions.ignoreLargeCaves)
		self.addControl(self.minLargeCaveSpinner, ControlTarget.CAVE_DETECTION, opts)		
		
		# Create and position the (true) Cave Detection label
		opts.startX = 0
		opts.startY += 1
		opts.width = 2
		opts.paddingLeft = 15
		self.caveDetectionLabel = JLabel("When more than one cave is detected for a chunk, the true one is:")
		self.addControl(self.caveDetectionLabel, ControlTarget.CAVE_DETECTION, opts)
		
		# Create and position the (true) Cave Detection Combobox
		opts.startY += 1
		opts.setWeightAll(1)
		self.trueCaveModeCombobox = JComboBox(['The largest', 'The northmost directionally', 'The southmost directionally', 'The westmost directionally', 'The eastmost directionally', 'The highest positionally', 'The lowest positionally', 'The leftmost positionally', 'The rightmost positionally'])
		if self.startingOptions.trueCaveMode == 'largest':
			self.trueCaveModeCombobox.setSelectedIndex(0)
		elif self.startingOptions.trueCaveMode == 'northmost':
			self.trueCaveModeCombobox.setSelectedIndex(1)
		elif self.startingOptions.trueCaveMode == 'southmost':
			self.trueCaveModeCombobox.setSelectedIndex(2)
		elif self.startingOptions.trueCaveMode == 'westmost':
			self.trueCaveModeCombobox.setSelectedIndex(3)
		elif self.startingOptions.trueCaveMode == 'eastmost':
			self.trueCaveModeCombobox.setSelectedIndex(4)
		elif self.startingOptions.trueCaveMode == 'highest':
			self.trueCaveModeCombobox.setSelectedIndex(5)
		elif self.startingOptions.trueCaveMode == 'lowest':
			self.trueCaveModeCombobox.setSelectedIndex(6)
		elif self.startingOptions.trueCaveMode == 'leftmost':
			self.trueCaveModeCombobox.setSelectedIndex(7)
		elif self.startingOptions.trueCaveMode == 'rightmost':
			self.trueCaveModeCombobox.setSelectedIndex(8)
		self.addControl(self.trueCaveModeCombobox, ControlTarget.CAVE_DETECTION, opts)	
		
		
	def initializeAngleMeasurementTab(self):
	
		# Builds the panel for the Angle Measurements tab.
		self.angleMeasurementLayout = GridBagLayout()
		self.angleMeasurementTab = JPanel(self.angleMeasurementLayout)
		
		# We also need a panel for showing a preview.
		self.angleMeasurementPreviewPanel = JPanel()
		self.angleMeasurementPreviewPanel.setLayout(None)
		
		# Create and position the Angle Measurements label
		opts = ControlPositioningOptions()
		opts.setPaddingAll(10)
		opts.paddingBottom = 0
		opts.setWeightAll(0)
		opts.anchor = GridBagConstraints.LINE_START
		
		# Create and position the Zero Degrees Direction label
		opts.setWidth = 1
		opts.startY = 1
		self.zeroDegreesDirectionLabel = JLabel("Rays of 90 degrees point in this direction:")
		self.addControl(self.zeroDegreesDirectionLabel, ControlTarget.ANGLE_MEASUREMENT, opts)
		
		# Create and position the Zero Degrees Direction dropdown
		opts.startX = 1
		self.zeroDegreesDirectionCombobox = JComboBox(["North", "South", "East", "West"])
		# Remember, the settings file shows where 0 degrees points, but the dialog asks for where 90 degrees points...
		if self.startingOptions.angleAxisZeroDirection == "north":
			if self.startingOptions.angleAxisDirectionClockwise:
				self.zeroDegreesDirectionCombobox.setSelectedIndex(2)
			else:
				self.zeroDegreesDirectionCombobox.setSelectedIndex(3)			
		elif self.startingOptions.angleAxisZeroDirection == "south":
			if self.startingOptions.angleAxisDirectionClockwise:
				self.zeroDegreesDirectionCombobox.setSelectedIndex(3)
			else:
				self.zeroDegreesDirectionCombobox.setSelectedIndex(2)	
		elif self.startingOptions.angleAxisZeroDirection == "east":
			if self.startingOptions.angleAxisDirectionClockwise:
				self.zeroDegreesDirectionCombobox.setSelectedIndex(1)
			else:
				self.zeroDegreesDirectionCombobox.setSelectedIndex(0)
		elif self.startingOptions.angleAxisZeroDirection == "west":
			if self.startingOptions.angleAxisDirectionClockwise:
				self.zeroDegreesDirectionCombobox.setSelectedIndex(0)
			else:
				self.zeroDegreesDirectionCombobox.setSelectedIndex(1)	
		self.zeroDegreesDirectionCombobox.addActionListener(AxisZeroDirectionChangedListener())
		self.addControl(self.zeroDegreesDirectionCombobox, ControlTarget.ANGLE_MEASUREMENT, opts)
		
		# Create and position the Angle Axis Direction label
		opts.startY = 2
		opts.startX = 0
		self.angleAxisDirectionLabel = JLabel("Angles increment from zero degrees in this direction:")
		self.addControl(self.angleAxisDirectionLabel, ControlTarget.ANGLE_MEASUREMENT, opts)
		
		# Create and position the Angle Axis Direction dropdown
		opts.startX = 1
		self.angleAxisCombobox = JComboBox(["Clockwise", "Counter-Clockwise"])
		if self.startingOptions.angleAxisDirectionClockwise:
			self.angleAxisCombobox.setSelectedIndex(0)
		else:
			self.angleAxisCombobox.setSelectedIndex(1)
		self.angleAxisCombobox.addActionListener(AxisDirectionClockwiseChangedListener())
		self.addControl(self.angleAxisCombobox, ControlTarget.ANGLE_MEASUREMENT, opts)
		
		# Create and position the Angle Axis Scale label
		opts.startY = 3
		opts.startX = 0
		self.angleAxisScaleLabel = JLabel("The axis uses this scale for angle measurements:")
		self.addControl(self.angleAxisScaleLabel, ControlTarget.ANGLE_MEASUREMENT, opts)
		
		# Create and position the Angle Axis Scale dropdown
		opts.startX = 1
		self.angleAxisScaleCombobox = JComboBox(["0-360 degrees", "-180 to 180 degrees"])
		if self.startingOptions.angleAxisScaleZeroTo360:
			self.angleAxisScaleCombobox.setSelectedIndex(0)
		else:
			self.angleAxisScaleCombobox.setSelectedIndex(1)
		self.angleAxisScaleCombobox.addActionListener(AxisScaleZeroTo360ChangedListener())
		self.addControl(self.angleAxisScaleCombobox, ControlTarget.ANGLE_MEASUREMENT, opts)
		
		# Position the Axis Preview Panel
		opts.startY = 4
		opts.startX = 0
		opts.width = 2
		opts.setWeightAll(1)
		opts.anchor = GridBagConstraints.CENTER
		opts.dock = True
		self.addControl(self.angleMeasurementPreviewPanel, ControlTarget.ANGLE_MEASUREMENT, opts)
		
		# Create and position the label for the North Axis Angle Preview
		self.axisPreviewNorthLabel = JLabel()
		self.angleMeasurementPreviewPanel.add(self.axisPreviewNorthLabel)
		self.axisPreviewNorthLabel.setBounds(172, 20, 100, 50)
		self.axisPreviewNorthLabel.setHorizontalAlignment(SwingConstants.CENTER)
		
		# Create and position the label for the West Axis Angle Preview
		self.axisPreviewWestLabel = JLabel()
		self.angleMeasurementPreviewPanel.add(self.axisPreviewWestLabel)
		self.axisPreviewWestLabel.setBounds(20, 167, 100, 50)
		self.axisPreviewWestLabel.setHorizontalAlignment(SwingConstants.CENTER)
		
		# Create and position the Axis Image label
		self.axisImageLabel = JLabel('<html><body><img style="display: inline-block" src="file:///' + self.htmlPathToImages + '/axis.png"></body></html>')
		self.angleMeasurementPreviewPanel.add(self.axisImageLabel)
		self.axisImageLabel.setBounds(98, 70, 247, 247)
		
		# Create and position the East Axis Angle Preview
		self.axisPreviewEastLabel = JLabel()
		self.angleMeasurementPreviewPanel.add(self.axisPreviewEastLabel)
		self.axisPreviewEastLabel.setBounds(326, 167, 100, 50)
		self.axisPreviewEastLabel.setHorizontalAlignment(SwingConstants.CENTER)
		
		# Create and position the South Axis Angle Preview
		self.axisPreviewSouthLabel = JLabel()
		self.angleMeasurementPreviewPanel.add(self.axisPreviewSouthLabel)
		self.axisPreviewSouthLabel.setBounds(172, 320, 100, 50)
		self.axisPreviewSouthLabel.setHorizontalAlignment(SwingConstants.CENTER)
		
		# Display the correct values in the Axis Angle Preview Labels
		self.updateAxisPreview(None)
		
		
	def initializeOutputTab(self):
	
		# Builds the panel for the Output tab.		
		self.outputLayout = GridBagLayout()
		self.outputTab = JPanel(self.outputLayout)
		
		# There's also a panel for Image Options...
		self.outputImageOptionsLayout = GridBagLayout()
		self.outputImageOptionsPanel = JPanel(self.outputImageOptionsLayout)
		
		# A subpanel for Image Options pertaining to successful chunks...
		self.outputImageGoodChunksOptionsLayout = GridBagLayout()
		self.outputImageGoodChunksOptionsPanel = JPanel(self.outputImageGoodChunksOptionsLayout)
		
		# And a subpanel for Image Options pertaining to disqualified chunks.
		self.outputImageDisqualifiedChunksOptionsLayout = GridBagLayout()
		self.outputImageDisqualifiedChunksOptionsPanel = JPanel(self.outputImageDisqualifiedChunksOptionsLayout)
		
		# A panel at the top; main selections are in the left of the panel, with some options on the right.
		self.outputTabTopPanel = JPanel()
		self.outputTabTopPanel.setLayout(BoxLayout(self.outputTabTopPanel, BoxLayout.X_AXIS))
		self.mainOptionsPanel = JPanel()
		self.mainOptionsPanel.setLayout(BoxLayout(self.mainOptionsPanel, BoxLayout.Y_AXIS))
		self.mainOptionsPanel.setAlignmentY(Component.TOP_ALIGNMENT)
		self.subOptionsPanel = JPanel()
		self.subOptionsPanel.setLayout(BoxLayout(self.subOptionsPanel, BoxLayout.Y_AXIS))
		self.subOptionsPanel.setAlignmentY(Component.TOP_ALIGNMENT)
				
		# Create and position the Results Table checkbox
		opts = ControlPositioningOptions()
		opts.setPaddingAll(10)
		opts.paddingBottom = 0
		opts.setWeightAll(0)
		opts.anchor = GridBagConstraints.FIRST_LINE_START
		self.outputResultsTableCheckbox = JCheckBox("Results Table", self.startingOptions.outputResultsTable)
		self.outputResultsTableCheckbox.setAlignmentX(Component.LEFT_ALIGNMENT)
		self.mainOptionsPanel.add(self.outputResultsTableCheckbox)
		self.mainOptionsPanel.add(Box.createRigidArea(Dimension(0, 5)))
		
		# Create and position the Chunk Summary checkbox
		opts.startY += 1
		self.outputChunkSummaryCheckbox = JCheckBox("Chunk Summary   ", self.startingOptions.outputCellSummary)
		self.outputChunkSummaryCheckbox.setAlignmentX(Component.LEFT_ALIGNMENT)
		self.mainOptionsPanel.add(self.outputChunkSummaryCheckbox)
		self.mainOptionsPanel.add(Box.createRigidArea(Dimension(0, 5)))
		
		# Create and position the Rose Diagram checkbox
		opts.startY += 1
		self.outputRoseDiagramCheckbox = JCheckBox("Rose Diagram", self.startingOptions.outputRoseDiagram, actionPerformed = self.outputRoseDiagramCheckboxCheckedChanged)
		self.outputRoseDiagramCheckbox.setAlignmentX(Component.LEFT_ALIGNMENT)
		self.mainOptionsPanel.add(self.outputRoseDiagramCheckbox)
		self.mainOptionsPanel.add(Box.createRigidArea(Dimension(0, 5)))
		
		# Create and position the Overlay checkbox
		opts.startY += 1
		self.outputOverlayCheckbox = JCheckBox("Overlay", self.startingOptions.outputOverlay, actionPerformed = self.outputOverlayCheckboxCheckedChanged)
		self.outputOverlayCheckbox.setAlignmentX(Component.LEFT_ALIGNMENT)
		self.mainOptionsPanel.add(self.outputOverlayCheckbox)
		self.mainOptionsPanel.add(Box.createRigidArea(Dimension(0, 5)))
		
		# Create and position the Image checkbox
		opts.startY += 1
		self.outputImageCheckbox = JCheckBox("Image", self.startingOptions.outputImage, actionPerformed = self.outputImageCheckboxCheckedChanged)
		self.outputImageCheckbox.setAlignmentX(Component.LEFT_ALIGNMENT)
		self.mainOptionsPanel.add(self.outputImageCheckbox)
		
		self.outputTabTopPanel.add(self.mainOptionsPanel)
		self.outputTabTopPanel.add(Box.createRigidArea(Dimension(35, 0)))
		self.outputTabTopPanel.add(self.subOptionsPanel)
		self.addControl(self.outputTabTopPanel, ControlTarget.OUTPUT, opts)
		
		# Position a panel to hold controls for Rose Diagram options
		rdBorder = TitledBorder("Rose Diagram Options")
		self.outputRoseDiagramOptionsPanel = JPanel(GridBagLayout())
		ropts = ControlPositioningOptions()
		ropts.anchor = GridBagConstraints.WEST
		ropts.setPaddingAll(5)
		self.outputRoseDiagramOptionsPanel.setBorder(rdBorder)
		self.subOptionsPanel.add(self.outputRoseDiagramOptionsPanel)
		
		# Add all the controls for Rose Diagram Options
		self.roseDiagramBarSizeLabel = JLabel("Bar size:")
		self.addControl(self.roseDiagramBarSizeLabel, ControlTarget.ROSEDIAGRAM_OPTIONS, ropts)
		ropts.startX = 1
		
		self.roseDiagramBarSizeCombobox = JComboBox(["20 degrees", "15 degrees", "10 degrees", "5 degrees"])
		if self.startingOptions.outputRoseDiagramBarSize == 20:
			self.roseDiagramBarSizeCombobox.setSelectedIndex(0)
		elif self.startingOptions.outputRoseDiagramBarSize == 15:
			self.roseDiagramBarSizeCombobox.setSelectedIndex(1)
		elif self.startingOptions.outputRoseDiagramBarSize == 10:
			self.roseDiagramBarSizeCombobox.setSelectedIndex(2)
		elif self.startingOptions.outputRoseDiagramBarSize == 5:
			self.roseDiagramBarSizeCombobox.setSelectedIndex(3)
		self.addControl(self.roseDiagramBarSizeCombobox, ControlTarget.ROSEDIAGRAM_OPTIONS, ropts)
		ropts.startX = 0
		ropts.startY += 1
			
		self.roseDiagramAngleMarkersLabel = JLabel("Angle markers every")
		self.addControl(self.roseDiagramAngleMarkersLabel, ControlTarget.ROSEDIAGRAM_OPTIONS, ropts)
		ropts.startX = 1
		
		self.roseDiagramAngleMarkersCombobox = JComboBox(["90 degrees", "45 degrees", "30 degrees"])
		if self.startingOptions.outputRoseDiagramMarkerIncrement == 90:
			self.roseDiagramAngleMarkersCombobox.setSelectedIndex(0)
		elif self.startingOptions.outputRoseDiagramMarkerIncrement == 45:
			self.roseDiagramAngleMarkersCombobox.setSelectedIndex(1)
		elif self.startingOptions.outputRoseDiagramMarkerIncrement == 30:
			self.roseDiagramAngleMarkersCombobox.setSelectedIndex(2)	
                self.addControl(self.roseDiagramAngleMarkersCombobox, ControlTarget.ROSEDIAGRAM_OPTIONS, ropts)
		ropts.startX = 0
		ropts.startY += 1
		
		self.roseDiagramAxisSizeLabel = JLabel("Axis Size (0 for autosize):")
		self.addControl(self.roseDiagramAxisSizeLabel, ControlTarget.ROSEDIAGRAM_OPTIONS, ropts)
		ropts.startX = 1
		
		self.roseDiagramAxisSizeSpinner = JSpinner(SpinnerNumberModel(self.startingOptions.outputRoseDiagramAxisSize, 0, 1000000, 1))
		self.addControl(self.roseDiagramAxisSizeSpinner, ControlTarget.ROSEDIAGRAM_OPTIONS, ropts)

                x = self.roseDiagramAxisSizeSpinner.getPreferredSize()
		self.roseDiagramAxisSizeSpinner.setMinimumSize(x)
		
		x1 = self.roseDiagramBarSizeCombobox.getPreferredSize()
                if x1.width < x.width:
                        self.roseDiagramBarSizeCombobox.setPreferredSize(x)

		x2 = self.roseDiagramAngleMarkersCombobox.getPreferredSize()
                if x2.width < x.width:
                        self.roseDiagramAngleMarkersCombobox.setPreferredSize(x)
		
		self.outputRoseDiagramCheckboxCheckedChanged(None)
		
		# Position a panel to hold controls for Overlay options
		olBorder = TitledBorder("Overlay Options")
		self.outputOverlayOptionsPanel = JPanel(GridBagLayout())
		self.outputOverlayOptionsPanel.setBorder(olBorder)
		ovopts = ControlPositioningOptions()
		ovopts.setPaddingAll(10)
		ovopts.setWeightAll(1)
		ovopts.anchor = GridBagConstraints.FIRST_LINE_START
		
		# Add all the controls for Overlay options
		self.overlayArrowsCheckbox = JCheckBox("Arrows", self.startingOptions.outputOverlayArrows)
		self.addControl(self.overlayArrowsCheckbox, ControlTarget.OVERLAY_OPTIONS, ovopts)
		ovopts.startX += 1
		self.overlayLabelsCheckbox = JCheckBox("Labels", self.startingOptions.outputOverlayLabels)
		self.addControl(self.overlayLabelsCheckbox, ControlTarget.OVERLAY_OPTIONS, ovopts)
		ovopts.startX += 1
		self.overlayAnglesCheckbox = JCheckBox("Angles", self.startingOptions.outputOverlayAngles)
		self.addControl(self.overlayAnglesCheckbox, ControlTarget.OVERLAY_OPTIONS, ovopts)	
		self.outputOverlayCheckboxCheckedChanged(None)		
                opts.startY += 1
                opts.horizontalFill = True
		self.addControl(self.outputOverlayOptionsPanel, ControlTarget.OUTPUT, opts)
		
		
		# Position a panel to hold controls for Image options
		opts.startY += 1
		opts.setWeightAll(1)
		border = TitledBorder("Image Options")
		self.outputImageOptionsPanel.setBorder(border)
		self.addControl(self.outputImageOptionsPanel, ControlTarget.OUTPUT, opts)
		
		# Position a subpanel to hold checkboxes for Processed Chunks specifically
		opts = ControlPositioningOptions()
		opts.setPaddingAll(10)
		opts.dock = True
		processedBorder = TitledBorder("Draw the following for Successfully Processed Chunks:")
		self.outputImageGoodChunksOptionsPanel.setBorder(processedBorder)
		self.addControl(self.outputImageGoodChunksOptionsPanel, ControlTarget.IMAGE_OPTIONS, opts)
		
		# Position a subpanel to hold checkboxes for Disqualified Chunks
		opts.startY += 1
		disqualifiedBorder = TitledBorder("Draw the following disqualified chunks:")
		self.outputImageDisqualifiedChunksOptionsPanel.setBorder(disqualifiedBorder)
		self.addControl(self.outputImageDisqualifiedChunksOptionsPanel, ControlTarget.IMAGE_OPTIONS, opts)
		
		# Create and position the margin spinner		
		opts.startY += 1
		self.outputImageMarginLabel = JLabel("Add gray margin to the right? (Width in Pixels):")
		self.outputImageMarginLabel.setMinimumSize(self.outputImageMarginLabel.getPreferredSize())
		self.outputImageMarginSpinner = JSpinner(SpinnerNumberModel(self.startingOptions.outputImageMarginPixels, 0, 1000, 1))
		self.outputImageMarginSpinner.setMinimumSize(self.outputImageMarginSpinner.getPreferredSize())
		marginPanel = JPanel()
		marginLayout = FlowLayout(FlowLayout.LEFT)
		marginPanel.setLayout(marginLayout)
		marginPanel.add(self.outputImageMarginLabel)
		marginPanel.add(self.outputImageMarginSpinner)
		marginPanel.setMinimumSize(marginPanel.getPreferredSize())
		self.addControl(marginPanel, ControlTarget.IMAGE_OPTIONS, opts)
		
		# Create and position the Draw Arrows checbox
		opts = ControlPositioningOptions()
		opts.setPaddingAll(10)
		opts.setWeightAll(1)
		opts.anchor = GridBagConstraints.FIRST_LINE_START
		self.drawArrowsCheckbox = JCheckBox("Arrows", self.startingOptions.outputImageArrows)
		self.addControl(self.drawArrowsCheckbox, ControlTarget.PROCESSED_IMAGE_OPTIONS, opts)
		
		# Create and position the Draw Chunk Labels checkbox
		opts.startX += 1
		self.drawLabelsCheckbox = JCheckBox("Labels", self.startingOptions.outputImageLabels)
		self.addControl(self.drawLabelsCheckbox, ControlTarget.PROCESSED_IMAGE_OPTIONS, opts)
		
		# Create and position the Draw Chunk Angles checkbox
		opts.startX += 1
		self.drawAnglesCheckbox = JCheckBox("Angles", self.startingOptions.outputImageAngles)
		self.addControl(self.drawAnglesCheckbox, ControlTarget.PROCESSED_IMAGE_OPTIONS, opts)
		
		# Create and position the Draw Plastic Wrap dropdown
		opts.startY += 1
		opts.startX = 0
		opts.width = 3
		self.drawPlasticWrapCombobox = JComboBox()
		self.populatePlasticWrapComboboxItems(self.startingOptions.getColorPlasticWrap(), self.startingOptions.getColorPlasticWrapNew())
		self.addControl(self.drawPlasticWrapCombobox, ControlTarget.PROCESSED_IMAGE_OPTIONS, opts)
                		
		# Create and position the Draw Noise checkbox
		opts = ControlPositioningOptions()
		opts.setPaddingAll(10)
		opts.paddingBottom = 0
		opts.setWeightAll(1)
		opts.anchor = GridBagConstraints.FIRST_LINE_START
		self.drawRemovedNoiseCheckbox = JCheckBox('Removed Noise', self.startingOptions.outputImageNoise)
		self.drawRemovedNoiseCheckbox.setForeground(self.startingOptions.getColorNoise())
		self.drawRemovedNoiseCheckbox.setMinimumSize(self.drawRemovedNoiseCheckbox.getPreferredSize())
		self.addControl(self.drawRemovedNoiseCheckbox, ControlTarget.DISQUALIFIED_IMAGE_OPTIONS, opts)

		# Create and position the Draw Removed Conglomerates checkbox
		opts.startY += 1
		self.drawRemovedConglomeratesCheckbox = JCheckBox('Removed Conglomerates', self.startingOptions.outputImageConglomerates)
		self.drawRemovedConglomeratesCheckbox.setForeground(self.startingOptions.getColorConglomerates())
		self.drawRemovedConglomeratesCheckbox.setMinimumSize(self.drawRemovedConglomeratesCheckbox.getPreferredSize())
		self.addControl(self.drawRemovedConglomeratesCheckbox, ControlTarget.DISQUALIFIED_IMAGE_OPTIONS, opts)
		
		# Create and position the Draw Removed Border Chunks checkbox
		opts.startY += 1
		opts.setWeightAll(1)
		opts.paddingBottom = 10
		self.drawRemovedBorderChunksCheckbox = JCheckBox('Removed Border Chunks', self.startingOptions.outputImageRemovedBorderCells)
		self.drawRemovedBorderChunksCheckbox.setForeground(self.startingOptions.getColorBorderChunks())
		self.drawRemovedBorderChunksCheckbox.setMinimumSize(self.drawRemovedBorderChunksCheckbox.getPreferredSize())
		self.addControl(self.drawRemovedBorderChunksCheckbox, ControlTarget.DISQUALIFIED_IMAGE_OPTIONS, opts)

		# Create and position the Draw Removed Oblong chunks checkbox
		opts.startY = 0
		opts.startX = 1
		opts.setWeightAll(0)
		opts.paddingBottom = 0
		self.drawRemovedOblongChunksCheckbox = JCheckBox('Removed Doublet/Oblong Chunks', self.startingOptions.outputImageRemovedOblongCells)
		self.drawRemovedOblongChunksCheckbox.setForeground(self.startingOptions.getColorOblongChunks())
		self.drawRemovedOblongChunksCheckbox.setMinimumSize(self.drawRemovedOblongChunksCheckbox.getPreferredSize())
		self.addControl(self.drawRemovedOblongChunksCheckbox, ControlTarget.DISQUALIFIED_IMAGE_OPTIONS, opts)
		
		# Create and position the Draw Bad Chunks checkbox
		opts.startY += 1
		self.drawBadChunksCheckbox = JCheckBox('Removed Bad/Caveless Chunks', self.startingOptions.outputImageBadCells)
		self.drawBadChunksCheckbox.setForeground(self.startingOptions.getColorBadChunks())
		self.drawBadChunksCheckbox.setMinimumSize(self.drawBadChunksCheckbox.getPreferredSize())
		self.addControl(self.drawBadChunksCheckbox, ControlTarget.DISQUALIFIED_IMAGE_OPTIONS, opts)

	def initializeColorsTab(self):
                self.drawingLayout = GridBagLayout()
                self.drawingTab = JPanel(self.drawingLayout)
                
                self.colorsLayout = GridBagLayout()
		self.colorsTab = JPanel(self.colorsLayout)
		colorsBorder = TitledBorder("Colors")
		self.colorsTab.setBorder(colorsBorder)

		opts = ControlPositioningOptions()

		self.revertAllColorsButton = JButton('Set All Colors to Default', actionPerformed = self.setColorToDefault)
		self.revertAllColorsButton.setName('revertAllColorsButton')
                self.revertAllColorsButton.setMinimumSize(self.revertAllColorsButton.getPreferredSize())
                opts.width = 3
                opts.anchor = GridBagConstraints.EAST
                opts.setWeightAll(0)
                opts.setPaddingAll(10)
                self.addControl(self.revertAllColorsButton, ControlTarget.COLORS, opts)

                opts.paddingBottom = 0
                opts.width = 1
                opts.startY += 1
                opts.anchor = GridBagConstraints.WEST

                colorArrowsLabel = JLabel('Arrows')
                self.addControl(colorArrowsLabel, ControlTarget.COLORS, opts)

                opts.startX += 1
                
                self.colorArrowsButton = JButton(' ', actionPerformed = self.colorButtonClicked)
		self.colorArrowsButton.setMinimumSize(self.colorArrowsButton.getPreferredSize())
		self.colorArrowsButton.setBackground(self.startingOptions.getColorArrows())
		self.addControl(self.colorArrowsButton, ControlTarget.COLORS, opts)

		opts.startX += 1

		self.colorArrowsDefaultButton = JButton('Set to Default', actionPerformed = self.setColorToDefault)
		self.colorArrowsDefaultButton.setName('colorArrowsDefaultButton')
		self.colorArrowsDefaultButton.setMinimumSize(self.colorArrowsDefaultButton.getPreferredSize())
		self.addControl(self.colorArrowsDefaultButton, ControlTarget.COLORS, opts)

		opts.startX = 0
		opts.startY += 1

                colorLabelsLabel = JLabel('Labels')
                self.addControl(colorLabelsLabel, ControlTarget.COLORS, opts)

                opts.startX += 1
                
                self.colorLabelsButton = JButton(' ', actionPerformed = self.colorButtonClicked)
		self.colorLabelsButton.setMinimumSize(self.colorLabelsButton.getPreferredSize())
		self.colorLabelsButton.setBackground(self.startingOptions.getColorLabels())
		self.addControl(self.colorLabelsButton, ControlTarget.COLORS, opts)

		opts.startX += 1

		self.colorLabelsDefaultButton = JButton('Set to Default', actionPerformed = self.setColorToDefault)
		self.colorLabelsDefaultButton.setName('colorLabelsDefaultButton')
		self.colorLabelsDefaultButton.setMinimumSize(self.colorLabelsDefaultButton.getPreferredSize())
		self.addControl(self.colorLabelsDefaultButton, ControlTarget.COLORS, opts)

		opts.startX = 0
		opts.startY += 1

                colorPlasticWrapLabel = JLabel('Plastic Wrap')
                self.addControl(colorPlasticWrapLabel, ControlTarget.COLORS, opts)

                opts.startX += 1

                self.colorPlasticWrapButton = JButton(' ', actionPerformed = self.colorButtonClicked)
                self.colorPlasticWrapButton.setName('colorPlasticWrapButton')
		self.colorPlasticWrapButton.setMinimumSize(self.colorPlasticWrapButton.getPreferredSize())
		self.colorPlasticWrapButton.setBackground(self.startingOptions.getColorPlasticWrap())
		self.addControl(self.colorPlasticWrapButton, ControlTarget.COLORS, opts)

		opts.startX += 1

		self.colorPlasticWrapDefaultButton = JButton('Set to Default', actionPerformed = self.setColorToDefault)
		self.colorPlasticWrapDefaultButton.setName('colorPlasticWrapDefaultButton')
		self.colorPlasticWrapDefaultButton.setMinimumSize(self.colorPlasticWrapDefaultButton.getPreferredSize())
		self.addControl(self.colorPlasticWrapDefaultButton, ControlTarget.COLORS, opts)

		opts.startX = 0
		opts.startY += 1

                colorPlasticWrapNewLabel = JLabel('Plastic Wrap (New Pixels)')
                self.addControl(colorPlasticWrapNewLabel, ControlTarget.COLORS, opts)

                opts.startX += 1

                self.colorPlasticWrapNewButton = JButton(' ', actionPerformed = self.colorButtonClicked)
                self.colorPlasticWrapNewButton.setName('colorPlasticWrapNewButton')
		self.colorPlasticWrapNewButton.setMinimumSize(self.colorPlasticWrapNewButton.getPreferredSize())
		self.colorPlasticWrapNewButton.setBackground(self.startingOptions.getColorPlasticWrapNew())
		self.addControl(self.colorPlasticWrapNewButton, ControlTarget.COLORS, opts)

		opts.startX += 1

		self.colorPlasticWrapNewDefaultButton = JButton('Set to Default', actionPerformed = self.setColorToDefault)
		self.colorPlasticWrapNewDefaultButton.setName('colorPlasticWrapNewDefaultButton')
		self.colorPlasticWrapNewDefaultButton.setMinimumSize(self.colorPlasticWrapNewDefaultButton.getPreferredSize())
		self.addControl(self.colorPlasticWrapNewDefaultButton, ControlTarget.COLORS, opts)

		opts.startX = 0
		opts.startY += 1                
                
                colorNoiseLabel = JLabel('Removed Noise')
                self.addControl(colorNoiseLabel, ControlTarget.COLORS, opts)

                opts.startX += 1
                
                self.colorNoiseButton = JButton(' ', actionPerformed = self.colorButtonClicked)
                self.colorNoiseButton.setName('colorNoiseButton')
		self.colorNoiseButton.setMinimumSize(self.colorNoiseButton.getPreferredSize())
		self.colorNoiseButton.setBackground(self.startingOptions.getColorNoise())
		self.addControl(self.colorNoiseButton, ControlTarget.COLORS, opts)

		opts.startX += 1

		self.colorNoiseDefaultButton = JButton('Set to Default', actionPerformed = self.setColorToDefault)
		self.colorNoiseDefaultButton.setName('colorNoiseDefaultButton')
		self.colorNoiseDefaultButton.setMinimumSize(self.colorNoiseDefaultButton.getPreferredSize())
		self.addControl(self.colorNoiseDefaultButton, ControlTarget.COLORS, opts)

		opts.startX = 0
		opts.startY += 1

                colorConglomeratesLabel = JLabel('Removed Conglomerates')
                self.addControl(colorConglomeratesLabel, ControlTarget.COLORS, opts)

                opts.startX += 1

                self.colorConglomeratesButton = JButton(' ', actionPerformed = self.colorButtonClicked)
                self.colorConglomeratesButton.setName('colorConglomeratesButton')
                self.colorConglomeratesButton.setMinimumSize(self.colorConglomeratesButton.getPreferredSize())
                self.colorConglomeratesButton.setBackground(self.startingOptions.getColorConglomerates())
                self.addControl(self.colorConglomeratesButton, ControlTarget.COLORS, opts)

                opts.startX += 1

                self.colorConglomeratesDefaultButton = JButton('Set to Default', actionPerformed = self.setColorToDefault)
		self.colorConglomeratesDefaultButton.setName('colorConglomeratesDefaultButton')
		self.colorConglomeratesDefaultButton.setMinimumSize(self.colorConglomeratesDefaultButton.getPreferredSize())
		self.addControl(self.colorConglomeratesDefaultButton, ControlTarget.COLORS, opts)

		opts.startX = 0
		opts.startY += 1

                colorBorderChunksLabel = JLabel('Removed Border Chunks')
                self.addControl(colorBorderChunksLabel, ControlTarget.COLORS, opts)

                opts.startX += 1
                
                self.colorBorderChunksButton = JButton(' ', actionPerformed = self.colorButtonClicked)
                self.colorBorderChunksButton.setName('colorBorderChunksButton')
		self.colorBorderChunksButton.setMinimumSize(self.colorBorderChunksButton.getPreferredSize())
		self.colorBorderChunksButton.setBackground(self.startingOptions.getColorBorderChunks())
		self.addControl(self.colorBorderChunksButton, ControlTarget.COLORS, opts)

		opts.startX += 1

		self.colorBorderChunksDefaultButton = JButton('Set to Default', actionPerformed = self.setColorToDefault)
		self.colorBorderChunksDefaultButton.setName('colorBorderChunksDefaultButton')
		self.colorBorderChunksDefaultButton.setMinimumSize(self.colorBorderChunksDefaultButton.getPreferredSize())
		self.addControl(self.colorBorderChunksDefaultButton, ControlTarget.COLORS, opts)

		opts.startX = 0
		opts.startY += 1

                colorOblongChunksLabel = JLabel('Removed Oblong Chunks')
                self.addControl(colorOblongChunksLabel, ControlTarget.COLORS, opts)

                opts.startX += 1
                
                self.colorOblongChunksButton = JButton(' ', actionPerformed = self.colorButtonClicked)
                self.colorOblongChunksButton.setName('colorOblongChunksButton')
		self.colorOblongChunksButton.setMinimumSize(self.colorOblongChunksButton.getPreferredSize())
		self.colorOblongChunksButton.setBackground(self.startingOptions.getColorOblongChunks())
		self.addControl(self.colorOblongChunksButton, ControlTarget.COLORS, opts)

		opts.startX += 1

		self.colorOblongChunksDefaultButton = JButton('Set to Default', actionPerformed = self.setColorToDefault)
		self.colorOblongChunksDefaultButton.setName('colorOblongChunksDefaultButton')
		self.colorOblongChunksDefaultButton.setMinimumSize(self.colorOblongChunksDefaultButton.getPreferredSize())
		self.addControl(self.colorOblongChunksDefaultButton, ControlTarget.COLORS, opts)

		opts.startX = 0
		opts.startY += 1

		colorBadChunksLabel = JLabel('Removed Bad Chunks')
                self.addControl(colorBadChunksLabel, ControlTarget.COLORS, opts)

                opts.startX += 1
                
                self.colorBadChunksButton = JButton(' ', actionPerformed = self.colorButtonClicked)
                self.colorBadChunksButton.setName('colorBadChunksButton')
		self.colorBadChunksButton.setMinimumSize(self.colorBadChunksButton.getPreferredSize())
		self.colorBadChunksButton.setBackground(self.startingOptions.getColorBadChunks())
		self.addControl(self.colorBadChunksButton, ControlTarget.COLORS, opts)

		opts.startX += 1

		self.colorBadChunksDefaultButton = JButton('Set to Default', actionPerformed = self.setColorToDefault)
		self.colorBadChunksDefaultButton.setName('colorBadChunksDefaultButton')
		self.colorBadChunksDefaultButton.setMinimumSize(self.colorBadChunksDefaultButton.getPreferredSize())
		self.addControl(self.colorBadChunksDefaultButton, ControlTarget.COLORS, opts)

		opts.startX = 0
		opts.startY += 1

		colorRoseDiagramLabel = JLabel('Rose Diagram Bars')
                self.addControl(colorRoseDiagramLabel, ControlTarget.COLORS, opts)

                opts.startX += 1
                
                self.colorRoseDiagramButton = JButton(' ', actionPerformed = self.colorButtonClicked)
		self.colorRoseDiagramButton.setMinimumSize(self.colorRoseDiagramButton.getPreferredSize())
		self.colorRoseDiagramButton.setBackground(self.startingOptions.getColorRoseDiagram())
		self.addControl(self.colorRoseDiagramButton, ControlTarget.COLORS, opts)

		opts.startX += 1

		self.colorRoseDiagramDefaultButton = JButton('Set to Default', actionPerformed = self.setColorToDefault)
		self.colorRoseDiagramDefaultButton.setName('colorRoseDiagramDefaultButton')
		self.colorRoseDiagramDefaultButton.setMinimumSize(self.colorRoseDiagramDefaultButton.getPreferredSize())
		self.addControl(self.colorRoseDiagramDefaultButton, ControlTarget.COLORS, opts)

		opts.startY += 1
                opts.startX = 3
		opts.width = 1
		opts.setWeightAll(1)

		self.addControl(JLabel(' '), ControlTarget.COLORS, opts)

                self.annotationLayout = GridBagLayout()
		self.annotationPanel = JPanel(self.annotationLayout)
		atb = TitledBorder("Annotation")
		self.annotationPanel.setBorder(atb)

                opts = ControlPositioningOptions()
                opts.anchor = GridBagConstraints.WEST
                opts.setWeightAll(0)
                opts.setPaddingAll(10)
                opts.paddingBottom = 0

                self.drawingFontSizeLabel = JLabel('Label Font Size')
                self.addControl(self.drawingFontSizeLabel, ControlTarget.ANNOTATION, opts)

                opts.startX += 1

                self.drawingFontSizeSpinner = JSpinner(SpinnerNumberModel(self.startingOptions.drawingFontSize, 4, 1000, 1))
                self.drawingFontSizeSpinner.setMinimumSize(self.drawingFontSizeSpinner.getPreferredSize())
                self.addControl(self.drawingFontSizeSpinner, ControlTarget.ANNOTATION, opts)

                opts.startX += 1
                
                self.drawingFontSizeDefaultButton = JButton('Set to Default', actionPerformed = self.drawingFontSizeDefaultButtonClicked)
                self.drawingFontSizeDefaultButton.setMinimumSize(self.drawingFontSizeDefaultButton.getPreferredSize())
                self.addControl(self.drawingFontSizeDefaultButton, ControlTarget.ANNOTATION, opts)

                opts.startX = 0
                opts.startY += 1

                self.drawingArrowheadSizeLabel = JLabel('Arrowhead Size')
                self.addControl(self.drawingArrowheadSizeLabel, ControlTarget.ANNOTATION, opts)

                opts.startX += 1

                self.drawingArrowheadSizeSpinner = JSpinner(SpinnerNumberModel(self.startingOptions.drawingArrowheadSize, 1, 1000, 1))
                self.drawingArrowheadSizeSpinner.setMinimumSize(self.drawingArrowheadSizeSpinner.getPreferredSize())
                self.addControl(self.drawingArrowheadSizeSpinner, ControlTarget.ANNOTATION, opts)

                opts.startX += 1

                self.drawingArrowheadSizeDefaultButton = JButton('Set to Default', actionPerformed = self.drawingArrowheadSizeDefaultButtonClicked)
                self.drawingArrowheadSizeDefaultButton.setMinimumSize(self.drawingArrowheadSizeDefaultButton.getPreferredSize())
                self.addControl(self.drawingArrowheadSizeDefaultButton, ControlTarget.ANNOTATION, opts)

                opts.startX = 0
                opts.startY += 1
                opts.paddingBottom = 10

                self.drawingArrowlineSizeLabel = JLabel('Arrow Line Width')
                self.addControl(self.drawingArrowlineSizeLabel, ControlTarget.ANNOTATION, opts)

                opts.startX += 1

                self.drawingArrowlineSizeSpinner = JSpinner(SpinnerNumberModel(self.startingOptions.drawingArrowlineSize, 1, 1000, 1))
                self.drawingArrowlineSizeSpinner.setMinimumSize(self.drawingArrowlineSizeSpinner.getPreferredSize())
                self.addControl(self.drawingArrowlineSizeSpinner, ControlTarget.ANNOTATION, opts)

                opts.startX += 1

                self.drawingArrowlineSizeDefaultButton = JButton('Set to Default', actionPerformed = self.drawingArrowlineSizeDefaultButtonClicked)
                self.drawingArrowlineSizeDefaultButton.setMinimumSize(self.drawingArrowlineSizeDefaultButton.getPreferredSize())
                self.addControl(self.drawingArrowlineSizeDefaultButton, ControlTarget.ANNOTATION, opts)

                self.drawingFontSizeLabel.setMinimumSize(self.drawingArrowlineSizeLabel.getPreferredSize())
                self.drawingArrowheadSizeLabel.setMinimumSize(self.drawingArrowlineSizeLabel.getPreferredSize())                

		opts = ControlPositioningOptions()
		opts.anchor = GridBagConstraints.EAST
                opts.setWeightAll(0)
                opts.setPaddingAll(0)
                opts.paddingTop = 10
                opts.paddingLeft = 10                

		self.addControl(self.colorsTab, ControlTarget.DRAWING, opts)                

		opts.startX += 1
                self.addControl(JLabel(' '), ControlTarget.DRAWING, opts)

                opts.startX = 0
                opts.startY += 1
                self.addControl(self.annotationPanel, ControlTarget.DRAWING, opts)

                opts.startX += 1
                self.addControl(JLabel(' '), ControlTarget.DRAWING, opts)

                opts.startX = 0
                opts.startY += 1
                opts.width = 2
                opts.setWeightAll(1)
                self.addControl(JLabel(' '), ControlTarget.DRAWING, opts)
		
	def initializeTabs(self):
	
		# Displays the tab panes we designed.
	
		self.tabbedPane = JTabbedPane()
		
		self.tabbedPane.add("Chunk Detection", self.chunkExclusionsTab)
		self.tabbedPane.add("Cave Detection", self.caveDetectionTab)
		self.tabbedPane.add("Angle Measurements", self.angleMeasurementTab)
		self.tabbedPane.add("Output", self.outputTab)
		self.tabbedPane.add("Drawing", self.drawingTab)
		
		opts = ControlPositioningOptions()
		opts.dock = True
		
		self.outputImageCheckboxCheckedChanged(None)
		
		self.addControl(self.tabbedPane, ControlTarget.SELF, opts)
			
	def addControl(self, control, target, options=None):
	
		# A convenience method for adding controls to different containers in the dialog
		
		if options is None:
			options = ControlPositioningOptions()
	
		gbc = GridBagConstraints()
		gbc.gridx = options.startX
		gbc.gridy = options.startY
		gbc.gridwidth = options.width
		gbc.gridheight = options.height
		gbc.weightx = options.weightX
		gbc.weighty = options.weightY
		if options.paddingTop > 0 or options.paddingLeft > 0 or options.paddingRight > 0 or options.paddingBottom > 0:
			gbc.insets = Insets(options.paddingTop, options.paddingLeft, options.paddingBottom, options.paddingRight)
		gbc.anchor = options.anchor
		if options.dock == True:
			gbc.fill = GridBagConstraints.BOTH
		elif options.horizontalFill == True:
			gbc.fill = GridBagConstraints.HORIZONTAL
		elif options.verticalFill == True:
			gbc.fill = GridBagConstraints.VERTICAL
		if target == ControlTarget.SELF:
			self.contentLayout.setConstraints(control, gbc)
			self.add(control)
		elif target == ControlTarget.DIALOG_BUTTONS:
			self.dialogButtonLayout.setConstraints(control, gbc)
			self.dialogButtonPanel.add(control)
		elif target == ControlTarget.CHUNK_EXCLUSION:
			self.chunkExclusionsLayout.setConstraints(control, gbc)
			self.chunkExclusionsTab.add(control)
		elif target == ControlTarget.CAVE_DETECTION:
			self.caveDetectionLayout.setConstraints(control, gbc)
			self.caveDetectionTab.add(control)
		elif target == ControlTarget.ANGLE_MEASUREMENT:
			self.angleMeasurementLayout.setConstraints(control, gbc)
			self.angleMeasurementTab.add(control)
		elif target == ControlTarget.OUTPUT:
			self.outputLayout.setConstraints(control, gbc)
			self.outputTab.add(control)
		elif target == ControlTarget.IMAGE_OPTIONS:
			self.outputImageOptionsLayout.setConstraints(control, gbc)
			self.outputImageOptionsPanel.add(control)
		elif target == ControlTarget.PROCESSED_IMAGE_OPTIONS:
			self.outputImageGoodChunksOptionsLayout.setConstraints(control, gbc)
			self.outputImageGoodChunksOptionsPanel.add(control)
		elif target == ControlTarget.DISQUALIFIED_IMAGE_OPTIONS:
			self.outputImageDisqualifiedChunksOptionsLayout.setConstraints(control, gbc)
			self.outputImageDisqualifiedChunksOptionsPanel.add(control)
		elif target == ControlTarget.ROSEDIAGRAM_OPTIONS:
                        self.outputRoseDiagramOptionsPanel.add(control, gbc)
                elif target == ControlTarget.OVERLAY_OPTIONS:
                        self.outputOverlayOptionsPanel.add(control, gbc)
                elif target == ControlTarget.BASIC_CHUNK_EXCLUSIONS:
                        self.basicChunkExclusionsPanel.add(control, gbc)
                elif target == ControlTarget.DOUBLETS:
                        self.doubletsPanel.add(control, gbc)
                elif target == ControlTarget.COLORS:
                        self.colorsTab.add(control, gbc)
                elif target == ControlTarget.DRAWING:
                        self.drawingTab.add(control, gbc)
                elif target == ControlTarget.ANNOTATION:
                        self.annotationPanel.add(control, gbc)
			
	def setSelectedOptions(self):		
		# Looks at the values of all the controls on the options dialog and sets the options according to them.
		# Doing this all in one swoop is a little cleaner than having a bunch of different event handlers.
		
		# Chunk Exclusion Tab settings
		self.selectedOptions.removeNoise = self.removeNoiseCheckbox.isSelected()
		self.selectedOptions.noiseMaxSize = self.maxNoiseSpinner.getValue()
		self.selectedOptions.removeConglomerates = self.removeConglomeratesCheckbox.isSelected()
		self.selectedOptions.conglomeratesMinSize = self.minConglomerateSpinner.getValue()
		self.selectedOptions.excludeBorderCells = self.excludeBorderCellsCheckbox.isSelected()
		self.selectedOptions.excludeBorderCellsDistance = self.excludeBorderCellsDistanceSpinner.getValue()

		self.selectedOptions.splitDoubletsW = self.splitDoubletsWCheckbox.isSelected()
		if self.selectedOptions.splitDoubletsW == True:
                        self.selectedOptions.splitDoubletsMultiplierW = self.splitDoubletsWMultiplierSpinner.getValue()

                self.selectedOptions.splitDoubletsH = self.splitDoubletsHCheckbox.isSelected()
		if self.selectedOptions.splitDoubletsH == True:
                        self.selectedOptions.splitDoubletsMultiplierH = self.splitDoubletsHMultiplierSpinner.getValue()

                self.selectedOptions.excludeOblongCellsW = self.excludeDoubletsWCheckbox.isSelected()
                if self.selectedOptions.excludeOblongCellsW == True:
                        self.selectedOptions.oblongMultiplierW = self.excludeDoubletsWMultiplierSpinner.getValue()

                self.selectedOptions.excludeOblongCellsH = self.excludeDoubletsHCheckbox.isSelected()
                if self.selectedOptions.excludeOblongCellsH == True:
                        self.selectedOptions.oblongMultiplierH = self.excludeDoubletsHMultiplierSpinner.getValue()
		
		# Cave Detection Tab settings
		self.selectedOptions.usePlasticWrap = self.applyPlasticWrapCheckbox.isSelected()
		self.selectedOptions.ignoreSmallCaves = self.ignoreSmallCavesCheckbox.isSelected()
		self.selectedOptions.smallCaveMaxSize = self.maxSmallCaveSpinner.getValue()
		self.selectedOptions.ignoreLargeCaves = self.ignoreLargeCavesCheckbox.isSelected()
		self.selectedOptions.largeCaveMinSize = self.minLargeCaveSpinner.getValue()
		self.selectedOptions.trueCaveMode = 'largest'
		trueCaveMode = self.trueCaveModeCombobox.getSelectedIndex()
		if trueCaveMode == 1:
			self.selectedOptions.trueCaveMode = 'northmost'
		elif trueCaveMode == 2:
			self.selectedOptions.trueCaveMode = 'southmost'
		elif trueCaveMode == 3:
			self.selectedOptions.trueCaveMode = 'westmost'
		elif trueCaveMode == 4:
			self.selectedOptions.trueCaveMode = 'eastmost'
		elif trueCaveMode == 5:
			self.selectedOptions.trueCaveMode = 'highest'
		elif trueCaveMode == 6:
			self.selectedOptions.trueCaveMode = 'lowest'
		elif trueCaveMode == 7:
			self.selectedOptions.trueCaveMode = 'leftmost'
		elif trueCaveMode == 8:
			self.selectedOptions.trueCaveMode = 'rightmost'
			
		# Angle Measurement (Axis) Tab settings
		# These are mostly actually handled in event handlers anyway...
		# This is due to the nature of comboboxes and needed to update a preview image,
		# making event handler classes required.
		
		if self.selectedOptions.angleAxisDirectionClockwise == True:
		
			if self.selectedOptions.angleAxisScaleZeroTo360 == True:
				self.selectedOptions.angleAxisMode = 'E'
				if self.selectedOptions.angleAxisZeroDirection == 'east':
					self.selectedOptions.angleAxisMode = 'F'
				elif self.selectedOptions.angleAxisZeroDirection == 'south':
					self.selectedOptions.angleAxisMode = 'G'
				elif self.selectedOptions.angleAxisZeroDirection == 'west':
					self.selectedOptions.angleAxisMode = 'H'
			else:
				self.selectedOptions.angleAxisMode = 'M'
				if self.selectedOptions.angleAxisZeroDirection == 'east':
					self.selectedOptions.angleAxisMode = 'N'
				elif self.selectedOptions.angleAxisZeroDirection == 'south':
					self.selectedOptions.angleAxisMode = 'O'
				elif self.selectedOptions.angleAxisZeroDirection == 'west':
					self.selectedOptions.angleAxisMode = 'P'
		
		else:
			
			if self.selectedOptions.angleAxisScaleZeroTo360 == True:
				self.selectedOptions.angleAxisMode = 'A'
				if self.selectedOptions.angleAxisZeroDirection == 'east':
					self.selectedOptions.angleAxisMode = 'B'
				elif self.selectedOptions.angleAxisZeroDirection == 'south':
					self.selectedOptions.angleAxisMode = 'C'
				elif self.selectedOptions.angleAxisZeroDirection == 'west':
					self.selectedOptions.angleAxisMode = 'D'
			else:
				self.selectedOptions.angleAxisMode = 'I'
				if self.selectedOptions.angleAxisZeroDirection == 'east':
					self.selectedOptions.angleAxisMode = 'J'
				elif self.selectedOptions.angleAxisZeroDirection == 'south':
					self.selectedOptions.angleAxisMode = 'K'
				elif self.selectedOptions.angleAxisZeroDirection == 'west':
					self.selectedOptions.angleAxisMode = 'L'
					
		# Output Tab settings
		self.selectedOptions.outputResultsTable = self.outputResultsTableCheckbox.isSelected()
		self.selectedOptions.outputCellSummary = self.outputChunkSummaryCheckbox.isSelected()
		self.selectedOptions.outputRoseDiagram = self.outputRoseDiagramCheckbox.isSelected()
		
		rdBarSize = self.roseDiagramBarSizeCombobox.getSelectedIndex()
		self.selectedOptions.outputRoseDiagramBarSize = 20
		if rdBarSize == 1:
			self.selectedOptions.outputRoseDiagramBarSize = 15
		elif rdBarSize == 2:
			self.selectedOptions.outputRoseDiagramBarSize = 10
		elif rdBarSize == 3:
			self.selectedOptions.outputRoseDiagramBarSize = 5
		
		rdIncrement = self.roseDiagramAngleMarkersCombobox.getSelectedIndex()
		self.selectedOptions.outputRoseDiagramMarkerIncrement = 90
		if rdIncrement == 1:
			self.selectedOptions.outputRoseDiagramMarkerIncrement = 45
		elif rdIncrement == 2:
			self.selectedOptions.outputRoseDiagramMarkerIncrement = 30	
		self.selectedOptions.outputRoseDiagramAxisSize = self.roseDiagramAxisSizeSpinner.getValue()
		
		self.selectedOptions.outputOverlayArrows = self.overlayArrowsCheckbox.isSelected()
		self.selectedOptions.outputOverlayLabels = self.overlayLabelsCheckbox.isSelected()
		self.selectedOptions.outputOverlayAngles = self.overlayAnglesCheckbox.isSelected()
		
		self.selectedOptions.outputImage = self.outputImageCheckbox.isSelected()
		self.selectedOptions.outputImageArrows = self.drawArrowsCheckbox.isSelected()
		self.selectedOptions.outputImageLabels = self.drawLabelsCheckbox.isSelected()
		self.selectedOptions.outputImageAngles = self.drawAnglesCheckbox.isSelected()
		
		self.selectedOptions.outputImagePlasticWrapBorder = False
		self.selectedOptions.outputImagePlasticWrapAddedWeight = False
		plasticWrapMode = self.drawPlasticWrapCombobox.getSelectedIndex()
		if plasticWrapMode > 0:
			self.selectedOptions.outputImagePlasticWrapBorder = True
			if plasticWrapMode > 1:
				self.selectedOptions.outputImagePlasticWrapAddedWeight = True
				
		self.selectedOptions.outputImageRemovedBorderCells = self.drawRemovedBorderChunksCheckbox.isSelected()
		self.selectedOptions.outputImageNoise = self.drawRemovedNoiseCheckbox.isSelected()
		self.selectedOptions.outputImageConglomerates = self.drawRemovedConglomeratesCheckbox.isSelected()
		self.selectedOptions.outputImageRemovedOblongCells = self.drawRemovedOblongChunksCheckbox.isSelected()
		self.selectedOptions.outputImageBadCells = self.drawBadChunksCheckbox.isSelected()
		
		self.selectedOptions.outputImageMarginPixels = self.outputImageMarginSpinner.getValue()
		
		self.selectedOptions.outputOverlay = self.outputOverlayCheckbox.isSelected()

		# Drawing/Color tab settings
		self.selectedOptions.setColorNoise(self.colorNoiseButton.getBackground())
		self.selectedOptions.setColorConglomerates(self.colorConglomeratesButton.getBackground())
		self.selectedOptions.setColorBorderChunks(self.colorBorderChunksButton.getBackground())
		self.selectedOptions.setColorOblongChunks(self.colorOblongChunksButton.getBackground())
		self.selectedOptions.setColorBadChunks(self.colorBadChunksButton.getBackground())
		self.selectedOptions.setColorArrows(self.colorArrowsButton.getBackground())
		self.selectedOptions.setColorLabels(self.colorLabelsButton.getBackground())
		self.selectedOptions.setColorRoseDiagram(self.colorRoseDiagramButton.getBackground())
		self.selectedOptions.setColorPlasticWrap(self.colorPlasticWrapButton.getBackground())
		self.selectedOptions.setColorPlasticWrapNew(self.colorPlasticWrapNewButton.getBackground())

		self.selectedOptions.drawingFontSize = self.drawingFontSizeSpinner.getValue()
		self.selectedOptions.drawingArrowheadSize = self.drawingArrowheadSizeSpinner.getValue()
		self.selectedOptions.drawingArrowlineSize = self.drawingArrowlineSizeSpinner.getValue()
		
			
	def eventOkClicked(self, event):
		self.userCanceled = False
		self.setSelectedOptions()
		self.setVisible(False)
		
	def eventCancelClicked(self, event):
		self.setVisible(False)
	
	def removeNoiseCheckboxCheckedChanged(self, event):
		checked = event.getSource().isSelected()
		self.maxNoiseSpinner.setEnabled(checked)

	def removeConglomeratesCheckboxCheckedChanged(self, event):
                checked = event.getSource().isSelected()
                self.minConglomerateSpinner.setEnabled(checked)

	def excludeBorderCellsCheckboxCheckedChanged(self, event):
		checked = event.getSource().isSelected()
		self.excludeBorderCellsDistanceSpinner.setEnabled(checked)

	def splitDoubletsWCheckboxCheckedChanged(self, event):
                checked = event.getSource().isSelected()
                self.splitDoubletsWMultiplierSpinner.setEnabled(checked)

        def excludeDoubletsWCheckboxCheckedChanged(self, event):
                checked = event.getSource().isSelected()
                self.excludeDoubletsWMultiplierSpinner.setEnabled(checked)

        def splitDoubletsHCheckboxCheckedChanged(self, event):
                checked = event.getSource().isSelected()
                self.splitDoubletsHMultiplierSpinner.setEnabled(checked)

        def excludeDoubletsHCheckboxCheckedChanged(self, event):
                checked = event.getSource().isSelected()
                self.excludeDoubletsHMultiplierSpinner.setEnabled(checked)

        def ignoreSmallCavesCheckboxCheckedChanged(self, event):
		checked = event.getSource().isSelected()
		self.maxSmallCaveSpinner.setEnabled(checked)

	def ignoreLargeCavesCheckboxCheckedChanged(self, event):
                checked = event.getSource().isSelected()
                self.minLargeCaveSpinner.setEnabled(checked)
		
	def updateAxisPreview(self, event):
	
		labelTemplate = '<html><body style="font-size: 16pt; font-weight: bold;">[VAL]&#176;</body></html>'
		
		if self.selectedOptions.angleAxisZeroDirection == "north":
			
			self.axisPreviewNorthLabel.setText(labelTemplate.replace("[VAL]", "0"))
			self.axisPreviewSouthLabel.setText(labelTemplate.replace("[VAL]", "180"))
			
			if self.selectedOptions.angleAxisDirectionClockwise:
				self.axisPreviewEastLabel.setText(labelTemplate.replace("[VAL]", "90"))
				self.axisPreviewWestLabel.setText(labelTemplate.replace("[VAL]", "-90"))
				if self.selectedOptions.angleAxisScaleZeroTo360:
					self.axisPreviewWestLabel.setText(labelTemplate.replace("[VAL]", "270"))
					
			else:
				self.axisPreviewWestLabel.setText(labelTemplate.replace("[VAL]", "90"))
				self.axisPreviewEastLabel.setText(labelTemplate.replace("[VAL]", "-90"))
				if self.selectedOptions.angleAxisScaleZeroTo360:
					self.axisPreviewEastLabel.setText(labelTemplate.replace("[VAL]", "270"))
					
		elif self.selectedOptions.angleAxisZeroDirection == "south":
				
			self.axisPreviewSouthLabel.setText(labelTemplate.replace("[VAL]", "0"))
			self.axisPreviewNorthLabel.setText(labelTemplate.replace("[VAL]", "180"))
			
			if self.selectedOptions.angleAxisDirectionClockwise:
				self.axisPreviewWestLabel.setText(labelTemplate.replace("[VAL]", "90"))
				self.axisPreviewEastLabel.setText(labelTemplate.replace("[VAL]", "-90"))
				if self.selectedOptions.angleAxisScaleZeroTo360:
					self.axisPreviewEastLabel.setText(labelTemplate.replace("[VAL]", "270"))
					
			else:
				self.axisPreviewEastLabel.setText(labelTemplate.replace("[VAL]", "90"))
				self.axisPreviewWestLabel.setText(labelTemplate.replace("[VAL]", "-90"))
				if self.selectedOptions.angleAxisScaleZeroTo360:
					self.axisPreviewWestLabel.setText(labelTemplate.replace("[VAL]", "270"))
					
		elif self.selectedOptions.angleAxisZeroDirection == "east":
		
			self.axisPreviewEastLabel.setText(labelTemplate.replace("[VAL]", "0"))
			self.axisPreviewWestLabel.setText(labelTemplate.replace("[VAL]", "180"))
			
			if self.selectedOptions.angleAxisDirectionClockwise:
				self.axisPreviewSouthLabel.setText(labelTemplate.replace("[VAL]", "90"))
				self.axisPreviewNorthLabel.setText(labelTemplate.replace("[VAL]", "-90"))
				if self.selectedOptions.angleAxisScaleZeroTo360:
					self.axisPreviewNorthLabel.setText(labelTemplate.replace("[VAL]", "270"))
					
			else:
				self.axisPreviewNorthLabel.setText(labelTemplate.replace("[VAL]", "90"))
				self.axisPreviewSouthLabel.setText(labelTemplate.replace("[VAL]", "-90"))
				if self.selectedOptions.angleAxisScaleZeroTo360:
					self.axisPreviewSouthLabel.setText(labelTemplate.replace("[VAL]", "270"))
					
		elif self.selectedOptions.angleAxisZeroDirection == "west":
		
			self.axisPreviewWestLabel.setText(labelTemplate.replace("[VAL]", "0"))
			self.axisPreviewEastLabel.setText(labelTemplate.replace("[VAL]", "180"))
			
			if self.selectedOptions.angleAxisDirectionClockwise:
				self.axisPreviewNorthLabel.setText(labelTemplate.replace("[VAL]", "90"))
				self.axisPreviewSouthLabel.setText(labelTemplate.replace("[VAL]", "-90"))
				if self.selectedOptions.angleAxisScaleZeroTo360:
					self.axisPreviewSouthLabel.setText(labelTemplate.replace("[VAL]", "270"))
					
			else:
				self.axisPreviewSouthLabel.setText(labelTemplate.replace("[VAL]", "90"))
				self.axisPreviewNorthLabel.setText(labelTemplate.replace("[VAL]", "-90"))
				if self.selectedOptions.angleAxisScaleZeroTo360:
					self.axisPreviewNorthLabel.setText(labelTemplate.replace("[VAL]", "270"))
					
	def outputRoseDiagramCheckboxCheckedChanged(self, event):
		checked = self.outputRoseDiagramCheckbox.isSelected()
		self.outputRoseDiagramOptionsPanel.setEnabled(checked)
		for subpanel in self.outputRoseDiagramOptionsPanel.getComponents():
			subpanel.setEnabled(checked)
			for control in subpanel.getComponents():
				control.setEnabled(checked)
		
	def outputOverlayCheckboxCheckedChanged(self, event):
		checked = self.outputOverlayCheckbox.isSelected()
		self.outputOverlayOptionsPanel.setEnabled(checked)
		for control in self.outputOverlayOptionsPanel.getComponents():
			control.setEnabled(checked)
	
	def outputImageCheckboxCheckedChanged(self, event):
		checked = self.outputImageCheckbox.isSelected()
		self.outputImageOptionsPanel.setEnabled(checked)
		for subpanel in self.outputImageOptionsPanel.getComponents():
			subpanel.setEnabled(checked)
			for control in subpanel.getComponents():
				control.setEnabled(checked)

        def populatePlasticWrapComboboxItems(self, pwColor, pwNewColor):
                selIndex = 0
                if self.drawPlasticWrapCombobox.getItemCount() > 0:
                        selIndex = self.drawPlasticWrapCombobox.getSelectedIndex()
                        self.drawPlasticWrapCombobox.removeAllItems()
                else:
                        if self.startingOptions.outputImagePlasticWrapBorder:
                                selIndex = 1
                                if self.startingOptions.outputImagePlasticWrapAddedWeight:
                                        selIndex = 2  
                        
                self.drawPlasticWrapCombobox.addItem('Do not highlight plastic wrap pixels')
                
                pwHtml = '#{:02x}{:02x}{:02x}'.format(pwColor.getRed(), pwColor.getGreen(), pwColor.getBlue())
                self.drawPlasticWrapCombobox.addItem('<html><body>Draw all plastic wrap pixels in <span style="background-color: ' + pwHtml + '">this color</span></body></html>')

                pwnHtml = '#{:02x}{:02x}{:02x}'.format(pwNewColor.getRed(), pwNewColor.getGreen(), pwNewColor.getBlue())
                self.drawPlasticWrapCombobox.addItem('<html><body>Draw newly-added plastic wrap pixels in <span style="background-color: ' + pwnHtml + '">this color</span>, and in <span style="background-color: ' + pwHtml + '">this color</span> otherwise</body></html>')

                self.drawPlasticWrapCombobox.setSelectedIndex(selIndex)

        def drawingFontSizeDefaultButtonClicked(self, event):
                self.drawingFontSizeSpinner.setValue(12)

        def drawingArrowheadSizeDefaultButtonClicked(self, event):
                self.drawingArrowheadSizeSpinner.setValue(5)

        def drawingArrowlineSizeDefaultButtonClicked(self, event):
                self.drawingArrowlineSizeSpinner.setValue(3)

        def colorButtonClicked(self, event):
                colorButton = event.getSource()
		selectedColor = JColorChooser.showDialog(self, "Choose Color", colorButton.getBackground())
		if selectedColor is not None:
                        buttonName = colorButton.getName()
			colorButton.setBackground(selectedColor)
			if buttonName == 'colorNoiseButton':
                                self.drawRemovedNoiseCheckbox.setForeground(selectedColor)
                        elif buttonName == 'colorConglomeratesButton':
                                self.drawRemovedConglomeratesCheckbox.setForeground(selectedColor)
                        elif buttonName == 'colorBorderChunksButton':
                                self.drawRemovedBorderChunksCheckbox.setForeground(selectedColor)
                        elif buttonName == 'colorOblongChunksButton':
                                self.drawRemovedOblongChunksCheckbox.setForeground(selectedColor)
                        elif buttonName == 'colorBadChunksButton':
                                self.drawBadChunksCheckbox.setForeground(selectedColor)
                        elif buttonName == 'colorPlasticWrapButton':
                                self.populatePlasticWrapComboboxItems(selectedColor, self.colorPlasticWrapNewButton.getBackground())
                        elif buttonName == 'colorPlasticWrapNewButton':
                                self.populatePlasticWrapComboboxItems(self.colorPlasticWrapButton.getBackground(), selectedColor)
                                

	def setColorToDefault(self, event):
                buttonName = event.getSource().getName()
                if buttonName == 'colorArrowsDefaultButton':
                        self.colorArrowsButton.setBackground(self.defaultColors.getArrowDefaultColor())
                elif buttonName == 'colorLabelsDefaultButton':
                        self.colorLabelsButton.setBackground(self.defaultColors.getLabelDefaultColor())
                elif buttonName == 'colorPlasticWrapDefaultButton':
                        plasticWrapColor = self.defaultColors.getPlasticWrapDefaultColor()
                        self.colorPlasticWrapButton.setBackground(plasticWrapColor)
                        self.populatePlasticWrapComboboxItems(plasticWrapColor, self.colorPlasticWrapNewButton.getBackground())
                elif buttonName == 'colorPlasticWrapNewDefaultButton':
                        plasticWrapNewColor = self.defaultColors.getPlasticWrapNewDefaultColor()
                        self.colorPlasticWrapNewButton.setBackground(plasticWrapNewColor)
                        self.populatePlasticWrapComboboxItems(self.colorPlasticWrapButton.getBackground(), plasticWrapNewColor)
                elif buttonName == 'colorNoiseDefaultButton':
                        noiseColor = self.defaultColors.getNoiseDefaultColor()
                        self.colorNoiseButton.setBackground(noiseColor)
                        self.drawRemovedNoiseCheckbox.setForeground(noiseColor)
                elif buttonName == 'colorConglomeratesDefaultButton':
                        conglomeratesColor = self.defaultColors.getConglomeratesDefaultColor()
                        self.colorConglomeratesButton.setBackground(conglomeratesColor)
                        self.drawRemovedConglomeratesCheckbox.setForeground(conglomeratesColor)
                elif buttonName == 'colorBorderChunksDefaultButton':
                        borderColor = self.defaultColors.getBorderChunksDefaultColor()
                        self.colorBorderChunksButton.setBackground(borderColor)
                        self.drawRemovedBorderChunksCheckbox.setForeground(borderColor)
                elif buttonName == 'colorOblongChunksDefaultButton':
                        oblongColor = self.defaultColors.getOblongChunksDefaultColor()
                        self.colorOblongChunksButton.setBackground(oblongColor)
                        self.drawRemovedOblongChunksCheckbox.setForeground(oblongColor)
                elif buttonName == 'colorBadChunksDefaultButton':
                        badColor = self.defaultColors.getBadChunksDefaultColor()
                        self.colorBadChunksButton.setBackground(badColor)
                        self.drawBadChunksCheckbox.setForeground(badColor)
                elif buttonName == 'colorRoseDiagramDefaultButton':
                        self.colorRoseDiagramButton.setBackground(self.defaultColors.getRoseDiagramDefaultColor())
                elif buttonName == 'revertAllColorsButton':
                        self.colorArrowsButton.setBackground(self.defaultColors.getArrowDefaultColor())
                        self.colorLabelsButton.setBackground(self.defaultColors.getLabelDefaultColor())
                        plasticWrapColor = self.defaultColors.getPlasticWrapDefaultColor()
                        self.colorPlasticWrapButton.setBackground(plasticWrapColor)
                        plasticWrapNewColor = self.defaultColors.getPlasticWrapNewDefaultColor()
                        self.colorPlasticWrapNewButton.setBackground(plasticWrapNewColor)
                        self.populatePlasticWrapComboboxItems(plasticWrapColor, plasticWrapNewColor)
                        noiseColor = self.defaultColors.getNoiseDefaultColor()
                        self.colorNoiseButton.setBackground(noiseColor)
                        self.drawRemovedNoiseCheckbox.setForeground(noiseColor)
                        conglomeratesColor = self.defaultColors.getConglomeratesDefaultColor()
                        self.colorConglomeratesButton.setBackground(conglomeratesColor)
                        self.drawRemovedConglomeratesCheckbox.setForeground(conglomeratesColor)
                        borderColor = self.defaultColors.getBorderChunksDefaultColor()
                        self.colorBorderChunksButton.setBackground(borderColor)
                        self.drawRemovedBorderChunksCheckbox.setForeground(borderColor)
                        oblongColor = self.defaultColors.getOblongChunksDefaultColor()
                        self.colorOblongChunksButton.setBackground(oblongColor)
                        self.drawRemovedOblongChunksCheckbox.setForeground(oblongColor)
                        badColor = self.defaultColors.getBadChunksDefaultColor()
                        self.colorBadChunksButton.setBackground(badColor)
                        self.drawBadChunksCheckbox.setForeground(badColor)
                        self.colorRoseDiagramButton.setBackground(self.defaultColors.getRoseDiagramDefaultColor())

	def fixSize(self):
                for c in (self.outputImageGoodChunksOptionsPanel, self.outputImageDisqualifiedChunksOptionsPanel, self.outputImageOptionsPanel, self.outputOverlayOptionsPanel, self.outputRoseDiagramOptionsPanel, self.subOptionsPanel, self.mainOptionsPanel, self.outputTabTopPanel, self):
                        c.setMinimumSize(c.getPreferredSize())
                        c.validate()
                self.pack()
                
		

class AxisZeroDirectionChangedListener(ActionListener):
	def actionPerformed(self, event):
		comboBox = event.getSource()
		choice = comboBox.getSelectedIndex()
		if choice in [0, 1, 2, 3]:
			dialog = comboBox.getParent().getParent().getParent().getParent().getParent().getParent()
			if choice == 0:
				# 90 Degrees is north
				if dialog.selectedOptions.angleAxisDirectionClockwise:
					dialog.selectedOptions.angleAxisZeroDirection = "west"
				else:
					dialog.selectedOptions.angleAxisZeroDirection = "east"
			elif choice == 1:
				# 90 Degrees is south
				if dialog.selectedOptions.angleAxisDirectionClockwise:
					dialog.selectedOptions.angleAxisZeroDirection = "east"
				else:
					dialog.selectedOptions.angleAxisZeroDirection = "west"
			elif choice == 2:
				# 90 Degrees is east
				if dialog.selectedOptions.angleAxisDirectionClockwise:
					dialog.selectedOptions.angleAxisZeroDirection = "north"
				else:
					dialog.selectedOptions.angleAxisZeroDirection = "south"
			else:
				# 90 Degrees is west
				if dialog.selectedOptions.angleAxisDirectionClockwise:
					dialog.selectedOptions.angleAxisZeroDirection = "south"
				else:
					dialog.selectedOptions.angleAxisZeroDirection = "north"
			dialog.updateAxisPreview(event)
			
class AxisDirectionClockwiseChangedListener(ActionListener):
	def actionPerformed(self, event):
		comboBox = event.getSource()
		choice = comboBox.getSelectedIndex()
		if choice in [0, 1]:
			dialog = comboBox.getParent().getParent().getParent().getParent().getParent().getParent()
			if choice == 0:
				dialog.selectedOptions.angleAxisDirectionClockwise = True					
			else:
				dialog.selectedOptions.angleAxisDirectionClockwise = False
			
			# Account for displayed axis direction being 90 degrees and not 0
			if dialog.selectedOptions.angleAxisZeroDirection == "north":
				dialog.selectedOptions.angleAxisZeroDirection = "south"
			elif dialog.selectedOptions.angleAxisZeroDirection == "south":
				dialog.selectedOptions.angleAxisZeroDirection = "north"
			elif dialog.selectedOptions.angleAxisZeroDirection == "east":
				dialog.selectedOptions.angleAxisZeroDirection = "west"
			else: # "west"
				dialog.selectedOptions.angleAxisZeroDirection = "east"
			
			dialog.updateAxisPreview(event)
			
class AxisScaleZeroTo360ChangedListener(ActionListener):
	def actionPerformed(self, event):
		comboBox = event.getSource()
		choice = comboBox.getSelectedIndex()
		if choice in [0, 1]:
			dialog = comboBox.getParent().getParent().getParent().getParent().getParent().getParent()
			if choice == 0:
				dialog.selectedOptions.angleAxisScaleZeroTo360 = True
			else:
				dialog.selectedOptions.angleAxisScaleZeroTo360 = False
			dialog.updateAxisPreview(event)

# This part only runs if the script is run directly, which should not happen.
if __name__ == "__main__" or __name__ == "__builtin__":
	print "This module is not meant to be run directly."
		
