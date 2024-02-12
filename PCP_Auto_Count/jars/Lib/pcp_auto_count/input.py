# Classes and functions to help interact with the user.
from ij.gui import GenericDialog

# Just show an error in a dialog with an OK button.
def showErrorDialog(title, message):
	errorForm = GenericDialog(title)
	errorForm.addMessage(message)
	errorForm.hideCancelButton()
	errorForm.showDialog()

# This part only runs if the script is run directly, which should not happen.
if __name__ == "__main__" or __name__ == "__builtin__":
	print "This module is not meant to be run directly."
		