from flask import Flask, request, send_from_directory
import os
import json

from imageCache import ImageLoader
from gps import GpsReader

app = Flask(__name__)

loader = ImageLoader()

gps = GpsReader()
gps.start()

@app.route('/')
def hello_world():
    return send_from_directory("/home/pi/theBoat/html", 'index.html')


@app.route('/dist/<path:path>')
def staticfile(path):
    return send_from_directory("/home/pi/theBoat/html/dist", path)


@app.route('/img/<zoom>/<lat>/<lon>.png')
def getmap(zoom, lat, lon):
    print zoom, lat, lon
    #return loader.get_image(lat,lon,zoom)
    head, tail = os.path.split(loader.get_image(lat, lon, zoom))
    return send_from_directory(head, tail)


#return "" + zoom + "" + lat + "" + lon

@app.route('/gps')
def getGps():
    data = gps.getLatLon()
    #print data
    return json.dumps(data)


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0')#, debug=True)
    except Exception, e:
        print e
    finally:
        gps.running = False