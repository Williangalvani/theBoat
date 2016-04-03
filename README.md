# theBoat


##How it works:
A webserver runs on the raspberry PI, serving a html+js client that serves as remote control and camera display. the client communicates using http requests, an receives the camera image via websocket.


##Requirements:
-Raspberry Pi setup as a hotspot, with camera properly enabled
-ServoBlaster
-Usb GPS
-Flask
-nginx

##Setup
-Make server.py run on boot with a cron job.
-copy the "nginxsite" to /etc/nginx/sites-enabled  and set the right path to the project on this file.

##Usage

-open the browser on raspberrypi:5001

(if there's a internet connection, the map will be downloaded/cached)


