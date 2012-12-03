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

import Image, itertools as its, re
from auxlib import *

class RLEImage:
    ''' Manage images in fixed-columns-size RLE, and thus the produced image can be randomly accessed (at least for the row, the columns can't be directly accessed but it's very easy and quick to process them in a loop) '''

    def __init__(self, debug=False):
        self.debug = debug
        # Regular Expression to find all RLE pairs of (nbpixels,colorvalue)
        self._re_pixel_get = re.compile(r'((\d+)([a-zA-Z]+))', re.IGNORECASE)

    @staticmethod
    def runlength_dec(xs):
        '''Expand a run-length encoded stream.

        Each element of xs is a pair, (count, x).

        >>> ys = runlength_dec(((3, 'A'), (2, 'B')))
        >>> next(ys)
        'A'
        >>> ''.join(ys)
        'AABB'
        '''
        return its.chain.from_iterable(its.repeat(x, n) for n, x in xs)

    @staticmethod
    def ilen(it):
        '''Return the length of an iterable.

        >>> ilen(range(7))
        7
        '''
        return sum(1 for _ in it)

    @staticmethod
    def runlength_enc(xs):
        '''Return a run-length encoded version of the stream, xs.

        >>> ys = runlength_enc('AAABBCCC')
        >>> next(ys)
        Run(count=3, value='A')
        >>> list(ys)
        [Run(count=2, value='B'), Run(count=3, value='C')]
        '''
        ilen = RLEImage.ilen
        return [("%s%s" %(ilen(gp), ('B' if x=='0' else 'W'))) for x, gp in its.groupby(xs)]

    def openImage(self, path):
        ''' Open an image using PIL '''
        self.image = Image.open(path)
        self.width, self.height = self.image.size
        return (self.image, self.width, self.height)

    def getPixelsListInRows(self, width=None, height=None, image=None):
        ''' Return a list of the pixels from the image, organized in rows '''
        if not image:
            image = self.image
        if not width or not height:
            width, height = image.size
        #help(image.getdata)
        pixels = list(image.getdata())
        pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]
        return pixels


    def encodePixels(self, pixels):
        ''' Encode a list of pixels into a fixed RLE encoded string (rows being of the same size, thus it can be used for random access using a pointer) '''
        maxcol = 0
        # First pass: we encode every columns of each row in RLE, and we find the biggest RLE string (maximum columns)
        strlist = []
        runlength_enc = RLEImage.runlength_enc # optimization
        for row in pixels:
            #print(row)
            rlestr = ''.join([str(item) for item in row]) # First we merge every pixel's intensity in the row in a string
            tmp = ''.join(runlength_enc(rlestr)) # we encode the string in RLE
            strlist.append(tmp) # add this row into our list
            curcol = len(tmp) # compute the length of the current row
            if curcol > maxcol: # get the maximum columns size
                maxcol = curcol

        # Second pass: we pad every row to a fixed size (the maximum columns we computed previously)
        strlist2 = []
        for row in strlist:
            dlen = maxcol - len(row) # compute the delta length (difference of length between the current row's length and the fixed length)
            strlist2.append(row+"0"*dlen)  # pad the missing length with zeros

        # Finally: merge every rows in a string
        strenc = ''.join(strlist2)

        if self.debug:
            print(strenc)
            print("maxcol: %s" %maxcol)

        self.maxcol = maxcol
        return (maxcol, strenc)

    def forgeHeaders(self, height, width, maxcol):
        ''' headers are in the following format: 3DC R/C ROWSxCOLUMNS COLSIZE HEADERSLENGTH
        where 3DC is a constant, R/C is the run-length encoding direction (row or column)
        ROWSxCOLUMNS the original size of image
        COLSIZE the fixed number of columns/bytes for every row of the run-length encoding (not of the image!) - this allows to directly access a specific row without loading the whole image in memory
        HEADERSLENGTH is the precise length of the headers, this is necessary to be able to do a random access from the beginning of the file, using something like hlen+y*colsize
        '''
        headers = "3DC R %sx%s %s" % (height,width,maxcol)
        # Compute the precise length of the headers line
        hlen = len(headers) + 2
        hlen += len("%s" % hlen) # add the size of the length +2 because of the space and line return
        headers += " %s\n" % hlen # append the length in the string
        return headers

    def getHeaders(self, str=None):
        ''' Decode the RLE image parameters from a string '''
        if not str:
            str = self.headers

        id, dir, size, maxcol, hlen = str.strip().split(' ')
        height, width = size.split('x')
        return int(height), int(width), int(maxcol), int(hlen)

    def getPixelValue(self, row, x):
        ''' Return the intensity value of a pixel from a given RLE encoded row (string format)
        This function works by looping into each range stored in the RLE encoded row, and find if the given x position fits in any of these ranges
        This is both easy on CPU and easy on RAM because we don't have to unpack the whole list of pixels, we just loop over the ranges (so we have a lot less number of iterations)
        '''

        # Get all RLE pairs of (nbpixels,colorvalue)
        m = re.findall(self._re_pixel_get, row)

        # Loop through each pair until we hit the right x position, or until we reach the end of row
        lastpos = 0 # relative pointer to know our absolute position in the row
        for _, xrange, color in m: # for each RLE pair
            xrange = int(xrange) # convert nbpixels from string to int...
            if lastpos <= x <= (xrange+lastpos): # if the x position fits in the current range, then it's OK!
                return color # return the color of this range and of the pixel at x
            else: # else the x position does not fit, it's necessarily above the current range, so we go to the next iteration
                lastpos += xrange # remember the current absolute position

            if self.debug:
                print("%s%s" % (xrange, color))

        return None # Return None if no value was found


    def save(self, path, str):
        f = open(path, 'wb') # open in binary mode to avoid line returns translation (else the reading will be flawed!). We have to do it both at saving and at reading.
        f.write(str)
        f.close()

    def open(self, path):
        ''' Open a fixed RLE encoded image and returns the headers infos '''
        self.image = open(path, 'rb') # open in binary mode to avoid line returns translation (else the reading will be flawed!). We have to do it both at saving and at reading.
        self.headers = self.image.readline()
        headerslist = self.getHeaders(self.headers)
        self.height, self.width, self.maxcol, self.hlen = headerslist

        if self.debug:
            print(self.headers)
            print(len(self.headers))
            print(self.getHeaders(self.headers))

        return (self.image, headerslist)

    def getRow(self, y, image=None, maxcol=None, hlen=None):
        ''' Get a row from a fixed RLE encoded image, directly from file and with random access '''
        if not maxcol:
            maxcol = self.maxcol
        if not hlen:
            hlen = self.hlen
        if not image:
            image = self.image

        #image.seek(f.tell()) # relative seeking
        #image.seek(maxcol*y, 1) # relative seeking
        image.seek(hlen + maxcol*y, 0) # absolute seeking: position to the beginning of the row
        row = image.read(maxcol) # read the entire row
        return row # return the row

    def checkPixelValue(self, x, y, color='W', img=None, width=None, height=None):
        ''' Check the intensity value of a pixel, given its coordinate, and a reference color: true if same, false if different '''

        if not width:
            width = self.width
        if not height:
            height = self.height

        # Make sure the parameters are integers
        x = str2int(x)
        y = str2int(y)

        # Get the row from the file
        row = self.getRow(y, image=img)

        # Check that the given positions are in a valid range
        if x < 0 or y < 0 or x > width or y > height:
            print('Pixel position outside range: %i %i' % (x,y))
            return None

        # Check if the pixel's color match the reference color
        if color == self.getPixelValue(row, x): # match, return true
            return True
        else: # different, return false
            return False

    def convertImageToRLE(self, inpath, outpath):
        ''' Facade function to convert an image into fixed columns size RLE '''
        # Open the original image
        (image, width, height) = self.openImage(inpath)
        # Get the list of pixels in rows
        pixels = self.getPixelsListInRows(width, height, image)
        # RLE encode the pixels
        (maxcol, strenc) = self.encodePixels(pixels)
        # Forge the RLE image headers
        headers = self.forgeHeaders(height, width, maxcol)
        # Save the headers+encoded pixels into an RLE image
        self.save(outpath, headers+strenc)
        # Free memory
        del image

    def openAndCheck(self, path, x, y, color='W'):
        ''' Facade function to open an RLE image and directly check the pixel '''
        (image, headers) = self.open(path) # open RLE image
        result = self.checkPixelValue(x, y, color) # check the pixel value directly from the file
        del image # free memory
        return result


# Some debug testing here
if __name__ == '__main__':

    xy = "1162:401"
    (x, y) = xy.split(':')

    rle = RLEImage(debug=False)
    rle.convertImageToRLE('solmasks/2b0dd73eb4e58c48b02f7d2f924a0ff.png', 'solmasks/2b0dd73eb4e58c48b02f7d2f924a0ff.rle')
    del rle

    rle = RLEImage(debug=False)
    result = rle.openAndCheck('solmasks/2b0dd73eb4e58c48b02f7d2f924a0ff.rle', x, y)
    del rle
    print("Resultat est: %s" % result)
