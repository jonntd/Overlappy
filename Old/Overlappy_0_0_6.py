####################################################################################################################

# https://www.highend3d.com/maya/script/overlappy-for-maya-105076     <<<     main link to download script and bug report
# https://www.highend3d.com/users/geneugene
# https://www.artstation.com/geneugene
# https://vk.com/geneugene3d

####################################################################################################################
""" Information
This is a simple tool for add some overlaps. Baking of translation and rotation is divided by 2 differrent steps
 
Based on:
	- https://vimeo.com/196234485
	- https://www.youtube.com/watch?v=BTBZgLYO6eo&feature=youtu.be&t=490

Features:
	- nParticle based
	- animation baking to layers for every selected object
	- work with cycles in (60 fps baking)

How to use:
	- For install just open script in script editor and press button "Save Script to Shelf"
	- Selected objects must have keyed channels ( Translation and Rotation )
	
	- RUN TRANSLATION BAKING: you need select 1 or more objects
	
	- Run ROTATION BAKING: you need select 2 or more objects. Last selected object will be the target for the previous one
	
	- RESET ALL: clears all values in script window
	
	- DELETE ALL LAYERS: only for "OVERLAPPY" layer delete and everything inside it. Dont forget rename and pull out layers with the animation that you need
	
	- Looping animation: 
		- For baking clear loops you need use 60 fps. On another fps you script will bake incorrect loops
		- Strong recomended to use animation minimum with 1 phase before and after animation cycle. Simple way to do it just use pre and post infinity with "Cycle" option
		- Or you can bake animation with off cycle checkbox into 3 or more loops, then move animation to your main animation range and delete remains
		
	- Aim reverse: for reorientation aim for rotation script. May be useful when rotation sim bake animation with incorrect rotations

Known problems:
	- In Maya 2019 animation caching can break creating constraints by script
	- After simulation script leaves attribute "blendParent1" on object
 
p.s. This is my first script on maya python, so please report bugs and leave some comments, if you have ideas to modify the code
"""
####################################################################################################################
""" Version history

v 0.0.0
	- created Translation simulation script
	- added baking animation to layers
v 0.0.1
	- created ui and test
	- added layouts and descriptions
v 0.0.2
	- added Rotation simulation script
	- fixed symbols issue (":" and "|" will replaced by "_" symbol)
	- few text corrections
	- added instruction (rus)
v 0.0.3
	- can use locked translations and rotations
	- added checkbox reverse aim axis Y ( 1, -1 )
	- combined 2 checkboxes to 1 for loop animation
v 0.0.4
	- replaced all descriptions and comments to english
	- changed font size of buttons
	- rewrite main instruction
v 0.0.5
	- separated reset for TRANSLATION and ROTATION variables and added CHECKBOX reset
	- full reconstructed UI
	- rewrited some script blocks
	- added new test checkboxes for future features
	- added "Set cycle infinity" checkbox for cycle/constant infinity
v 0.0.6
	- removed "Set cycle infinity" checkbox (combined with "Looping animation")
	- fixed RESET CHECKBOX button event
	- fixed all reset events debug log
	- small text/descriptions fixes
	- set new default values
	- added new variables for UI and other
"""
####################################################################################################################
""" TO DO
	- !!! fix chain baking (when baking a chain of objects, some of the last objects look incorrect)
	- add progress bar
	- add switch checkbox to 60 fps when baking loops
	- add checkbox for rebaking animation to exists layer
	- add button for merge all layers created by script
	- additive layer baking
	- hidden low priority checkboxes
	- add debug log "object not selected" to translation baking
"""
####################################################################################################################
import maya.cmds as cmds
####################################################################################################################

def setCheckboxValues():
	global cycle; cycle = False # Animation cycle check
	global cycleInfinity; cycleInfinity = False
	global aimVectorReverse; aimVectorReverse = False # Reverse aim vector

def setTranslationValues():
	global goalSmooth; goalSmooth = 1.5 # Translation goal smooth
	global timeScale; timeScale = 0.3 # Translation time scale
	global goalW; goalW = 0.5 # Translation goal weight

def setRotationValues():
	global goalSmoothRot; goalSmoothRot = 1.5 # Rotation goal smooth
	global timeScaleRot; timeScaleRot = 0.3 # Rotation time scale
	global goalWRot; goalWRot = 0.5 # Rotation goal weight

def setOtherValues():

	global pRad; pRad = 0.253 # Radius of nParticle mesh
	global pShape; pShape = 4 # Type of nParticle mesh
	
	global minLoopScale; minLoopScale = -1 # Start simulation time
	global maxLoopScale; maxLoopScale = 2 # End simulation time
	
	global slWidth; slWidth = 300 # Slider width
	global slHeight; slHeight = 30 # Slider height
	global buttonHeight; buttonHeight = 30 # Button height
	
	global Bg1; Bg1 = 0.85
	global Bg2; Bg2 = 0.3
	
	global rW1; rW1 = 163
	global rW2; rW2 = 4
	global rW3; rW3 = 163
	
	global frameColor1; frameColor1 = ( 0.1, 0.1, 0.1 )
	global frameColor2; frameColor2 = ( 1, 0.4, 0.4 )
	
	global resValColor1; resValColor1 = ( 0.6, 1, 0.45 )
	global resValColor2; resValColor2 = ( 0.6, 1, 0.45 )
	global resCheckColor1; resCheckColor1 = ( 0.6, 1, 0.45 )
	global resAllColor1; resAllColor1 = ( 0.8, 1, 0.2 )
	
	global simColor1; simColor1 = ( 0.3, 0.85, 1 )
	global simColor2; simColor2 = ( 0.3, 0.85, 1 )
	
	global deleteColor1; deleteColor1 = ( 0.9, 0.5, 0.3 )
	
	global endColor1; endColor1 = ( 0.9, 0.5, 0.5 )
	
	global linkColor1; linkColor1 = ( 0.9, 0.55, 0.55 )
	global linkColor2; linkColor2 = ( 0.9, 0.4, 0.4 )
	
def setText():
	mainScriptName = "Overlappy "
	mainScriptVersion = "v0.0.6"
	
	posScriptLabelTAB = ""
	posScriptName = "TRANSLATION VALUES"
	posScriptVersion = ""
	
	rotScriptLabelTAB = ""
	rotScriptName = "ROTATION VALUES"
	rotScriptVersion = ""

	global windowName; windowName = mainScriptName + mainScriptVersion # Main window name ( Overlappy v0.0.0 )
	global posScriptLabel; posScriptLabel = posScriptLabelTAB + posScriptName + posScriptVersion
	global rotScriptLabel; rotScriptLabel = rotScriptLabelTAB + rotScriptName + rotScriptVersion
	
	global goalSmoothAnn; goalSmoothAnn = " Goal smooth from 0.5 to 4 "
	global timeScaleAnn; timeScaleAnn = " Time scale from 0.15 to 0.4 "
	global goalWeightAnn; goalWeightAnn = " Goal weight 0.3 to 0.7 "

	#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

	global s1Max; s1Max = 4.0 # slider1 max smooth slider
	global s2Max; s2Max = 0.5 # slider2 max scale slider
	global s3Max; s3Max = 1.0 # slider1 max weight slider

	global s4Max; s4Max = s1Max # slider4 max smooth slider
	global s5Max; s5Max = s2Max # slider5 max scale slider
	global s6Max; s6Max = s3Max # slider6 max weight slider

#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

def setCheckboxSliders():
	cmds.checkBox( "checkCycle", e=True, v=cycle )
	cmds.checkBox( "checkVectorReverse", e=True, v=aimVectorReverse )
	cmds.checkBox( "checkInfinity", e=True, v=cycleInfinity )

def setTranslationSliders():
	cmds.floatSliderGrp( "s1", e=True, f=True, min=0.0, max=s1Max, fmx=10, v=goalSmooth )
	cmds.floatSliderGrp( "s2", e=True, f=True, min=0.0, max=s2Max, fmx=10, v=timeScale )
	cmds.floatSliderGrp( "s3", e=True, f=True, min=0.0, max=s3Max, v=goalW )

def setRotationSliders():
	cmds.floatSliderGrp( "s4", e=True, f=True, min=0.0, max=s4Max, fmx=10, v=goalSmoothRot )
	cmds.floatSliderGrp( "s5", e=True, f=True, min=0.0, max=s5Max, fmx=10, v=timeScaleRot )
	cmds.floatSliderGrp( "s6", e=True, f=True, min=0.0, max=s6Max, v=goalWRot )

#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

def resetCheckbox():
	setCheckboxValues()
	setCheckboxSliders()
	print "\n||| OVERLAPPY RESET OPTIONS |||\n"

def resetTranslation():
	setTranslationValues()
	setTranslationSliders()
	print "\n||| OVERLAPPY RESET TRANSLATION |||\n"

def resetRotation():
	setRotationValues()
	setRotationSliders()
	print "\n||| OVERLAPPY RESET ROTATION |||\n"

def resetAllButton():
	setCheckboxValues()
	setTranslationValues()
	setRotationValues()
	setCheckboxSliders()
	setTranslationSliders()
	setRotationSliders()
	print "\n||| OVERLAPPY RESET ALL |||\n"

def resetAll():
	setCheckboxValues()
	setTranslationValues()
	setRotationValues()
	setOtherValues()
	setText()
	print "\n||| OVERLAPPY RESET ALL |||\n"

####################################################################################################################

def FuncCheckCycle():
	cycle = cmds.checkBox( "checkCycle", q=True, v=True )
	print "Cycle animation =", cycle
	return cycle

def FuncCheckVector():
	aimVectorReverse = cmds.checkBox( "checkVectorReverse", q=True, v=True )
	print "Y VECTOR REVERSE =", aimVectorReverse
	return aimVectorReverse

def FuncCheckCycleInfinity():
	cycleInfinity = cmds.checkBox( "checkInfinity", q=True, v=True )
	print "Infinity = ", cycleInfinity
	return cycleInfinity

####################################################################################################################

def printSmoothV():
	goalSmooth = cmds.floatSliderGrp( "s1", q=True, v=True )
	print "Translation smooth =", goalSmooth
	return goalSmooth
	
def printScaleV():
	timeScale = cmds.floatSliderGrp( "s2", q=True, v=True )
	print "Translation scale =", timeScale
	return timeScale
	
def printWeightV():
	goalW = cmds.floatSliderGrp( "s3", q=True, v=True )
	print "Translation weight =", goalW
	return goalW

#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

def printRotSmoothV():
	goalSmoothRot = cmds.floatSliderGrp ("s4", q=True, v=True)
	print "Rotation smooth =", goalSmoothRot
	return goalSmoothRot
	
def printRotScaleV():
	timeScaleRot = cmds.floatSliderGrp ("s5", q=True, v=True)
	print "Rotation scale =", timeScaleRot
	return timeScaleRot
	
def printRotWeightV():
	goalWRot = cmds.floatSliderGrp ("s6", q=True, v=True)
	print "Rotation weight =", goalWRot
	return goalWRot

####################################################################################################################

def uiCreation():
	
	if cmds.window( "main", exists = True ):
		cmds.deleteUI( "main" )

	overUI = cmds.window( "main", title=windowName, mxb=False, s=False )
	cmds.window( "main", e=True, wh=( 10, 10 ) , rtf=True )
	
	cmds.columnLayout( 'layout1', rs=4, adj=True )
	
	#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
	
	cmds.frameLayout( 'testestes', l=posScriptLabel, cll=1, bgc=frameColor1, p="main", sbm="Translation script", cc=('cmds.window( "main", e=True, h=10, rtf=True )') )
	
	cmds.floatSliderGrp( "s1", l='Smooth', f=True, min=0.0, max=s1Max, fmx=10, 
	v=goalSmooth, cc=('goalSmooth=printSmoothV()'), pre=2, w=slWidth, ann=goalSmoothAnn, cal=(1, "left"), cw3=( 45, 50, 10 )  )
	
	cmds.floatSliderGrp( "s2", l='Scale', f=True, min=0.0, max=s2Max, fmx=10, 
	v=timeScale, cc=('timeScale=printScaleV()'), pre=2, w=slWidth, ann=timeScaleAnn, cal=(1, "left"), cw3=( 45, 50, 10 )  )
	
	cmds.floatSliderGrp( "s3", l='Weight', f=True, min=0.0, max=s3Max, 
	v=goalW, cc=('goalW=printWeightV()'), pre=2, w=slWidth, ann=goalWeightAnn, cal=(1, "left"), cw3=( 45, 50, 10 )  )
	
	cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[ (1, rW1), (2, rW2), (3, rW3) ] )

	cmds.button( label="RESET VALUES", command=( 'resetTranslation()' ), bgc=resValColor1 , h=buttonHeight, ann='Reset all translation values' )
	cmds.separator( h=buttonHeight/1.25 , style='none' )
	cmds.button( label="RUN TRANSLATION BAKING", command=( 'translationStart()' ), bgc=simColor1 , h=buttonHeight )

	#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
	
	cmds.frameLayout( "rotLayout", l=rotScriptLabel, cll=1, bgc=frameColor1, p="main", sbm="Rotation script", cc=('cmds.window( "main", e=True, h=10, rtf=True )') )
	
	cmds.floatSliderGrp( "s4", l='Smooth', f=True, min=0.0, max=s4Max, fmx=10, 
	v=goalSmoothRot, cc=('goalSmoothRot=printRotSmoothV()'), pre=2, w=slWidth, ann=goalSmoothAnn, cal=(1, "left"), cw3=( 45, 50, 10 )  )
	
	cmds.floatSliderGrp( "s5", l='Scale', f=True, min=0.0, max=s5Max, fmx=10, 
	v=timeScaleRot, cc=('timeScaleRot=printRotScaleV()'), pre=2, w=slWidth, ann=timeScaleAnn, cal=(1, "left"), cw3=( 45, 50, 10 )  )
	
	cmds.floatSliderGrp( "s6", l='Weight', f=True, min=0.0, max=s6Max, 
	v=goalWRot, cc=('goalWRot=printRotWeightV()'), pre=2, w=slWidth, ann=goalWeightAnn, cal=(1, "left"), cw3=( 45, 50, 10 )  )
	
	cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[ (1, rW1), (2, rW2), (3, rW3) ] )
	
	cmds.button( label="RESET VALUES", command=( 'resetRotation()' ), bgc=resValColor2 , h=buttonHeight, ann='Reset all rotation values' )
	cmds.separator( h=buttonHeight/1.25 , style='none' )
	cmds.button( label="RUN ROTATION BAKING", command=( 'rotationStart()' ), bgc=simColor2 , h=buttonHeight )

	#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
	
	cmds.frameLayout( "buttonLayout", l='OPTIONS', cll=1, bgc=frameColor1, p="main", sbm="Options", cc=('cmds.window( "main", e=True, h=10, rtf=True )') )
	cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[ (1, rW1), (2, rW2), (3, rW3) ] )

	cmds.separator( h=buttonHeight/4 , style='none' )
	cmds.separator( h=buttonHeight/4 , style='none' )
	cmds.separator( h=buttonHeight/4 , style='none' )

	# checkbox �1
	cmds.checkBox( "checkCycle", label="Looping animation", v=cycle, cc=( 'cycle=FuncCheckCycle(); cycleInfinity = cycle;' ), bgc=(Bg1, Bg1, Bg1), ann=
	'''USE 60 FPS
Strong recomended to use animation minimum
with 1 phase before and after animation cycle.

Simple way to do it just use pre and post infinity
with "Cycle" option in graph editor.

After baking loop animation on layer will be set cycle infinity''' )

	cmds.separator( h=buttonHeight/1.25 , style='none' )
	
	# checkbox �2
	cmds.checkBox( "checkVectorReverse", label="Aim reverse", v=aimVectorReverse, cc=( 'aimVectorReverse=FuncCheckVector()' ), bgc=(Bg1, Bg1, Bg1), ann=
	'''For reorientation aim for rotation script. May be useful
when rotation simulation bake animation with incorrect rotations.''' )

	# checkbox �3
	cmds.checkBox( "checkInfinity", label="Switch to 60 fps", v=False, en=False, cc=( 'print "Work in progress"' ), bgc=(Bg2, Bg2, Bg2), ann="Work in progress" )
	cmds.separator( h=buttonHeight/1.25 , style='none' )
	# checkbox �4
	cmds.checkBox( "test1", label="Merge layers after baking", v=False, en=False, bgc=(Bg2, Bg2, Bg2), ann="Work in progress" )
	
	#cmds.checkBox( "test2", label="Additive layer", v=False, en=False, bgc=(Bg2, Bg2, Bg2), ann="Work in progress" )
	#cmds.separator( h=buttonHeight/1.25 , style='none' )
	#cmds.checkBox( "test3", label="Baking without layers", v=False, en=False, bgc=(Bg2, Bg2, Bg2), ann="Work in progress" )
	
	cmds.separator( h=1 , style='none' )
	
	#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
	
	cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[ (1, 115), (2, 80), (3, 135) ], p="buttonLayout" )
	cmds.button( label="RESET OPTIONS", command=( 'resetCheckbox()' ), bgc=resCheckColor1 , h=buttonHeight, ann='Reset all options' )
	cmds.button( label="RESET ALL", command=( 'resetAllButton()' ), bgc=resAllColor1 , h=buttonHeight, ann='Reset all values and options in script window' )
	cmds.button( label="!!! DELETE ALL LAYERS !!!", command=( 'deleteMainLayer()' ), bgc=deleteColor1 , h=buttonHeight, ann='Delete main layer "OVERLAPPY" with all layers inside' )

	cmds.separator( h=4 , style='none' )

	cmds.columnLayout( 'endColumn', rs=4, adj=True, p="main", bgc=endColor1 )
	cmds.frameLayout( "informLayout", l='ABOUT', cll=1, bgc=frameColor2, cl=1, p="endColumn", sbm="Options", cc=('cmds.window( "main", e=True, h=10, rtf=True )') )
	cmds.text( "Report bugs and leave rewiew please", h=20 )
	cmds.text( "vk.com/geneugene3d", hl=True, h=20, bgc=linkColor1 )
	cmds.text( "www.artstation.com/geneugene", hl=True, h=20, bgc=linkColor1 )
	cmds.text( "www.highend3d.com/users/geneugene", hl=True, h=20, bgc=linkColor2 )
	cmds.text( "www.highend3d.com/maya/script/overlappy-for-maya-105076", hl=True, h=20, bgc=linkColor2 )
	
	#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
	
	cmds.showWindow( overUI )

""" Progress bar test. DO NOT USE
objCount = 10

def progBar():
	progressWindow = cmds.window( "pBar", title="Please wait", s=False, rtf=True )
	cmds.columnLayout()

	mVal = 100
	steps = 10
	ccc = mVal/steps
	
	wW = 300

	global progressControl; progressControl = cmds.progressBar( maxValue=mVal, width=wW )
	
	cmds.button( label='Make Progress!', command='cmds.progressBar( progressControl, edit=True, step=steps )' )
	
	cmds.window( progressWindow, e=True, wh=(wW, 45) )
	cmds.showWindow( progressWindow )

progBar()
"""

####################################################################################################################

def deleteMainLayer():
	if ( cmds.objExists( "OVERLAPPY" )):
		cmds.delete( mainLayerName )
	else:
		print "\n||| Layer not created |||\n"

def resetLoopTime():
	cmds.playbackOptions( e=True, min=asT, max=aeT )
	cmds.currentTime( asT )

def setTimeToMin():
	cmds.currentTime( minLoopTime )

"""Set 60 fps. DO NOT USE
def set60Fps():
	cmds.currentUnit ( time="ntscf" )
	# game: 15 fps
	# film: 24 fps
	# pal: 25 fps
	# ntsc: 30 fps
	# show: 48 fps
	# palf: 50 fps
	# ntscf: 60 fps
"""

####################################################################################################################

def translationStart():
	
	global asT; asT = cmds.playbackOptions( query=True, min=True ) # Get min anim range
	global aeT; aeT = cmds.playbackOptions( query=True, max=True ) # Get max anim range
	resetLoopTime()
	
	global listObjects; listObjects = cmds.ls( sl=True ) # Get list of selected objects
	
	#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

	global listFixed; listFixed = listObjects [:]

	for i in range( len( listFixed ) ):
		listFixed[i] = listFixed[i].replace( "|", "_" )
		listFixed[i] = listFixed[i].replace( ":", "_" )

	#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
	
	global mainLayerName; mainLayerName = "OVERLAPPY" # Name of main layer

	if( cmds.objExists( mainLayerName ) ):
		print "\n||| OVERLAPPY start |||\n"
	else:
		cmds.animLayer( mainLayerName )
		print "\n||| OVERLAPPY start ||| Layer created |||\n"

	#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

	for i in range( len( listFixed ) ):
		
		global aimLoc; aimLoc = listFixed[i] + "_aim_loc" # Aim locator name
		global tempLoc; tempLoc = listFixed[i] + "_temp_loc" # Physical locator name
		global tempPart; tempPart = listFixed[i] + "_temp_part" # nParticle name
		global tempNucl; tempNucl = "nucleus1" # Nucleus node name
	
		global partAimLoc; partAimLoc = aimLoc + ".translate" # Aim locator position pull
		global partRtype; partRtype = tempPart + "Shape.particleRenderType" # nParticle render type pull
		global partRrad; partRrad = tempPart + "Shape.radius" # nParticle shape radius
		global partRsm; partRsm = tempPart + "Shape.goalSmoothness" # Goal smoothness pull
		global partRwe; partRwe = tempPart + "Shape.goalWeight[0]" # Goal weight pull
		global partPos; partPos = tempPart + ".center" # nParticle center position pull
		global partNucl; partNucl = tempNucl + ".timeScale" # Time scale pull
		global nuclStart; nuclStart = tempNucl + ".startFrame" # Start frame of simulation nucleus node
		
		cmds.spaceLocator( n = tempLoc )
		cmds.matchTransform( tempLoc, listObjects[i], pos=True )
		
		objCenter = tempLoc + ".translate"
		objC = cmds.getAttr( objCenter )
		
		locCenter = tempLoc + ".center"
		locTr = tempLoc + ".translate"
		
		cmds.nParticle( p = objC, n = tempPart , c = 1 )
		cmds.goal( tempPart, w=goalW, utr=1, g = tempLoc )
		
		cmds.select( tempLoc, r=True )
		cmds.select( listObjects[i], add=True )
		cmds.parent( r=True )
		
		cmds.matchTransform( tempLoc, listObjects[i], pos=True )


	#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

		cmds.setAttr( partRtype, pShape )
		cmds.setAttr( partRrad, pRad )
		cmds.setAttr( partRsm, goalSmooth )
		cmds.setAttr( partRwe, goalW )
		cmds.setAttr( partNucl, timeScale )
		cmds.setAttr( nuclStart, asT )
		
	#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

		cmds.duplicate( tempLoc, rr=True, n = aimLoc )
		cmds.select( aimLoc, r=True )
		cmds.parent( w=True )
		cmds.connectAttr( partPos, partAimLoc, f=True )
		
		global minLoopTime; minLoopTime = aeT * minLoopScale
		global maxLoopTime; maxLoopTime = aeT * maxLoopScale
		
		if( cycle ):
			
			cmds.setAttr( nuclStart, minLoopTime )
				
			cmds.bakeResults( aimLoc, t = ( minLoopTime, maxLoopTime ), sm=True, at = "translate")
			cmds.delete( tempLoc, tempPart, tempNucl )

			setTimeToMin()
			
			cmds.select( aimLoc, r=True )
			cmds.select( listObjects[i], add=True )
			cmds.parentConstraint( mo=True, sr=["x", "y", "z"], w = 1 )
			
			resetLoopTime()

		else:
			
			cmds.bakeResults( aimLoc, t = ( asT, aeT ), sm=True, at = "translate" )
			cmds.delete( tempLoc, tempPart, tempNucl )
			
			resetLoopTime()
			
			cmds.select( aimLoc, r=True )
			cmds.select( listObjects[i], add=True )
			
			#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
			
			attrX = listObjects[i] + '.translateX'
			attrY = listObjects[i] + '.translateY'
			attrZ = listObjects[i] + '.translateZ'
			
			lockX = cmds.getAttr( attrX, lock=True )
			lockY = cmds.getAttr( attrY, lock=True )
			lockZ = cmds.getAttr( attrZ, lock=True )

			if ( lockX != True ):
				cmds.parentConstraint( mo=True, st=["y","z"], sr=["x","y","z"], w = 1 )

			if ( lockY != True ):
				cmds.parentConstraint( mo=True, st=["x","z"], sr=["x","y","z"], w = 1 )
				
			if ( lockZ != True ):
				cmds.parentConstraint( mo=True, st=["x","y"], sr=["x","y","z"], w = 1 )

	#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

		layerBase = "translate_"
		layerName = layerBase + listFixed[i]
		layerComp = listFixed[i] + '_layer_{0}'.format("0")

		if ( cmds.objExists( layerName ) ):
			
			cmds.bakeResults( listObjects[i], t = (asT, aeT), sm=True, bol=True, at = "translate")
			cmds.select( listObjects[i], r=True )
			
			if (cycleInfinity): cmds.setInfinity( pri="cycle", poi="cycle" )
			else: cmds.setInfinity( pri="constant", poi="constant" )
			
			cmds.delete( aimLoc )
			cmds.container( "BakeResultsContainer", e=True, rc=True )
			cmds.animLayer( "BakeResults", e=True, p = layerName )
			cmds.rename( "BakeResults", layerComp )
			#cmds.deleteAttr( n=listObjects[i], at="blendParent1" )
			
			resetLoopTime()
		else:
			cmds.animLayer (layerName)
			cmds.animLayer (layerName, e=True, p = mainLayerName)
			cmds.bakeResults (listObjects[i], t = (asT, aeT), sm=True, bol=True, at = "translate")
			cmds.select (listObjects[i], r=True)
			
			if (cycleInfinity): cmds.setInfinity( pri="cycle", poi="cycle" )
			else: cmds.setInfinity( pri="constant", poi="constant" )
			
			cmds.delete (aimLoc)
			cmds.container("BakeResultsContainer", e=True, rc=True)
			cmds.animLayer ("BakeResults", e=True, p = layerName)
			cmds.rename ("BakeResults", layerComp)
			#cmds.deleteAttr( n=listObjects[i], at="blendParent1" )
			
			resetLoopTime()

		
		cmds.select (d=True)
		
	for l in listObjects:
		cmds.select (l, add=True)
		
	print "\n||| OVERLAPPY end |||\n"

def rotationStart():
	
	global asT; asT = cmds.playbackOptions (query=True, min=True)
	global aeT; aeT = cmds.playbackOptions (query=True, max=True)
	resetLoopTime()
	
	global listObjects; listObjects = cmds.ls (sl=True)
	
	if( len( listObjects ) <= 1 ):
		
		print "\n||| Need to select two or more objects |||\n"
	
	else:
			
		#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
	
		global listFixed; listFixed = listObjects [:]
	
		for i in range( len( listFixed ) ):
			listFixed[i] = listFixed[i].replace( "|", "_" )
			listFixed[i] = listFixed[i].replace( ":", "_" )
	
	
		#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
		
		global mainLayerName; mainLayerName = "OVERLAPPY"
	
		if (cmds.objExists(mainLayerName)):
			print "\n||| OVERLAPPY start |||\n"
		else:
			cmds.animLayer (mainLayerName)
			print "\n||| OVERLAPPY start ||| Layer created |||\n"
	
		#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
	
		for i in range(len(listFixed)):
			
			if ( i+1 != len(listFixed) ):
			
				global zeroLoc; zeroLoc = listFixed[i] + "_base_loc"
				global aimLoc; aimLoc = listFixed[i] + "_aim_loc"
				global tempLoc; tempLoc = listFixed[i] + "_temp_loc"
				global tempAimLoc; tempAimLoc = listFixed[i] + "_tempAim_loc"
				
				global tempPart; tempPart = listFixed[i] + "_temp_part"
				global tempNucl; tempNucl = "nucleus1"
				
				global partRtype; partRtype = tempPart + "Shape.particleRenderType"
				global partRrad; partRrad = tempPart + "Shape.radius"
				global partRsm; partRsm = tempPart + "Shape.goalSmoothness"
				global partRwe; partRwe = tempPart + "Shape.goalWeight[0]"
				global partNucl; partNucl = tempNucl + ".timeScale"
				global nuclStart; nuclStart = tempNucl + ".startFrame"
				
				if aimVectorReverse: rotAimVector = -1
				else: rotAimVector = 1
				
			#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
				
				cmds.spaceLocator( n = zeroLoc )
				cmds.spaceLocator( n = aimLoc )
				cmds.spaceLocator( n = tempLoc )
				
				cmds.matchTransform ( zeroLoc, listObjects[i], pos=True )
				cmds.matchTransform ( tempLoc, listObjects[i+1], pos=True )
				
				cmds.select( tempLoc, r=True )
				cmds.duplicate( n = tempAimLoc )
				
				cmds.select( listObjects[0], r=True )
				cmds.select( zeroLoc, add=True )
				cmds.parentConstraint( mo=True, w = 1 )
				
				cmds.select( aimLoc, r=True )
				cmds.select( zeroLoc, add=True )
				cmds.parent( r=True )
				
				cmds.select( listObjects[1], r=True )
				cmds.select( tempLoc, add=True )
				cmds.parentConstraint( mo=True, sr=["x", "y", "z"], w = 1 )
				
				aimPosName = tempLoc + ".translate"
				partCenter = tempPart + ".center"
				aimLocPos = tempAimLoc + ".translate"
				
				aimPos = cmds.getAttr( aimPosName )
				cmds.nParticle( p = aimPos , n = tempPart , c = 1 )
				cmds.goal( tempPart, w=0.5, utr=1, g = tempLoc )
				cmds.connectAttr( partCenter, aimLocPos, f=True )
				
				cmds.select( tempAimLoc, r=True )
				cmds.select( aimLoc, add=True )
				cmds.aimConstraint( w=1, aim=(0, rotAimVector, 0), u=(0, 1, 0), wut="vector", wu=(0, 1, 0), sk="y" )
		
			#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
				
				cmds.setAttr (partRtype, pShape)
				cmds.setAttr (partRrad, pRad)
				cmds.setAttr (partRsm, goalSmoothRot)
				cmds.setAttr (partRwe, goalWRot)
				cmds.setAttr (partNucl, timeScaleRot)
				cmds.setAttr (nuclStart, asT)
				
			#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
		
				global minLoopTime; minLoopTime = aeT * minLoopScale
				global maxLoopTime; maxLoopTime = aeT * maxLoopScale
		
		
				if (cycle):
					
					cmds.setAttr( nuclStart, minLoopTime )
					
					cmds.bakeResults( zeroLoc, t = (asT, aeT), sm=True, at=( "translate", "rotate") )
					cmds.bakeResults( aimLoc, t = (minLoopTime, maxLoopTime), sm=True, at="rotate" )
					cmds.delete( tempAimLoc, tempLoc, tempPart, tempNucl )
					
					zeroParent = zeroLoc + "_parentConstraint1"
					cmds.delete( zeroParent )
					
					setTimeToMin()
					
					cmds.select( aimLoc, r=True )
					cmds.select( listObjects[i], add=True )
					
					#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
					
					attrX = listObjects[i] + '.rotateX'
					attrY = listObjects[i] + '.rotateY'
					attrZ = listObjects[i] + '.rotateZ'
					
					lockX = cmds.getAttr( attrX, lock=True )
					lockY = cmds.getAttr( attrY, lock=True )
					lockZ = cmds.getAttr( attrZ, lock=True )

					if ( lockX != True ):
						cmds.parentConstraint( mo=True, st=["x","y","z"], sr=["y","z"], w = 1 )
				
					if ( lockY != True ):
						cmds.parentConstraint( mo=True, st=["x","y","z"], sr=["x","z"], w = 1 )
					
					if ( lockZ != True ):
						cmds.parentConstraint( mo=True, st=["x","y","z"], sr=["x","y"], w = 1 )
					
					resetLoopTime()
		
				else:
					
					cmds.bakeResults( zeroLoc, t = (asT, aeT), sm=True, at=( "translate", "rotate") )
					cmds.bakeResults( aimLoc, t = (asT, aeT), sm=True, at="rotate" )
					cmds.delete( tempAimLoc, tempLoc, tempPart, tempNucl )
					
					zeroParent = zeroLoc + "_parentConstraint1"
					cmds.delete( zeroParent )
					
					resetLoopTime()
					
					cmds.select( aimLoc, r=True )
					cmds.select( listObjects[i], add=True )
					
					#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
					
					attrX = listObjects[i] + '.rotateX'
					attrY = listObjects[i] + '.rotateY'
					attrZ = listObjects[i] + '.rotateZ'
					
					lockX = cmds.getAttr( attrX, lock=True )
					lockY = cmds.getAttr( attrY, lock=True )
					lockZ = cmds.getAttr( attrZ, lock=True )

					if ( lockX != True ):
						cmds.parentConstraint( mo=True, st=["x","y","z"], sr=["y","z"], w = 1 )
					
					if ( lockY != True ):
						cmds.parentConstraint( mo=True, st=["x","y","z"], sr=["x","z"], w = 1 )
					
					if ( lockZ != True ):
						cmds.parentConstraint( mo=True, st=["x","y","z"], sr=["x","y"], w = 1 )
					
			#||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
		
				layerBase = "rotate_"
				layerName = layerBase + listFixed[i]
				layerComp = listFixed[i] + '_layer_{0}'.format("0")
		
				if ( cmds.objExists( layerName ) ):
					
					cmds.bakeResults( listObjects[i], t = (asT, aeT), sm=True, bol=True, at = "rotate" )
					cmds.select( listObjects[i], r=True )
					
					if (cycleInfinity): cmds.setInfinity( pri="cycle", poi="cycle" )
					else: cmds.setInfinity( pri="constant", poi="constant" )
					
					cmds.delete( aimLoc, zeroLoc )
					cmds.container( "BakeResultsContainer", e=True, rc=True )
					cmds.animLayer( "BakeResults", e=True, p = layerName )
					cmds.rename( "BakeResults", layerComp )
					#cmds.deleteAttr( n=listObjects[i], at="blendParent1" )
					
					resetLoopTime()
				else:
					cmds.animLayer( layerName )
					cmds.animLayer( layerName, e=True, p = mainLayerName )
					cmds.bakeResults( listObjects[i], t = (asT, aeT), sm=True, bol=True, at = "rotate" )
					cmds.select( listObjects[i], r=True )
					
					if (cycleInfinity): cmds.setInfinity( pri="cycle", poi="cycle" )
					else: cmds.setInfinity( pri="constant", poi="constant" )
					
					cmds.delete( aimLoc, zeroLoc )
					cmds.container( "BakeResultsContainer", e=True, rc=True )
					cmds.animLayer( "BakeResults", e=True, p = layerName )
					cmds.rename( "BakeResults", layerComp )
					#cmds.deleteAttr( n=listObjects[i], at="blendParent1" )
					
					resetLoopTime()
		
				
				cmds.select (d=True)
		
	for l in listObjects:
		cmds.select (l, add=True)
		
	print "\n||| OVERLAPPY end |||\n"

####################################################################################################################
### Run code

resetAll()
uiCreation()

####################################################################################################################
### End