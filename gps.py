import serial
from pynmea import nmea
import threading
import time


class Boat(threading.Thread):
    def __init__(self):
        super(Boat, self).__init__()
        self.lat = 0
        self.lon = 0
        self.fix = False
        self.waypoints = []

        self.gps = GpsReader(self)
        self.gps.start()


    def stop(self):
        self.gps.running = False

    def getLatLon(self):
        return [self.lat, self.lon, self.fix]


class GpsReader(threading.Thread):
    def __init__(self, boat):
        super(GpsReader, self).__init__()
        self.boat = boat
        self.running = True

    def run(self):

        ser = serial.Serial('/dev/ttyUSB0', 4800)
        while self.running:

            myline = ser.readline()
            gpgga = nmea.GPGGA()
            gpgsa = nmea.GPGSA()

            if (myline.startswith('$GPGGA')):
                # Ask the object to parse the data
                gpgga.parse(myline)

                #time2 = float(gpgga.timestamp)
                lat = float(gpgga.latitude)
                lon = float(gpgga.longitude)

                self.boat.lat = lat
                self.boat.lon = lon

            elif (myline.startswith("$GPGSA")):
                gpgsa.parse(myline)
                # print gpgsa.mode, gpgsa.mode_fix_type
                if gpgsa.mode_fix_type != "3" and gpgsa.mode_fix_type != "2":
                    #print "No fix!", gpgsa.mode_fix_type
                    self.boat.fix = False
                else:
                    self.boat.fix = True
