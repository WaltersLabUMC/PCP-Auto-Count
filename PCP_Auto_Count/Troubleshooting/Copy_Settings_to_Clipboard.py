from ij import IJ
from java.awt import Toolkit
from java.awt.datatransfer import Clipboard, StringSelection
from pcp_auto_count.settings import settingsFileExists, getSettingsFilePath

def settingsToClipboard():

    if settingsFileExists() == False:
        return

    settingsFilePath = getSettingsFilePath()
    if IJ.isWindows() == False:
        settingsFilePath = settingsFilePath.replace('\\','/')

    text = ''
    with open(settingsFilePath, 'r') as settingsFile:
        text = settingsFile.read()
    
    tk = Toolkit.getDefaultToolkit()
    cb = tk.getSystemClipboard()
    strsel = StringSelection(text)
    cb.setContents(strsel, None)
    return

if __name__ == "__main__":
    settingsToClipboard()
