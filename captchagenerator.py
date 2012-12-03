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

from worldgenerator import WorldGenerator
from rleimage import RLEImage
import random
import os

import cStringIO as StringIO
from panda3d.core import StringStream, Texture

import Image

class CaptchaGenerator:
    ''' Captcha generator class '''

    def __init__(self, showRefModel=True, showRefName=False, jpgquality=16, debugPng=False, debug=False, **kwargs):
        ''' Initialize the captcha generator. You can set any parameters of the World generator as **kwargs '''

        self.debug = debug
        self.debugPng = debugPng
        self.showRefModel = showRefModel
        self.showRefName = showRefName
        self.jpgquality = jpgquality # between 0..100

        # Loading a 3D world (optimization: we generate one world for the whole captcha generator)
        w = WorldGenerator(debug=self.debug, **kwargs)
        self.world = w

    def randomID(self):
        ''' Generate a random, unique ID '''
        return hex(random.getrandbits(128))[2:-1]

    def renderCaptcha(self, cpath='', solpath='', cname=None):
        ''' Generate one captcha set (captcha image + solution mask) '''

        # == INIT
        # Position the reference image (clickable model-only image) to the left or to the right? (this adds more complexity for bots)
        rightorleft = random.random()
        # Generate a random name, unless it was specified otherwise
        if not cname:
            cname = "%s" % self.randomID()

        # Generating a 3D scene
        w = self.world
        w.generateScene()

        # == GENERATING CAPTCHA SOLUTION MASK
        # Render and save clickable mask
        #w.renderClickableArea() # Already rendered just after the generation of the world
        imgMask = w.renderToPNM()
        if rightorleft < 0.5:
            imgMask.expandBorder(left=imgMask.getReadXSize(), right=0, bottom=0, top=0, color=(0,0,0,1))
        else:
            imgMask.expandBorder(left=0, right=imgMask.getReadXSize(), bottom=0, top=0, color=(0,0,0,1))

        # Save the solution mask as a PNG then RLE
        # TODO find a way to convert from PNMImage to RLE directly in-memory without saving it to a file
        pngpath = os.path.join(cpath, "%s.png" % cname)
        imgMask.write(pngpath) # save image as png to avoid losing information (important since it's the solution mask!)
        imgMask.clear() # freeing memory
        #w.renderAndSave('testmask.png')

        # Convert PNG to RLE
        rle = RLEImage()
        rle.convertImageToRLE(pngpath, os.path.join(cpath, "%s.rle" % cname))
        del rle # freeing memory

        if not self.debug and not self.debugPng:
            os.remove(pngpath) # delete the png, not needed and it frees some space

        # == GENERATING CAPTCHA QUESTION
        # Render and save captcha image (the one that will be presented to the user)

        # First we generate the whole captcha scene (where the user will have to click)
        w.renderReset()
        img1 = w.renderToPNM()
        # Second, we generate the reference model alone so that the user know what he has to look for
        w.renderClickableModel(self.showRefModel, self.showRefName)
        img2 = w.renderToPNM()

        # Place the reference image randomly at the right side or at the left side (to confuse bots a little bit more)
        if rightorleft < 0.5:
            img1.expandBorder(left=img2.getReadXSize(), right=0, bottom=0, top=0, color=(0,0,0,1)) # resizing the first image to the size of two images (reference image + whole scene image)
            img1.copySubImage(img2, 0, 0) # copying reference image onto the first one, side by side
        else:
            img1.expandBorder(left=0, right=img2.getReadXSize(), bottom=0, top=0, color=(0,0,0,1))
            img1.copySubImage(img2, img2.getReadXSize(), 0)

        # Saving final image
        # First step: we save the jpg image
        jpgpath = os.path.join(solpath, "%s.jpg" % cname)
        img1.write( jpgpath ) # save image (using jpg will add even more complexity for bots, because JPEG is a lossy image compression using psycho-human optimization: lossy + adapted to human = worst for bots) TODO: add a parameter to adjust the JPEG quality and loss

        img2.clear() # freeing memory
        img1.clear() # freeing memory

        # Second step: reload the jpg in PIL and resave with a different quality (because Panda3D doesn't allow to set jpg quality)
        # This is important: saving with a lower quality reduce bandwidth but also raise the difficulty for the bots
        img = Image.open(jpgpath, 'r')
        img.save(jpgpath, quality = self.jpgquality, optimize=False, progressive=True) # Optimize does an extra pass. Not needed here: we don't want to optimize for bots.
        del img # freeing memory

        if self.debug:
            w.base.run() # if debug mode enabled, we show a window with the world we have just generated

        return cname # return the ID of the generated captcha

    def renderCaptchaMulti(self, nb=1, cpath='', solpath='', cname=None):
        ''' Generate multiple captcha sets in a row (useful to pregenerate captchas) '''
        for i in xrange(nb):
            if cname:
                self.renderCaptcha(cpath, solpath, "%s%s" % (cname, i))
            else:
                self.renderCaptcha(cpath, solpath)



class CaptchaChecker:
    ''' Checks the validity of a Captcha answer (and other security stuffs) '''

    def checkSolution(self, solpath, name, x, y):
        ''' Check if a Captcha response is correct '''
        rle = RLEImage()
        result = rle.openAndCheck( os.path.join(solpath, "%s.rle" % name) , x, y)
        del rle
        return result


# Some debug testing here
if __name__ == '__main__':

    captcha = CaptchaGenerator(True, True, debugPng=True, debug=False, nbElem=4, modelsPath='bammodels', windowWidth='320', windowHeight='240')

    #captcha.renderCaptcha('solmasks', 'solmasks')
    captcha.renderCaptchaMulti(4, 'solmasks', 'solmasks')

    #import time

    #time.sleep(20)
