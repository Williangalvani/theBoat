from os.path import abspath, dirname

#http://maps.googleapis.com/maps/api/staticmap?center=#X,#Y&zoom=#Z&size=200x200&sensor=false
WHERE_AM_I = abspath(dirname(__file__))
from tileLoader import TileLoader
from math import ceil
from datetime import datetime
from horizon.horizon import Horizon
import sys
import pygame
from pygame.locals import *
from comm import TelemetryReader

if not pygame.font: print 'Warning, fonts disabled'
if not pygame.mixer: print 'Warning, sound disabled'


#   import pdb

class MyApp(object):

    def __init__(self, width=320,height=240):
        pygame.init()
        self.width = width
        self.height = height

        """Create the Screen"""
        self.screen = pygame.display.set_mode((self.width,self.height),HWSURFACE | RESIZABLE | DOUBLEBUF,32 )
        pygame.display.toggle_fullscreen()
        self.last_scroll = datetime.now()


        self.window = self.screen
        self.FPS = 60
        self.FPSCLOCK = pygame.time.Clock()
        self.longitude = 23.824245
        self.latitude =  62.790583 
        self.points = [(self.longitude,self.latitude),(0.0,0.0),(180,36.8),(-47.886829,-15.793751)]
        self.tracked = [0,0]
        self.tracking = True
        self.zoom = 17
        self.button = 0
        self.x,self.y = 0,0
        self.pointer_x = 0
        self.pointer_y = 0
        self.dx = 0
        self.dy = 0
        self.to_draw = True
        self.sprites = None
        self.draw_gui_only_flag = False
        # Connect signals
        self.tile_loader = TileLoader(self)
        #self.window.show()
        self.sprites = pygame.sprite.Group()    
        self.instruments = pygame.sprite.Group()
       # self.horizon = Horizon()
        self.telemetry_reader = TelemetryReader(self)
        self.main_loop()
        print "init done"


    def zoom_in(self,widget = None,event = None):
        self.zoom+=1
        if self.zoom>20:
            self.zoom = 20

    def zoom_out(self,widget = None,event = None):
        self.zoom-=1
        if self.zoom < 2:
            self.zoom = 2
        print self.zoom

    def on_scroll(self,zoom_in):
        if (datetime.now() - self.last_scroll).microseconds > 100000:
            if zoom_in: # UP
                self.zoom_in()
            else:
                self.zoom_out()
            self.queue_draw()
            self.last_scroll = datetime.now()

    def on_click(self,event):
        #print self.tile_loader.cache["loading"]
        if event.button ==1:
            self.button = event.button
        elif event.button ==4:
            self.on_scroll(1)
        elif event.button ==5:
            self.on_scroll(0)
    def on_release(self,event):
        self.button = 0


    def set_zoom(self,zoom):
        self.zoom = zoom

    def set_focus(self,long,lat):
        self.longitude = long
        self.latitude = lat



    def on_move(self,event):
        x, y = event.pos
        dx = x-self.pointer_x
        dy = y - self.pointer_y
        self.pointer_x, self.pointer_y = x, y
        if self.button == 1:
            dlongitude, dlatitude = self.tile_loader.dpix_to_dcoord(dx, self.latitude, dy, self.zoom)
            self.longitude -= dlongitude
            self.latitude -= dlatitude
           # print "dragged"

            if self.longitude >  180:
                self.longitude = 180.0
            if self.longitude <  -180:
                self.longitude = -180.0
            if self.latitude >  85.0:
                self.latitude = 85.0
            if self.latitude <  -85.0:
                self.latitude = -85.0

            self.queue_draw()

    def draw_center_circle(self, x_pos, y_pos):
        pygame.draw.circle(self.screen, (255,0,0), (int(x_pos),int(y_pos)), 5, 2)


    def draw_cross(self):
        x_center = self.width/2# - 128
        y_center = self.height/2# -
        pointsx = [(x_center+10,y_center),
                  (x_center-10,y_center)]
        pointsy = [(x_center,y_center+10),
                  (x_center,y_center-10)]

        pygame.draw.lines(self.screen, (0,0,0), False, pointsx, 2)
        pygame.draw.lines(self.screen, (0,0,0), False, pointsy, 2)



    def drawInfo(self):
        pending = len(self.tile_loader.pending_tiles) + len(self.tile_loader.loading_tiles)
        font = pygame.font.Font(None, 24)
        height = 0
        width = 0
        texts = ["{0} pending tiles".format(pending),
                 "long:{0}".format(self.longitude),
                 "lat: {0}".format(self.latitude)]
        gtexts = [font.render(text, 1, (10, 10, 10)) for text in texts]

        try:
            height = gtexts[0].get_rect().height
            width = 0
            for text in gtexts:
                twidth = text.get_rect().width
                if twidth > width:
                    width = twidth
        except:
            pass


        gui = pygame.Surface((width,height*len(gtexts)))
        gui.set_alpha(180)
        gui.fill((127,127,127))
        self.screen.blit(gui,(0,0))


        current_z = 10
        for text in gtexts:
            textpos = text.get_rect()
            textpos.centery = current_z
            current_z = current_z + textpos.height
            self.screen.blit(text, textpos)


    def draw_points(self):
        for point in self.points:
            x,y = self.tile_loader.dcord_to_dpix(point[0],self.longitude,point[1],self.latitude,self.zoom)
            self.draw_center_circle(x+self.width/2,y+self.height/2)

    def draw_tracked_object(self):
        if self.tracking:
            point = self.tracked
            x,y = self.tile_loader.dcord_to_dpix(point[0],self.longitude,point[1],self.latitude,self.zoom)
            self.draw_center_circle(x+self.width/2,y+self.height/2)

    def set_tracked_position(self,longitude,latitude):
        if self.tracked[0] != longitude or self.tracked[1] != latitude:
            self.tracked = (longitude,latitude)
            self.latitude = latitude
            self.longitude = longitude
            self.queue_draw()

    def set_attitude(self,roll,pitch,yaw=0):
        pass
    #    if self.horizon.tilt != pitch or self.horizon.roll != roll or self.horizon.yaw != yaw:
   #         self.horizon.tilt = pitch
  #          self.horizon.roll = roll
 #           self.horizon.yaw = yaw
#            self.queue_draw(True)


    def draw_tiles(self):
        span_x = self.width
        span_y = self.height
        tiles_x = int(ceil(span_x/256.0))
        tiles_y = int(ceil(span_y/256.0))

        tiles = self.tile_loader.load_area(self.longitude,self.latitude,self.zoom,tiles_x,tiles_y)
        tile_number=0
        line_number=0

        self.sprites.empty()

        x_center = self.width/2# - 128
        y_center = self.height/2# - 128
        offset_x,offset_y = self.tile_loader.gmap_tile_xy_from_coord(self.longitude,self.latitude,self.zoom)

        xtiles = len(tiles[0])
        ytiles = len(tiles)

        self.screen.fill((1,1,1))
        for line in tiles:
            for tile in line:
                x = (tile_number - int(xtiles/2)) * 256 + x_center
                y = (line_number - int(ytiles/2)) * 256 + y_center
                finalx = x - offset_x  +128
                finaly = y - offset_y  +128
                tile.rect.centerx= finalx+self.dx
                tile.rect.centery =finaly+self.dy
                self.sprites.add(tile)
                tile_number += 1
            tile_number = 0
            line_number += 1


        self.sprites.draw(self.screen)
        self.to_draw = False

    def draw(self):
        self.draw_tiles()
        self.draw_gui()
        pygame.display.flip()

    def draw_gui(self):
        self.drawInfo()
        self.draw_cross()
        self.draw_points()
        self.draw_tracked_object()
        self.draw_instruments()

    def draw_gui_only(self):
        self.sprites.draw(self.screen)
        self.draw_gui()
        pygame.display.flip()

    def draw_instruments(self):
        pass
        #bottom = self.height-self.horizon.newsurf.get_rect().height
        #self.horizon.update()
        #self.screen.blit(self.horizon.newsurf,(0,bottom))


    def queue_draw(self,gui_only=False):
        self.to_draw = not gui_only
        self.draw_gui_only_flag = gui_only

    def main_loop(self):
        """This is the Main Loop of the Game"""
        while 1:
            if self.to_draw:
                self.draw()
            if self.draw_gui_only_flag:
                self.draw_gui_only()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.tile_loader.run = 0
                    self.telemetry_reader.run = False
                    sys.exit()
                elif event.type == pygame.MOUSEMOTION:
                    self.on_move(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.on_click(event)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.on_release(event)
                elif event.type == pygame.VIDEORESIZE:
                    self.width = event.w
                    self.height= event.h
                    self.screen = pygame.display.set_mode((self.width
                                               , self.height),RESIZABLE)
                    self.draw()
            self.FPSCLOCK.tick(self.FPS)



if __name__ == '__main__':
    gui = MyApp()
    #pdb.set_trace()
    #Gtk.main()
