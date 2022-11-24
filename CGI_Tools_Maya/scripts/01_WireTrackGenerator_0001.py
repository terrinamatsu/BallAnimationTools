"""
    A Maya Python script for generating straight and circular wire tracks.  

    Jacob Worgan (s5107963) @ Bournemouth University, CGI Techniques
    v1.0 14/01/2022  

    (References at start of block in which they are used)  
    (Code was directly copied, but was learned from specific tutorials for Maya Python techniques.)
    Referenced in this script:
        annooshukla, 2017. Autodesk, Create mesh from list - Autodesk Community - Maya [Online] Available at: https://forums.autodesk.com/t5/maya-programming/create-mesh-from-list/td-p/7575371 [Accessed 12 2021]
"""

import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.OpenMaya as om1
import math as maths


class Generator():
    def __init__(self):
        """ Initialises the generator (does nothing). """
        pass

    def GenerateWireTrack(self):
        """ Find a selected curve and creates a wire track along it, possibly with ball keyframed to travel along it? """
        for selection in cmds.ls(selection = True):
            print (cmds.objectType(selection))
            if ( cmds.objectType(selection) == "curve" ):
                print("Yatta!")

    def GenerateStraightWireTrack(self, length = 15, lengthSubdivisions = 36, wireRadius = 0.5, wireSubdivisions = 5, trackRadius=3.0, trackDegrees=180, wireNumber = 4, connectorNumber = 15, connectorSubdivisions = 20, wireCaps = True):
        """ Generate a straight wire track. 
        
            length                  :    The length of track to generate.
            lengthSubdivisions      :    The number of subdivisions to generate along the length of each wire.
            
            wireRadius              :    The radius of the individual wires that make up the track
            wireSubdivisions        :    The number of subdivisions around each wire
            wireNumber              :    The number of wires to generate around the track circle.
            wireCaps                :    Boolean value, whether or not to generate caps at the ends of the wire, if not generating the full circle.
            
            trackRadius             :    The radius of the track circle the wires generate around.
            trackDegrees            :    The number of degrees to generate of the track circle. 
            
            connectorNumber         :    The number of connector wires to generate evenly spaced along the wires.
            connectorSubdivisions   :    The number of subdivisions to generate for the connector wires. 

            -No return
        """
        # Information on how to create a mesh from user defined verts using openmaya MFnMesh ::
        # https://forums.autodesk.com/t5/maya-programming/create-mesh-from-list/td-p/7575371
        

        # Boundary Checks
        # Quit if there are fewer than 3 subdivisions on the wire as it wont make a complete mesh
        if((wireSubdivisions < 3) or (lengthSubdivisions < 1) or (length <= 0) or (wireRadius <= 0) or (trackRadius < 0)):
            print("ABORT: Radius or Subdivisions too low.")
            return -1
        if((wireNumber * wireRadius) > (trackRadius * maths.pi * (trackDegrees / 360.0))):
            print("ABORT: Too many wires of too wide radius, will overlap.")
            return -1 #wireRadius = (trackRadius * maths.pi * (trackDegrees / 360.0)) / wireNumber

        mesh = om.MFnMesh()
        
        # Define Vertices
        vertices = []
                    
        # Define Face Connects
        polygonConnects = []
        
        # Define Face Vertex Nos
        polyFaces = []

        # Create each wire in track line
        TrackAngle = trackDegrees / (wireNumber - 1)
        for i in range(0, wireNumber):
            vertNo = len(vertices)
        
            angle = TrackAngle * i
            angle2 = maths.radians(angle + (0.5 * (360 - trackDegrees)) - 90)
            currentRailXY = (trackRadius * maths.cos(angle2), -trackRadius * maths.sin(angle2))

            subdivisionAngle = 360.0/wireSubdivisions
            trackDivisionLength = (length) / lengthSubdivisions
            for j in range(0, lengthSubdivisions + 1):
                for i in range(0, wireSubdivisions  + 1):
                    # Check if this is the last point in the wire going around
                    if(i == (wireSubdivisions)):
                        # If this is the last point, reuse the first point
                        if(j > 0 and i > 0):
                            polygonConnects.append((j-1) * (wireSubdivisions) + (i-1) + vertNo)
                            polygonConnects.append((j-1) * (wireSubdivisions) + 0 + vertNo)
                            polygonConnects.append(j  * (wireSubdivisions) + 0 + vertNo)
                            polygonConnects.append(j * (wireSubdivisions) + (i-1) + vertNo)
                            
                            polyFaces.append(4)
                    else:
                        # If not the last point, make a new point
                        x = (wireRadius * maths.cos(maths.radians(subdivisionAngle * i))) #radians(circleangle  * j)
                        y = wireRadius * maths.sin(maths.radians(subdivisionAngle * i))
                        z = trackDivisionLength * j #+ (wireRadius * maths.cos(maths.radians(subdivisionAngle * i)))

                        # Extra rotation to the wire   
                        #x, y, z = self.RotateXYZ(XYZ=(x, y, z), RotationAxis="X", Rotation=rotation[0])
                        #x, y, z = self.RotateXYZ(XYZ=(x, y, z), RotationAxis="X", Rotation=rotation[1])
                        #x, y, z = self.RotateXYZ(XYZ=(x, y, z), RotationAxis="X", Rotation=rotation[2])
 
                        # Append point
                        #vertices.append(om.MPoint(x, y, z))
                        vertices.append(om.MPoint(x + currentRailXY[0], y + currentRailXY[1], z))

                        # Connect the points to polygon
                        if(j > 0 and i > 0):
                            polygonConnects.append((j-1) * (wireSubdivisions) + (i-1) + vertNo)
                            polygonConnects.append((j-1) * (wireSubdivisions) + i + vertNo)
                            polygonConnects.append(j  * (wireSubdivisions) + i + vertNo)
                            polygonConnects.append(j * (wireSubdivisions) + (i-1) + vertNo)
                            
                            polyFaces.append(4)

            # Add Wire Caps
            if(wireCaps):
                for i in range(wireSubdivisions - 1, -1, -1):
                    polygonConnects.append(i + vertNo)
                for i in range(wireSubdivisions - 1, -1, -1):
                    polygonConnects.append(len(vertices) - i - 1)
                polyFaces.append(wireSubdivisions)
                polyFaces.append(wireSubdivisions)


        # Create each Wire Track Connector
        connectorDistance = length / connectorNumber
        for i in range(0, connectorNumber + 1):
            connectorCentre = (0, 0, connectorDistance * i)

            self.GenSingleWireArc(vertices, polygonConnects, polyFaces, trackRadius +(2* wireRadius), connectorSubdivisions, trackDegrees, centre=connectorCentre, wireRadius=wireRadius, wireSubdivisions=wireSubdivisions, wireCaps=True, flipXY=True, rotation=(0,0,0))


        # Create Mesh
        mesh.create(vertices, polyFaces, polygonConnects)

    def RotateXYZ(self, XYZ = (0,0,0), RotationAxis="Y", Rotation = 0):
        """ Rotate an XYZ about an axis, either X, Y, or Z, of a given rotation. 

            XYZ             :   The point to rotate.
            RotationAxis    :   The axis about which to rotate (char, either X Y or Z)
            Rotation        :   The amount, in degrees, to rotate.

            - Returns the X Y Z. 
        """

        theta = maths.radians(Rotation)

        if(RotationAxis == "Y"):
            X = XYZ[0]
            Y = XYZ[1] * maths.cos(theta) - XYZ[2] * maths.sin(theta)
            Z = XYZ[1] * maths.sin(theta) + XYZ[2] * maths.cos(theta)
        elif(RotationAxis == "X"):
            X = XYZ[0] * maths.cos(theta) + XYZ[2] * maths.sin(theta)
            Y = XYZ[1] 
            Z = - XYZ[0] * maths.sin(theta) + XYZ[2] * maths.cos(theta)
        elif(RotationAxis == "Z"):
            X = XYZ[0] * maths.cos(theta) - XYZ[1] * maths.sin(theta)
            Y = XYZ[0] * maths.sin(theta) + XYZ[1] * maths.cos(theta)
            Z = XYZ[2] 

        return X, Y, Z

    def GenSingleWireArc(self, vertices, polygonConnects, polyFaces, circleRadius, circleSubdivisions, degreesToGenerate, centre=(0,0,0), wireRadius = 0.5, wireSubdivisions = 5, wireCaps = True, flipXY = False, rotation = (0,0,0)):
        """ Function to generate a single circular wire segment.
            
            vertices            :    Reference to the ongoing list of vertices
            polygonConnects     :    Reference to the ongoing list of polygonConnects
            polyFaces           :    Reference to the ongoing list of polyFaces
            
            circleRadius        :    The radius of the circle the wire is to be generated on.
            circleSubdivisions  :    The number of polygons that will be generated along the circle for each wire.
            degreesToGenerate   :    The degrees of the circle that will be generated, if the user only wants part of a circle (but defaults to the full circle of 360 degrees).

            centre              :    The centre point of the wire, so the wire can be generated in different locations.
            rotation            :    A rotation to add to the generated wire arc. 
            flipXY              :    Boolean, if true to flip the X and Y values of the arc so it is vertically oriented. 

            wireRadius          :    The radius of the 4 individual wires that make up the track
            wireSubdivisions    :    The number of subdivisions 
            wireCaps            :    Boolean value, whether or not to generate caps at the ends of the wire, if not generating the full circle.

            -No return
        """
        
        vertNo = len(vertices)
        
        subdivisionAngle = 360.0/wireSubdivisions
        circleAngle = (degreesToGenerate) / circleSubdivisions
        for j in range(0, circleSubdivisions + 1):
            for i in range(0, wireSubdivisions  + 1):
                # Check if this is the last point in the wire going around
                if(i == (wireSubdivisions)):
                    # If this is the last point, reuse the first point
                    if(j > 0 and i > 0):
                        polygonConnects.append((j-1) * (wireSubdivisions) + (i-1) + vertNo)
                        polygonConnects.append((j-1) * (wireSubdivisions) + 0 + vertNo)
                        polygonConnects.append(j  * (wireSubdivisions) + 0 + vertNo)
                        polygonConnects.append(j * (wireSubdivisions) + (i-1) + vertNo)
                        
                        polyFaces.append(4)
                else:
                    # If not the last point, make a new point
                    angle = circleAngle * j
                    angle2 = maths.radians(angle + (0.5 * (360 - degreesToGenerate)) - 90)
                    # Might want to look at taurus generation as it might simplify this a bit...
                    # X = position around circle + wire point * wire ring rotation along circle
                    x = circleRadius * maths.cos(angle2) + (wireRadius * maths.cos(maths.radians(subdivisionAngle * i))) * maths.cos(angle2) #radians(circleangle  * j)
                    y = wireRadius * maths.sin(maths.radians(subdivisionAngle * i))
                    z = circleRadius * maths.sin(angle2) + (wireRadius * maths.cos(maths.radians(subdivisionAngle * i))) * maths.sin(angle2)
                    
                    if(flipXY):
                        y, z = -z, y
                        
                    x, y, z = self.RotateXYZ(XYZ=(x, y, z), RotationAxis="X", Rotation=rotation[0])
                    x, y, z = self.RotateXYZ(XYZ=(x, y, z), RotationAxis="X", Rotation=rotation[1])
                    x, y, z = self.RotateXYZ(XYZ=(x, y, z), RotationAxis="X", Rotation=rotation[2])
                    

                    #z += 

                    vertices.append(om.MPoint(x + centre[0], y + centre[1], z + centre[2]))
                    if(j > 0 and i > 0):
                        polygonConnects.append((j-1) * (wireSubdivisions) + (i-1) + vertNo)
                        polygonConnects.append((j-1) * (wireSubdivisions) + i + vertNo)
                        polygonConnects.append(j  * (wireSubdivisions) + i + vertNo)
                        polygonConnects.append(j * (wireSubdivisions) + (i-1) + vertNo)
                        
                        polyFaces.append(4)

        # Number of vertices in object
        #polyFaces = [4] * (int(len(polygonConnects)/4))#(((wireSubdivisions) * (circleSubdivisions - 1)) + 1)

        # Add Wire Caps
        if(wireCaps and circleAngle < 360):
            for i in range(wireSubdivisions - 1, -1, -1):
                polygonConnects.append(i + vertNo)
            for i in range(wireSubdivisions - 1, -1, -1):
                polygonConnects.append(len(vertices) - i - 1)
            polyFaces.append(wireSubdivisions)
            polyFaces.append(wireSubdivisions)


    def GenerateWireTrack_Circular(self, circleRadius = 15, circleSubdivisions = 36, degreesToGenerate = 15, wireRadius = 0.5, wireSubdivisions = 5, trackRadius=3.0, trackDegrees=180, wireNumber = 4, connectorNumber = 15, connectorSubdivisions = 20, wireCaps = True):
        """
            Function to generate a circular or segment wire track.
            
            circleRadius        :    The radius of the circle the wire is to be generated on.
            circleSubdivisions  :    The number of polygons that will be generated along the circle for each wire.
            degreesToGenerate   :    The degrees of the circle that will be generated, if the user only wants part of a circle (but defaults to the full circle of 360 degrees).
            
            wireRadius              :    The radius of the individual wires that make up the track
            wireSubdivisions        :    The number of subdivisions around each wire
            wireNumber              :    The number of wires to generate around the track circle.
            wireCaps                :    Boolean value, whether or not to generate caps at the ends of the wire, if not generating the full circle.
            
            trackRadius             :    The radius of the track circle the wires generate around.
            trackDegrees            :    The number of degrees to generate of the track circle. 
            
            connectorNumber         :    The number of connector wires to generate evenly spaced along the wires.
            connectorSubdivisions   :    The number of subdivisions to generate for the connector wires. 

            - no return
        """
        
        # Information on how to create a mesh from user defined verts using openmaya MFnMesh ::
        # https://forums.autodesk.com/t5/maya-programming/create-mesh-from-list/td-p/7575371
        

        # Boundary Checks
        # Quit if there are fewer than 3 subdivisions on the wire as it wont make a complete mesh
        if((wireSubdivisions < 3) or (circleSubdivisions < 2) or (circleRadius <= 0) or (wireRadius <= 0) or (trackRadius < 0)):
            print("ABORT: Radius or Subdivisions too low.")
            return -1
        if((wireNumber * wireRadius) > (trackRadius * maths.pi * (trackDegrees / 360.0))):
            print("ABORT: Too many wires of too wide radius, will overlap.")
            return -1 #wireRadius = (trackRadius * maths.pi * (trackDegrees / 360.0)) / wireNumber

        mesh = om.MFnMesh()
        
        # Define Vertices
        vertices = []
                    
        # Define Face Connects
        polygonConnects = []
        
        # Define Face Vertex Nos
        polyFaces = []

        # Create each wire in track circle
        TrackAngle = trackDegrees / (wireNumber - 1)
        for i in range(0, wireNumber):
            angle = TrackAngle * i
            angle2 = maths.radians(angle + (0.5 * (360 - trackDegrees)) - 90)
            currentRailXY = (trackRadius * maths.cos(angle2)  + circleRadius, -trackRadius * maths.sin(angle2))
            self.GenSingleWireArc(vertices, polygonConnects, polyFaces, currentRailXY[0], circleSubdivisions, degreesToGenerate, wireRadius=wireRadius, wireSubdivisions=wireSubdivisions, centre=(0,currentRailXY[1],0))
        
        # Create each Wire Track Connector
        connectorAngle = degreesToGenerate / connectorNumber
        for i in range(0, connectorNumber + 1):
            # Add in rotation to angle gap down z-axis
            angle = connectorAngle * i
            angle2 = angle + (0.5 * (360 - degreesToGenerate)) - 90
            angle2rad = maths.radians(angle2)

            connectorCentre = (circleRadius * maths.cos(angle2rad), 0, circleRadius * maths.sin(angle2rad))

            angle3 = 360 - angle2
            self.GenSingleWireArc(vertices, polygonConnects, polyFaces, trackRadius +(2* wireRadius), connectorSubdivisions, trackDegrees, centre=connectorCentre, wireRadius=wireRadius, wireSubdivisions=wireSubdivisions, wireCaps=True, flipXY=True, rotation=(0,angle3,0))
        
       
        '''print(len(vertices))
        print(len(polyFaces))
        print(len(polygonConnects))
        
        print(vertices)
        print(polyFaces)
        print(polygonConnects)'''

        # Create Mesh
        mesh.create(vertices, polyFaces, polygonConnects)


class MainWindow():
    """ Creates and handles the UI elements of the stair generator program and their associated functions. """
    
    def __init__(self):
        ''' Initialises the MainWindow objects, as well as the Wire Track Generator maya ui elements. '''

        self.NewGenerator = Generator()
        
        ## Create Window ##
        
        # window creation
        self.windowID="Maya Wire Track Generator"
        self.windowTitle="Wire Track Generator"
        if cmds.window(self.windowID, exists=True):
            cmds.deleteUI(self.windowID)
        
        self.Window=cmds.window(self.windowID, title=self.windowTitle, widthHeight=(600,2000))
        
        # __ START LAYOUT __ #
        #form = cmds.formLayout()
        #self.tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
        #cmds.formLayout(form, edit=True, attachForm=((self.tabs, 'top', 0), (self.tabs, 'left', 0), (self.tabs, 'bottom', 0), (self.tabs, 'right', 0)))

        #
        #   Circle Wire Track UI
        #

        # UI Variables
        self.CW_TrackLength_val = 10.0
        self.CW_TrackSubdivisions_val = 2
        self.CW_WireRadius_Val = 0.5
        self.CW_WireDivisions_Val = 5
        self.CW_CircleRadius_val = 15.0
        self.CW_CircleCompletionAngle_val = 360.0
        self.CW_CircleDivisions_val = 36
        self.CW_TrackRadius_val = 3.0
        self.CW_TrackCompletionAngle_val = 180.0
        self.CW_WireNumber_Val = 4
        self.CW_ConnectorNumber_val = 15
        self.CW_ConnectorDivisions_val = 15

        shelf3 = cmds.rowColumnLayout()#"Circle Wire Track Generator")
        self.CW_TrackType = cmds.radioButtonGrp(label='Track Type', labelArray2=['Circular','Straight'], numberOfRadioButtons=2, sl=1, cc=self.RadioButtonUpdate_CW_TrackType)
        self.CW_TrackLength = cmds.floatSliderGrp(label='Track Length',  field=True, min=0.1, max = 1000.0, value=self.CW_TrackLength_val, step=0.1, dc=self.SliderUpdate_CW_CircleRadius)
        self.CW_TrackSubdivisions = cmds.intSliderGrp(label='Track Subdivisions', field=True, min=5, max = 360, value=self.CW_TrackSubdivisions_val, step=1, dc=self.SliderUpdate_CW_CircleDivisions)
        self.CW_WireRadius = cmds.floatSliderGrp(label='Wire Radius',  field=True, min=0.1, max = 90.0, value=self.CW_WireRadius_Val, step=0.1, dc=self.SliderUpdate_CW_WireRadius)
        self.CW_WireDivisions = cmds.intSliderGrp(label='Wire Subdivisions', field=True, min=3, max = 50, value=self.CW_WireDivisions_Val, step=1, dc=self.SliderUpdate_CW_WireDivisions)
        self.CW_CircleRadius = cmds.floatSliderGrp(label='Circle Radius',  field=True, min=0.1, max = 90.0, value=self.CW_CircleRadius_val, step=0.1, dc=self.SliderUpdate_CW_CircleRadius)
        self.CW_CircleCompletionAngle = cmds.floatSliderGrp(label='Circle Completion Angle',  field=True, min=5.0, max = 360.0, value=self.CW_CircleCompletionAngle_val, step=0.1, dc=self.SliderUpdate_CW_CircleCompletionAngle)
        self.CW_CircleDivisions = cmds.intSliderGrp(label='Circle Subdivisions', field=True, min=5, max = 360, value=self.CW_CircleDivisions_val, step=1, dc=self.SliderUpdate_CW_CircleDivisions)
        self.CW_TrackRadius = cmds.floatSliderGrp(label='Track Circle Radius',  field=True, min=0.1, max = 90.0, value=self.CW_TrackRadius_val, step=0.1, dc=self.SliderUpdate_CW_TrackRadius)
        self.CW_TrackCompletionAngle = cmds.floatSliderGrp(label='Track Circle Completion Angle',  field=True, min=5.0, max = 360.0, value=self.CW_TrackCompletionAngle_val, step=0.1, dc=self.SliderUpdate_CW_TrackCompletionAngle)
        self.CW_WireNumber = cmds.intSliderGrp(label='No of Wires', field=True, min=1, max = 50, value=self.CW_WireNumber_Val, step=1, dc=self.SliderUpdate_CW_WireNumber)
        self.CW_ConnectorNumber = cmds.intSliderGrp(label='No of Connectors', field=True, min=1, max = 50, value=self.CW_ConnectorNumber_val, step=1, dc=self.SliderUpdate_CW_ConnectorNumber)
        self.CW_ConnectorDivisions = cmds.intSliderGrp(label='Connector Subdivisions', field=True, min=3, max = 50, value=self.CW_ConnectorDivisions_val, step=1, dc=self.SliderUpdate_CW_ConnectorDivisions)
        cmds.button(label='Build Circular Wire Track', c= self.BuildCircularWireTrack, width=200)
        # Cancel Button
        cmds.button(label='cancel', command="cmds.deleteUI('%s')" % self.Window, width=200)

        self.RadioButtonUpdate_CW_TrackType()

        

        # \\ END LAYOUT \\ #

        # show window
        cmds.showWindow(self.Window)
        
    #
    #   Circle Wire Track UI Functions
    #
    def RadioButtonUpdate_CW_TrackType(self, *_):
        """ Updates which UI elements are active based on the Track Type radio buttons. """

        # Enable/Disable UI related to each Terrain Generation Type
        if (cmds.radioButtonGrp(self.CW_TrackType, q=True, sl=True) == 1):
            # Disable Straight Track UI
            cmds.floatSliderGrp(self.CW_TrackLength, e=True, enable=False)
            cmds.intSliderGrp(self.CW_TrackSubdivisions, e=True, enable=False)
            # Enable Circle Track UI
            cmds.floatSliderGrp(self.CW_CircleRadius, e=True, enable=True)
            cmds.floatSliderGrp(self.CW_CircleCompletionAngle, e=True, enable=True)
            cmds.intSliderGrp(self.CW_CircleDivisions, e=True, enable=True)
        else:
            # Enable Straight Track UI
            cmds.floatSliderGrp(self.CW_TrackLength, e=True, enable=True)
            cmds.intSliderGrp(self.CW_TrackSubdivisions, e=True, enable=True)
            # Disable Circle Track UI
            cmds.floatSliderGrp(self.CW_CircleRadius, e=True, enable=False)
            cmds.floatSliderGrp(self.CW_CircleCompletionAngle, e=True, enable=False)
            cmds.intSliderGrp(self.CW_CircleDivisions, e=True, enable=False)


    def SliderUpdate_CW_WireRadius(self, *_):
        """ Updates the Circle Wire Wire Radius variable with the value from the associated slider. """
        self.CW_WireRadius_Val = cmds.floatSliderGrp(self.CW_WireRadius, q=True, v=True)

    def SliderUpdate_CW_WireDivisions(self, *_):
        """ Updates the Circle Wire Wire Subdivisions variable with the value from the associated slider. """
        self.CW_WireDivisions_Val = cmds.intSliderGrp(self.CW_WireDivisions, q=True, v=True)

    def SliderUpdate_CW_TrackLength(self, *_):
        """ Updates the Circle Wire Straight Track Length variable with the value from the associated slider. """
        self.CW_TrackLength_val = cmds.floatSliderGrp(self.CW_TrackLength, q=True, v=True)

    def SliderUpdate_CW_TrackSubdivisions(self, *_):
        """ Updates the Circle Wire Straight Track Subdivisions variable with the value from the associated slider. """
        self.CW_TrackSubdivisions_val = cmds.intSliderGrp(self.CW_TrackSubdivisions, q=True, v=True)

    def SliderUpdate_CW_CircleRadius(self, *_):
        """ Updates the Circle Wire Circle Radius variable with the value from the associated slider. """
        self.CW_CircleRadius_val = cmds.floatSliderGrp(self.CW_CircleRadius, q=True, v=True)

    def SliderUpdate_CW_CircleCompletionAngle(self, *_):
        """ Updates the Circle Wire Circle Completion Angle variable with the value from the associated slider. """
        self.CW_CircleCompletionAngle_val = cmds.floatSliderGrp(self.CW_CircleCompletionAngle, q=True, v=True)

    def SliderUpdate_CW_CircleDivisions(self, *_):
        """ Updates the Circle Wire Circle Subdivisions variable with the value from the associated slider. """
        self.CW_CircleDivisions_val = cmds.intSliderGrp(self.CW_CircleDivisions, q=True, v=True)

    def SliderUpdate_CW_TrackRadius(self, *_):
        """ Updates the Circle Wire Track Radius variable with the value from the associated slider. """
        self.CW_TrackRadius_val = cmds.floatSliderGrp(self.CW_TrackRadius, q=True, v=True)

    def SliderUpdate_CW_TrackCompletionAngle(self, *_):
        """ Updates the Circle Wire Track Completion Angle with the value from the associated slider. """
        self.CW_TrackCompletionAngle_val = cmds.floatSliderGrp(self.CW_TrackCompletionAngle, q=True, v=True)

    def SliderUpdate_CW_WireNumber(self, *_):
        """ Updates the Circle Wire Number of Wires variable with the value from the associated slider. """
        self.CW_WireNumber_Val = cmds.intSliderGrp(self.CW_WireNumber, q=True, v=True)

    def SliderUpdate_CW_ConnectorNumber(self, *_):
        """ Updates the Circle Wire Number of Connectors variable with the value from the associated slider. """
        self.CW_ConnectorNumber_val = cmds.intSliderGrp(self.CW_ConnectorNumber, q=True, v=True)

    def SliderUpdate_CW_ConnectorDivisions(self, *_):
        """ Updates the Circle Wire Connector Subdivisions variable with the value from the associated slider. """
        self.CW_ConnectorDivisions_val = cmds.intSliderGrp(self.CW_ConnectorDivisions, q=True, v=True)

    def BuildCircularWireTrack(self, *_):
        """ Starts the building of the circular wire track. """
        # Recall all CW functions in case user has manually typed new values (which doesn't call the update functions...)
        self.SliderUpdate_CW_WireRadius()
        self.SliderUpdate_CW_WireDivisions()
        self.SliderUpdate_CW_TrackLength()
        self.SliderUpdate_CW_TrackSubdivisions()
        self.SliderUpdate_CW_CircleRadius()
        self.SliderUpdate_CW_CircleCompletionAngle()
        self.SliderUpdate_CW_CircleDivisions()
        self.SliderUpdate_CW_TrackRadius()
        self.SliderUpdate_CW_TrackCompletionAngle()
        self.SliderUpdate_CW_WireNumber()
        self.SliderUpdate_CW_ConnectorNumber()
        self.SliderUpdate_CW_ConnectorDivisions()

        # Then call the generator
        if (cmds.radioButtonGrp(self.CW_TrackType, q=True, sl=True) == 1):
            self.NewGenerator.GenerateWireTrack_Circular(circleRadius=self.CW_CircleRadius_val, circleSubdivisions=self.CW_CircleDivisions_val, degreesToGenerate=self.CW_CircleCompletionAngle_val, wireRadius=self.CW_WireRadius_Val, wireSubdivisions=self.CW_WireDivisions_Val, connectorNumber=self.CW_ConnectorNumber_val, trackRadius=self.CW_TrackRadius_val, trackDegrees=self.CW_TrackCompletionAngle_val, wireNumber=self.CW_WireNumber_Val, connectorSubdivisions=self.CW_ConnectorDivisions_val)
        else:
            self.NewGenerator.GenerateStraightWireTrack(length=self.CW_TrackLength_val, lengthSubdivisions=self.CW_TrackSubdivisions_val, wireRadius=self.CW_WireRadius_Val, wireSubdivisions=self.CW_WireDivisions_Val, connectorNumber=self.CW_ConnectorNumber_val, trackRadius=self.CW_TrackRadius_val, trackDegrees=self.CW_TrackCompletionAngle_val, wireNumber=self.CW_WireNumber_Val, connectorSubdivisions=self.CW_ConnectorDivisions_val)
            
# start the main program
if __name__=="__main__":
    main = MainWindow()