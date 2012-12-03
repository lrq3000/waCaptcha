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

from captchagenerator import CaptchaGenerator, CaptchaChecker
import os, shutil, time
from multiprocessing import Process
from auxlib import call_it

#pathname = os.path.dirname(os.path.realpath(__file__))
#sys.path.append(os.path.join(pathname, 'lib'))
#import mp_guard

class CaptchaManager:
    '''
    A wrapper class to manage the safe handling of Captcha images (optimization using pregeneration of images, deleting captchas after each access, etc.)
    '''

    def __init__(self, cpath=None, solpath=None, precpath=None, presolpath=None, preindexpath=None, watch_filepattern='pre', watch_delay=60, watch_minthreshold=20, watch_maxthreshold=50, *args, **kwargs):
        if preindexpath:
            self.preindexpath = preindexpath
        if cpath:
            self.cpath = cpath
        if solpath:
            self.solpath = solpath
        if precpath:
            self.precpath = precpath
        if presolpath:
            self.presolpath = presolpath

        self.watch_filepattern = watch_filepattern
        self.watch_delay = watch_delay
        self.watch_minthreshold = watch_minthreshold
        self.watch_maxthreshold = watch_maxthreshold

        self.watching = False # flag to false to say that the coroutine is not yet running

        self.captchagen = CaptchaGenerator(*args, **kwargs)
        self.captchachecker = CaptchaChecker()
        return

    def makeCaptcha(self, startid, filepattern):
        '''
        Make a batch of captcha images given a filename pattern and a starting id (will generate as many captchas as the difference between starting id and maximum threshold)
        '''
        for i in xrange(self.watch_maxthreshold):
            self.captchagen.renderCaptcha(self.precpath, self.presolpath, "%s%s" % (filepattern, startid+i))

        return startid + self.watch_maxthreshold

    def watchCaptcha(self):
        '''
        Coroutine to pregenerate captchas images and solutions in the background, and also manage the number of available pregenerated captchas between a minimum and maximum threshold
        '''
        self.watching = True # Notify that the coroutine is running

        while self.watching: # Stop when the watching flag is set to false (or when the application closes)

            lastid = None
            try:
                with open(self.preindexpath, 'rb') as f: # at first we only read the file in a non blocking way to check how many captchas are left
                    (pattern, currentid, lastid) = f.read().strip().split(' ')
                    lastid = int(lastid)
                    currentid = int(currentid)
            except:
                pass

            # Generate a set of captcha if either the file is not yet set or either the number of pregenerated captchas are below the minimum threshold
            newlastid = None
            if not lastid:
                pattern = self.watch_filepattern
                newlastid = self.makeCaptcha(1, pattern)

                with open(self.preindexpath, 'wb') as f:
                    f.write("%s 1 %s" % (pattern, newlastid))
            elif lastid - currentid <= self.watch_minthreshold: # continue from the last id
                newlastid = self.makeCaptcha(lastid, pattern)

                # Update the new last id into the index file
                with open(self.preindexpath, 'r+b') as f:
                    (pattern, currentid, lastid) = f.read().strip().split(' ')
                    f.seek(0) # place the cursor at the beginning of the file to overwrite everything
                    f.write("%s %s %s" % (pattern, currentid, newlastid))

            # Sleep a bit until next iteration
            time.sleep(self.watch_delay)


    def spawnCoroutine(self):
        '''
        Spawn the captcha watcher coroutine
        '''
        process = Process(target=call_it, args=(self, 'watchCaptcha'))
        process.start()
        return True


    def getCaptcha(self):
        '''
        Get a captcha image and returns the captcha id (either pick in pregenerated captchas or generate on-the-fly)
        '''

        # Get a pregenerated captcha image if available
        try:
            if not hasattr(self, 'preindexpath'):
                raise Exception("Pregeneration of captcha images disabled")

            with open(self.preindexpath, 'r+b') as f:

                # Read the parameters
                (pattern, currentid, lastid) = f.read().strip().split(' ')
                lastid = int(lastid)
                currentid = int(currentid)

                # Check that we are not out of range
                if lastid - currentid < 0:
                    raise Exception('Pregenerated image index out of range')

                # Save the new data as soon as possible to avoid race conditions
                # Note about race conditions: if the image was already taken, no problem: we generate a new image on the fly, and since we still incremented the counter, next time the currentid should be OK (if not it will be increased another time, etc..)
                nextid = int(currentid) + 1
                f.seek(0) # place the cursor at the beginning of the file to overwrite everything
                f.write("%s %s %s" % (pattern, nextid, lastid)) # increment the current id cursor and save it in the index file

                # Get the captcha
                cid = self.captchagen.randomID() # we generate a captcha id
                shutil.move(os.path.join(self.precpath, "%s%s.jpg" % (pattern, currentid)), os.path.join(self.cpath, "%s.jpg" % cid))
                shutil.move(os.path.join(self.presolpath, "%s%s.rle" % (pattern, currentid)), os.path.join(self.solpath, "%s.rle" % cid))
                try: # try to also move the png files if debugPng is enabled
                    shutil.move(os.path.join(self.presolpath, "%s%s.png" % (pattern, currentid)), os.path.join(self.solpath, "%s.png" % cid))
                except:
                    pass

                if lastid - currentid < self.watch_minthreshold and not self.watching:
                    self.watching = True
                    self.spawnCoroutine()

        # Else we create a new captcha image on-the-fly
        except:
            # List files in pre folders: if at least one is available in both folders with same name then OK
            cid = self.captchagen.renderCaptcha(self.cpath, self.solpath)

        return cid

    def checkCaptcha(self, cid, x, y):
        '''
        Check a captcha response and delete the captcha
        '''
        result = captchachecker.checkSolution(self.solpath, cid, x, y)
        self.delCaptcha(cid)
        return result

    def delCaptcha(self, cid):
        '''
        Delete a captcha (client image and solution mask)
        '''
        os.remove(os.path.join(self.cpath, "%s.jpg" % cid))
        os.remove(os.path.join(self.solpath, "%s.rle" % cid))
        return True

if __name__ == '__main__':
    width = 320
    height = 240
    cpath = 'solmasks'
    solpath = cpath
    precpath = 'solmaskspre'
    presolpath = precpath

    cm = CaptchaManager(precpath, presolpath, preindexpath='preindex.txt', watch_delay=3, watch_minthreshold=1, watch_maxthreshold=4, showRefModel=True, showRefName=True, debugPng=True, debug=False, nbElem=4, modelsPath='bammodels', windowWidth=width, windowHeight=height)
    #cm.spawnCoroutine()
    #cm.watchCaptcha()
    print cm.getCaptcha()
