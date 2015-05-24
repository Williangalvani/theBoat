import serial
from pynmea import nmea
import threading
import time

class GpsReader(threading.Thread):
    
    def __init__(self):        
        super(GpsReader, self).__init__()
        self.lat = 0
        self.lon = 0
        self.fix = False
        self.running = True
        print "resetting"
        
    def getLatLon(self):
        print self.fix,self.lat,self.lon
        return self.fix,self.lat,self.lon

    def run(self):

        ser = serial.Serial('/dev/ttyUSB0', 4800)
        print "starting loop"
        while self.running:

            myline =  ser.readline()
            gpgga = nmea.GPGGA()
            gpgsa = nmea.GPGSA()

            if(myline.startswith('$GPGGA')):
        # Ask the object to parse the data
                gpgga.parse(myline)

                time2 = float(gpgga.timestamp)
                lat = float(gpgga.latitude)
                lon = float(gpgga.longitude)

                self.lat = lat
                self.lon = lon
                print self.fix,self.lat,self.lon
                #print "Time %f Lat %f Long %f" % ( time2, lat, lon)
          
            elif(myline.startswith("$GPGSA")):
            	gpgsa.parse(myline)
                #print gpgsa.mode, gpgsa.mode_fix_type
                if gpgsa.mode_fix_type != "3" and gpgsa.mode_fix_type != "2":
                    #print "No fix!", gpgsa.mode_fix_type
                    self.fix = False
                else:
                    self.fix = True   
