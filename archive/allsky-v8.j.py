# -*- coding: utf-8 -*-

import datetime
import time    
import os
import ephem
from configparser import ConfigParser

class ImagingControl:
    def __init__(self,inifile):
        self.config = ConfigParser()
        self.config.read(inifile)
        self.archive_path = self.config["Paths"]["Archive_Path"]
        self.device_name = self.config["Paths"]["Camera_ID"]
        self.Twilight_Sunrise = False
        self.Twilight_Sunset = False
        self.day_dir = False
        self.isNight = False
        self.cronitor = "curl https://cronitor.link/p/" + self.config["Cronitor"]["Cronitor_Key"] + "/" + self.config["Cronitor"]["Cronitor_Key"] + "-allsky"
        self.iso_set = 'gphoto2 --set-config iso=' + self.config["Camera"]["ISO_Position"]
        self.take = ImagingControl.take_string(self)
        print('init done')
        
    def take_string(self):
        press = 'gphoto2 --set-config eosremoterelease=Immediate --wait-event=' 
        time = self.config["Camera"]["Exposure"] + 's'
        release = ' --set-config eosremoterelease="Release Full" --wait-event-and-download=2s'
        tofile = ' --filename=' + self.config["Camera"]["Prefix"] + '_%Y-%m-%dT%H-%M-%S.cr3'
        
        take_string = press + time + release + tofile
        return take_string

    def observing_details(self):        
        camera_loc=ephem.Observer()
        camera_loc.lat, camera_loc.lon = self.config["Location"]["Camera_Latitude"], self.config["Location"]["Camera_Longitude"] 
        camera_loc.elevation = int(self.config["Location"]["Camera_Altitude"]) 
        camera_loc.horizon = str(self.config["Time"]["Twilight_Alt"])
        camera_loc.date = datetime.datetime.utcnow() 
        camera_loc.pressure = 0 # no refraction correction.
        camera_loc.epoch = ephem.J2000

        sun = ephem.Sun()
        sun.compute(camera_loc)
        self.Twilight_Sunrise = camera_loc.next_rising(sun) 

        if float(sun.alt) < 0:
            self.isNight = True
            camera_loc.date = datetime.datetime.utcnow() - datetime.timedelta(hours = 22)
            sun.compute(camera_loc)
            self.Twilight_Sunset = camera_loc.next_setting(sun) 
        else:
            self.isNight = False
            self.Twilight_Sunset = camera_loc.next_setting(sun)

        print("Next Twiglight Sunrise ",self.Twilight_Sunrise)
        print("Next/Last Twiglight Sunset ",self.Twilight_Sunset)
        print('isNight',self.isNight)

    def set_directory(self):
        day_string = self.Twilight_Sunset.__str__().split(' ')[0].replace('/','-')
        device_dir = os.path.join(self.archive_path, self.device_name)
        self.day_dir = os.path.join(device_dir, day_string)

        if not os.path.isdir(device_dir) : os.mkdir(device_dir)
        if not os.path.isdir(self.day_dir) : os.mkdir(self.day_dir)

        os.chdir(self.day_dir)
        
    def allsky(self):
        ImagingControl.observing_details(self)
        ImagingControl.set_directory(self)
        
        if self.config["Time"]["Wait_Night"] == "True":
            while ephem.Date(datetime.datetime.utcnow()) <= self.Twilight_Sunset:
                print("daylight_sleeping")
                a = self.cronitor + "?msg='Daylight'"
                os.system(a)
                time.sleep(120)   

        a = "pkill -f gphoto2"
        print(a)
        os.system(a)
        a = "gphoto2 --reset"
        print(a)
        os.system(a)
        a = self.iso_set
        print(a)
        os.system(a)

        os.chdir(self.day_dir)

        while ephem.Date(datetime.datetime.utcnow()) <= self.Twilight_Sunrise:
            print('sun below twilight limit...taking picture')
            a = self.take
            os.system(a)      
            a =  self.cronitor + "?msg='Imaging'"
            os.system(a)
            
            print('ímage done')
            time.sleep(120)
            print('next image')            

        print('waking up')
        a = self.cronitor + "?msg='WakingUp'"
        os.system(a)
        time.sleep(180)

def main():
    continuous = True
    while continuous == True:
        observe = ImagingControl(os.path.expanduser("~") + "/allsky.ini")
        observe.allsky()

    print("goodbye for some reason")            

if __name__ == "__main__":
    main()
