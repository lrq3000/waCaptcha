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

import os, random

class FormGenerator:

    def generateImageURL(self, cpath, cname):
        return None

    def generateForm(self, cpath, cname, imageWidth, imageHeight, embedImage=False):
        cweburl = "%s/%s.jpg" %(cpath, cname)

        kineticJS = self.includeLib(r'kineticjs-custombuild.js')

        randomString = hex(random.getrandbits(128))[2:-1] # used to force the refresh of css background images (prevent the browser from misleading caching it, and forget to reload it if it has the same name when in fact it's a completely different image)

        if embedImage:
            im = open(cweburl, 'rb')
            imstr = "data:image/jpeg;base64,%s" % im.read().encode("base64").replace("\n",'')
            im.close()
        else:
            imstr = cweburl+r'?forcerefresh='+randomString

        form = """
    <style>
      #captcharcanvas {
        background: url('"""+imstr+"""');
        display: inline-block;
        overflow: hidden;
        width: """+str(imageWidth)+"""px;
        height: """+str(imageHeight)+"""px;
      }
    </style>

    <script>
    """+kineticJS+"""
    </script>

    <script type='text/javascript'>//<![CDATA[
    window.onload=function(){

        var stage = new Kinetic.Stage({
          container: 'captcharcanvas',
          width: """+str(imageWidth)+""",
          height: """+str(imageHeight)+"""
        });
        var layer = new Kinetic.Layer();

        var base = new Kinetic.Rect({
            x:0,
            y:0,
            width:stage.getWidth(),
            height:stage.getHeight(),
            stroke:0
        });

        var targrect = new Kinetic.Rect({
            x: -3,
            y: -3,
            width: 6,
            height: 6,
            stroke: 'blue',
            strokeWidth: 2
        });

        var targcircle = new Kinetic.Circle({
          x: 0,
          y: 0,
          radius: 20,
          stroke: 'red',
          strokeWidth: 7,
          draggable: true
        });

        var target = new Kinetic.Group({
            draggable: true
        });

        target.add(targrect);
        target.add(targcircle);

        base.on('mousedown tap', function() {
            var mousePos = stage.getMousePosition();
            var x = mousePos.x - target.getX();
            var y = mousePos.y - target.getY();
            var x = mousePos.x - target.getX();
            var y = mousePos.y - target.getY();
            layer.clear();
            target.move(x,y);
            layer.draw();
            document.getElementById("csol").value = Math.round(target.getX()) + ":" + Math.round(target.getY());
        });

        target.on('dragend', function() {
            var mousePos = stage.getMousePosition();
            document.getElementById("csol").value = Math.round(target.getX()) + ":" + Math.round(target.getY());
        });


        layer.add(base);
        layer.add(target);
        base.moveToTop();
        target.moveToTop();

        stage.add(layer);

    }//]]>
    </script>

    <noscript>
        <input type="image" name="nojs_csol" src='"""+imstr+"""' title="Click on the reference object to pass the captcha test" alt="Click on the reference object to pass the captcha test" />
        <input type="submit" style="display: none;" /> <!-- For FireFox, else it will automatically add a submit button even when it's not needed. //-->
        <style>
            /* Hide the javascript captcha image */
            #captcharcanvas {
                background-image: none;
                display: none;
            }
        </style>
    </noscript>
    <div id="captcharcanvas"></div>
    <input type="text" name="csol" id="csol" value="NULL" />
    <input type="text" name="cid" id="cid" value='"""+cname+"""' />
    """

        return form

    def includeLib(self, path):
        f = open(path, 'rb')
        libcontent = f.read()
        f.close()
        return libcontent


# Some debug testing here
if __name__ == '__main__':

    fg = FormGenerator()

    form = fg.generateForm('solmasks', '8db596f9859088b7c3e951f1a6708175', 640, 240)
    f = open('formtest.html', 'wb')
    f.write(form)
    f.close()
    #captcha.renderCaptchaMulti(10, 'solmasks', 'solmasks')