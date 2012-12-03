#!/usr/bin/env python
#
# waCaptcha
# Copyright (C) 2012 Larroque Stephen
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the Affero GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import sys, random, os
sys.path.append("C:/Panda3D-1.8.0/")

from pprint import pprint
from math import sqrt

from auxlib import *

from panda3d.core import loadPrcFileData, PNMImage, PNMImageHeader, Point3, TextNode
from direct.gui.OnscreenImage import OnscreenImage

class WorldCacher:
    ''' Manage various caches to speedup the generation of a 3D scene '''

    def __init__(self, base=None, debug=False):
        # Set commandline rendering mode (unloading as many rendering module as possible and hiding rendering window)

        # hide rendering window (we don't need it)
        loadPrcFileData("",
        """
           load-display p3tinydisplay # to force CPU only rendering (to make it available as an option if everything else fail, use aux-display p3tinydisplay)
           window-type offscreen # Spawn an offscreen buffer (use window-type none if you don't need any rendering)
           audio-library-name null # Prevent ALSA errors
           show-frame-rate-meter 0
           sync-video 0
        """)

        # Init 3D world
        if base:
            self.base = base
        else:
            from direct.showbase.ShowBase import ShowBase
            self.base = ShowBase()


    @staticmethod
    def cacheListOfModels(modelspath, cachepath):
        ''' Cache a list of models names '''
        cache = "\n".join(os.listdir(modelspath))
        f = open(cachepath, 'wb')
        f.write(cache)
        f.close()
        return True


    def cacheListOfModelsWithBounds(self, modelspath, cachepath):
        ''' Cache a list of models names along their precomputed tight bounds size '''
        cacheList = os.listdir(modelspath)

        finalList = []
        for modelName in cacheList:
            # Load the model in the engine
            model = loader.loadModel(os.path.join(modelspath, modelName))

            # Get the tight bound of the model (return two points representing the tightest axis-aligned box enclosing the model)
            minLimit, maxLimit = model.getTightBounds()

            # Convert to a 3D dimensions object
            dimensions = Point3(maxLimit - minLimit)

            # Get the size of the object from its maximum size in either the X,Y or Z direction
            modelSize = max([dimensions.getX(), dimensions.getY(), dimensions.getZ()])

            # Remove the model (freeing memory)
            model.remove()

            finalList.append([modelName, str(modelSize)])

        finalList = ["|".join(x) for x in finalList]

        # Save the result in the cache file
        f = open(cachepath, 'wb')
        f.write("\n".join(finalList))
        f.close()
        return True

    def model2Bam(self, modelpath, bampath):
        ''' Standard way to convert any 3D model (from any supported format by Panda3D) into a BAM (compiled runtime)
        equivalent to: egg2bam -o foo.bam foo.egg
        WARNING: BAM files only work for the very specific version of Panda3D they were built with, so you should keep the original 3D models somewhere and use BAM files only for runtime!
        '''

        model=loader.loadModel(modelpath)

        #do some fancy calculations on the normals, or texture coordinates that you dont
        #want to do at runtime

        #Save your new custom Panda
        model.writeBamFile(bampath)

        # Free memory
        model.remove()

        return True

    def model2BamMulti(self, modeldir, bamdir):
        ''' Convert in batch all 3D models in a directory into BAM '''

        for model in os.listdir(modeldir):
            modelName = model.split('.')[0] # Get only the model name, without extension
            self.model2Bam( os.path.join(modeldir, model), os.path.join(bamdir, "%s.bam" % modelName) ) # convert it to BAM

        return True




class WorldGenerator:
    ''' 3D scene generator class '''

    def __init__(self, nbElem=10, minClickablePercentage=2.0, maxClickablePercentage=100.0, uniqueColors=False, minModelSize=15, maxModelSize=25, modelsPath='models', modelsCacheList='modelscache.txt', modelsExceptionList='modelsexception.txt', backgroundsPath='backgrounds', backgroundsCacheList='backgroundslist.txt', colorTint=True, windowWidth=640, windowHeight=480, debug=False):
        # Vars
        self.debug = debug
        self.minClickablePercentage = minClickablePercentage
        self.maxClickablePercentage = maxClickablePercentage
        self.nbElem = nbElem
        self.uniqueColors = uniqueColors # The reference object has a unique color?
        self.modelsPath = modelsPath
        self.modelsCacheList = modelsCacheList
        self.modelsExceptionList = modelsExceptionList
        self.minModelSize = minModelSize
        self.maxModelSize = maxModelSize
        self.rangeModelSize = maxModelSize - minModelSize # precompute the range (optimization)
        self.backgroundsPath = backgroundsPath
        self.backgroundsCacheList = backgroundsCacheList
        self.colorTint = colorTint

        # Set commandline rendering mode (unloading as many rendering module as possible and hiding rendering window)
        if debug: # show rendering window if in debug mode
            loadPrcFileData("",
            """
               load-display p3tinydisplay # to force CPU only rendering (to make it available as an option if everything else fail, use aux-display p3tinydisplay)
               window-type onscreen # Spawn an offscreen buffer (use window-type none if you don't need any rendering)
               audio-library-name null # Prevent ALSA errors
               show-frame-rate-meter 0
               sync-video 0
               win-size """+str(windowWidth)+' '+str(windowHeight)+"""
            """)
        else: # hide rendering window if not in debug mode
            loadPrcFileData("",
            """
               load-display p3tinydisplay # to force CPU only rendering (to make it available as an option if everything else fail, use aux-display p3tinydisplay)
               window-type offscreen # Spawn an offscreen buffer (use window-type none if you don't need any rendering)
               audio-library-name null # Prevent ALSA errors
               show-frame-rate-meter 0
               sync-video 0
               win-size """+str(windowWidth)+' '+str(windowHeight)+"""
            """)

        # Init 3D world
        from direct.showbase.ShowBase import ShowBase
        self.base = ShowBase()

        # Init Cache
        self.cacher = WorldCacher(base=self.base)

        # Init scene camera
        self.base.camLens.setFov(45)

        # Reset colors (else we will see the clickable mask by default)
        #self.renderReset()
        #self.clickableModel.clearColorScale()
        #self.clickableModel.setColor(1,1,1,1)

    def generateScene(self):
        ''' Generate a random 3D scene '''
        # Load models and ensure that the clickable area is reasonable
        clickableAreaOk = False
        while (not clickableAreaOk):
            self.loadBackground()
            self.loadModels(self.nbElem, self.minModelSize, self.maxModelSize, self.modelsPath, self.modelsCacheList, self.modelsExceptionList, self.colorTint)                  # Load and position our models
            clickableAreaOk = self.checkClickableArea(self.minClickablePercentage, self.maxClickablePercentage) # Check that the clickable area is reasonable

    def loadBackground(self, bgdir=None, bgcache=None):
        ''' Load a random background image behind the models '''

        if not bgdir:
            bgdir = self.backgroundsPath
        if not bgcache:
            bgcache = self.backgroundsCacheList

        # Remove the previous background
        if (hasattr(self, 'background')):
            self.background.remove()

        # Create the cache (list of background images) if not already done
        if not os.path.isfile(bgcache):
            WorldCacher.cacheListOfModels(bgdir, bgcache)

        # Pick a random image from the cache
        (bgimage, cur) = fastRandLine(bgcache)

        # Load the background image in the scene
        # We use a special trick of Panda3D: by default we have two 2D renderers: render2d and render2dp, the two being equivalent. We can then use render2d for front rendering (like modelName), and render2dp for background rendering.
        self.background = OnscreenImage(parent=render2dp, image=os.path.join(bgdir, bgimage)) # Load an image object
        base.cam2dp.node().getDisplayRegion(0).setSort(-20) # Force the rendering to render the background image first (so that it will be put to the bottom of the scene since other models will be necessarily drawn on top)

    def loadModels(self, nbElem=None, minModelSize=None, maxModelSize=None, modelsPath=None, modelsCacheList=None, modelsExceptionList=None, colorTint=True):
        ''' Load a given number of models (picked randomly) and set their parameters randomly
        This generates a scene with a unique reference model, and repeatable non clickable models
        '''

        if not nbElem:
            nbElem = self.nbElem
        if not modelsPath:
            modelsPath = self.modelsPath
        if not modelsCacheList:
            modelsCacheList = self.modelsCacheList
        if not modelsExceptionList:
            modelsExceptionList = self.modelsExceptionList
        if not minModelSize:
            minModelSize = self.minModelSize
        if not maxModelSize:
            maxModelSize = self.maxModelSize

        # Open the models list (we cache the list to avoid fetching the whole list of files, which may be very big! and slow down a lot the application)
        if not os.path.isfile(modelsCacheList):
            self.cacher.cacheListOfModelsWithBounds(modelsPath, modelsCacheList) # create the models list if it doesn't exist
            # cacheListOfModels(modelsPath, modelsCacheList)
        modelsList = open(modelsCacheList, 'rb') # open the models list

        # Open the models exception list (these models will be excluded for the reference model)
        if modelsExceptionList and os.path.isfile(modelsExceptionList):
            f = open(modelsExceptionList, 'rb') # open the models list
            exceptionList = [line.strip() for line in f]
        else:
            exceptionList = None

        # Drop all previous objects if we're regenerating the scene
        if (hasattr(self, 'nonClickable')):
            self.nonClickable.remove()

        if (hasattr(self, 'clickable')):
            self.clickable.remove()

        # Create 2 group nodes: one for the clickable model (reference model), and one for all the other objects (the non clickable models)
        self.nonClickable = render.attachNewNode("Non Clickable Objects");
        self.clickable = render.attachNewNode("Clickable Object");

        # Loading randomly picked objects with random parameters
        exceptionCur = [] # list that will contain the reference model, so that we don't load it twice
        for i in xrange(nbElem): # Loading nbElem objects

            # == Loading a random model

            # Pick a random model from the list
            if i == 0: # reference model: picking a random model except the ones listed as exceptions
                (line, cur) = fastRandLine(modelsList, exceptlist=exceptionList)
            else: # other models: picking a random model except the reference model (other models can be repeated, but not the reference model which is unique)
                (line, cur) = fastRandLine(modelsList, exceptposlist=exceptionCur)
            (randomModel, modelSize) = line.split("|") # model name and size are separated by | delimiter
            modelSize = float(modelSize) # get the model size as float instead of string

            # Try to load the random model
            try:
                model = loader.loadModel(os.path.join(modelsPath, randomModel))
            # If the model loading failed, probably the model doesn't exist anymore and the cache isn't up-to-date
            except:
                # in this case, we regenerate the models list
                modelsList.close()
                self.cacher.cacheListOfModelsWithBounds(modelsPath, modelsCacheList)
                #cacheListOfModels(modelsPath, modelsCacheList)
                modelsList = open(modelsCacheList, 'rb')

                # Pick a random model from the list TODO: this is not an elegant code, this is just a copy paste of the code above...
                if i == 0: # reference model: picking a random model except the ones listed as exceptions
                    (line, cur) = fastRandLine(modelsList, exceptlist=exceptionList)
                else: # other models: picking a random model except the reference model (other models can be repeated, but not the reference model which is unique)
                    (line, cur) = fastRandLine(modelsList, exceptposlist=exceptionCur)
                (randomModel, modelSize) = line.split("|") # model name and size are separated by | delimiter
                modelSize = float(modelSize) # get the model size as float instead of string

                model = loader.loadModel(os.path.join(modelsPath, randomModel))



            # == Set random parameters for the model

            # Pick a random color
            randomColor = [random.random(), random.random(), random.random()]
            # Attach the model to the scene
            if i == 0: # the first object is the clickable object (reference model), we do special treatement for it
                self.clickableModel = model # memorize it as the clickable object
                model.reparentTo(self.clickable) # reparent the object to the scene (make it appear in the scene), in the clickable tree
                self.clickableColor = randomColor # memorize the color of the clickable object
                self.clickableColorSet = set(randomColor) # create a set for the clickable color (easiest, fastest and most pythonic way to check that this is a unique color)
                self.clickableModelSize = modelSize # store the model size (to easily and quickly scale and renormalize it)
                self.clickableModelName = randomModel.split('.')[0] # store model name (to be able to print it below the model) - get only the base name without the extension
                exceptionCur.append(cur) # add this model to the list of exceptions (so that any other object cannot be the same as the reference model)
            else: # else for all other non clickable object
                model.reparentTo(self.nonClickable) # reparent the object to the scene, in the nonClickable tree

            # Set random parameters
            model.setPos(random.uniform(20,-20),random.uniform(35, 120),random.uniform(-10, 15)) # set position
            model.setHpr(random.uniform(0, 360), random.uniform(-30, 30), random.uniform(30, -30)) # set orientation
            model = self.normalizeModelSize(model, minModelSize, maxModelSize, modelSize) # set size (normalize size and set a random size in the normalized range)

            # Set color tint
            # check that the color of the non clickable models are not the same as the clickable model
            if self.uniqueColors and i > 0:
                while (self.clickableColorSet.intersection(randomColor)): # check that the same color isn't already applied to the clickable object
                    randomColor = [random.random(), random.random(), random.random()] # generate a new color until we get one that is not assigned to the clickable object
            randomColor.append(1.0) # set color alpha transparency (opaque)
            # Set color tint (keep object's texture)
            if colorTint:
                model.setColorScale(*randomColor)
            # Or set the whole color (overwrites the object's texture)
            else:
                model.setColor(*randomColor)

        # close the models list (freeing memory)
        modelsList.close()

    def normalizeModelSize(self, model, minModelSize, maxModelSize, modelSize=None):
        ''' Normalize a model size in the scene between the given lower and higher bounds '''
        # Check if the range was already precomputed (optimization)
        if self.rangeModelSize:
            rangeModelSize = self.rangeModelSize
        else:
            rangeModelSize = maxModelSize - minModelSize

        # If model size was already precomputed and stored in cache, we don't need to recompute it. Else, we recompute it here.
        if not modelSize:
            # Get the tight bound of the model (return two points representing the tightest axis-aligned box enclosing the model)
            minLimit, maxLimit = model.getTightBounds()

            # Convert to a 3D dimensions object
            dimensions = Point3(maxLimit - minLimit)

            # Get the size of the object from its maximum size in either the X,Y or Z direction
            modelSize = max([dimensions.getX(), dimensions.getY(), dimensions.getZ()])

        # If the model's size is not already in the specified bounds, we resize it
        if not (minModelSize < modelSize < maxModelSize):
            model.setScale( ((random.random()*rangeModelSize) + minModelSize) / modelSize ) # resize the object between the bounds, normalized to 1.0 (since the original scale of the object is set to 1.0, here it is hidden in the numerator)

        # return the new normalized rescaled model
        return model

    def renderClickableArea(self):
        ''' Render the clickable area (visible areas of the reference model painted in white and everything else black)'''
        self.base.setBackgroundColor(0,0,0,1) # set background to black
        self.background.hide()
        if hasattr(self, 'clickableText'):
            self.clickableText.hide()
        self.nonClickable.setColor(0,0,0) # set non clickable objects to black
        self.clickableModel.clearColorScale() # clear clickable object's color (to set a whole new color, else it will be another layer over the previous color)
        self.clickableModel.setColor(1,1,1) # set clickable object to white

    def renderClickableModel(self, showModel=True, showName=False):
        ''' Render just the clickable (reference) model '''
        # Hide all non clickable objects
        self.nonClickable.clearColor()
        self.nonClickable.hide()
        # Show the clickable model with the original texture and color
        self.clickableModel.clearColor()
        self.clickableModel.clearColorScale()
        if showModel:
            # Place it in front of the user, face-to-face (we try to randomly parametrize the position and orientation of the reference model but in a way that the user can clearly see it face-to-face)
            self.clickableModel.setPos(0,40,0)
            self.clickableModel = self.normalizeModelSize(self.clickableModel, self.minModelSize, self.maxModelSize, self.clickableModelSize) # set size (normalize size and set a random size in the normalized range)
            self.clickableModel.setHpr(random.uniform(-45, 45), random.uniform(-15, 15), 0)
            self.clickableModel.setColorScale(random.random(), random.random(), random.random(), 1.0)
        else:
            self.clickable.hide()

        if showName:
            if not hasattr(self, 'clickableText') or self.clickableText != self.clickableModelName:
                if hasattr(self, 'clickableText'):
                    self.clickableText.remove()
                text = TextNode('reference model name')
                text.setText(self.clickableModelName)
                text.setAlign(TextNode.ACenter)
                self.clickableText = render2d.attachNewNode(text)
                self.clickableText.setScale( 0.2 )
                self.clickableText.setPos( 0, 0, -0.8 )

    def renderReset(self):
        ''' Reset the colors and stuffs '''
        self.base.setBackgroundColor(0, 0, 0, a=1) # Clear the background color (we set it to fully transparent, just the same way it is done inside Panda3D core)
        self.background.show() # show the background image
        if hasattr(self, 'clickableText'):
            self.clickableText.hide()
        self.nonClickable.clearColor()
        self.nonClickable.clearColorScale()
        self.nonClickable.show()
        self.clickable.show()
        self.clickableModel.clearColor()
        self.clickableModel.clearColorScale()
        color = list(self.clickableColor) # copy the clickable color
        color.append(1)
        self.clickableModel.setColorScale(*color)
        #self.clickableModel.setColor(*self.clickableColor)


    def checkClickableArea(self, threshold, maxthreshold):
        ''' Facade function that returns True or False if the total visible clickable area of the reference model is above a given threshold '''
        if threshold <= self.getTotalClickableArea() <= maxthreshold:
            return True
        else:
            return False


    #def checkBiggestClickableArea(self, threshold):
        #'''Compute the biggest contiguous area of clickable pixels, and compute its percentage relative to the image total size'''
        #print('TODO!')
        #retun True


    def getTotalClickableArea(self):
        '''Compute the total clickable area, and compute its percentage relative to the image total size'''
        ### RENDERING CLICKABLE AREA
        # Prepare the rendering of the clickable area
        self.renderClickableArea()
        # Render the frame
        self.base.graphicsEngine.renderFrame()

        ### FETCHING THE RENDERED IMAGE
        # Prepare the variable that will store the frame image (in a PNMImage class, this is NOT a file format, but a convenient image manipulation class offered by Panda3D)
        screenshot = PNMImage()
        # Set display region to the default
        dr = base.camNode.getDisplayRegion(0)
        # Store the rendered frame into the variable screenshot
        dr.getScreenshot(screenshot)

        ### COMPUTE THE CLICKABLE AREA PERCENTAGE
        # Prepare an histogram object
        hist = PNMImage().Histogram()
        # Compute the histogram
        screenshot.makeHistogram(hist)
        # Get the number of white opaque pixels (the clickable area)
        totalClickableArea = hist.getCount(PNMImageHeader.PixelSpec(255,255,255, 255))
        # Get the percentage of clickable area relative to the total image size
        totalClickableAreaPercentage = float(totalClickableArea) * 100 / (screenshot.getReadXSize() * screenshot.getReadYSize())

        if self.debug:
            print("Total unique intensity pixels: %f" % hist.getNumPixels())
            print("Total clickable area: %f" % totalClickableArea)
            totalClickableAreaSqrt = sqrt(float(totalClickableArea))
            print("Total clickable area sqrt: %f" % totalClickableAreaSqrt)
            print("Size of image X*Y: %f * %f" %(screenshot.getReadXSize(), screenshot.getReadYSize()))
            print("Total clickable area percentage: %f" % totalClickableAreaPercentage)

            blackarea = hist.getCount(PNMImageHeader.PixelSpec(0,0,0, 255))
            print("Total black area: %f" % blackarea)
            print("Total black area percentage: %f" % (float(blackarea) * 100 / (screenshot.getReadXSize() * screenshot.getReadYSize()))  )

        return totalClickableAreaPercentage


    def renderToPNM(self):
        ### RENDER IMAGE
        # Render the frame
        self.base.graphicsEngine.renderFrame()

        ### FETCHING THE RENDERED IMAGE
        # Prepare the variable that will store the frame image (in a PNMImage class, this is NOT a file format, but a convenient image manipulation class offered by Panda3D)
        image = PNMImage()
        # Set display region to the default
        dr = base.camNode.getDisplayRegion(0)
        # Store the rendered frame into the variable screenshot
        dr.getScreenshot(image)

        return image


    def renderAndSave(self, path='screenshot'):
        ''' Render the scene and save it directly to an image file on disk '''
        base.graphicsEngine.renderFrame()
        base.screenshot(namePrefix=path, defaultFilename=0, source=None, imageComment="")


# Some debug testing here
if __name__ == '__main__':
    wc = WorldCacher()
    wc.cacheListOfModelsWithBounds('models', 'modelscache2.txt')
    wc.model2BamMulti('models', 'bammodels')
