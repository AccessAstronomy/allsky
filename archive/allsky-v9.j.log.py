# -*- coding: utf-8 -*-

import datetime
import time    
import os
import ephem
from configparser import ConfigParser
import logging
import fnmatch

class ImagingControl:
    def __init__(self,inifile):
        self.config = ConfigParser()
        self.config.read(inifile)
        self.archive_path = self.config["Paths"]["Archive_Path"]
        self.device_name = self.config["Paths"]["Camera_ID"]
        self.suffix = self.config["Camera"]["Suffix"]
        self.Twilight_Sunrise = False
        self.Twilight_Sunset = False
        self.day_dir = False
        self.isNight = False
        self.loop_waits = int(self.config["Time"]["Loop_Waits"])
        self.cronitor = "curl https://cronitor.link/p/" + self.config["Cronitor"]["Cronitor_Key"] + "/" + self.config["Cronitor"]["Cronitor_Root"] + "-allsky"
        self.iso_set = 'gphoto2 --set-config iso=' + self.config["Camera"]["ISO_Position"]
        self.alt_iso_set = 'gphoto2 --set-config iso=' + self.config["Camera"]["Alt_ISO_Position"]
        self.take = ImagingControl.take_string(self)
        self.alt_take = ImagingControl.alt_take_string(self)
        self.day_string = False
        self.log_filename = False
        self.power_toggle = 'mosquitto_pub -h localhost -t cmnd/' + self.config["Paths"]["Camera_Plug_MQQT"] + '/POWER -m toggle'
        self.power_on = 'mosquitto_pub -h localhost -t cmnd/' + self.config["Paths"]["Camera_Plug_MQQT"] + '/POWER -m on'
        self.power_off = 'mosquitto_pub -h localhost -t cmnd/' + self.config["Paths"]["Camera_Plug_MQQT"] + '/POWER -m off'
        logging.debug("Init done")
        
    def take_string(self):
        press = 'gphoto2 --set-config eosremoterelease=Immediate --wait-event=' 
        time = self.config["Camera"]["Exposure"] + 's'
        release = ' --set-config eosremoterelease="Release Full" --wait-event-and-download=2s'
        tofile = ' --filename=' + self.config["Camera"]["Prefix"] + '_%Y-%m-%dT%H-%M-%S.' + self.suffix
        
        take_string = press + time + release + tofile
        return take_string

    def alt_take_string(self):
        press = 'gphoto2 --set-config eosremoterelease=Immediate --wait-event=' 
        time = self.config["Camera"]["Alt_ISO_Exposure"] + 's'
        release = ' --set-config eosremoterelease="Release Full" --wait-event-and-download=2s'
        tofile = ' --filename=' + self.config["Camera"]["Prefix"] + '_%Y-%m-%dT%H-%M-%S_ALT_ISO.' + self.suffix
        
        take_string = press + time + release + tofile
        return take_string

    def observing_details(self):        
        camera_loc=ephem.Observer()
        camera_loc.lat, camera_loc.lon = self.config["Location"]["Camera_Latitude"], self.config["Location"]["Camera_Longitude"] 
        camera_loc.elevation = int(self.config["Location"]["Camera_Altitude"]) 
        camera_loc.horizon = self.config["Time"]["Twilight_Alt"]
        camera_loc.date = datetime.datetime.utcnow() 
        camera_loc.pressure = 0 # no refraction correction.
        camera_loc.epoch = ephem.J2000

        sun = ephem.Sun()
        sun.compute(camera_loc)
        self.Twilight_Sunrise = camera_loc.next_rising(sun) 
        self.Twilight_Sunset = camera_loc.next_setting(sun)

        if self.Twilight_Sunrise < self.Twilight_Sunset:
            self.isNight = True
            camera_loc.date = datetime.datetime.utcnow() - datetime.timedelta(hours = 22)
            sun.compute(camera_loc)
            self.Twilight_Sunset = camera_loc.next_setting(sun) 
        else:
            self.isNight = False

    def set_directory(self):
        date_list = self.Twilight_Sunset.__str__().split(' ')[0].split('/')
        self.day_string = f"{int(date_list[0]):04d}-{int(date_list[1]):02d}-{int(date_list[2]):02d}"
        device_dir = os.path.join(self.archive_path, self.device_name)
        self.day_dir = os.path.join(device_dir, self.day_string)

        if not os.path.isdir(device_dir) : os.mkdir(device_dir)
        if not os.path.isdir(self.day_dir) : os.mkdir(self.day_dir)
        a = f"cp allsky.ini {self.day_dir}"
        os.system(a)
        os.chdir(self.day_dir)
    
    def buildLog(self):
        
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
            
        self.log_filename = os.path.join(self.day_dir, ('%s-allsky-' % self.day_string) + self.device_name + '.log')
        logging.basicConfig(level=logging.DEBUG, filename=self.log_filename, format="%(asctime)s - %(levelname)s - %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")

        logging.debug("New Run for " + self.day_string) 
        logging.debug("-----Logging Setup Information-----")
        logging.info("day_string: " + self.day_string)
        logging.info("device_name: " + self.device_name)
        logging.info("archive_path: " + self.archive_path)
        logging.info("day_dir: " + self.day_dir)
        logging.info("Twilight_Sunset: " + str(self.Twilight_Sunset))
        logging.info("Twilight_Sunrise: " + str(self.Twilight_Sunrise))
        logging.info("isNight: " + str(self.isNight))
        logging.info("loop_waits: " + str(self.loop_waits))
        logging.info("iso_set: " + self.iso_set)
        logging.info("take: " + self.take)
        logging.info("cronitor: " + self.cronitor)
        logging.debug("-----Run Start Information-------")
        logging.info("Next Twiglight Sunrise at " + str(self.Twilight_Sunrise))
        logging.info("Next/Last Twiglight Sunset at " + str(self.Twilight_Sunset))
        logging.debug("-----Run Log-----")

    def allsky(self):
        ImagingControl.observing_details(self)
        ImagingControl.set_directory(self)
        
        ImagingControl.buildLog(self)
        logging.warning("Begin Observing Pattern")        
        sleep_trigger = 0
        if self.config["Time"]["Wait_Night"] == "True":
            while ephem.Date(datetime.datetime.utcnow()) <= self.Twilight_Sunset:
                if sleep_trigger == 0: logging.debug("daylight_sleeping")
                sleep_trigger += 1
                a = self.cronitor + "?msg='Daylight'"
                os.system(a)
                time.sleep(self.loop_waits)   

        logging.warning("Sun has gone down!")
        if not os.path.isfile(self.log_filename): ImagingControl.buildLog(self)
        
        a = "pkill -f gphoto2"
        os.system(a)

        a = "gphoto2 --reset"
        os.system(a)

        os.chdir(self.day_dir)

        a = self.iso_set
        os.system(a)

        fail_count = 3
        counter = 1
        while ephem.Date(datetime.datetime.utcnow()) <= self.Twilight_Sunrise:
            logging.debug('Sun below twilight limit...taking image')

            file_count = len(fnmatch.filter(os.listdir(self.day_dir), '*.' + self.suffix))
            a = self.take
            os.system(a)
            new_count = len(fnmatch.filter(os.listdir(self.day_dir), '*.' + self.suffix))

            if new_count == file_count:
                logging.critical("PANIC: No Image Saved In Loop")
                a = "pkill -f gphoto2"
                os.system(a)
                a = "gphoto2 --reset"
                os.system(a)
                fail_count += 1
            else:
                a = self.cronitor + "?msg='Imaging'"
                os.system(a)            
                logging.debug('Image %d done' % counter)
                counter += 1

            if fail_count % 5 == 0:
                logging.error('Cycling Camera Power')
                a = self.power_off
                os.system(a)
                time.sleep(10)
                a = self.power_on
                os.system(a)
                fail_count += 1

            this_wait = self.loop_waits

            if self.config["Camera"]["Alt_ISO"] == "True":
                if counter % int(self.config["Camera"]["Alt_ISO_Frequency"]) == 0:
                    a = self.alt_iso_set
                    os.system(a)
                    a = self.alt_take
                    os.system(a)
                    a = self.iso_set
                    os.system(a)
                    this_wait = this_wait - int(self.config["Camera"]["Alt_ISO_Exposure"]) - 2
                    if this_wait < 0: this_wait = 0
                    logging.debug('Alt_ISO done after image %d' % counter)

            time.sleep(this_wait)
            logging.debug('Next image')  
          
        file_count = len(fnmatch.filter(os.listdir(self.day_dir), '*.' + self.suffix)) - 1
        logging.info("%d images taken overnight on counter" % counter)
        logging.info("%d images saved in folder" % file_count)
        if counter != file_count: logging.warning("File Count mismatch -- Check Errors")
        logging.debug('Nautical Sunrise ' + str(self.Twilight_Sunrise))
        logging.debug('Time now ' + str(datetime.datetime.utcnow()))
        logging.debug('Bed Time, I sleep in the Day!')
        a = self.cronitor + "?msg='WakingUp'"
        os.system(a)
        time.sleep(self.loop_waits * 2)

def main():
    continuous = True
    while continuous == True:
        observe = ImagingControl(os.path.expanduser("~") + "/allsky.ini")
        observe.allsky()
        logging.debug("Build New Night")

    logging.error("goodbye for some reason")            

if __name__ == "__main__":
    main()
