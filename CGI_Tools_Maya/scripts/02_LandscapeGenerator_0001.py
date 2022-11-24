"""
    A Maya Python script to generate landscapes from input image files.

    Jacob Worgan (s5107963) @ Bournemouth University, CGI Techniques
    v1.0 14/01/2022

    (Reference links at start of block in which they are used, all accessed January 2022.)
    (2nd reference code not direcly used but learned technique)
    (Others used in bounded comments.)
    Referenced in this script:
        Macey, J., 2011. Using the Maya MScriptUtil class in Python. [Online] Available at: http://jonmacey.blogspot.com/2011/04/using-maya-mscriptutil-class-in-python.html [Accessed 12 2021]
        annooshukla, 2017. Autodesk, Create mesh from list - Autodesk Community - Maya [Online] Available at: https://forums.autodesk.com/t5/maya-programming/create-mesh-from-list/td-p/7575371 [Accessed 12 2021]
        https://stackoverflow.com/questions/8220108/how-do-i-check-the-operating-system-in-python
"""

import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.OpenMaya as om1

# Class referenced & adapted from:
# http://jonmacey.blogspot.com/2011/04/using-maya-mscriptutil-class-in-python.html 
## START REFERENCE
class Imager():
    """ The wrapper class for the OpenMaya MImage class with a getPixel function. """
    def __init__(self, fileName):
        """ Initialises the Imager variables by opening file of input fileName. """
        # Create MImage and Load File
        self.image = om1.MImage()
        self.image.readFromFile(fileName)
        
        # Get Width, Height (very short, thanks openmaya api 2!)
        #self.width, self.height = self.image.getSize() < I think api2 is causing bugs...
        # Seems like api2 has makes things nicer by returning ints but this is incompatible with api1 only stuff...
        scriptUtilWidth = om1.MScriptUtil()
        scriptUtilHeight = om1.MScriptUtil()
        # Create unsigned int pointers for width & height
        widthPtr = scriptUtilWidth.asUintPtr()
        heightPtr = scriptUtilHeight.asUintPtr()
        ## Set pointers to 0 value
        scriptUtilWidth.setUint(widthPtr, 0)
        scriptUtilHeight.setUint(heightPtr, 0)
        # Call MImage getSize passing in the pointers
        self.image.getSize(widthPtr, heightPtr)
        # ..and convert the values to int
        self.width = scriptUtilWidth.getUint(widthPtr)
        self.height = scriptUtilHeight.getUint(heightPtr)

        # Get Pixel Pointer
        self.pixelPtr = self.image.pixels()

        # Create pointer to function getUcharArrayItem for pixel accessing later
        scriptUtil = om1.MScriptUtil()
        self.getUcharArrayItem = scriptUtil.getUcharArrayItem

    def Resize(self, width, height):
        """ Resize the image with a width and height. """
        self.width = width
        self.height = height
        self.image.resize(height, width)

    def GetPixel(self, x, y):
        """ Get the pixel at x,y and return tuple of rgba. """
        # Bounds check
        if((x < 0) or (x > self.width)):
            print("Out of bounds X.\n")
            return 
        if((y < 0) or (y > self.height)):
            print("Out of bounds X.\n")
            return 
        # Calculate index for 1D array
        index = (y * self.width * 4) + (x * 4)
        # Get the Pixel
        red =   self.getUcharArrayItem(self.pixelPtr, index)
        green = self.getUcharArrayItem(self.pixelPtr, index+1)
        blue =  self.getUcharArrayItem(self.pixelPtr, index+2)
        alpha = self.getUcharArrayItem(self.pixelPtr, index+3)

        return (red, green, blue, alpha)

    def GetRGB(self, x, y):
        """ Return RGB values from input X Y coordinates. """
        r, g, b, a = self.GetPixel(x, y)
        return (r, g, b)

    def Width(self):
        """ Return image width. """
        return self.width

    def Height(self):
        """ Return image height. """
        return self.height
## END REFERENCE

class Generator():
    """ Controls the generation of landscapes. """
    def __init__(self):
        """ Initialise the generator (blank). """
        pass

        
    def GenerateEnvironment(self):
        """ Generate scattered environment, using premade meshes? or also generated basic meshes?"""
        # User selects meshes to scatter on landscape
        # Meshes centred with centre of the base on the origin
        # Would need a scattering algorithm...
        pass

    def GenerateSquareWallDecor(self):
        """ Generate the Sonic Emerald Hill Zone style square wall paterns.  """
        pass

        
    def GenerateLandscapeFromScratch(self, XScale=1, YScale=1, XSubdiv=100, YSubdiv=100, Height=5, WaterPlane=True):
        """ Generates a background landscape using layered perlin noise.

            XScale      :   The scale of the landscape, in maya units, along the X-Axis.
            YScale      :   The scale of the landscape, in maya units, along the Y-Axis.
            XSubdiv     :   The subdivisions of the landscape to generate along the X-Axis.
            YSubdiv     :   The subdivisions of the landscape to generate along the Y-Axis.
            Height      :   The height scalar of the landscape, landscape generates from y=0 to y=height. 
            WaterPlane  :   A boolean for whether or not to add a waterplane. 

            - no return
        """

        pass

    def GenerateLandscapeFromImage(self, SourceImage,  XScale=1, YScale=1, XSubdiv=100, YSubdiv=100, Height=5, WaterPlane=True) :
        """ Generates a background landscape from an input SourceImage.

            SourceImage :   The source image to generate the landscape from. Generates height using the Red channel value. 
            XScale      :   The scale of the landscape, in maya units, along the X-Axis.
            YScale      :   The scale of the landscape, in maya units, along the Y-Axis.
            XSubdiv     :   The subdivisions of the landscape to generate along the X-Axis.
            YSubdiv     :   The subdivisions of the landscape to generate along the Y-Axis.
            Height      :   The height scalar of the landscape, landscape generates from y=0 to y=height. 
            WaterPlane  :   A boolean for whether or not to add a waterplane at half height. 

            - no return
        """

        # Information on how to create a mesh from user defined verts using openmaya MFnMesh ::
        # https://forums.autodesk.com/t5/maya-programming/create-mesh-from-list/td-p/7575371
        
        # Initialise the procedural mesh
        landscapeMesh = om.MFnMesh()

        # Define Vertices
        vertices = []
                    
        # Define Faces
        polygonConnects = []

        # Calculate X and Y scale 
        XStep = XScale/XSubdiv
        YStep = YScale/YSubdiv

        XHalf = XScale / 2
        YHalf = YScale / 2

        # Loop for each vertex in landscape, adding vertices & defining faces
        for x in range(0, SourceImage.width):
            for y in range(0, SourceImage.height):
                # Generate point
                VertHeight = (SourceImage.GetPixel(x, y)[2] / 255) * Height 
                vertices.append(om.MPoint((x * XStep) - XHalf, VertHeight, (y * YStep) - YHalf))
                if(x > 0 and y > 0):
                    # Define a face if not on first edge
                    polygonConnects.append((x-1) * SourceImage.height + (y-1))
                    polygonConnects.append((x-1) * SourceImage.height + y)
                    polygonConnects.append(x * SourceImage.height + y)
                    polygonConnects.append(x * SourceImage.height + (y-1))

        # Number of vertices in object
        polyFaces = [4] * ((SourceImage.width-1) * (SourceImage.height-1))

        # Create Mesh
        landscapeMesh.create(vertices, polyFaces, polygonConnects)

        # Create Water Plane
        if(WaterPlane):
            self.WaterPlane = cmds.polyPlane(n="Water Plane", w=XScale, h=YScale)
            cmds.move(self.WaterPlane, y=(Height/2))

        # Colour
        # create plane colour shaders
        self.WaterBlinn = cmds.shadingNode('blinn', asShader=True)
        cmds.setAttr(self.WaterBlinn + '.color', 0.3, 0.5, 1)   
        self.GroundBlinn = cmds.shadingNode('blinn', asShader=True)
        cmds.setAttr(self.GroundBlinn + '.color', 1, 1, 0.5)
        
        # assign plane colour shaders
        cmds.select(self.WaterPlane)
        #cmds.hyperShade(assign=self.WaterBlinn)
        #cmds.select(landscapeMesh.name())
        #landscapeMesh.setName("LandMesh")
        #landscapeMesh.createColorSet("LandscapeColour")
        #landscapeMesh.setColor(om.MColor(10,10,20), "LandscapeColour")
        #cmds.hyperShade(assign=self.GroundBlinn)

class MainWindow():
    """ Creates and handles the UI elements of the landscape generator program and their associated functions. """
    
    def __init__(self):
        """ Initialise the MainWindow objects, and the landscape maya ui elements."""

        # Initialise the Generator
        self.NewGenerator = Generator()

        # Test Halton Sequence
        #print(self.NewGenerator.GenerateHaltonSequence2D(50, 50, 10))

        ## Create Window ##
        
        # window creation
        self.windowID="Maya Landscape Generator"
        self.windowTitle="Landscape Generator"
        # Close if a version of this script is already open
        if cmds.window(self.windowID, exists=True):
            cmds.deleteUI(self.windowID)
        
        self.Window=cmds.window(self.windowID, title=self.windowTitle, widthHeight=(600,800))
        
        # __ START LAYOUT __ #
        form = cmds.formLayout()
        #self.tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
        #cmds.formLayout(form, edit=True, attachForm=((self.tabs, 'top', 0), (self.tabs, 'left', 0), (self.tabs, 'bottom', 0), (self.tabs, 'right', 0)))

        #
        #   Landscape UI
        #

        # UI Variables
        self.L_XSubdivisions_Val = 100
        self.L_YSubdivisions_Val = 100
        self.L_XScale_Val = 10.0
        self.L_YScale_Val = 10.0
        self.L_HeightMultiplier_Val = 0.15

        shelf4 = cmds.rowColumnLayout()#"Landscape Generator")
        self.L_TerrainType = cmds.radioButtonGrp(label='Type', labelArray2=['Heightmap','Generated'], numberOfRadioButtons=2, sl=1, cc=self.RadioButtonUpdate_L_TerrainType)
        self.L_PicFileLoadButton = cmds.textFieldButtonGrp(label='Height Map File', bl='Browse...', bc= self.FileDialogBox_L, width=400, enable=True)
        cmds.separator(style='shelf')
        self.L_XScale = cmds.floatSliderGrp(label='X Axis Scale',  field=True, min=1.0, max = 100.0, value=self.L_XScale_Val, step=0.1, dc=self.SliderUpdate_L_XScale)
        self.L_YScale = cmds.floatSliderGrp(label='Y Axis Scale',  field=True, min=1.0, max = 100.0, value=self.L_YScale_Val, step=0.1, dc=self.SliderUpdate_L_YScale)
        self.L_XSubdivisions = cmds.intSliderGrp(label='X Axis Subdivisions', field=True, min=10, max = 1000, value=self.L_XSubdivisions_Val, step=10, dc=self.SliderUpdate_L_XSubdivisions)
        self.L_YSubdivisions = cmds.intSliderGrp(label='Y Axis Subdivisions', field=True, min=10, max = 1000, value=self.L_YSubdivisions_Val, step=10, dc=self.SliderUpdate_L_YSubdivisions)
        cmds.separator(style='shelf')
        self.L_HeightMultiplier = cmds.floatSliderGrp(label='Height Multiplier', field=True, min=0.01, max = 1, value=self.L_HeightMultiplier_Val, step=0.01, dc=self.SliderUpdate_L_HeightMultiplier)
        cmds.button(label='Build Landscape', c=self.BuildLandscape, width=200)
        # Cancel Button
        cmds.button(label='cancel', command="cmds.deleteUI('%s')" % self.Window, width=200)
 
        # & Number of objects to scatter of each type selected
        

        # \\ END LAYOUT \\ #

        # show window
        cmds.showWindow(self.Window)


    #
    #   Landscape UI Functions
    #
    def RadioButtonUpdate_L_TerrainType(self, *_):
        """ Updates which UI elements are active based on the Terrain Type radio buttons. """

        # Enable/Disable UI related to each Terrain Generation Type
        if (cmds.radioButtonGrp(self.L_TerrainType, q=True, sl=True) == 2):
            cmds.textFieldButtonGrp(self.L_PicFileLoadButton, e=True, enable=False)
        else:
            cmds.textFieldButtonGrp(self.L_PicFileLoadButton, e=True, enable=True)

    def FileDialogBox_L(self, *_):
        """ Opens the dialog box to browse for a suitable image file to use as the heightmap. """
        
        pictureFilter="*.*"
        self.L_fileLocal = cmds.fileDialog2(cap='Import Height Map', ds=1, ff=pictureFilter, fm=1)
        
        # File dialogue return is different on each system...
        # https://stackoverflow.com/questions/8220108/how-do-i-check-the-operating-system-in-python
        ## START REFERENCED CODE
        from sys import platform
        if platform == "linux" or platform == "linux2":
            # linux
            print("Linux")
            self.L_fileLocal = str(self.L_fileLocal)[3:-2] 
        elif platform == "darwin":
            # OS X
            print("Didn't have mac to test on, so file dialogue might not work. Will use windows settings.")
            self.L_fileLocal = str(self.L_fileLocal)[2:-2] 
        elif platform == "win32":
            # Windows
            print("Windows")
            self.L_fileLocal = str(self.L_fileLocal)[2:-2] 
        ## END REFERENCED CODE

        print(self.L_fileLocal)

        import os.path
        if(os.path.isfile(self.L_fileLocal)):
            self.L_SourceImage = Imager(self.L_fileLocal)
            print("Imported Image")
            cmds.intSliderGrp(self.L_XSubdivisions, e=True, v=self.L_SourceImage.width)
            self.SliderUpdate_L_XSubdivisions()
            cmds.intSliderGrp(self.L_YSubdivisions, e=True, v=self.L_SourceImage.height)
            self.SliderUpdate_L_XSubdivisions()

        cmds.textFieldButtonGrp(self.L_PicFileLoadButton, tx=str(self.L_fileLocal), e=True)

    def SliderUpdate_L_XScale(self, *_):
        """ Updates the landscape X Scale variable with the value from the associated slider. """
        self.L_XScale_Val = cmds.floatSliderGrp(self.L_XScale, q=True, v=True)

    def SliderUpdate_L_YScale(self, *_):
        """ Updates the landscape Y Scale variable with the value from the associated slider. """
        self.L_YScale_Val = cmds.floatSliderGrp(self.L_YScale, q=True, v=True)

    def SliderUpdate_L_XSubdivisions(self, *_):
        """ Updates the landscape X Subdivisions variable with the value from the associated slider. """
        self.L_XSubdivisions_Val = cmds.intSliderGrp(self.L_XSubdivisions, q=True, v=True)

    def SliderUpdate_L_YSubdivisions(self, *_):
        """ Updates the landscape Y Subdivisions variable with the value from the associated slider. """
        self.L_YSubdivisions_Val = cmds.intSliderGrp(self.L_YSubdivisions, q=True, v=True)

    def SliderUpdate_L_HeightMultiplier(self, *_):
        """ Updates the landscape Height Multiplier variable with the value from the associated slider. """
        self.L_HeightMultiplier_Val = cmds.floatSliderGrp(self.L_HeightMultiplier, q=True, v=True)

    def BuildLandscape(self, *_):
        """ Setup and then call the generator build function for the Landscape.

            - no parameters, returns -1 if process fails.
        """

        # First recall all Landscape functions in case user manually typed new values.  
        self.RadioButtonUpdate_L_TerrainType()
        self.SliderUpdate_L_XScale()
        self.SliderUpdate_L_YScale()
        self.SliderUpdate_L_XSubdivisions()
        self.SliderUpdate_L_YSubdivisions()
        self.SliderUpdate_L_HeightMultiplier()

        # Switch on terrain type, from heightmap or generated
        if(cmds.radioButtonGrp(self.L_TerrainType, q=True, sl=True) == 1):
            import os.path
            if(os.path.isfile(self.L_fileLocal)):
                self.L_SourceImage = Imager(self.L_fileLocal)
                #self.SourceImage.Resize(self.XSubdivisions_Val, self.YSubdivisions_Val) =P
                #print(self.XScale_Val, self.YScale_Val)
                self.NewGenerator.GenerateLandscapeFromImage(self.L_SourceImage, XScale=self.L_XScale_Val, YScale=self.L_YScale_Val, XSubdiv=self.L_XSubdivisions_Val, YSubdiv=self.L_YSubdivisions_Val, Height=self.L_HeightMultiplier_Val)
            else:
                return -1
        else:
            # Generate the landscape using perlin noise
            return -1


# start the main program
if __name__=="__main__":
    main = MainWindow()
    


#Code:
#   Could do procedural environment generation?
#       Loading in scatter meshses with info for spacing & no. (over landscape)
#       Rules? Could fit to paths?