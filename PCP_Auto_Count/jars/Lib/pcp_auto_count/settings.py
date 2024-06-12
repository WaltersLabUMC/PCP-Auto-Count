# A module that deals with the persistence of user-supplied options.
from ij import IJ
from java.lang.System import getProperty
from os.path import exists
from os import mkdir
from java.awt import Color

settingsFileName = 'settings.ini'
anglesCacheFileName = 'rdangles.txt'

# A class that contains all the options selected from the options dialog.
class ProcessingOptions:
	def __init__(self, removeNoise=True, noiseMaxSize=50, excludeBorderCells=False, trueCaveMode='largest', usePlasticWrap=False, angleAxisDirectionClockwise=False, angleAxisScaleZeroTo360=False, angleAxisZeroDirection='north', outputResultsTable=True, outputImage=True, outputImageArrows=True, outputImageLabels=True, outputImageAngles=True, outputImageRemovedBorderCells=True, outputImageNoise=True, outputImageBadCells=True, outputImagePlasticWrapBorder=False, outputImagePlasticWrapAddedWeight=False, outputCellSummary=True):
		self.removeNoise = removeNoise
		self.noiseMaxSize = noiseMaxSize
		self.removeConglomerates = False
		self.conglomeratesMinSize = 1000
		self.usePlasticWrap = usePlasticWrap
		self.ignoreSmallCaves = False
		self.smallCaveMaxSize = 1
		self.ignoreLargeCaves = False
		self.largeCaveMinSize = 1000
		self.trueCaveMode = trueCaveMode
		self.excludeBorderCells = excludeBorderCells
		self.excludeBorderCellsDistance = 0
		self.excludeOblongCellsW = False
		self.excludeOblongCellsH = False
		self.oblongMultiplierW = 4.0
		self.oblongMultiplierH = 4.0
		self.splitDoubletsW = False
		self.splitDoubletsH = False
		self.splitDoubletsMultiplierW = 2.7
		self.splitDoubletsMultiplierH = 2.7
		self.angleAxisDirectionClockwise = angleAxisDirectionClockwise
		self.angleAxisScaleZeroTo360 = angleAxisScaleZeroTo360
		self.angleAxisZeroDirection = angleAxisZeroDirection
		self.outputResultsTable = outputResultsTable
		self.outputResultsTableIncludeBadChunks = False
		self.outputImage = outputImage
		self.outputImageArrows = outputImageArrows
		self.outputImageLabels = outputImageLabels
		self.outputImageAngles = outputImageAngles
		self.outputImageRemovedBorderCells = outputImageRemovedBorderCells
		self.outputImageNoise = outputImageNoise
		self.outputImageConglomerates = False
		self.outputImageRemovedOblongCells = False
		self.outputImageBadCells = outputImageBadCells
		self.outputImagePlasticWrapBorder = outputImagePlasticWrapBorder
		self.outputImagePlasticWrapAddedWeight = outputImagePlasticWrapAddedWeight
		self.outputImageMarginPixels = 0
		self.outputCellSummary = outputCellSummary
		self.outputRoseDiagram = False
		self.outputRoseDiagramAxisSize = 0
		self.outputRoseDiagramMarkerIncrement = 90
		self.outputRoseDiagramBarSize = 15
		self.outputOverlay = False
		self.outputOverlayArrows = True
		self.outputOverlayLabels = True
		self.outputOverlayAngles = False

                self.drawingFontSize = 12
		self.drawingArrowheadSize = 5
		self.drawingArrowlineSize = 3
		
		self.angleAxisMode = 'I'

		# Drawing (Colors and Font)

		defaultColors = DefaultDrawingColors()

		noiseColor = defaultColors.getNoiseDefaultColor()
		self.color_noise_red = noiseColor.getRed()
		self.color_noise_green = noiseColor.getGreen()
		self.color_noise_blue = noiseColor.getBlue()
		self.color_noise_alpha = noiseColor.getAlpha()

		conglomeratesColor = defaultColors.getConglomeratesDefaultColor()
		self.color_conglomerates_red = conglomeratesColor.getRed()
		self.color_conglomerates_green = conglomeratesColor.getGreen()
		self.color_conglomerates_blue = conglomeratesColor.getBlue()
		self.color_conglomerates_alpha = conglomeratesColor.getAlpha()

                borderColor = defaultColors.getBorderChunksDefaultColor()
		self.color_border_chunks_red = borderColor.getRed()
		self.color_border_chunks_green = borderColor.getGreen()
		self.color_border_chunks_blue = borderColor.getBlue()
		self.color_border_chunks_alpha = borderColor.getAlpha()

                oblongColor = defaultColors.getOblongChunksDefaultColor()
		self.color_oblong_chunks_red = oblongColor.getRed()
		self.color_oblong_chunks_green = oblongColor.getGreen()
		self.color_oblong_chunks_blue = oblongColor.getBlue()
		self.color_oblong_chunks_alpha = oblongColor.getAlpha()

                badColor = defaultColors.getBadChunksDefaultColor()
		self.color_bad_chunks_red = badColor.getRed()
		self.color_bad_chunks_green = badColor.getGreen()
		self.color_bad_chunks_blue = badColor.getBlue()
		self.color_bad_chunks_alpha = badColor.getAlpha()

                pwColor = defaultColors.getPlasticWrapDefaultColor()
		self.color_plastic_wrap_red = pwColor.getRed()
		self.color_plastic_wrap_green = pwColor.getGreen()
		self.color_plastic_wrap_blue = pwColor.getBlue()
		self.color_plastic_wrap_alpha = pwColor.getAlpha()

                pwnColor = defaultColors.getPlasticWrapNewDefaultColor()
		self.color_plastic_wrap_new_red = pwnColor.getRed()
		self.color_plastic_wrap_new_green = pwnColor.getGreen()
		self.color_plastic_wrap_new_blue = pwnColor.getBlue()
		self.color_plastic_wrap_new_alpha = pwnColor.getAlpha()

                arrowColor = defaultColors.getArrowDefaultColor()
		self.color_arrows_red = arrowColor.getRed()
		self.color_arrows_green = arrowColor.getGreen()
		self.color_arrows_blue = arrowColor.getBlue()
		self.color_arrows_alpha = arrowColor.getAlpha()

                labelColor = defaultColors.getLabelDefaultColor()
		self.color_labels_red = labelColor.getRed()
		self.color_labels_green = labelColor.getGreen()
		self.color_labels_blue = labelColor.getBlue()
		self.color_labels_alpha = labelColor.getAlpha()

                rdColor = defaultColors.getRoseDiagramDefaultColor()
		self.color_rose_diagram_red = rdColor.getRed()
		self.color_rose_diagram_green = rdColor.getGreen()
		self.color_rose_diagram_blue = rdColor.getBlue()
		self.color_rose_diagram_alpha = rdColor.getAlpha()
		
	def toIniString(self):
		iniString = '[processing]\n'
		iniString += 'remove_noise = ' + str(self.removeNoise).lower() + '\n'
		iniString += 'noise_max_size = ' + str(self.noiseMaxSize) + '\n'
		iniString += 'remove_conglomerates = ' + str(self.removeConglomerates).lower() + '\n'
		iniString += 'conglomerates_min_size = ' + str(self.conglomeratesMinSize) + '\n'
		iniString += 'exclude_border_cells = ' + str(self.excludeBorderCells).lower() + '\n'
		iniString += 'exclude_border_cells_distance = ' + str(self.excludeBorderCellsDistance) + '\n'
		iniString += 'exclude_oblong_cells_w = ' + str(self.excludeOblongCellsW).lower() + '\n'
		iniString += 'exclude_oblong_cells_h = ' + str(self.excludeOblongCellsH).lower() + '\n'
		iniString += 'oblong_multiplier_w = ' + str(self.oblongMultiplierW) + '\n'
		iniString += 'oblong_multiplier_h = ' + str(self.oblongMultiplierH) + '\n'
		iniString += 'split_doublets_w = ' + str(self.splitDoubletsW).lower() + '\n'
		iniString += 'split_doublets_h = ' + str(self.splitDoubletsH).lower() + '\n'
		iniString += 'split_doublets_multiplier_w = ' + str(self.splitDoubletsMultiplierW) + '\n'
		iniString += 'split_doublets_multiplier_h = ' + str(self.splitDoubletsMultiplierH) + '\n'
		iniString += 'true_cave_mode = ' + self.trueCaveMode.lower() + '\n'
		iniString += 'use_plastic_wrap = ' + str(self.usePlasticWrap).lower() + '\n'
		iniString += 'ignore_small_caves = ' + str(self.ignoreSmallCaves).lower() + '\n'
		iniString += 'small_cave_max_size = ' + str(self.smallCaveMaxSize) + '\n'
		iniString += 'ignore_large_caves = ' + str(self.ignoreLargeCaves).lower() + '\n'
		iniString += 'large_cave_min_size = ' + str(self.largeCaveMinSize) + '\n'
		iniString += 'angle_axis_direction_clockwise = ' + str(self.angleAxisDirectionClockwise).lower() + '\n'
		iniString += 'angle_axis_scale_zero_to_360 = ' + str(self.angleAxisScaleZeroTo360).lower() + '\n'
		iniString += 'angle_axis_zero_direction = ' + str(self.angleAxisZeroDirection).lower() + '\n'
		iniString += 'angle_axis_mode = ' + self.angleAxisMode.upper() + '\n\n'
		iniString += '[output]\n'
		iniString += 'output_results_table = ' + str(self.outputResultsTable).lower() + '\n'
		iniString += 'output_results_table_include_bad_chunks = ' + str(self.outputResultsTableIncludeBadChunks).lower() + '\n'
		iniString += 'output_image = ' + str(self.outputImage).lower() + '\n'
		iniString += 'output_image_arrows = ' + str(self.outputImageArrows).lower() + '\n'
		iniString += 'output_image_labels = ' + str(self.outputImageLabels).lower() + '\n'
		iniString += 'output_image_angles = ' + str(self.outputImageAngles).lower() + '\n'
		iniString += 'output_image_removed_border_cells = ' + str(self.outputImageRemovedBorderCells).lower() + '\n'
		iniString += 'output_image_noise = ' + str(self.outputImageNoise).lower() + '\n'
		iniString += 'output_image_conglomerates = ' + str(self.outputImageConglomerates).lower() + '\n'
		iniString += 'output_image_removed_oblong_cells = ' + str(self.outputImageRemovedOblongCells).lower() + '\n'
		iniString += 'output_image_bad_cells = ' + str(self.outputImageBadCells).lower() + '\n'
		iniString += 'output_image_plastic_wrap_border = ' + str(self.outputImagePlasticWrapBorder).lower() + '\n'
		iniString += 'output_image_plastic_wrap_added_weight = ' + str(self.outputImagePlasticWrapAddedWeight).lower() + '\n'
		iniString += 'output_image_margin_pixels = ' + str(self.outputImageMarginPixels) + '\n'
		iniString += 'output_cell_summary = ' + str(self.outputCellSummary).lower() + '\n'
		iniString += 'output_rose_diagram = ' + str(self.outputRoseDiagram).lower() + '\n'
		iniString += 'output_rose_diagram_axis_size = ' + str(self.outputRoseDiagramAxisSize) + '\n'
		iniString += 'output_rose_diagram_marker_increment = ' + str(self.outputRoseDiagramMarkerIncrement) + '\n'
		iniString += 'output_rose_diagram_bar_size = ' + str(self.outputRoseDiagramBarSize) + '\n'
		iniString += 'output_overlay = ' + str(self.outputOverlay).lower() + '\n'
		iniString += 'output_overlay_arrows = ' + str(self.outputOverlayArrows).lower() + '\n'
		iniString += 'output_overlay_labels = ' + str(self.outputOverlayLabels).lower() + '\n'
		iniString += 'output_overlay_angles = ' + str(self.outputOverlayAngles).lower() + '\n\n'
		
		iniString += '[colors]\n'
                iniString += 'color_noise_red = ' + str(self.color_noise_red) + '\n'
		iniString += 'color_noise_green = ' + str(self.color_noise_green) + '\n'
		iniString += 'color_noise_blue = ' + str(self.color_noise_blue) + '\n'
		iniString += 'color_noise_alpha = ' + str(self.color_noise_alpha) + '\n'
		iniString += 'color_conglomerates_red = ' + str(self.color_conglomerates_red) + '\n'
		iniString += 'color_conglomerates_green = ' + str(self.color_conglomerates_green) + '\n'
		iniString += 'color_conglomerates_blue = ' + str(self.color_conglomerates_blue) + '\n'
		iniString += 'color_conglomerates_alpha = ' + str(self.color_conglomerates_alpha) + '\n'
		iniString += 'color_border_chunks_red = ' + str(self.color_border_chunks_red) + '\n'
		iniString += 'color_border_chunks_green = ' + str(self.color_border_chunks_green) + '\n'
		iniString += 'color_border_chunks_blue = ' + str(self.color_border_chunks_blue) + '\n'
		iniString += 'color_border_chunks_alpha = ' + str(self.color_border_chunks_alpha) + '\n'
		iniString += 'color_oblong_chunks_red = ' + str(self.color_oblong_chunks_red) + '\n'
		iniString += 'color_oblong_chunks_green = ' + str(self.color_oblong_chunks_green) + '\n'
		iniString += 'color_oblong_chunks_blue = ' + str(self.color_oblong_chunks_blue) + '\n'
		iniString += 'color_oblong_chunks_alpha = ' + str(self.color_oblong_chunks_alpha) + '\n'
		iniString += 'color_bad_chunks_red = ' + str(self.color_bad_chunks_red) + '\n'
		iniString += 'color_bad_chunks_green = ' + str(self.color_bad_chunks_green) + '\n'
		iniString += 'color_bad_chunks_blue = ' + str(self.color_bad_chunks_blue) + '\n'
		iniString += 'color_bad_chunks_alpha = ' + str(self.color_bad_chunks_alpha) + '\n'
		iniString += 'color_plastic_wrap_red = ' + str(self.color_plastic_wrap_red) + '\n'
		iniString += 'color_plastic_wrap_green = ' + str(self.color_plastic_wrap_green) + '\n'
		iniString += 'color_plastic_wrap_blue = ' + str(self.color_plastic_wrap_blue) + '\n'
		iniString += 'color_plastic_wrap_alpha = ' + str(self.color_plastic_wrap_alpha) + '\n'
		iniString += 'color_plastic_wrap_new_red = ' + str(self.color_plastic_wrap_new_red) + '\n'
		iniString += 'color_plastic_wrap_new_green = ' + str(self.color_plastic_wrap_new_green) + '\n'
		iniString += 'color_plastic_wrap_new_blue = ' + str(self.color_plastic_wrap_new_blue) + '\n'
		iniString += 'color_plastic_wrap_new_alpha = ' + str(self.color_plastic_wrap_new_alpha) + '\n'
		iniString += 'color_arrows_red = ' + str(self.color_arrows_red) + '\n'
		iniString += 'color_arrows_green = ' + str(self.color_arrows_green) + '\n'
		iniString += 'color_arrows_blue = ' + str(self.color_arrows_blue) + '\n'
		iniString += 'color_arrows_alpha = ' + str(self.color_arrows_alpha) + '\n'
		iniString += 'color_labels_red = ' + str(self.color_labels_red) + '\n'
		iniString += 'color_labels_green = ' + str(self.color_labels_green) + '\n'
		iniString += 'color_labels_blue = ' + str(self.color_labels_blue) + '\n'
		iniString += 'color_labels_alpha = ' + str(self.color_labels_alpha) + '\n'
		iniString += 'color_rose_diagram_red = ' + str(self.color_rose_diagram_red) + '\n'
		iniString += 'color_rose_diagram_green = ' + str(self.color_rose_diagram_green) + '\n'
		iniString += 'color_rose_diagram_blue = ' + str(self.color_rose_diagram_blue) + '\n'
		iniString += 'color_rose_diagram_alpha = ' + str(self.color_rose_diagram_alpha) + '\n\n'

		iniString += '[drawing]\n'
		iniString += 'drawing_font_size = ' + str(self.drawingFontSize) + '\n'
		iniString += 'drawing_arrowhead_size = ' + str(self.drawingArrowheadSize) + '\n'
		iniString += 'drawing_arrowline_size = ' + str(self.drawingArrowlineSize)
		
		return iniString

	def getColorNoise(self):
                return Color(self.color_noise_red, self.color_noise_green, self.color_noise_blue, self.color_noise_alpha)

        def setColorNoise(self, newColor):
                self.assignColorValues(('color_noise_red', 'color_noise_green', 'color_noise_blue', 'color_noise_alpha'), newColor)

        def getColorConglomerates(self):
                return Color(self.color_conglomerates_red, self.color_conglomerates_green, self.color_conglomerates_blue, self.color_conglomerates_alpha)

        def setColorConglomerates(self, newColor):
                self.assignColorValues(('color_conglomerates_red', 'color_conglomerates_green', 'color_conglomerates_blue', 'color_conglomerates_alpha'), newColor)

        def getColorBorderChunks(self):
                return Color(self.color_border_chunks_red, self.color_border_chunks_green, self.color_border_chunks_blue, self.color_border_chunks_alpha)

        def setColorBorderChunks(self, newColor):
                self.assignColorValues(('color_border_chunks_red', 'color_border_chunks_green', 'color_border_chunks_blue', 'color_border_chunks_alpha'), newColor)

        def getColorOblongChunks(self):
                return Color(self.color_oblong_chunks_red, self.color_oblong_chunks_green, self.color_oblong_chunks_blue, self.color_oblong_chunks_alpha)

        def setColorOblongChunks(self, newColor):
                self.assignColorValues(('color_oblong_chunks_red', 'color_oblong_chunks_green', 'color_oblong_chunks_blue', 'color_oblong_chunks_alpha'), newColor)

        def getColorBadChunks(self):
                return Color(self.color_bad_chunks_red, self.color_bad_chunks_green, self.color_bad_chunks_blue, self.color_bad_chunks_alpha)

        def setColorBadChunks(self, newColor):
                self.assignColorValues(('color_bad_chunks_red', 'color_bad_chunks_green', 'color_bad_chunks_blue', 'color_bad_chunks_alpha'), newColor)

        def getColorArrows(self):
                return Color(self.color_arrows_red, self.color_arrows_green, self.color_arrows_blue, self.color_arrows_alpha)

        def setColorArrows(self, newColor):
                self.assignColorValues(('color_arrows_red', 'color_arrows_green', 'color_arrows_blue', 'color_arrows_alpha'), newColor)

        def getColorLabels(self):
                return Color(self.color_labels_red, self.color_labels_green, self.color_labels_blue, self.color_labels_alpha)

        def setColorLabels(self, newColor):
                self.assignColorValues(('color_labels_red', 'color_labels_green', 'color_labels_blue', 'color_labels_alpha'), newColor)

        def getColorRoseDiagram(self):
                return Color(self.color_rose_diagram_red, self.color_rose_diagram_green, self.color_rose_diagram_blue, self.color_rose_diagram_alpha)

        def setColorRoseDiagram(self, newColor):
                self.assignColorValues(('color_rose_diagram_red', 'color_rose_diagram_green', 'color_rose_diagram_blue', 'color_rose_diagram_alpha'), newColor)

        def getColorPlasticWrap(self):
                return Color(self.color_plastic_wrap_red, self.color_plastic_wrap_green, self.color_plastic_wrap_blue, self.color_plastic_wrap_alpha)

        def setColorPlasticWrap(self, newColor):
                self.assignColorValues(('color_plastic_wrap_red', 'color_plastic_wrap_green', 'color_plastic_wrap_blue', 'color_plastic_wrap_alpha'), newColor)

        def getColorPlasticWrapNew(self):
                return Color(self.color_plastic_wrap_new_red, self.color_plastic_wrap_new_green, self.color_plastic_wrap_new_blue, self.color_plastic_wrap_new_alpha)

        def setColorPlasticWrapNew(self, newColor):
                self.assignColorValues(('color_plastic_wrap_new_red', 'color_plastic_wrap_new_green', 'color_plastic_wrap_new_blue', 'color_plastic_wrap_new_alpha'), newColor)

        def assignColorValues(self, rgba, newColor):
                setattr(self, rgba[0], newColor.getRed())
                setattr(self, rgba[1], newColor.getGreen())
                setattr(self, rgba[2], newColor.getBlue())
                setattr(self, rgba[3], newColor.getAlpha())

def getSettingsFilePath():	
	if IJ.isWindows():
		return str(getProperty('user.home')) + '\\AppData\\Roaming\\PCP Auto Count\\' + settingsFileName
	else:
		return str(getProperty('user.home')) + '/.PCP Auto Count/' + settingsFileName
		
def settingsFileExists():
	if exists(getSettingsFilePath().replace('\\', '/')):
		return True
	else:
		return False
		
def createDefaultSettingsFile():
	
	settingsFilePath = getSettingsFilePath()
	
	if IJ.isWindows():
		settingsDirectory = settingsFilePath.replace('\\','/').replace('/settings.ini','')
		if exists(settingsDirectory) == False:
			mkdir(settingsDirectory)
			
	defaultSettings = ProcessingOptions()

	writer = open(settingsFilePath, 'w')
	writer.writelines(defaultSettings.toIniString())
	writer.close()
	
def getProcessingOptionsFromSettingsFile():        
	
	settingsFilePath = getSettingsFilePath().replace('\\','/')
	
	savedOptions = ProcessingOptions()

	savedProps = dir(savedOptions)
	colorKey = []
	for p in savedProps:
                if p.startswith('color_'):
                        colorKey.append(p)
	
	lines = []
	
	with open(settingsFilePath, 'r') as settingsFile:
		lines = settingsFile.readlines()
	
	for line in lines:
		
		line = line.replace('\n','').lower()

		if line.startswith('#') or line.startswith('['):
                        continue

                if len(line) < 5:
                        continue
                        		
                if line.startswith('remove_noise = '):
                        x = line[15:]
                        if x == 'true':
                                savedOptions.removeNoise = True
                        elif x == 'false':
                                savedOptions.removeNoise = False
                                
                elif line.startswith('noise_max_size = '):
                        x = line[17:]
                        if x.isnumeric():
                                n = int(x)
                                if n > 0:
                                        savedOptions.noiseMaxSize = n

                elif line.startswith('remove_conglomerates = '):
                        x = line[23:]
                        if x == 'true':
                                savedOptions.removeConglomerates = True
                        elif x == 'false':
                                savedOptions.removeConglomerates = False

                elif line.startswith('conglomerates_min_size = '):
                        x = line[25:]
                        if x.isnumeric():
                                n = int(x)
                                if n > 0:
                                        savedOptions.conglomeratesMinSize = n
                
                elif line.startswith('exclude_border_cells = '):
                        x = line[23:]
                        if x == 'true':
                                savedOptions.excludeBorderCells = True
                        elif x == 'false':
                                savedOptions.excludeBorderCells = False

                elif line.startswith('exclude_border_cells_distance = '):
                        x = line[32:]
                        if x.isnumeric():
                                n = int(x)
                                if n >= 0:
                                        savedOptions.excludeBorderCellsDistance = n

                elif line.startswith('exclude_oblong_cells_w = '):
                        x = line[25:]
                        if x == 'true':
                                savedOptions.excludeOblongCellsW = True
                        elif x == 'false':
                                savedOptions.excludeOblongCellsW = False

                elif line.startswith('exclude_oblong_cells_h = '):
                        x = line[25:]
                        if x == 'true':
                                savedOptions.excludeOblongCellsH = True
                        elif x == 'false':
                                savedOptions.excludeOblongCellsH = False

                elif line.startswith('oblong_multiplier_w = '):
                        x = line[22:]
                        n = toFloat(x)
                        if n >= 0.1:
                                savedOptions.oblongMultiplierW = n

                elif line.startswith('oblong_multiplier_h = '):
                        x = line[22:]
                        n = toFloat(x)
                        if n >= 0.1:
                                savedOptions.oblongMultiplierH = n

                elif line.startswith('split_doublets_w = '):
                        x = line[19:]
                        if x == 'true':
                                savedOptions.splitDoubletsW = True
                        elif x == 'false':
                                savedOptions.splitDoubletsW = False

                elif line.startswith('split_doublets_h = '):
                        x = line[19:]
                        if x == 'true':
                                savedOptions.splitDoubletsH = True
                        elif x == 'false':
                                savedOptions.splitDoubletsH = False

                elif line.startswith('split_doublets_multiplier_w = '):
                        x = line[30:]
                        n = toFloat(x)
                        if n >= 0.1:
                                savedOptions.splitDoubletsMultiplierW = n

                elif line.startswith('split_doublets_multiplier_h = '):
                        x = line[30:]
                        n = toFloat(x)
                        if n >= 0.1:
                                savedOptions.splitDoubletsMultiplierH = n    
                                
                elif line.startswith('true_cave_mode = '):
                        x = line[17:]
                        if x in ['largest', 'northmost', 'southmost', 'eastmost', 'westmost', 'highest', 'lowest', 'leftmost', 'rightmost']:
                                savedOptions.trueCaveMode = x
                                
                elif line.startswith('use_plastic_wrap = '):
                        x = line[19:]
                        if x == 'true':
                                savedOptions.usePlasticWrap = True
                        elif x == 'false':
                                savedOptions.usePlasticWrap = False
                                
                elif line.startswith('ignore_small_caves = '):
                        x = line[21:]
                        if x == 'true':
                                savedOptions.ignoreSmallCaves = True
                        elif x == 'false':
                                savedOptions.ignoreSmallCaves = False
                        
                elif line.startswith('small_cave_max_size = '):
                        x = line[22:]
                        if x.isnumeric():
                                n = int(x)
                                if n >= 0:
                                        savedOptions.smallCaveMaxSize = n

                elif line.startswith('ignore_large_caves = '):
                        x = line[21:]
                        if x == 'true':
                                savedOptions.ignoreLargeCaves = True
                        elif x == 'false':
                                savedOptions.ignoreLargeCaves = False

                elif line.startswith('large_cave_min_size = '):
                        x = line[22:]
                        if x.isnumeric():
                                n = int(x)
                                if n >= 0:
                                        savedOptions.largeCaveMinSize = n
                                
                elif line.startswith('angle_axis_direction_clockwise = '):
                        x = line[33:]
                        if x == 'true':
                                savedOptions.angleAxisDirectionClockwise = True
                        elif x == 'false':
                                savedOptions.angleAxisDirectionClockwise = False
                                
                elif line.startswith('angle_axis_scale_zero_to_360 = '):
                        x = line[31:]
                        if x == 'true':
                                savedOptions.angleAxisScaleZeroTo360 = True
                        elif x == 'false':
                                savedOptions.angleAxisScaleZeroTo360 = False
                                
                elif line.startswith('angle_axis_zero_direction = '):
                        x = line[28:]
                        if x in ["north", "south", "east", "west"]:
                                savedOptions.angleAxisZeroDirection = x
                
                elif line.startswith('angle_axis_mode = '):
                        x = line[18:].upper()
                        if x in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']:
                                savedOptions.angleAxisMode = x
                                
                elif line.startswith('output_rose_diagram = '):
                        x = line[22:]
                        if x == 'true':
                                savedOptions.outputRoseDiagram = True
                        elif x == 'false':
                                savedOptions.outputRoseDiagram = False
                                
                elif line.startswith('output_rose_diagram_axis_size = '):
                        x = line[32:]
                        if x.isnumeric():
                                n = int(x)
                                if n >= 0:
                                        savedOptions.outputRoseDiagramAxisSize = n
                                        
                elif line.startswith('output_rose_diagram_marker_increment = '):
                        x = line[39:]
                        if x in ['90', '45', '30']:
                                savedOptions.outputRoseDiagramMarkerIncrement = int(x)
                                
                elif line.startswith('output_rose_diagram_bar_size = '):
                        x = line[31:]
                        if x in ['5', '10', '15', '20']:
                                savedOptions.outputRoseDiagramBarSize = int(x)
                
                elif line.startswith('output_results_table = '):
                        x = line[23:]
                        if x == 'true':
                                savedOptions.outputResultsTable = True
                        elif x == 'false':
                                savedOptions.outputResultsTable = False

                elif line.startswith('output_results_table_include_bad_chunks = '):
                        x = line[42:]
                        if x == 'true':
                                savedOptions.outputResultsTableIncludeBadChunks = True
                        elif x == 'false':
                                savedOptions.outputResultsTableIncludeBadChunks = False
                
                elif line.startswith('output_image = '):
                        x = line[15:]
                        if x == 'true':
                                savedOptions.outputImage = True
                        elif x == 'false':
                                savedOptions.outputImage = False
                
                elif line.startswith('output_image_arrows = '):
                        x = line[22:]
                        if x == 'true':
                                savedOptions.outputImageArrows = True
                        elif x == 'false':
                                savedOptions.outputImageArrows = False
                                
                elif line.startswith('output_image_labels = '):
                        x = line[22:]
                        if x == 'true':
                                savedOptions.outputImageLabels = True
                        elif x == 'false':
                                savedOptions.outputImageLabels = False
                
                elif line.startswith('output_image_angles = '):
                        x = line[22:]
                        if x == 'true':
                                savedOptions.outputImageAngles = True
                        elif x == 'false':
                                savedOptions.outputImageAngles = False
                
                elif line.startswith('output_image_removed_border_cells = '): #36
                        x = line[36:]
                        if x == 'true':
                                savedOptions.outputImageRemovedBorderCells = True
                        elif x == 'false':
                                savedOptions.outputImageRemovedBorderCells = False
                                
                elif line.startswith('output_image_noise = '): #21
                        x = line[21:]
                        if x == 'true':
                                savedOptions.outputImageNoise = True
                        elif x == 'false':
                                savedOptions.outputImageNoise = False

                elif line.startswith('output_image_conglomerates = '):
                        x = line[29:]
                        if x == 'true':
                                savedOptions.outputImageConglomerates = True
                        elif x == 'false':
                                savedOptions.outputImageConglomerates = False

                elif line.startswith('output_image_removed_oblong_cells = '): #36
                        x = line[36:]
                        if x == 'true':
                                savedOptions.outputImageRemovedOblongCells = True
                        elif x == 'false':
                                savedOptions.outputImageRemovedOblongCells = False
                
                elif line.startswith('output_image_bad_cells = '): #25
                        x = line[25:]
                        if x == 'true':
                                savedOptions.outputImageBadCells = True
                        elif x == 'false':
                                savedOptions.outputImageBadCells = False
                                
                elif line.startswith('output_image_plastic_wrap_border = '):
                        x = line[35:]
                        if x == 'true':
                                savedOptions.outputImagePlasticWrapBorder = True
                        elif x == 'false':
                                savedOptions.outputImagePlasticWrapBorder = False
                                
                elif line.startswith('output_image_plastic_wrap_added_weight = '):
                        x = line[41:]
                        if x == 'true':
                                savedOptions.outputImagePlasticWrapAddedWeight = True
                        elif x == 'false':
                                savedOptions.outputImagePlasticWrapAddedWeight = False
                                
                elif line.startswith('output_image_margin_pixels = '):
                        x = line[29:]
                        if x.isnumeric():
                                n = int(x)
                                if n > -1:
                                        savedOptions.outputImageMarginPixels = n

                elif line.startswith('output_cell_summary = '):
                        x = line[22:]
                        if x == 'true':
                                savedOptions.outputCellSummary = True
                        elif x == 'false':
                                savedOptions.outputCellSummary = False
                                
                elif line.startswith('output_overlay = '):
                        x = line[17:]
                        if x == 'true':
                                savedOptions.outputOverlay = True
                        elif x == 'false':
                                savedOptions.outputOverlay = False
                                
                elif line.startswith('output_overlay_arrows = '):
                        x = line[24:]
                        if x == 'true':
                                savedOptions.outputOverlayArrows = True
                        elif x == 'false':
                                savedOptions.outputOverlayArrows = False
                                
                elif line.startswith('output_overlay_labels = '):
                        x = line[24:]
                        if x == 'true':
                                savedOptions.outputOverlayLabels = True
                        elif x == 'false':
                                savedOptions.outputOverlayLabels = False
                                
                elif line.startswith('output_overlay_angles = '):
                        x = line[24:]
                        if x == 'true':
                                savedOptions.outputOverlayAngles = True
                        elif x == 'false':
                                savedOptions.outputOverlayAngles = False

                elif line.startswith('drawing_font_size = '):
                        x = line[20:]
                        if x.isnumeric():
                                n = int(x)
                                if n > 3 and n < 1001:
                                        savedOptions.drawingFontSize = n

                elif line.startswith('drawing_arrowhead_size = '):
                        x = line[25:]
                        if x.isnumeric():
                                n = int(x)
                                if n > 0 and n < 1001:
                                        savedOptions.drawingArrowheadSize = n

                elif line.startswith('drawing_arrowline_size = '):
                        x = line[25:]
                        if x.isnumeric():
                                n = int(x)
                                if n > 0 and n < 1001:
                                        savedOptions.drawingArrowlineSize = n

                elif line.startswith('color_'):
                        
                        c = line.rfind(' ') + 1
                        if c < 1:
                                continue
                        if c >= len(line):
                                continue
                        s = line.find(' ')
                        if s < 1:
                                continue
                        colorProp = line[0:s]
                        colorProp = colorProp.lower()
                        if not colorProp in colorKey:
                                continue
                        x = line[c:]
                        if not x.isnumeric():
                                continue
                        n = int(x)
                        if n < 0:
                                n = 0
                        elif n > 255:
                                n = 255

                        setattr(savedOptions, colorProp, n)                     
        
	return savedOptions
	
def writeProcessingOptionsToSettingsFile(options):

	settingsFilePath = getSettingsFilePath()
	
	settingsDirectory = settingsFilePath
	
	if IJ.isWindows():
		settingsDirectory = settingsDirectory.replace('\\','/')
	
	settingsDirectory = settingsDirectory.replace('/settings.ini','')	
		
	if exists(settingsDirectory) == False:
		mkdir(settingsDirectory)

	writer = open(settingsFilePath, 'w')
	writer.writelines(options.toIniString())
	writer.close()

def toFloat(value):
        try:
                return float(value)
        except:
                return -1.0

class DefaultDrawingColors:
        def getArrowDefaultColor(self):
                return Color(0, 185, 0, 255)
        def getLabelDefaultColor(self):
                return Color(211, 84, 0, 255)
        def getPlasticWrapDefaultColor(self):
                return Color(255, 255, 0, 255)
        def getPlasticWrapNewDefaultColor(self):
                return Color(0, 255, 255, 255)
        def getNoiseDefaultColor(self):
                return Color(255, 0, 255, 255)
        def getConglomeratesDefaultColor(self):
                return Color(194, 30, 86, 255)
        def getBorderChunksDefaultColor(self):
                return Color(80, 16, 208, 255)
        def getOblongChunksDefaultColor(self):
                return Color(100, 149, 237, 255)
        def getBadChunksDefaultColor(self):
                return Color(255, 0, 0, 255)
        def getRoseDiagramDefaultColor(self):
                return Color(166, 202, 240, 255)

# The following functions deal with the angles cache file (sort of like a settings file, but more of a cache.)

def angleStringIsValid(astr):
        if astr.replace('.','').isdigit():
                return True
        return False

def angleTextToFloats(angleText):
        # Takes a text blob of angles and returns a float array representation.
        # Removes any "nonsense" strings from the list.
        angles = angleText.splitlines()
        floatAngles = []
        for astr in angles:
                astr = str(astr)
                if angleStringIsValid(astr):
                        floatAngles.append(float(astr))
        return floatAngles

def writeAnglesToCacheFile(angles):
        # Write the angles to the cache file.
        count = len(angles)
        if count < 1:
                return
        angleText = str(angles[0])
        if count > 1:
                for i in range(1, count, 1):
                        angleText += ('\n' + str(angles[i]))        

        cacheFilePath = getAnglesCacheFilePath()	
	cacheDirectory = cacheFilePath
	
	if IJ.isWindows():
		cacheDirectory = cacheDirectory.replace('\\','/')
	
	cacheDirectory = cacheDirectory.replace('/rdangles.txt','')	
		
	if exists(cacheDirectory) == False:
		mkdir(cacheDirectory)

	with open(cacheFilePath, 'w') as cacheFile:
                cacheFile.write(angleText)

def readAnglesFromCacheFile():
        # Returns the text in the angles cache file, with any nonsense lines removed.
        angleText = ''
        if not anglesCacheFileExists():
                return angleText
        cacheFilePath = getAnglesCacheFilePath()
        if IJ.isWindows():
		cacheFilePath = cacheFilePath.replace('\\','/')
	lines = []
        with open(cacheFilePath, 'r') as cacheFile:
                linesBlob = cacheFile.read()

        lines = linesBlob.splitlines()
        count = len(lines)
        
        if count < 1:
                return angleText
        if angleStringIsValid(str(lines[0])):
                angleText += str(lines[0])
        if count == 1:
                return angleText
        for i in range(1, count, 1):
                astr = str(lines[i])
                if angleStringIsValid(astr):
                        angleText += ('\n' + astr)
        return angleText
        

def getAnglesCacheFilePath():	
	if IJ.isWindows():
		return str(getProperty('user.home')) + '\\AppData\\Roaming\\PCP Auto Count\\' + anglesCacheFileName
	else:
		return str(getProperty('user.home')) + '/.PCP Auto Count/' + anglesCacheFileName
		
def anglesCacheFileExists():
	if exists(getAnglesCacheFilePath().replace('\\', '/')):
		return True
	else:
		return False
		

        
        

                

# This part only runs if the script is run directly, which should not happen.
if __name__ == "__main__" or __name__ == "__builtin__":
	print "This module is not meant to be run directly."
	
