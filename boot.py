import usocket as socket
from machine import Pin
import network
import esp
esp.osdebug(None)

import gc
gc.collect()

network.WLAN(network.STA_IF).active(False)  # WiFi station interface
network.WLAN(network.AP_IF).active(False)  # access-point interface

ssid = 'Fofr1'
password = 'iadnuiadnu1'
ssid = 'BTECH-openspace-public'
password = 'btech1234'



station = network.WLAN(network.STA_IF)

station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

gc.collect()

print('Connection successful')
print(station.ifconfig())

#led = Pin(2, Pin.OUT)
