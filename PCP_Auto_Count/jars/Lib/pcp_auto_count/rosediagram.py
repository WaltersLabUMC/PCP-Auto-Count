# Code to generate a rose diagram.
from ij import IJ
from ij.gui import Line, TextRoi, OvalRoi, ShapeRoi
from java.awt import Color, Font, BasicStroke
from java.awt.geom import Arc2D
from pcp_auto_count.umath import getEndpoint

dashedLine = BasicStroke(1.0, BasicStroke.CAP_BUTT, BasicStroke.JOIN_BEVEL, 10.0, [3.0, 4.0], 0)
legendFont = Font("Arial", Font.PLAIN, 14)
smallFont = Font("Arial", Font.PLAIN, 10)
degreeSign = u"\N{DEGREE SIGN}"
skyblueColor = Color(166, 202, 240)

''' Angle Axis Modes
A: 0 to 360 counter-clockwise, 0 at (0, 1)
B: 0 to 360 counter-clockwise, 0 at (1, 0)
C: 0 to 360 counter-clockwise, 0 at (0, -1)
D: 0 to 360 counter-clockwise, 0 at (-1, 0)
E: 0 to 360 clockwise, 0 at (0, 1)
F: 0 to 360 clockwise, 0 at (1, 0)
G: 0 to 360 clockwise, 0 at (0, -1)
H: 0 to 360 clockwise, 0 at (-1, 0)
I: -180 to 180 counter-clockwise, 0 at (0, 1)
J: -180 to 180 counter-clockwise, 0 at (1, 0)
K: -180 to 180 counter-clockwise, 0 at (0, -1)
L: -180 to 180 counter-clockwise, 0 at (-1, 0)
M: -180 to 180 clockwise, 0 at (0, 1)
N: -180 to 180 clockwise, 0 at (1, 0)
O: -180 to 180 clockwise, 0 at (0, -1)
P: -180 to 180 clockwise, 0 at (-1, 0)
'''

class RoseDiagram:

	@staticmethod
	def generate(angles=[], mode="B", angleStats=None, barCount=24, scaleMax=-1, preferredAxisSize=1, markerIncrement=90, barColor=None):	
			
		# Create a new ImageJ image to draw the rose diagram on	
		IJ.newImage("Rose Diagram", "RGB", 600, 600, 1)
		imp = IJ.getImage()
		processor = imp.getProcessor()
	
		# Draw the circles and "crosshairs" of the diagram	
		RoseDiagram.__drawDiagramGrid(processor, markerIncrement)
		
		# Draw the directional labels onto the diagram
		RoseDiagram.__drawDirectionalLabels(processor, mode, markerIncrement)
		
		# The next thing to draw is the scale labels for the rings on the diagram.
		# We need to do math before we can draw those though.
		
		# For the math, examine the provided angle values and group them based on the number of bars.
		bars = RoseDiagram.__getBarsFromAngles(angles, barCount, mode)
		
		# Also determine the bar with the most members.
		
		largestBarSize = RoseDiagram.__getLargestBar(bars)
		if preferredAxisSize > largestBarSize:
			largestBarSize = preferredAxisSize
		
		# From this, we can decide what our scale will be, and how to label the grid circles.
		measurementAngles = RoseDiagram.__getCircleLabelValues(largestBarSize, scaleMax)
				
		# We've done enough math to now actually draw the circle labels.
		RoseDiagram.__drawCircleLabels(processor, measurementAngles, markerIncrement)		
				
		# Finally we can draw the bars.
		if barColor is None:
                        barColor = skyblueColor
		RoseDiagram.__drawBars(processor, mode, bars, largestBarSize, barColor)
		
		# Show the average angle as well.
		if len(angles) > 0:
			RoseDiagram.__drawMeanAngle(processor, angleStats, mode)
		
		# Update and return the ImagePlus.
		imp.updateAndRepaintWindow()
		return imp
		
	@staticmethod
	def __drawDiagramGrid(processor, markerIncrement):
		circle = OvalRoi(250, 250, 100, 100)
		circle.setFillColor(None)
		circle.setStrokeColor(Color.BLACK)
		circle.setStroke(dashedLine)
		processor.drawRoi(circle)
		
		circle2 = OvalRoi(200, 200, 200, 200)
		circle2.setFillColor(None)
		circle2.setStrokeColor(Color.BLACK)
		circle2.setStroke(dashedLine)
		processor.drawRoi(circle2)
		
		circle3 = OvalRoi(150, 150, 300, 300)
		circle3.setFillColor(None)
		circle3.setStrokeColor(Color.BLACK)
		circle3.setStroke(dashedLine)
		processor.drawRoi(circle3)
		
		circle4 = OvalRoi(100, 100, 400, 400)
		circle4.setFillColor(None)
		circle4.setStrokeColor(Color.BLACK)
		circle4.setStroke(dashedLine)
		processor.drawRoi(circle4)
		
		circle5 = OvalRoi(50, 50, 500, 500)
		circle5.setFillColor(None)
		circle5.setStrokeColor(Color.BLACK)
		processor.drawRoi(circle5)
		
		vline = Line(300, 40, 300, 560)
		vline.setFillColor(None)
		vline.setStrokeColor(Color.BLACK)
		processor.drawRoi(vline)
		
		hline = Line(40, 300, 560, 300)
		hline.setFillColor(None)
		hline.setStrokeColor(Color.BLACK)
		processor.drawRoi(hline)
		
		incrementAngles = []	
		
		if markerIncrement == 45:
			incrementAngles = [45.0, 135.0]				
		
		elif markerIncrement == 30:
			incrementAngles = [30.0, 60.0, 120.0, 150.0]
			
		if len(incrementAngles) > 0:
			for i in incrementAngles:
				endA = getEndpoint(300, 300, i, 260.0)
				startA = getEndpoint(300, 300, i + 180.0, 260.0)
				lineA = Line(startA[0], startA[1], endA[0], endA[1])
				lineA.setFillColor(None)
				lineA.setStrokeColor(Color.DARK_GRAY)
				processor.drawRoi(lineA)
	
	@staticmethod
	def __drawDirectionalLabels(processor, mode, increment=90):
	
		# Directional labels clockwise, starting north
		directionalLabels = ["", "", "", ""]
		directionalLabels45 = ["", "", "", ""]
		directionalLabels30 = ["", "", "", ""]
		
		if mode == "A":
			directionalLabels = ["0", "270", "180", "90"]
			directionalLabels45 = ["315", "225", "135", "45"]
			directionalLabels30 = ["330", "300", "240", "210", "150", "120", "60", "30"]
		elif mode == "B":
			directionalLabels = ["90", "0", "270", "180"]
			directionalLabels45 = ["45", "315", "225", "135"]
			directionalLabels30 = ["60", "30", "330", "300", "240", "210", "150", "120"]
		elif mode == "C":
			directionalLabels = ["180", "90", "0", "270"]
			directionalLabels45 = ["135", "45", "315", "225"]
			directionalLabels30 = ["150", "120", "60", "30", "330", "300", "240", "210"]
		elif mode == "D":
			directionalLabels = ["270", "180", "90", "0"]
			directionalLabels45 = ["225", "135", "45", "315"]
			directionalLabels30 = ["240", "210", "150", "120", "60", "30", "330", "300"]
		elif mode == "E":
			directionalLabels = ["0", "90", "180", "270"]
			directionalLabels45 = ["45", "135", "225", "315"]
			directionalLabels30 = ["30", "60", "120", "150", "210", "240", "300", "330"]
		elif mode == "F":
			directionalLabels = ["270", "0", "90", "180"]
			directionalLabels45 = ["315", "45", "135", "225"]
			directionalLabels30 = ["300", "330", "30", "60", "120", "150", "210", "240"]
		elif mode == "G":
			directionalLabels = ["180", "270", "0", "90"]
			directionalLabels45 = ["225", "315", "45", "135"]
			directionalLabels30 = ["210", "240", "300", "330", "30", "60", "120", "150"]
		elif mode == "H":
			directionalLabels = ["90", "180", "270", "0"]
			directionalLabels45 = ["135", "225", "315", "45"]
			directionalLabels30 = ["120", "150", "210", "240", "300", "330", "30", "60"]
		elif mode == "I":
			directionalLabels = ["0", "-90", "180", "90"]
			directionalLabels45 = ["-45", "-135", "135", "45"]
			directionalLabels30 = ["-30", "-60", "-120", "-150", "150", "120", "60", "30"]
		elif mode == "J":
			directionalLabels = ["90", "0", "-90", "180"]
			directionalLabels45 = ["45", "-45", "-135", "135"]
			directionalLabels30 = ["60", "30", "-30", "-60", "-120", "-150", "150", "120"]
		elif mode == "K":
			directionalLabels = ["180", "90", "0", "-90"]
			directionalLabels45 = ["135", "45", "-45", "-135"]
			directionalLabels30 = ["150", "120", "60", "30", "-30", "-60", "-120", "-150"]
		elif mode == "L":
			directionalLabels = ["-90", "180", "90", "0"]
			directionalLabels45 = ["-135", "135", "45", "-45"]
			directionalLabels30 = ["-120", "-150", "150", "120", "60", "30", "-30", "-60"]
		elif mode == "M":
			directionalLabels = ["0", "90", "180", "-90"]
			directionalLabels45 = ["45", "135", "-135", "-45"]
			directionalLabels30 = ["30", "60", "120", "150", "-150", "-120", "-60", "-30"]
		elif mode == "N":
			directionalLabels = ["-90", "0", "90", "180"]
			directionalLabels45 = ["-45", "45", "135", "-135"]
			directionalLabels30 = ["-60", "-30", "30", "60", "120", "150", "-150", "-120"]
		elif mode == "O":
			directionalLabels = ["180", "-90", "0", "90"]
			directionalLabels45 = ["-135", "-45", "45", "135"]
			directionalLabels30 = ["-150", "-120", "-60", "-30", "30", "60", "120", "150"]
		elif mode == "P":
			directionalLabels = ["90", "180", "-90", "0"]
			directionalLabels45 = ["135", "-135", "-45", "45"]
			directionalLabels30 = ["120", "150", "-150", "-120", "-60", "-30", "30", "60"]
			
		# Cardinal direction labels every 90 degrees (always drawn)
			
		nRoi = TextRoi(300, 15, directionalLabels[0] + degreeSign)
		nRoi.setColor(Color.BLACK)
		nRoi.setFillColor(Color.WHITE)
		nRoi.setFont(legendFont)
		nRoi.setJustification(1)
		processor.drawRoi(nRoi)
		
		eRoi = TextRoi(575, 290, directionalLabels[1] + degreeSign)
		eRoi.setColor(Color.BLACK)
		eRoi.setFillColor(Color.WHITE)
		eRoi.setFont(legendFont)
		eRoi.setJustification(1)
		processor.drawRoi(eRoi)
		
		sRoi = TextRoi(300, 570, directionalLabels[2] + degreeSign)
		sRoi.setColor(Color.BLACK)
		sRoi.setFillColor(Color.WHITE)
		sRoi.setFont(legendFont)
		sRoi.setJustification(1)
		processor.drawRoi(sRoi)
		
		wRoi = TextRoi(20, 290, directionalLabels[3] + degreeSign)
		wRoi.setColor(Color.BLACK)
		wRoi.setFillColor(Color.WHITE)
		wRoi.setFont(legendFont)
		wRoi.setJustification(1)
		processor.drawRoi(wRoi)
		
		# Labels drawn every 45 degrees
		if increment == 45:
			for i, angle in enumerate([45.0, 315.0, 225.0, 135.0]):
				labelPosition = getEndpoint(300, 300, angle, 285.0)
				tRoi = TextRoi(labelPosition[0], labelPosition[1], directionalLabels45[i] + degreeSign)
				tRoi.setColor(Color.BLACK)
				tRoi.setFillColor(Color.WHITE)
				tRoi.setFont(legendFont)
				tRoi.setJustification(1)
				processor.drawRoi(tRoi)
		elif increment == 30:
			for i, angle in enumerate([60.0, 30.0, 330.0, 300.0, 240.0, 210.0, 150.0, 120.0]):
				labelPosition = getEndpoint(300, 300, angle, 285.0)
				tRoi = TextRoi(labelPosition[0], labelPosition[1], directionalLabels30[i] + degreeSign)
				tRoi.setColor(Color.BLACK)
				tRoi.setFillColor(Color.WHITE)
				tRoi.setFont(legendFont)
				tRoi.setJustification(1)
				processor.drawRoi(tRoi)
			
		
	@staticmethod
	def __getBarsFromAngles(angles, barCount, mode):
		barAngleSize = 360.0 / float(barCount)
		bars = [0] * barCount
		
		isZeroTo360 = False
		if mode in ["A", "B", "C", "D", "E", "F", "G", "H"]:
			isZeroTo360 = True
		
		straddleOffset = barAngleSize / 2.0
		
		for i in range(barCount):
		
			startAngle = 0.0
			
			if isZeroTo360:
				startAngle = (0.0 + (barAngleSize * float(i))) - straddleOffset
				if i == 0:
					startAngle = startAngle + 360.0
			else:		
				startAngle = (-180.0 + (barAngleSize * float(i))) - straddleOffset
				if i == 0:
					startAngle = startAngle + 360.0
				
			endAngle = startAngle + barAngleSize
			if i == 0:
				endAngle = endAngle - 360.0
			
			for a in angles:
				af = float(a)
				if isZeroTo360:
					if i == 0:
						if (af >= startAngle and af < 360.0) or (af >= 0.0 and af < endAngle):
							bars[i] = bars[i] + 1
					else:	
						if af >= startAngle and af < endAngle:
							bars[i] = bars[i] + 1
				else:
					if i == 0:
						if (af > startAngle and af <= 180.0) or (af > -180.0 and af <= endAngle):
							bars[i] = bars[i] + 1
					else:
						if af > startAngle and af <= endAngle:
							bars[i] = bars[i] + 1
					
		return bars
		
	@staticmethod
	def __getBarsFromAngles_OLD(angles, barCount, mode):
		barAngleSize = 360.0 / float(barCount)
		bars = [0] * barCount
		
		for i in range(barCount):
			startAngle = -180.0 + (barAngleSize * float(i))
			if mode in ["A", "B", "C", "D", "E", "F", "G", "H"]:
				startAngle = 0.0 + (barAngleSize * float(i))
			endAngle = startAngle + barAngleSize
			
			for a in angles:
				af = float(a)
				if mode in ["A", "B", "C", "D", "E", "F", "G", "H"]:
					if af >= startAngle and af < endAngle:
						bars[i] = bars[i] + 1
				else:
					if af > startAngle and af <= endAngle:
						bars[i] = bars[i] + 1
					
		return bars
		
	@staticmethod
	def __getLargestBar(bars):
		largestBarSize = 0
		for b in bars:
			if b > largestBarSize:
				largestBarSize = b
		return largestBarSize
		
	@staticmethod
	def __getCircleLabelValues(largestBarSize, scaleMax):
	
		outerCircleSize = float(scaleMax)
		
		if outerCircleSize < 0.0:
			if largestBarSize < 25:
				outerCircleSize = float(largestBarSize)
			else:
				outerCircleSize = largestBarSize
				while outerCircleSize % 5 <> 0:
					outerCircleSize = outerCircleSize + 1
				outerCircleSize = float(outerCircleSize)
			
		innermostCircleSize = outerCircleSize / 5.0
		
		# We'll store the labels for each circle here:
		measurementAngles = []
		
		for i in range(5):
			value = round(innermostCircleSize * float(i + 1), 2)
			if largestBarSize >= 25 or str(innermostCircleSize).endswith(".0"):
				value = int(value)
			measurementAngles.append(value)
			
		return measurementAngles
		
	@staticmethod
	def __drawCircleLabels(processor, labels, increment=90):
	
		# This array is a matrix of label positions for the lines at cardinal directions.
		mPos = [[[300, 243],[350, 293],[300, 343],[250, 293]], [[300, 193],[400, 293],[300, 393],[200, 293]], [[300, 143],[450, 293],[300, 443],[150, 293]], [[300, 93],[500, 293],[300, 493],[100, 293]], [[300, 51],[550, 293],[300, 535],[61, 293]]]
		
		for i in range(5):
	
			for m in range(4):
				x = mPos[i][m][0]
				y = mPos[i][m][1]
				# One specific label needs manually placed...
				if i == 4 and m == 1:
					tRoi = TextRoi(x, y, str(labels[i]))
					r = tRoi.getBoundingRect()
					x = x - (r.width / 2)
					tRoi = None
				RoseDiagram.__drawCircleLabel(processor, x, y, str(labels[i]))
				
		# Now, we have to deal with lines for 45 and 30 degree increments...
						
		if increment < 90:
			angles = [45.0, 315.0, 225.0, 135.0]
			if increment == 30:
				angles = [60.0, 30.0, 330.0, 300.0, 240.0, 210.0, 150.0, 120.0]
			for i, angle in enumerate(angles):
				for d in range(5):
					distance = 50.0 + (50.0 * float(d))
					if d == 4:
						distance = distance - 15.0
					labelPosition = getEndpoint(300, 300, angle, distance)
					RoseDiagram.__drawCircleLabel(processor, labelPosition[0], labelPosition[1], str(labels[d]), True)
					
	@staticmethod
	def __drawCircleLabel(processor, x, y, label, center=False):
		mRoi = TextRoi(x, y, label)
		mRoi.setColor(Color.BLACK)
		mRoi.setFillColor(Color.WHITE)
		mRoi.setFont(smallFont)
		mRoi.setJustification(1)
		if center == True:
			mRoi.setJustification(0)
			r = mRoi.getBoundingRect()
			xdiff = int(r.width / 2)
			ydiff = int(r.height / 2)
			mRoi.setLocation(x - xdiff, y - ydiff)
		processor.drawRoi(mRoi)
				
	@staticmethod
	def __drawBars(processor, mode, bars, largestBarSize, barColor):
	
		# Depending on the mode, where each bar goes around the circle will change wildly.
		# Bars are sorted from smallest angle to largest, so they're drawn from 0 or ~-180, depending on mode.
		# When supplying angles to get the arc shape, those measurements always use true polar coordinates on a 0-360 scale.
		
		# Return early if no bars
		if len(bars) == 0:
			return False
		
		# Does this mode measure 0 to 360, or -180 to 180?
		zeroTo360 = True
		if mode in ["I", "J", "K", "L", "M", "N", "O", "P"]:
			zeroTo360 = False
			
		# Does this mode increment clockwise or counter-clockwise?
		clockwise = False
		if mode in ["E", "F", "G", "H", "M", "N", "O", "P"]:
			clockwise = True
			
		# For this mode's axis, does 0 degrees point north, south, east, or west?
		zeroDirection = "N"
		if mode in ["B", "F", "J", "N"]:
			zeroDirection = "E"
		elif mode in ["C", "G", "K", "O"]:
			zeroDirection = "S"
		elif mode in ["D", "H", "L", "P"]:
			zeroDirection = "W"
			
		# How wide should the bars be (in angles)? What direction are bars drawn?
		barWidth = 360.0 / float(len(bars))
		if clockwise == True:
			barWidth = barWidth * -1.0
			
		# How does the mode's orientation determine where we start drawing bars?
		startAngle = 0.0 # This is true if zeroDirection is E
		if zeroDirection == "N":
			startAngle = 90.0
		elif zeroDirection == "W":
			startAngle = 180.0
		elif zeroDirection == "S":
			startAngle = 270.0
			
		# The starting location changes if we use the -180 to 180 axis
		if zeroTo360 == False:
			startAngle = startAngle + 180.0
			
		# Now that we straddle bars at the cardinal directions, further adjustment is needed...
		startAngle = startAngle - (barWidth / 2.0)
		
		# We should have enough information to draw the bars at this point.
		for i in range(len(bars)):
			
			barValue = bars[i]			
			if barValue > 0 and largestBarSize > 0:
				if float(barValue) <= float(largestBarSize):
					boundingSquareSize = 500.0 * (float(barValue) / float(largestBarSize))
					boundingSquareSize = int(boundingSquareSize)
					if boundingSquareSize > 500:
						boundingSquareSize = 500
					boundingSquareLocation = 50 + int(float((500 - boundingSquareSize) / 2))
					RoseDiagram.__drawBar(processor, boundingSquareLocation, boundingSquareLocation, boundingSquareSize, boundingSquareSize, startAngle, barWidth, barColor)
			startAngle = startAngle + (barWidth)		
		
	@staticmethod
	def __drawBar(processor, brectX, brectY, brectWidth, brectHeight, arcStartingAngle, arcAngleWidth, barColor):
	
		bar = Arc2D.Float(brectX, brectY, brectWidth, brectHeight, arcStartingAngle, arcAngleWidth, Arc2D.PIE)
		
		bRoi = ShapeRoi(bar)
		bRoi.setStrokeColor(Color.BLACK)
		bRoi.setFillColor(barColor)
		processor.drawRoi(bRoi)
		
		boRoi = ShapeRoi(bar)
		boRoi.setStrokeColor(Color.BLACK)
		processor.drawRoi(boRoi)
		
	@staticmethod
	def __drawMeanAngle(processor, angleStats, mode):
		# Return early if no bars
		if angleStats is None:
			return False
	
		# First transform the true angle to canvas angle based on mode components
	
		zeroOffset = 0.0
		
		meanAngle = angleStats[0]
			
		zeroDirection = "N"
		if mode in ["A", "E", "I", "M"]:
			zeroOffset = 90.0
		elif mode in ["C", "G", "K", "O"]:
			zeroOffset = 270.0
		elif mode in ["D", "H", "L", "P"]:
			zeroOffset = 180.0
			
		if mode in ["E", "F", "G", "H", "M", "N", "O", "P"]:
			# Clockwise
			if zeroOffset > 0.0:
				zeroOffset = zeroOffset * -1.0
			meanAngle = 360.0 - (meanAngle + zeroOffset)
		else:
			# Counter-clockwise
			meanAngle = meanAngle + zeroOffset
		
		meanLineEndpoint = getEndpoint(300, 300, meanAngle, 260)
		
		mlRoi = Line(300, 300, meanLineEndpoint[0], meanLineEndpoint[1])
		mlRoi.setStrokeColor(Color.BLACK)
		mlRoi.setStrokeWidth(3)
		processor.drawRoi(mlRoi)
		

# This part only runs if the script is run directly, which should not happen.
if __name__ == "__main__" or __name__ == "__builtin__":
	print "This module is not meant to be run directly."
