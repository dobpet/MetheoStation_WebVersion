from TM1637 import *
import select
import dht
import bme280
from machine import Pin, I2C, SPI, RTC, ADC, reset, PWM
#import PCD8544
import time
import ntptime
#import micropython

DisplayWindow = 0

def dstTime():
    year = time.localtime()[0] #get current year
    # print(year)
    HHMarch = time.mktime((year,3 ,(14-(int(5*year/4+1))%7),1,0,0,0,0,0)) #Time of March change to CEST
    HHNovember = time.mktime((year,10,(7-(int(5*year/4+1))%7),1,0,0,0,0,0)) #Time of November change to CET
    #print(HHNovember)
    now=time.time()
    if now < HHMarch : # we are before last sunday of march
        dst=time.localtime(now+3600) # CET: UTC+1H
    elif now < HHNovember : # we are before last sunday of october
        dst=time.localtime(now+7200) # CEST: UTC+2H
    else: # we are after last sunday of october
        dst=time.localtime(now+3600) # CET: UTC+1H
    return(dst)

# internal real time clock
rtc = RTC()
try:
    ntptime.settime()
    CET = dstTime()
    rtc.datetime( (CET[0], CET[1], CET[2], CET[6], CET[3], CET[4], CET[5], CET[7]) )
except:
    print('ntp dont succes')

#8segment display
DC_CLK=Pin(15)
RST_DIO=Pin(0)

LED = TM1637(clk=DC_CLK,dio=RST_DIO)
LED.brightness(0)
LED.show('----', False)
CE = Pin(2, Pin.OUT, value = 0)

#socekt        
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(1)
s.setblocking(True)

poller = select.poll()
poller.register(s, select.POLLIN)

#sensor DHT11
sensorDHT = dht.DHT11(Pin(16))
tempDHT = sensorDHT.temperature()
humDHT = sensorDHT.humidity()

#sensor DHT11 outside
CE.on()
tempDHTout = sensorDHT.temperature()
humDHTout = sensorDHT.humidity()

#sensor BME280
i2c = I2C(sda=Pin(4), scl=Pin(5), freq = 100000) #D1, D2
sensorBME = bme280.BME280(i2c=i2c)
tempBME, pressBME, _ = sensorBME.values
FAMSL = sensorBME.altitude()

#illumination
AIn = ADC(0)
illumination = AIn.read()
"""
#display
gc.collect()
CE.on()
spi = SPI(1)
#print(micropython.mem_info())
spi.init(baudrate=1000000, polarity=0, phase=0)
#bl = Pin(12, Pin.OUT, value=1)
bl = PWM(Pin(12), freq = 1000)
bl.duty(1024)#(1024)
lcd = PCD8544.PCD8544_FRAMEBUF(spi, Pin(2), Pin(15), Pin(0))

lcd.data(bytearray(b'\x80\x00\x00\x80\x00\x00\x80\x00\x00\x80\x00\x00\x80\x00\x00\x80\x00\x00\x80\x80\x40\x40\x40\x80\x80\xC0\xC0\x40\xC0\xA0\xE0\xC0\xE0\xE0\xF0\xF0\xF8\xF8\xF8\xFC\xFC\xFE\xEE\xF4\xF0\xF0\x70\x30\x00\x80\x00\x00\x80\x00\x0C\x9C\x1C\x38\xB8\x38\x38\xB8\xF8\xF0\xF0\xF0\xF0\xF0\xF0\xF0\xF0\xF0\xF0\xF0\xF0\xF0\xF0\xF0\xF0\xF0\xF8\xF8\xF8\xF8\x88\x20\x8A\x20\x08\x22\x08\x00\x0A\x00\x00\x02\x80\x71\xBA\xDA\xFD\xDD\xED\xDE\xEE\xF7\xFF\xFB\xFD\xFD\xFE\xFF\x7F\x3F\x1F\x9F\x3F\x7F\x6F\x0F\xAF\x1F\xBF\x3E\x3C\x7A\x78\x70\x22\x88\xA0\x2A\x80\x08\x62\xE0\xE0\xF2\xF0\x58\xDA\xF8\xFC\x92\xFE\xFF\xFF\xD3\xFF\xFD\xF3\xE1\xF0\xF9\x7F\xBF\x3F\x8F\x2F\x4F\xAF\x0F\x4F\xA7\x0F\xAF\x87\x2F\x82\x80\x20\xC0\x80\x80\x50\x40\xC4\xD0\xA0\xE8\xE4\xEA\xFF\xFB\xFD\xFF\xFF\xFF\xFF\xFF\xEF\x4F\x27\x53\xA8\x54\x29\x4A\xB5\x82\xAC\xA1\x8A\xB6\x50\x4D\x32\xA4\x4A\xB4\xA9\x4A\x52\xB4\xAA\x45\xA8\xDA\x22\xAC\xD2\x2A\x52\xA8\x52\x4C\xB0\xAD\x43\x5B\xB3\x45\xA8\x5B\xA3\xAB\x55\xA8\x52\x54\xA9\x56\xA8\x45\xBA\xA4\x49\x5A\xA2\x54\xAA\x52\xFE\xFF\xFF\xFE\xFD\xFF\xFF\xFF\xFE\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x7F\xFF\xFE\xBF\x7F\xBF\xBF\xFF\xDF\xBF\x5F\xDF\x7F\xDF\x7F\xDF\xAF\x7F\xEE\x8E\xF1\x6E\x99\xF7\x6A\xDD\xB2\x6E\xD5\x7A\xD7\xAC\x75\xDB\x6D\xD5\x7A\xD7\xAC\x7B\xE5\xDE\xA9\x77\xDA\xB5\xEE\x59\xB6\xEB\xDD\xB6\x69\xD6\xBF\xE8\x55\xEF\xB9\xD6\xED\xB5\x5B\xAB\xFF\xFD\xF7\xFF\x01\x01\x01\x01\xE1\xC1\x81\x03\x05\x0F\x1D\x2F\x7E\x01\x00\x01\x01\xFF\xFE\x03\x01\x01\x00\xF1\xF0\xF1\x71\xF1\xF1\xB1\xF1\x01\x01\x01\x03\xFE\xFF\x01\x01\x01\x01\xBE\x1B\x0D\x07\x03\x41\xE1\xF1\xF9\x6D\xFF\xFF\x00\x01\x01\x01\xFF\xFF\xEB\x3E\x0D\x03\x01\x41\x71\x70\x41\x01\x03\x0E\x3B\xEF\xFE\xFB\xEE\x7D\xF7\xFF\xFF\xFF\xFF\xFE\xFF\xF0\xF0\xF0\xF0\xFF\xFF\xFF\xFF\xFE\xFC\xF8\xF0\xF0\xF0\xF0\xF0\xF0\xFF\xFF\xF8\xF0\xF0\xF0\xF1\xF1\xF1\xF1\xF1\xF1\xF1\xF1\xF0\xF0\xF0\xF8\xFF\xFF\xF0\xF0\xF0\xF0\xFF\xFF\xFE\xFC\xF8\xF0\xF0\xF1\xF3\xF7\xFF\xFF\xF0\xF0\xF0\xF0\xFF\xF3\xF0\xF0\xF0\xFC\xFC\xFC\xFC\xFC\xFC\xFC\xFC\xF0\xF0\xF0\xF3\xFF\xFF\xFF\xFF\xFF'))
time.sleep_ms(2000)
"""
gc.collect()

#cycle program
while True:
    time.sleep_ms(1000)
    if not station.isconnected():
        reset()
        
    res = poller.poll(500)
    if res:
        try:
            conn, addr = s.accept()
            s.setblocking(True)
            print('Got a connection from %s' % str(addr))
            request = conn.recv(800)
            #request = str(request)            
            print('Content = %s' % request)
            request = ''
            gc.collect()
            time.sleep_ms(2000)
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n') 
            conn.sendall(
"""<!DOCTYPE HTML><html>
<head>
  <meta http-equiv="refresh" content="15" name="viewport" content="width=device-width, initial-scale=1" charset="UTF-8">
  <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">
  <style>
    html {
     font-family: Arial;
     display: inline-block;
     margin: 0px auto;
     text-align: center;
    }
    h2 { font-size: 3.0rem; }
    h3 { font-size: 2.0rem; }
    p { font-size: 3.0rem; }
    .units { font-size: 1.2rem; }
    .dht-labels{
      font-size: 1.5rem;
      vertical-align:middle;
      padding-bottom: 15px;
    }
  </style>
</head>
<body>
  <h2>Meteostanice</h2>
  <hr>
  <h3>vnitřní:</h3>
  <p>
    <i class="fas fa-thermometer-half" style="color:#059e8a;"></i> 
    <span class="dht-labels">Temperature</span> 
    <span>"""+str(tempDHT)+"""</span>
    <sup class="units">&deg;C</sup>
  </p>
  <p>
    <i class="fas fa-tint" style="color:#00add6;"></i> 
    <span class="dht-labels">Humidity</span>
    <span>"""+str(humDHT)+"""</span>
    <sup class="units">%</sup>
  </p>
  <p>
    <i class="fas fa-tachometer-alt" style="color:#EF3E3E;"></i> 
    <span class="dht-labels">Pressure</span>
    <span>"""+str(round(pressBME/100, 2))+"""</span>
    <sup class="units">hPa</sup>
  </p>
  <p>
    <i class="fas fa-mountain" style="color:#35DF85;"></i> 
    <span class="dht-labels">FAMSL</span>
    <span>"""+str(round(FAMSL,1))+"""</span>
    <sup class="units">m</sup>
  </p>
  <p>
    <i class="fas fa-sun" style="color:#FFFF00;"></i> 
    <span class="dht-labels">Illumination</span>
    <span>"""+str(round(illumination,1))+"""</span>
    <sup class="units">%</sup>
  </p>
  <hr>
</body>
</html>""")
            print('web sended')
            conn.close()
            gc.collect()
        except:
            continue

    else:

        #read temperature and humidity
        CE.off()
        sensorDHT.measure()
        tempDHT = sensorDHT.temperature()
        humDHT = sensorDHT.humidity()
        print('Sensor DHT -> Temperature: %3.1f °C, Humidity: %3.1f %%' %(tempDHT, humDHT))
         
        #read outside temperature and humidity
        try:
            CE.on()
            sensorDHT.measure()
            tempDHTout = sensorDHT.temperature()
            humDHTout = sensorDHT.humidity()
            print('Sensor DHT out -> Temperature: %3.1f °C, Humidity: %3.1f %%' %(tempDHTout, humDHTout))
        except:
            tempDHTout = -99
            humDHTout = -99
            print('Sensor DHT out -> not connected')
     
        #read temperature and pressure
        tempBME, pressBME, _ = sensorBME.values
        FAMSL = sensorBME.altitude()
        print('Sensor BME -> Temperature: %3.1f °C, Pressure: %6.1f Pa' %(tempBME, pressBME))
        print('Nadmořská výška: %3.1f m' %FAMSL)
        
        #read illumination
        illumination = (AIn.read() / 1023) * 100 #value 0-1023
        print('Osvit: %3.1f %%' % illumination)
        LED.brightness(int((illumination / 100) * 7))
        #print(int((illumination / 100) * 1023))
        #bl.duty(int((illumination / 100) * 1023))

        """
        if True:
            #read buttons:
            keys = LED.keys()
            if (keys & 0x08) == 0:
                DisplayWindow = DisplayWindow + 1
                if DisplayWindow > 3:
                    DisplayWindow = 0
            if (keys & 0x10) == 0:
                DisplayWindow = DisplayWindow - 1
                if DisplayWindow < 0:
                    DisplayWindow = 3

            #print(rtc.datetime())

            #1 char = 8x8
            lcd.fill(0)
            CE.on()
            if DisplayWindow == 0:
                ip_list = station.ifconfig()[0].split(".")
                lcd.text("IP:", 0, 0, 1)
                lcd.text("%s.%s." % (ip_list[0], ip_list[1]), 0, 10, 1)
                lcd.text(".%s.%s" % (ip_list[2], ip_list[3]), 0, 20, 1)
                #DisplayWindow = 1
            elif DisplayWindow == 1:
                # generate formated date/time strings from internal RTC
                date_str = "{2:02d}.{1:02d}.{0:4d}".format(*rtc.datetime())
                time_str = "{4:02d}:{5:02d}".format(*rtc.datetime()) #:{6:02d}
                lcd.text("Date/Time:", 0, 0, 1)
                lcd.text(date_str, 0, 10, 1)
                lcd.text(time_str, 16, 20, 1)
                #DisplayWindow = 2
            elif DisplayWindow == 2:
                lcd.text("inside:", 0, 0, 1)
                lcd.text(str(round(tempDHT,1)), 8, 10, 1)
                lcd.text('stC', 7*8, 10, 1)
                lcd.text(str(round(humDHT,1)), 8, 20, 1)
                lcd.text('%', 7*8, 20, 1)
                lcd.text(str(round(pressBME/100,1)), 8, 30, 1)
                lcd.text('hPa', 7*8, 30, 1)
                lcd.text(str(round(FAMSL,1)), 0, 40, 1)
                lcd.text('m', 7*8, 40, 1)           
                #DisplayWindow = 3
            elif DisplayWindow == 3:
                lcd.text("outside:", 0, 0, 1)
                lcd.text(str(round(tempDHTout,1)), 8, 10, 1)
                lcd.text('stC', 7*8, 10, 1)
                lcd.text(str(round(humDHTout,1)), 8, 20, 1)
                lcd.text('%', 7*8, 20, 1)
                lcd.text("illum.:", 0, 30, 1)
                lcd.text(str(round(illumination,1)), 8, 40, 1)
                lcd.text('%', 7*8, 40, 1)
                #DisplayWindow = 0
            lcd.show()
            gc.collect()
        """       
        
        #segment. display
        tmv=rtc.datetime()
        tstr = '{0: >2}{1:0>2}'.format(tmv[4], tmv[5])
        CE.on()
        LED.show(tstr, True)
        FSH=False
        nFSH=False
            
       
        