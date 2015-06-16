import serial
from pynmea import nmea
import threading
import time
import math
import os


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

    def getDirection(self):
        return math.pi

    def getLatLon(self):
        return [self.lat, self.lon, self.fix, self.getDirection()]


    def moveRudder(self, position):
        """
        :param position: int [-100,100]
        :return:
        """
        if -100 < position < 100:
            position = (position + 100)*0.5
            os.system("echo 0={0}% > /dev/servoblaster".format(position))

    def setThrottle(self, position):
        """
        :param position: int [-100,100]
        :return:
        """
        if -100 < position < 100:
            position = (position + 100)*0.5
            os.system("echo 1={0}% > /dev/servoblaster".format(position))


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
