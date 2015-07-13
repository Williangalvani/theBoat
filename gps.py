import serial
from pynmea import nmea
import threading
import time
import math
import os
from comm import TelemetryReader
from pid import PID


class Boat(threading.Thread):
    def __init__(self):
        super(Boat, self).__init__()
        self.lat = 0
        self.lon = 0
        self.fix = False
        self.waypoints = []

        self.gps = GpsReader(self)
        self.gps.start()
        self.mag = TelemetryReader()

        self.dirPID = PID(35,0,0)
        self.speedPID = PID(-0.005,0,0)


    def stop(self):
        self.gps.running = False

    def getDirection(self):
        try:

            angle = self.mag.attitude[2]
            if angle > 180:
                angle-=360  
            
            #print "----------------------ANGLE---------------" , angle
            angle = math.radians(angle)
            return angle
        except:
            return 0

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
        #print "RECEIVED -------------------------" ,position
        if -100 < position < 100:
            position = (position + 100)*0.5
            os.system("echo 1={0}% > /dev/servoblaster".format(position))
            print position

    def getDistanceAndBearingToCoordinate(self, coord):
        lat,lon, fix, direction = self.getLatLon()
        tlat,tlon = coord

        tlat, tlon = float(tlat), float(tlon)

        #from http://www.movable-type.co.uk/scripts/latlong.html

        R = 6371000; #// m
        dLat = math.radians(tlat-lat);
        dLon = math.radians(tlon-lon);
        lat1 = math.radians(lat);
        lat2 = math.radians(tlat);

        a = math.sin(dLat/2) * math.sin(dLat/2) + math.sin(dLon/2) * math.sin(dLon/2) * math.cos(lat1) * math.cos(lat2); 
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)); 
        d = R * c;

        cos = math.cos
        sin = math.sin
        atan2 = math.atan2

        lon1 = lon
        lat1 = lat
        lon2 = tlon
        lat2 = tlat
        #tc1= atan2(sin(lon2-lon1)*cos(lat2),cos(lat1)*sin(lat2)-sin(lat1)*cos(lat2)*cos(lon2-lon1)) % 2*math.pi
        tc1 = atan2(lon2-lon1,lat2-lat1)

        return d , tc1

    def controlloop(self):

        current_heading = self.getDirection()
        distance, targetdir = self.getDistanceAndBearingToCoordinate(self.waypoints[0])
        
        y,x = targetdir, current_heading   
        deviation = y-x
        if deviation > math.pi:
            deviation -= 2 * math.pi
        elif deviation < -math.pi:
            deviation += 2*math.pi

        if distance < 15:
            self.waypoints = self.waypoints[1:]
            motor = 0
            rudder = 0
        else:
            ##### rudder pid
                   
            rudder = self.dirPID.update(error=deviation)
            ##### motor pid
            motor = min(max(self.speedPID.update(distance),0.62)*100,70)
        self.moveRudder(rudder+15)
        #print "----------------------------------rudder ------" , rudder , current_heading
        #print "----------MOTOOORRR--------", motor
        #limit motor to 50%
        #print "HEADING: ", current_heading, "TARGET:" , targetdir, "DEVIATION:", deviation, "RUDDER:", rudder
        self.setThrottle(motor*0.1)
        print "distance:" , distance


    def run(self):
        self.setThrottle(100)
        time.sleep(1)
        self.setThrottle(0)
        while self.gps.running:
            if len(self.waypoints):
                self.controlloop()
            else:
                pass
                #print self.getDirection(), self.getLatLon()
            time.sleep(0.1)




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
