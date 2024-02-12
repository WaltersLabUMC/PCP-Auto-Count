# An options dialog window for the standalone Rose Diagram.
from ij.gui import GenericDialog
from javax.swing import JDialog, JPanel, JLabel, JComboBox, JButton, JSpinner, SpinnerNumberModel, JColorChooser, JTextArea, JScrollPane, JCheckBox, ScrollPaneConstants, SwingConstants
from javax.swing.border import TitledBorder
from java.awt import GridBagLayout, GridBagConstraints, Insets, Dimension, Color
from java.awt.event import ActionListener
import copy
from java.lang.System import getProperty
from pcp_auto_count.optionsdialog import ControlPositioningOptions
from pcp_auto_count.settings import ProcessingOptions, DefaultDrawingColors, readAnglesFromCacheFile, angleTextToFloats, writeAnglesToCacheFile

class ControlTarget():
    SELF = 0,
    AXIS_ORIENTATION = 1,
    AXIS_ORIENTATION_PREVIEW = 2,
    OTHER_OPTIONS = 3

class RoseDiagramOptionsDialog(JDialog):

    def __init__(self, startingOptions=None):

        # Get the main ImageJ window
        gd = GenericDialog("Rose Diagram Options")
        fijiWindow = gd.getOwner()
        gd.dispose()

        # Initialize the dialog
        JDialog.__init__(self, fijiWindow, "Rose Diagram Options", True)
        self.setDefaultCloseOperation(JDialog.HIDE_ON_CLOSE)
        self.contentLayout = GridBagLayout()
        self.setLayout(self.contentLayout)
        self.setResizable(False)

        # Boolean describing whether the user cancelled (Closed) or continued (pressed OK)
        self.userCanceled = True

        # Set starting options
        self.startingOptions = startingOptions
        if startingOptions is None:
            self.startingOptions = ProcessingOptions

        # Initialize result items
        self.selectedOptions = copy.deepcopy(self.startingOptions)

        # The following is needed to display images
        self.htmlPathToImages = getProperty('fiji.dir').replace('\\', '/') + '/lib/pcp_auto_count'

        # We'll need this for the ability to revert to the default Rose Diagram bar color
        self.defaultColors = DefaultDrawingColors()

        # Add options panels to the dialog
        self.initializeMainOptionsPanel()
        self.initializeAxisOrientationPanel()
        self.initializeDialogButtons()

        # Fix sizes of components and location of dialog
        self.fixSize()
        self.setLocationRelativeTo(None)

    def initializeDialogButtons(self):

        self.OKButton = JButton("OK", actionPerformed = self.eventOkClicked)
        self.CancelButton = JButton("Cancel", actionPerformed = self.eventCancelClicked)

        bPanel = JPanel(GridBagLayout())
        opts = ControlPositioningOptions()
        opts.paddingLeft = 10
        self.addControl(self.CancelButton, bPanel, opts)
        opts.startX += 1
        self.addControl(self.OKButton, bPanel, opts)

        

        opts = ControlPositioningOptions()
        opts.setPaddingAll(10)
        opts.paddingTop = 0
        opts.width = 2
        opts.startY = 2
        opts.anchor = GridBagConstraints.EAST
        self.addControl(bPanel, self, opts)

    def initializeMainOptionsPanel(self):
        # Angle entry subpanel
        self.anglesPanel = JPanel(GridBagLayout())
        aBorder = TitledBorder("Angles")
        self.anglesPanel.setBorder(aBorder)

        opts = ControlPositioningOptions()
        opts.setPaddingAll(10)
        opts.paddingBottom = 0
        opts.setWeightAll(0)
        opts.anchor = GridBagConstraints.LINE_START

        self.enterAnglesLabel = JLabel("Enter angles one per line:")
        self.addControl(self.enterAnglesLabel, self.anglesPanel, opts)

        opts.startY += 1
        opts.paddingBottom = 10

        startingAngles = ''
        try:
            startingAngles = readAnglesFromCacheFile()
        except:
            print "Rose Diagram Warning: could not open angle cache file to populate previously used angles."

        self.enterAnglesTextArea = JTextArea(startingAngles, 12, 30)
        jsp = JScrollPane(self.enterAnglesTextArea, ScrollPaneConstants.VERTICAL_SCROLLBAR_AS_NEEDED, ScrollPaneConstants.HORIZONTAL_SCROLLBAR_NEVER)
        self.addControl(jsp, self.anglesPanel, opts)

        # Options subpanel
        self.optionsPanel = JPanel(GridBagLayout())
        opBorder = TitledBorder("Rose Diagram Options")
        self.optionsPanel.setBorder(opBorder)

        opts = ControlPositioningOptions()
        opts.setPaddingAll(10)
        opts.paddingBottom = 0
        opts.setWeightAll(0)
        opts.anchor = GridBagConstraints.LINE_START

        self.roseDiagramBarSizeLabel = JLabel("Bar size:")
        self.addControl(self.roseDiagramBarSizeLabel, self.optionsPanel, opts)
        opts.startX = 1
        opts.width = 2

        self.roseDiagramBarSizeCombobox = JComboBox(["20 degrees", "15 degrees", "10 degrees", "5 degrees"])
        if self.startingOptions.outputRoseDiagramBarSize == 20:
            self.roseDiagramBarSizeCombobox.setSelectedIndex(0)
        elif self.startingOptions.outputRoseDiagramBarSize == 15:
            self.roseDiagramBarSizeCombobox.setSelectedIndex(1)
        elif self.startingOptions.outputRoseDiagramBarSize == 10:
            self.roseDiagramBarSizeCombobox.setSelectedIndex(2)
        elif self.startingOptions.outputRoseDiagramBarSize == 5:
            self.roseDiagramBarSizeCombobox.setSelectedIndex(3)
        self.addControl(self.roseDiagramBarSizeCombobox, self.optionsPanel, opts)
        opts.startX = 0
        opts.startY += 1
        opts.width = 1

        self.roseDiagramAngleMarkersLabel = JLabel("Angle markers every")
        self.addControl(self.roseDiagramAngleMarkersLabel, self.optionsPanel, opts)
        opts.startX = 1
        opts.width = 2

        self.roseDiagramAngleMarkersCombobox = JComboBox(["90 degrees", "45 degrees", "30 degrees"])
        if self.startingOptions.outputRoseDiagramMarkerIncrement == 90:
            self.roseDiagramAngleMarkersCombobox.setSelectedIndex(0)
        elif self.startingOptions.outputRoseDiagramMarkerIncrement == 45:
            self.roseDiagramAngleMarkersCombobox.setSelectedIndex(1)
        elif self.startingOptions.outputRoseDiagramMarkerIncrement == 30:
            self.roseDiagramAngleMarkersCombobox.setSelectedIndex(2)
        self.addControl(self.roseDiagramAngleMarkersCombobox, self.optionsPanel, opts)
        opts.startX = 0
        opts.startY += 1
        opts.width = 1

        self.roseDiagramAxisSizeLabel = JLabel("Axis Size (0 for autosize):")
        self.addControl(self.roseDiagramAxisSizeLabel, self.optionsPanel, opts)
        opts.startX = 1
        opts.width = 2

        self.roseDiagramAxisSizeSpinner = JSpinner(SpinnerNumberModel(self.startingOptions.outputRoseDiagramAxisSize, 0, 1000000, 1))
        self.addControl(self.roseDiagramAxisSizeSpinner, self.optionsPanel, opts)

        x = self.roseDiagramAxisSizeSpinner.getPreferredSize()
        self.roseDiagramAxisSizeSpinner.setMinimumSize(x)

        x1 = self.roseDiagramBarSizeCombobox.getPreferredSize()
        if x1.width < x.width:
            self.roseDiagramBarSizeCombobox.setPreferredSize(x)

        x2 = self.roseDiagramAngleMarkersCombobox.getPreferredSize()
        if x2.width < x.width:
            self.roseDiagramAngleMarkersCombobox.setPreferredSize(x)

        opts.startX = 0
        opts.startY += 1
        opts.width = 1

        self.addControl(JLabel('Rose Diagram Bars'), self.optionsPanel, opts)

        opts.startX += 1

        self.colorRoseDiagramButton = JButton(' ', actionPerformed = self.colorButtonClicked)
        self.colorRoseDiagramButton.setMinimumSize(self.colorRoseDiagramButton.getPreferredSize())
        self.colorRoseDiagramButton.setBackground(self.startingOptions.getColorRoseDiagram())
        self.addControl(self.colorRoseDiagramButton, self.optionsPanel, opts)

        opts.startX += 1
        opts.paddingLeft = 0
        opts.paddingRight = 0

        self.colorRoseDiagramDefaultButton = JButton('Set to Default', actionPerformed = self.setColorToDefault)
        self.colorRoseDiagramDefaultButton.setName('colorRoseDiagramDefaultButton')
        self.addControl(self.colorRoseDiagramDefaultButton, self.optionsPanel, opts)

        opts.startX = 0
        opts.startY += 1
        opts.width = 2
        opts.paddingLeft = 7
        opts.paddingBottom = 10

        self.summaryCheckbox = JCheckBox("Angle Summary", self.startingOptions.outputCellSummary)
        self.summaryCheckbox.setMinimumSize(self.summaryCheckbox.getPreferredSize())
        self.addControl(self.summaryCheckbox, self.optionsPanel, opts)

        opts.setWeightAll(1)
        opts.startX = 3
        opts.horizontalFill = True
        self.addControl(JLabel(' '), self.optionsPanel, opts)       
        

        # Add the angle entry panel to the main panel
        sopts = ControlPositioningOptions()
        sopts.setPaddingAll(10)
        sopts.paddingBottom = 0
        sopts.setWeightAll(0)
        sopts.anchor = GridBagConstraints.NORTHWEST
        self.addControl(self.anglesPanel, self, sopts)

        # Add the options panel to the main panel
        sopts.startY += 1
        sopts.horizontalFill = True
        self.addControl(self.optionsPanel, self, sopts)        

    def initializeAxisOrientationPanel(self):
        self.axisOrientationPanel = JPanel(GridBagLayout())
        aopBorder = TitledBorder("Axis Orientation Options")
        self.axisOrientationPanel.setBorder(aopBorder)

        self.axisOrientationPreviewPanel = JPanel()
        self.axisOrientationPreviewPanel.setLayout(None)
        aopSize = Dimension(370, 370)
        self.axisOrientationPreviewPanel.setMinimumSize(aopSize)
        self.axisOrientationPreviewPanel.setPreferredSize(aopSize)

        opts = ControlPositioningOptions()
        opts.setPaddingAll(10)
        opts.paddingBottom = 0
        opts.setWeightAll(0)
        opts.anchor = GridBagConstraints.LINE_START

        # Create and position the Zero Degrees Direction label
        self.zeroDegreesDirectionLabel = JLabel("90 degrees is due this direction:")
        self.addControl(self.zeroDegreesDirectionLabel, self.axisOrientationPanel, opts)

        opts.startX += 1

        # Create and position the Zero Degrees Direction dropdown
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
        self.addControl(self.zeroDegreesDirectionCombobox, self.axisOrientationPanel, opts)

        opts.startY += 1
        opts.startX = 0

        # Create and position the Angle Axis Direction label
        self.angleAxisDirectionLabel = JLabel("Angles increment from zero degrees in this direction:")
        self.addControl(self.angleAxisDirectionLabel, self.axisOrientationPanel, opts)

        opts.startX += 1

        # Create and position the Angle Axis Direction dropdown
        self.angleAxisCombobox = JComboBox(["Clockwise", "Counter-Clockwise"])
        if self.startingOptions.angleAxisDirectionClockwise:
            self.angleAxisCombobox.setSelectedIndex(0)
        else:
            self.angleAxisCombobox.setSelectedIndex(1)
        self.angleAxisCombobox.addActionListener(AxisDirectionClockwiseChangedListener())
        self.addControl(self.angleAxisCombobox, self.axisOrientationPanel, opts)

        opts.startY += 1
        opts.startX = 0

        # Create and position the Angle Axis Scale label
        self.angleAxisScaleLabel = JLabel("The axis uses this scale for angle measurements:")
        self.addControl(self.angleAxisScaleLabel, self.axisOrientationPanel, opts)

        opts.startX += 1

        # Create and position the Angle Axis Scale dropdown
        self.angleAxisScaleCombobox = JComboBox(["0-360 degrees", "-180 to 180 degrees"])
        if self.startingOptions.angleAxisScaleZeroTo360:
            self.angleAxisScaleCombobox.setSelectedIndex(0)
        else:
            self.angleAxisScaleCombobox.setSelectedIndex(1)
        self.angleAxisScaleCombobox.addActionListener(AxisScaleZeroTo360ChangedListener())
        self.addControl(self.angleAxisScaleCombobox, self.axisOrientationPanel, opts)

        # Place the Axis Preview Panel
        opts.startY += 1
        opts.startX = 0
        opts.width = 2
        opts.setWeightAll(1)
        opts.anchor = GridBagConstraints.CENTER
        opts.dock = True
        self.addControl(self.axisOrientationPreviewPanel, self.axisOrientationPanel, opts)

        # Create and position the label for the North Axis Angle Preview
        self.axisPreviewNorthLabel = JLabel()
        self.axisOrientationPreviewPanel.add(self.axisPreviewNorthLabel)
        self.axisPreviewNorthLabel.setBounds(172, 20, 100, 50)
        self.axisPreviewNorthLabel.setHorizontalAlignment(SwingConstants.CENTER)

        # Create and position the label for the West Axis Angle Preview
        self.axisPreviewWestLabel = JLabel()
        self.axisOrientationPreviewPanel.add(self.axisPreviewWestLabel)
        self.axisPreviewWestLabel.setBounds(20, 167, 100, 50)
        self.axisPreviewWestLabel.setHorizontalAlignment(SwingConstants.CENTER)

        # Create and position the Axis Image label
        self.axisImageLabel = JLabel('<html><body><img style="display: inline-block" src="file:///' + self.htmlPathToImages + '/axis.png"></body></html>')
        self.axisOrientationPreviewPanel.add(self.axisImageLabel)
        self.axisImageLabel.setBounds(98, 70, 247, 247)

        # Create and position the East Axis Angle Preview
        self.axisPreviewEastLabel = JLabel()
        self.axisOrientationPreviewPanel.add(self.axisPreviewEastLabel)
        self.axisPreviewEastLabel.setBounds(326, 167, 100, 50)
        self.axisPreviewEastLabel.setHorizontalAlignment(SwingConstants.CENTER)

        # Create and position the South Axis Angle Preview
        self.axisPreviewSouthLabel = JLabel()
        self.axisOrientationPreviewPanel.add(self.axisPreviewSouthLabel)
        self.axisPreviewSouthLabel.setBounds(172, 320, 100, 50)
        self.axisPreviewSouthLabel.setHorizontalAlignment(SwingConstants.CENTER)

        # Display the correct values in the Axis Angle Preview Labels
        self.updateAxisPreview(None)

        # Add the panel to the dialog
        popts = ControlPositioningOptions()
        popts.height = 2
        popts.setPaddingAll(10)
        popts.startX = 1
        self.addControl(self.axisOrientationPanel, self, popts)

    def addControl(self, control, target, options=None):
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
        target.add(control, gbc)

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

    def fixSize(self):
        for c in self.axisOrientationPanel.getComponents():
            c.setMinimumSize(c.getPreferredSize())
            c.validate()
        self.axisOrientationPanel.setMinimumSize(self.axisOrientationPanel.getPreferredSize())
        self.axisOrientationPanel.validate()
        self.pack()

    def setSelectedOptions(self):
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

        self.selectedOptions.setColorRoseDiagram(self.colorRoseDiagramButton.getBackground())

        self.selectedOptions.outputCellSummary = self.summaryCheckbox.isSelected()

        self.angles = angleTextToFloats(self.enterAnglesTextArea.getText())
        try:
            writeAnglesToCacheFile(self.angles)
        except:
            print "Rose Diagram Warning: could not write angles to cache file."

    def colorButtonClicked(self, event):
        colorButton = event.getSource()
        selectedColor = JColorChooser.showDialog(self, "Choose Color", colorButton.getBackground())
        if selectedColor is not None:
            colorButton.setBackground(selectedColor)

    def setColorToDefault(self, event):
        self.colorRoseDiagramButton.setBackground(self.defaultColors.getRoseDiagramDefaultColor())

    def eventOkClicked(self, event):
        self.userCanceled = False
        self.setSelectedOptions()
        self.setVisible(False)

    def eventCancelClicked(self, event):
        self.setVisible(False)

class AxisZeroDirectionChangedListener(ActionListener):
    def actionPerformed(self, event):
        comboBox = event.getSource()
        choice = comboBox.getSelectedIndex()
        if choice in [0, 1, 2, 3]:
            dialog = comboBox.getParent().getParent().getParent().getParent().getParent()
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
            dialog = comboBox.getParent().getParent().getParent().getParent().getParent()
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
            dialog = comboBox.getParent().getParent().getParent().getParent().getParent()
            if choice == 0:
                dialog.selectedOptions.angleAxisScaleZeroTo360 = True
            else:
                dialog.selectedOptions.angleAxisScaleZeroTo360 = False
            dialog.updateAxisPreview(event)
