from flask import Flask, request, send_from_directory
import os
import json

from imageCache import ImageLoader
from gps import Boat
from stream.picamstreamer import Streamer

app = Flask(__name__)

loader = ImageLoader()

boat = Boat()
boat.start()

streamer = Streamer()
streamer.start()

@app.route('/')
def hello_world():
    return send_from_directory("/home/pi/theBoat/html", 'index.html')


@app.route('/dist/<path:path>')
def staticfile(path):
    return send_from_directory("/home/pi/theBoat/html/dist", path)


@app.route('/fonts/<path:path>')
def staticfile2(path):
    return send_from_directory("/home/pi/theBoat/html/dist/fonts", path)


@app.route('/img/<zoom>/<lat>-<lon>.png')
def getmap(zoom, lat, lon):
    print zoom, lat, lon
    #return loader.get_image(lat,lon,zoom)
    head, tail = os.path.split(loader.get_image(lat, lon, zoom))
    return send_from_directory(head, tail)


#return "" + zoom + "" + lat + "" + lon

@app.route('/setServosTo/<x>/<y>')
def setServosto(x,y):
    x = 0.5+0.5*float(x)
    y = 0.5+0.5*float(y)
    x = max(min(1,x),-1)
    y = max(min(1,y),-1)

    rudder_str ="{0}={1}%\n".format(0, x*100.0)
    throttle_str ="{0}={1}%\n".format(1, y*100.0)
    print throttle_str

    
    with open("/dev/servoblaster", "wb") as f:
        f.write(rudder_str)
        f.write(throttle_str)        

    return ""

@app.route('/gps')
def getGps():
    data = boat.getLatLon()
    #print data
    return json.dumps(data)

@app.route('/newwaypoint/<lat>/<lon>')
def setWaypoint(lat,lon):
    boat.waypoints.append((lat,lon))
    return json.dumps(boat.waypoints)

@app.route('/movelastwaypoint/<lat>/<lon>')
def moveLastWaypoint(lat,lon):
    boat.waypoints.remove(boat.waypoints[-1] )
    boat.waypoints.append((lat,lon))
    return json.dumps(boat.waypoints)

@app.route('/getwaypoints')
def getWaypoints():
    return json.dumps(boat.waypoints)

@app.route('/delwaypoint/<ida>')
def delWaypoint(ida):
    boat.waypoints.remove(boat.waypoints[int(ida)])
    return json.dumps(boat.waypoints)



if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0')#, debug=True)
    except Exception, e:
        print e
    finally:
        boat.stop()
