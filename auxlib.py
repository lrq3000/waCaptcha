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

import sys, exceptions

def import_module(module_name):
    ''' Reliable import, courtesy of Armin Ronacher '''
    try:
        __import__(module_name)
    except ImportError:
        exc_type, exc_value, tb_root = sys.exc_info()
        tb = tb_root
        while tb is not None:
            if tb.tb_frame.f_globals.get('__name__') == module_name:
                raise exc_type, exc_value, tb_root
            tb = tb.tb_next
        return None
    return sys.modules[module_name]

def str2int(s):
    ''' Convert a string to int '''
    try:
        return int(s)
    except exceptions.ValueError:
        return int(float(s))

import os, random

def fastRandLine(file, exceptlist=None, exceptposlist=None, maxit=100):
    ''' Clever random line picker, courtesy of Jonathan Kupferman
    Enhanced to accept exceptions lists to avoid picking twice the same line we don't want
    The exception list based on cursor position is a bit more optimized than the one based on string content comparison
    '''
    close_flag = False
    if isinstance(file, str):
        file = open(file,'r')
        close_flag = True

    #Get the total file size
    #file_size = os.stat(filename)[6]
    file_size = os.fstat(file.fileno()).st_size

    # We use a loop in case we specified a list of exception (lines to NOT accept in the random pool)
    flag = 1
    it = 0
    while flag:
        #Seek to a place in the file which is a random distance away
        #Mod by file size so that it wraps around to the beginning
        file.seek((file.tell()+random.random()*(file_size-1))%file_size)

        #dont use the first readline since it may fall in the middle of a line UNLESS we are at the beginning of the file
        if file.tell() > 0:
            file.readline()

        # Get the current position (for the exception list based on cursor position)
        curpos = file.tell()
        # If we have specified a list of exception based on cursor position (faster than the exception list based on line comparison)
        if exceptposlist and \
            curpos in exceptposlist: # and if the current position is in the list of exceptions, we are not good!
            flag = 1
        # No exception list based on cursor position, OR the current cursor position is not in the list of exception, then we continue
        else:

            #this will return the next (complete) line from the file (the line we may want to return if not in exception list)
            line = file.readline()
            line = line.strip() # strip line endings, necessary for string comparison

            # If we have a list of exceptions based on line content
            if (exceptlist and \
                line in exceptlist) or \
                not line: # and if the line is found in this list, we are not good! (also if the line is empty, because we have tried to read last line + 1, we're not good!)
                    flag = 1

            # Else, we have passed all the exceptions checks, we are OK!
            else:
                flag = 0 # end of loop

        # Avoid infinite loop
        it += 1
        if it > maxit:
            return None

    if close_flag:
        file.close()

    #here is your random line in the file
    return (line, curpos)

def call_it(instance, name, args=(), kwargs=None):
    "indirect caller for instance methods and multiprocessing"
    if kwargs is None:
        kwargs = {}
    return getattr(instance, name)(*args, **kwargs)


# Some debug testing here
if __name__ == '__main__':
    print cacheListOfModels('models', 'modelscache.txt')
    f = open('modelscache.txt', 'rb')
    e1 = []
    e2 = []
    for i in xrange(20):
        (line, cur) = fastRandLine(f, e1, e2)
        e1.append(line)
        e2.append(cur)
        print line
    f.close()
