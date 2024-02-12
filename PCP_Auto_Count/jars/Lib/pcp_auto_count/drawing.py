# Utility functions for drawing things on an image.
from ij.gui import Arrow, TextRoi
from java.awt import Color, Font

# The color we'll draw arrows on the result image.
#arrowColor = Color(0, 185, 0)
#textColor = Color(211, 84, 0)

# A function for drawing an arrow on an image.
def drawArrow(imp, arrowColor, startX, startY, endX, endY):
	arw = Arrow(startX, startY, endX, endY)
	arw.setHeadSize(5)
	arw.setStrokeWidth(3)
	arw.setFillColor(arrowColor)

	processor = imp.getProcessor()			
	processor.drawRoi(arw)
		
	imp.updateAndRepaintWindow()

# A function to draw text on an image at specified coordinates.
def drawText(imp, text, x, y, textColor, fontSize = 12):

        textFont = Font("Default", Font.BOLD, fontSize)
	
	textRoi = TextRoi(x, y, text)
	textRoi.setColor(textColor)
	
	textRoi.setFont(textFont)
	
	processor = imp.getProcessor()
	processor.drawRoi(textRoi)
	
	imp.updateAndRepaintWindow()
	
# This part only runs if the script is run directly, which should not happen.
if __name__ == "__main__" or __name__ == "__builtin__":
	print "This module is not meant to be run directly."
