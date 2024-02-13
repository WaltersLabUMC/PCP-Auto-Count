# ﻿PCP Auto Count

## What is it? 

PCP Auto Count is a set of Python (Jython) based scripts that operate as a plug-in for ImageJ openware. The purpose of the plug-in is to automate the measurement of the orientations of individual cells or structures within black and white images of biological samples. 

## Use:

PCP Auto Count was designed for use in the analysis of images within the Java-based Fiji (or ImageJ) platform. The primary intention was for data collection pertaining to the planar cell polarity (PCP) of cells in an epithelial sheet, though it is also useful for any features in an image that conform to a “chunk” and “cave” structure which we define as a group of white pixels (chunk) with an inclusion or indentation of black pixels (cave). Any objects that conform to this morphology can be analyzed. The main outputs are a count of the number of chunks and the angles of orientation of each chunk based on the location of each cave. Though developed for biological samples, there are likely applications to other fields where the orientation of objects in a photograph need to be determined. 

## Getting Started:

The easiest method for importing PCP Auto Count into Fiji (or ImageJ) is to navigate to the Help tab in ImageJ, and click “Update…”  Click “Manage update sites”, click “Add Unlisted Site”, replace the name “New” with “PCP Auto Count” and enter the URL: https://sites.imagej.net/PCP-Auto-Count/ 
Then click “Apply and close”, then click “Apply Changes”. Restart ImageJ.
PCP Auto Count should now be an option under the “Analyze” tab.

## Getting Help:

You can launch the user manual for PCP Auto Count by clicking "Manual" on its menu. You can also find it [here](https://github.com/WaltersLabUMC/PCP-Auto-Count/blob/main/PCP_Auto_Count/lib/pcp_auto_count/Manual.pdf).

## License:

Please read the License document provided. PCP Auto Count is intended for use in research and the creators request to be cited in any resulting publications. 

## Contributing:

If problems occur, please use the troubleshoot option which will copy all settings to the clipboard, then email that information as well as a copy of the image being analyzed to luke@trimd.com and bwalters2@umc.edu

