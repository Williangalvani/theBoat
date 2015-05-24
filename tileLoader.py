__author__ = 'Will'

from math import sin, cos, log , pi
import threading
import time

from imageCache import ImageLoader


class FuncThread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args

        threading.Thread.__init__(self)

    def run(self):
        self._target(*self._args)


class TileLoader():
    def __init__(self,window):
        self.loader = ImageLoader()
        self.cache = {}
        self.window = window
        #self.cache["loading"] = Tile("loading.png")
        self.cache["loading"] = self.loader.getCache()
        self.pending_tiles = set()
        self.loading_tiles = set()
        self.threads = []
        self.list_lock = threading.Lock()
        self.ui_lock = threading.Lock()
        self.run = True
        for i in range(10):
            t = FuncThread(self.loading_thread, self.pending_tiles, self.cache, self.list_lock, i)
            self.threads.append(t)
            t.start()

    def stop_threads(self):
        self.run = False

    def coord_to_gmap_tile(self, lon,lat, zoom):
        sin_phi = sin(lat * pi / 180)
        norm_x = lon / 180
        norm_y = (0.5 * log((1 + sin_phi) / (1 - sin_phi))) / pi
        tile_x = (2 ** zoom) * ((norm_x + 1) / 2)
        tile_y = (2 ** zoom) * ((1 - norm_y) / 2)
        return tile_x, tile_y

    def dpix_to_dcoord(self,x, y0,y, zoom):
        sin_phi =  cos(y0 * pi / 180)
        long = 180.0/(2**zoom)*x / 128
        lat = - 180.0/(2**zoom)*y / 128 * sin_phi
        return long,lat

    def dcord_to_dpix(self, long, long0, lat, lat0, zoom):
        x0, y0 = self.coord_to_gmap_tile(long0, lat0, zoom)
        x,   y = self.coord_to_gmap_tile(long,  lat,  zoom)
        dx = (x - x0)*256
        dy = (y - y0)*256
        return dx, dy

    def gmap_tile_xy(self,tile_x, tile_y):
        return (tile_x - int(tile_x)) * 256,\
               (tile_y - int(tile_y)) * 256

    def gmap_tile_xy_from_coord(self, x, y, z):
        tile_x, tile_y = self.coord_to_gmap_tile(x, y, z)
        return (tile_x - int(tile_x)) * 256,\
               (tile_y - int(tile_y)) * 256

    def loadImageSurfaceFromTile(self, x, y, z):
        name = str((int(x), int(y),int(z)))
        #print name
        x, y, z = int(x), int(y), int(z)
        max = 2 ** z
        if x < 0 or y < 0 or x > (max -1) or y> (max-1):
            #print "out of bounds", x, y
            return self.cache["loading"]
        #else:
        #    print "ok", x,  y
        if self.cache.has_key(name):
                return self.cache[name]
        else:
            if (x, y, z) not in self.pending_tiles and (x, y, z) not in self.loading_tiles:
                self.pending_tiles.add((x, y, z))
            return self.cache["loading"]
        #print "fuck"
        return []

    def loading_thread(self, pending, cache, lock, id):
        while self.run:
            lock.acquire()
            if len(pending)>0:
                x, y, z = pending.pop()
                self.loading_tiles.add((x, y, z))
                lock.release()
                name = str((int(x),int(y),int(z)))
                try:
                    img = self.loader.get_image(x,y,z)
                    #img = cairo.ImageSurface.create_from_png(tile)
                    cache[name] = img
                    self.loading_tiles.remove((x,y,z))
                except Exception, e:
                    if "Unsupported" in str(e) or "reading" in str(e):
                        self.loader.remove(x,y,z)
                    print "error {2} loading tile {0} at thread {1}! ".format( name,id,e)
                    time.sleep(0.2)
                    self.loading_tiles.remove((x,y,z))
                    pending.add((x,y,z))
                    #print traceback.format_exc()
                self.ui_lock.acquire()
                self.window.queue_draw()
                self.ui_lock.release()
            else:
                lock.release()
            time.sleep(0.02)

    def load_area(self, x0, y0, z0, tiles_x, tiles_y):
        x0, y0 = self.coord_to_gmap_tile(x0, y0, z0)
        tiles_array = []
        x0 = int(x0)
        y0 = int(y0)
        x_span = (tiles_x/2)+1
        y_span = (tiles_y/2)+1
        for y in range(-y_span, y_span+1):
            y_list = []
            for x in range(-x_span, x_span+1):
                #print x,y
                y_list.append(self.loadImageSurfaceFromTile(x0+x, y0+y, z0))
            tiles_array.append(y_list)
        return tiles_array
