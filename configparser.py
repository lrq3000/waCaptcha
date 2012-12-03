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

from auxlib import *

json = import_module('ujson')
if json is None:
    json = import_module('json')
    if json is None:
        raise RuntimeError('Unable to find a json implementation')

class ConfigParser:
    def __init__(self, configpath):
        self.configpath = configpath
        self.config = []

    def loadconfig():
        try:
            f = open('testmask.rle', 'rb') # open in binary mode to avoid line returns translation (else the reading will be flawed!). We have to do it both at saving and at reading.
            self.config = json.loads( f.read() )
            f.close()
            return True
        except:
            return False

    def saveconfig():
        try:
            f = open(self.configpath, 'wb') # open in binary mode to avoid line returns translation (else the reading will be flawed!). We have to do it both at saving and at reading.
            f.write( json.dumps(self.config, sort_keys=True, indent=4) ) # write the config as a json serialized string, but beautified to be more human readable
            f.close()
            return True
        except:
            return False
