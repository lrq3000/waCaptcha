waCaptcha
=========

A 3D Captcha whose goals are to be both fun and useful!

Demo
----

If you want to try this captcha out for yourself, an online (fake) demo can be found at:

http://customfields.org/wacaptcha/

Please bear in mind that this is only a fake demo to demonstrate an overview usage of the captcha: the captcha images are not generated on the fly and there's no security. Thus you may see twice the same image (there's only a limited set in this demo).

When the real captcha server is working, captcha images are generated on-the-fly and you will never see the same image twice, plus you get a lot more security.

Description
-----------

Do you know about the game Where's Waldo? Then you will quickly understand how this captcha works and how it is different from others: here you don't have to decipher a very weirdly distorded text, but you just have to recognize and click on an object you have to recognize.

It may sound complicated at first, but if you try it, you'll see it's quite easy in fact. Quite easy for humans, that is.

The core idea is to exploit the limits of today's algorithms in Computer Vision by generating an artificial natural scene, and assigning a maximum of variance in the 3D scene with random parameters, as opposed to adding variance on a 2D image as usual captchas do.

There are a lot more parameters in a 3D scene that can be varied than in a 2D image, thus such a scene can be a lot more complex. Moreover, you will never get the same scene twice.

Here is a list of variance that are currently implemented:
- Rotation
- Partial obstruction
- Translation
- Colour
- Size

We will be adding more variance in the next releases.

Goals
-----

This project's goal is two-folds:
- be used as a human-friendly captcha to prevent spam
- be used for Computer Vision research as a quick testing framework to simulate natural scenes, with instant feedback and an infinite database of images for researchers to try their Computer Vision algorithms.

Technology
----------

The software is written in Python 2.7 and uses Panda3D 1.8 to generate the 3D scenes and images. You don't need a graphic card, this can all run on CPU.

It also uses KineticJS for the Javascript interface, but it's optional. Without Javascript, the captcha is automatically and totally HTML compliant so you can use it without Javascript at all.

License
-------

This software is licensed under Affero GNU Public License (AGPL) v3.0

However, you CAN use it in a commercial closed product: since the software is meant to be used as a web api, it can be considered as a case of linking (just like the Piwik project), and thus you can use it in your closed source commercial software.

Also, if you modify it, you just have to put online the sources of the modifications of this software only, you don't have to open source your own software (because as I said, this is only linking if you use it via the web api).

Current status
--------------

The software is currently at an alpha stage, but should soon reach beta.

To use it, either launch:
ppython webapirest.py
(ppython is installed with Panda 3D 1.8)

Or you can just launch any of the Python files to trigger different functionalities, for example to pregenerate images, launch:
ppython captchagenerator.py

This will be cleaned up in the next releases and replaced by commandline arguments on the main.py

What's remain to be done
------------------------

Oh a lot :)

But more urgent features include:
MILESTONE1 - BETA1:
- Background generation of images using a subprocess (to avoid web api lag on client's request)
- Configuration wrapper (there's no config file for now)
- Optimize a bit the RLE compression code
- Commandline arguments and main.py file (there's no main for now!)
- A reload button when the captcha is too hard or too old.
- Radiometrie variance (histogram background blending of objects)
- Add more standard security (IP logging, number of retries in a lapse of time, etc..)
LATER:
- A lot of other stuffs in my todo, will post them later...

A lot of debug tools are included to make profiling and optimization a lot easier and faster.

Acknowledgments
---------------

Thank's to the Panda3D community and developpers for their great help. I am not a game designer so it was a tough project for me at the beginning when I had to make 3D scenes on the fly, and they were a great help.

The Stanford's online AI class by Sebastian Thrun and Peter Norvig which taught me a lot and gave me the idea to do this project.
