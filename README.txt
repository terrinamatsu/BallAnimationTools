This is a README file for CGI Tools 2021-22. 

My project contains two separate files that can each be loaded into Maya, a landscape generator {02_LandscapeGenerator_0001.py} and a wire track generator {01_WireTrackGenerator_0001.py}. 

To load each, first open Maya's script edtor (the {;} icon at the bottom right by default) and choose file, Open Scirpt and locate either script file.
Then press the execute button (single triangle) and the UI should automagically appear. 

For the landscape generator you should then be able to load an image and adjust any parameters;
For the wire track generator you can select to either generate a straight or curved wire track, and similarly adjust parameters as needed. 

When you want to generate, click the 'Build ...' button. 
If you want to close, click the cancel button. 

## Both files are also ready for PyDoc to be run on them to generate extra code documentation. 


#######################################

4 versions of the rendered animation exist, as I was not sure of requirements. 
The longer orthographic file is what I designed to, although I understand if this is not to the requirements. 

- 2 use an orthographic camera, and 2 perspective.
- 2 are within the 250 frames, and 2 are slightly longer as they repeat frames to get a full animation loop 
  as I needed to repeat part of the loop to get both the ball exit and entrance to the scene as they are on different sides of the loop,
  although all animation frames are less than the 250 frames removing repeated frames as can be seen in the Maya file.