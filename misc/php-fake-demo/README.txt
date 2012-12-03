This is a PHP fake demo for waCaptcha.

This is used on my own website to demonstrate how waCaptcha concretely works, but without a really working waCaptcha server.

It's only a rewrite from Python in PHP of the form generator + RLE fixed-column-size format reader.

So you just have to drop in a few pregenerated images by your server, and voilà! You've got an online fake demo :)

WARNING: this is NOT meant to be used in production, because there's no security nor management of captchas (you will always get the same captchas, there's no generation of new ones nor deletion of old ones!).
