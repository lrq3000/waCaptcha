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

import os, sys
pathname = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(pathname, 'lib'))

import tornado.ioloop
import tornado.web

# from captchagenerator import CaptchaGenerator, CaptchaChecker
from captchamanager import CaptchaManager
from formgenerator import FormGenerator

width = 320
height = 240
cpath = 'solmasks'
solpath = cpath
precpath = 'solmaskspre'
presolpath = precpath

cm = CaptchaManager(cpath=cpath, solpath=solpath, precpath=precpath, presolpath=presolpath, preindexpath='preindex.txt', watch_delay=3, watch_minthreshold=1, watch_maxthreshold=4, showRefModel=True, showRefName=True, debugPng=True, debug=False, nbElem=4, modelsPath='bammodels', windowWidth=width, windowHeight=height)
#cm.spawnCoroutine()
#cm.watchCaptcha()

baseUrl = r'http://localhost/captcha/'
# baseUrl = r'file:///C:/Panda3D-1.8.0/samples/Carousel/captcha-core/' # works when copying the file locally, but doesn't work in browser

import Image
import cStringIO as StringIO

class MetaHandler(tornado.web.RequestHandler):
    def set_extra_headers(self, path):
        self.set_header("Cache-control", "no-cache")
        self.set_header("Expires", "0")
        self.set_header("Pragma", "no-cache") # Normally used by browsers, not by servers, but some user agents that we want to keep the image out of the cache...
        self.set_header("Connection", "close")

class MainHandler(MetaHandler):
    def get(self):
        name = self.get_argument('name', 'World')
        self.write("Hello, "+name+"!")

class TestHandler(MetaHandler):
    def get(self):
        name = self.get_argument('name', 'World')
        self.write("Test, "+name+"!")

class CaptchaGetUrlHandler(MetaHandler):

    def get(self):
        ip = self.get_argument('ip', None)

        cid = cm.getCaptcha()
        self.write( "%s%s/%s.jpg" % (baseUrl, cpath, cid) )

        self.finish()

class CaptchaGetImageHandler(MetaHandler):

    def get(self):
        ip = self.get_argument('ip', None)

        cid = cm.getCaptcha()

        image = Image.open( "%s/%s.jpg" % (cpath, cid) )

        imgbuff = StringIO.StringIO()
        image.save(imgbuff, format='JPEG')
        self.set_header('Content-Type', 'image/jpg')
        imgbuff.seek(0)
        self.write(imgbuff.read())

        self.finish()

class CaptchaGetFormHandler(MetaHandler):

    def get(self):
        ip = self.get_argument('ip', None)
        embed = self.get_argument('embedImage', False)

        fg = FormGenerator()

        cid = cm.getCaptcha()

        if embed:
            form = fg.generateForm(cpath, cid, width*2, height, embedImage=True)
        else:
            form = fg.generateForm("%s%s" % (baseUrl,cpath), cid, width*2, height, embedImage=False)

        self.write( form )

        self.finish()


class CaptchaPostResponseHandler(MetaHandler):

    def post(self):
        ip = self.get_argument('ip', None)
        cid = self.get_argument('cid', None)
        csol = self.get_argument('csol', None)
        nojs_csol_x = self.get_argument('nojs_csol_x', None)
        nojs_csol_y = self.get_argument('nojs_csol_y', None)

        if not csol or csol.lower() == 'null' or not len(csol):
            x = nojs_csol_x
            y = nojs_csol_y
        else:
            (x, y) = csol.split(':')

        result = cm.checkCaptcha(cid, x, y)

        if result:
            self.write('OK')
        else:
            self.write('KO')

        self.finish()

settings = {
    "gzip": True # accept gunzip encoding
}

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/test", TestHandler),
    (r"/captcha/geturl", CaptchaGetUrlHandler),
    (r"/captcha/getimage", CaptchaGetImageHandler),
    (r"/captcha/getform", CaptchaGetFormHandler),
    (r"/captcha/postresponse", CaptchaPostResponseHandler),
], **settings)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

    # For Google AppEngine, use WSGI:

    #import tornado.web
    #import tornado.wsgi
    #import wsgiref.handlers

    #application = tornado.wsgi.WSGIApplication([
    #        (r"/", MainHandler),
    #    ])
    #wsgiref.handlers.CGIHandler().run(application)