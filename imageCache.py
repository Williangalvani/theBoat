__author__ = 'Will'
import urllib
from os.path import abspath, dirname, join
import os
from PIL import Image
import traceback
import time
import pygame
WHERE_AM_I = abspath(dirname(__file__))

cachedir = join(WHERE_AM_I, "cache")


class Tile(pygame.sprite.Sprite):
    # Constructor. Pass in the color of the block,
    # and its x and y position
    def __init__(self, imagefile):
        self.filename = imagefile
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(imagefile)
        self.rect = self.image.get_rect()

    def __repr__(self):
        return self.filename


def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)


def try_to_remove(filename):
    try:
        os.remove(filename)
    except:
        print "could not delete" , filename

class ImageLoader(object):
    def __init__(self):
        self.address = "http://mt0.google.com/vt/lyrs=y&hl=en&x={0}&s=&y={1}&z={2}"

    def getCache(self):
        filename = join(WHERE_AM_I, "loading.png")
        return Tile(filename)

    def remove(self,x,y,z):
        level_dir = join(cachedir, str(z))
        filename = join(level_dir, "{0}-{1}.png".format(x,y))
        print "removing" , filename
        try:
            os.remove(filename)
        except Exception, e:
            print e

    def get_image(self, lat, long, level):
        got_image = False
        lat = int(lat)
        long = int(long)
        level = int(level)
        level_dir = join(cachedir, str(level))
        ensure_dir(level_dir)
        filename = join(level_dir, "{0}-{1}.png".format(lat, long))
        try:
            image = open(filename)
            image.close()
            got_image = True
        except Exception , e:
            #print e
            pass

        if not got_image:
            image_url = self.address.format(lat, long, level)
            print "miss, loading image from " , image_url
            temp_file = open(filename,'wb')
            temp_file.write(urllib.urlopen(image_url).read())
            temp_file.close()
        return filename
        #image = Tile(filename)
        #print image , type(image)
        #return image
