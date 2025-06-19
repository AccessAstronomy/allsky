# -*- coding: utf-8 -*-


import datetime
import time    
import numpy as np
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont,ImageOps
import math as m
from numpy import random 
from astropy.io import fits
import os
import ftplib
import sys
from scipy import ndimage
import ephem
#import astro
import scipy.signal
import shutil
import smtplib
import subprocess
#from analyseraw import rawanalyse
#from analyseraw import movie
#from analyseraw import make_jpg

print('Script started from top')

# Change where images will be stored
archive_path="/home/Archive"
dev_identifier = "Zernike_EOSRP"
device_dir = os.path.join(archive_path, dev_identifier)
day_dir = os.path.join(device_dir, str(datetime.datetime.now()).split(' ')[0])
if not os.path.isdir(device_dir) : os.mkdir(device_dir)
if not os.path.isdir(day_dir) : os.mkdir(day_dir)
os.chdir(day_dir)


#----Vorbereitung Ephemeriden
gatech=ephem.Observer()
gatech.lat, gatech.lon= '53.2401', '6.5366'
gatech.elevation=15
#gatech.date='2014/9/07 21:01'
gatech.pressure = 0 # no refraction correction.
gatech.epoch = ephem.J2000

t=time.time()-86400
a=time.localtime(t)
print(a)

#directory='allsky'
counter=0
#------------------------------------#
# initiale Berechnungen
#Koordinaten Oldenburg
# 53.1438 und 8.21388
longitude=gatech.lat
latitude= gatech.lon
#Umrechnen in Rad
B = m.pi *latitude / 180 


# Tag des Jahres berechnen
a=time.localtime()
print(a)

# für heute directory
#directory='/mnt/observatory/RP/Archive/RP_'+str(a[0])+'_'+str(a[1])+'_'+str(a[2])
#if not os.path.exists(directory):
#    os.mkdir(directory)

T=a[7]

#Zeitdifferenz Sommerzeit
if 85 <= T and T <= 296:
    tcor = 0
else:
    tcor = 0


#Declination der Sonne
Dec= 0.4095*m.sin(0.016906*(T-80.086))
#Refraktionskorrektur Sonnenaufgang nicht bei 0° sondern -0.83°
h=m.radians(-0.833)
#Zeitdifferenz
dt = 12*m.acos((m.sin(h) - m.sin(B)*m.sin(Dec)) / (m.cos(B)*m.cos(Dec)))/m.pi 
#Sonnenaufgang um 12-dt wahre Ortszeit
sunrise=12-dt
sunset=12+dt

#Zeitgleichung
deltaT = -0.170869921174742*m.sin(0.0336997028793971 * T + 0.465419984181394) - 0.129890681040717*m.sin(0.0178674832556871*T - 0.167936777524864)
MOZsunrise=sunrise-deltaT
MOZsunset=sunset-deltaT
#convert MOZ to MEZ/MESZ
MEZsunrise=MOZsunrise -longitude/15. + tcor 
MEZsunset=MOZsunset-longitude/15. + tcor
print("Sonnenaufgang:" , MEZsunrise)
print("Sonnenuntergang:", MEZsunset)


#--------------------------------------
#einmal Startzeit bestimmen 
cc=1
a=time.localtime()
x=a[3]+a[4]/60.
#zählt Bild Nummer
image_counter=1000
#zählt Bilder seit letzten ftp Transfer
allskycounter=0



#Dauerschleife, Abbruch mit CTRL + c
# Achtung ab hier läufz die Software ununterbrochen 
sunset_timer=0
while cc ==1:
    a=time.localtime()
    x=a[3]+a[4]/60.
    
    # Tag des Jahres berechnen
    a=time.localtime()
    T=a[7]
    
   
   
    #Zeitdifferenz Sommerzeit
    if 85 <= T and T <= 296:
        tcor = 0
    else:
        tcor = 0
    
    nautw = m.radians(-12)
    #Berechnung wahrer Mittag
    wm = 12-longitude/15. +tcor
    #Berechnung wahre Mitternacht
    wmn = wm - 12
                
    nautd = wm-(m.degrees(m.acos((m.sin(nautw)-m.sin(Dec)*m.sin(B))/(m.cos(Dec)*m.cos(B)))))/(360/24)
    nautd2 = wm+(m.degrees(m.acos((m.sin(nautw)-m.sin(Dec)*m.sin(B))/(m.cos(Dec)*m.cos(B)))))/(360/24)
                
    dmmrng = MEZsunrise - nautd
    dmmrng2 = nautd2 - MEZsunset
    
      
    exposure_counter=0
    dummy_counter=0
   
    #print(x)  
   
        

    if x >= MEZsunrise and x <= MEZsunset - 1:
            
            print("daylight_sleeping")
            a = "curl https://cronitor.link/p/945ebc5a62dd4efebd5f485648aad8bf/zernike-eosrp-allsky?msg='Daylight'"
            os.system(a)
            Datum = str(datetime.datetime.utcnow())
            #things to do once per day after first night (controlled by sunset time=0/1
            if sunset_timer==1:
                #Declination der Sonne
                Dec= 0.4095*m.sin(0.016906*(T-80.086))
                #Refraktionskorrektur Sonnenaufgang nicht bei 0° sondern -0.83°
                h=m.radians(-0.833)
                #Zeitdifferenz
                dt = 12*m.acos((m.sin(h) - m.sin(B)*m.sin(Dec)) / (m.cos(B)*m.cos(Dec)))/m.pi 
                #Sonnenaufgang um 12-dt wahre Ortszeit
                sunrise=12-dt
                sunset=12+dt
                #Zeitgleichung
                deltaT = -0.170869921174742*m.sin(0.0336997028793971 * T + 0.465419984181394) - 0.129890681040717*m.sin(0.0178674832556871*T - 0.167936777524864)
                MOZsunrise=sunrise-deltaT
                MOZsunset=sunset-deltaT
                #convert MOZ to MEZ/MESZ
                MEZsunrise=MOZsunrise -longitude/15. +tcor 
                MEZsunset=MOZsunset-longitude/15.+tcor
                
                #Sonnenwinkel unter dem Horizont für nautischen Dämmerung
                nautw = m.radians(-12)
                #Berechnung wahrer Mittag
                wm = 12-longitude/15. +tcor
                #Berechnung wahre Mitternacht
                wmn = wm - 12
                
                nautd = wm-(m.degrees(m.acos((m.sin(nautw)-m.sin(Dec)*m.sin(B))/(m.cos(Dec)*m.cos(B)))))/(360/24)
                nautd2 = wm+(m.degrees(m.acos((m.sin(nautw)-m.sin(Dec)*m.sin(B))/(m.cos(Dec)*m.cos(B)))))/(360/24)
                
                dmmrng = MEZsunrise - nautd
                dmmrng2 = nautd2 - MEZsunset
                
                print( "Sonnenaufgang neu" , MEZsunrise)
                print( "Sonnenuntergang neu", MEZsunset)
                print('wahrer Mittag:', wm)
                print('Daemmerung von:', nautd, 'bis', MEZsunrise, 'Dauer', dmmrng, 'vor Sonnenaufgang')
                print('Daemmerung von:', MEZsunset, 'bis', nautd2, 'Dauer', dmmrng2, 'nach Sonnenuntergang')                
                #path, counters ets           
                
                # create new directory
                 #directory
                
                #make_jpg(directory)
                #movie(directory)
                
                #directory='/mnt/observatory/RP/Archive/RP_'+str(a[0])+'_'+str(a[1])+'_'+str(a[2])
                #if not os.path.exists(directory):
                #    os.mkdir(directory)
                
                
                sunset_timer=0
             

                a=time.localtime()
                                
                
                counter = 0
                dummy_counter=0 
                counter = 0                
                
            time.sleep(120)   
    else:
        sunset_timer=1        
        dummy_counter=1.
        #counter = 1.
        
        print('after sunset before midnight...taking picture')
        a='gphoto2  --set-config eosremoterelease=Immediate --wait-event=30s --set-config eosremoterelease="Release Full" --wait-event-and-download=2s --filename=RP_%Y-%m-%dT%H-%M-%S_001.cr3'
        os.system(a)      
        a = "curl https://cronitor.link/p/945ebc5a62dd4efebd5f485648aad8bf/zernike-eosrp-allsky?msg='Daylight'"
        os.system(a)
        #analyse starten
        time.sleep(120)
        #rawanalyse(directory)
      
        print('next image...')
            
    

        
       
 
