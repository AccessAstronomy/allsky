# -*- coding: utf-8 -*-


import datetime
import time    
#import numpy as np
#import matplotlib.image as mpimg
#import matplotlib.pyplot as plt
#from PIL import Image, ImageDraw, ImageFont,ImageOps
#import math as m
#from numpy import random 
#from astropy.io import fits
import os
#import ftplib
#import sys
#from scipy import ndimage
import ephem
#import astro
#import scipy.signal
#import shutil
#import smtplib
#import subprocess
#from analyseraw import rawanalyse
#from analyseraw import movie
#from analyseraw import make_jpg

print('Script started from top')

# Change where images will be stored
archive_path="/home/Archive"
dev_identifier = "Lauwersoog_EOSRP"
device_dir = os.path.join(archive_path, dev_identifier)
day_dir = os.path.join(device_dir, str(datetime.datetime.now()).split(' ')[0])
if not os.path.isdir(device_dir) : os.mkdir(device_dir)
if not os.path.isdir(day_dir) : os.mkdir(day_dir)
os.chdir(day_dir)

camera_loc=ephem.Observer()
camera_loc.lat, camera_loc.lon = '53.2401', '6.5366'
camera_loc.elevation = 15
camera_loc.date = datetime.datetime.utcnow() 
camera_loc.pressure = 0 # no refraction correction.
camera_loc.epoch = ephem.J2000

counter=0
longitude = camera_loc.lat
latitude = camera_loc.lon

sun = ephem.Sun()

MEZsunrise = camera_loc.next_rising(sun) 

camera_loc.date = datetime.datetime.utcnow() - datetime.timedelta(hours=6)
MEZsunset = camera_loc.next_setting(sun)

print("Sonnenaufgang:" , MEZsunrise)
print("Sonnenuntergang:", MEZsunset)

#cc=1
#a=time.localtime()
#x=a[3]+a[4]/60.
#zählt Bild Nummer
#image_counter=1000
#zählt Bilder seit letzten ftp Transfer
#allskycounter=0

#Dauerschleife, Abbruch mit CTRL + c
# Achtung ab hier läufz die Software ununterbrochen 

cc=1
sunset_timer=0
while cc == 1:
    a=time.localtime()
    exposure_counter=0
    dummy_counter=0

    if ephem.Date(datetime.datetime.utcnow()) <= MEZsunrise and ephem.Date(datetime.datetime.utcnow()) <= MEZsunset:
            print("daylight_sleeping")
            a = "curl https://cronitor.link/p/945ebc5a62dd4efebd5f485648aad8bf/ldst-eosrp-allsky?msg='Daylight'"
            os.system(a)
            time.sleep(120)   
    elif ephem.Date(datetime.datetime.utcnow()) <= MEZsunrise:
        sunset_timer=1        
        dummy_counter=1.
        print('after sunset before sunrise...taking picture')
        a='gphoto2  --set-config eosremoterelease=Immediate --wait-event=30s --set-config eosremoterelease="Release Full" --wait-event-and-download=2s --filename=RP_%Y-%m-%dT%H-%M-%S.cr3'
        os.system(a)      
        a = "curl https://cronitor.link/p/945ebc5a62dd4efebd5f485648aad8bf/ldst-eosrp-allsky?msg='Imaging'"
        os.system(a)
        time.sleep(120)
        print('next image...')
    else:
        cc=0

print("goodbye")            
    

        
       
 
