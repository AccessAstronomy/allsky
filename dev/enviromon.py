# # -*- coding: utf-8 -*-

"""enviromon.py: Environment monitoring for All Sky Night Time Monitoring with Raspberry Pi and Canon Cameras"""
"""allsky-latest.py: Control for All Sky Night Time Monitoring with Raspberry Pi and Canon Cameras"""

__author__ = "Jake Noel-Storr"
__copyright__ = "Copyright 2025, AccessAstronomy.eu"
__credits__ = ["Jake Noel-Storr", "Dirk van der Geest"]
__license__ = "GPL"
__version__ = "0.2.1"
__maintainer__ = "Jake Noel-Storr"
__email__ = "jake@accessastronomy.eu"
__status__ = "Development"

import glob
import json
import board
import adafruit_dht
import os
import datetime as dt
import numpy as np
import openmeteo_requests
import requests_cache
from retry_requests import retry
from configparser import ConfigParser
import subprocess
from statusbyte import StatusByte


class EnviroMon:
	def __init__(self):
		self.config_file = "allsky.ini"
		self.status = StatusByte()
		self.status._read_status_file()


	def configure(self):
		config = ConfigParser()
		config.read(self.config_file)
		self.lat, self.lon = config["Location"]["Camera_Latitude"], config["Location"]["Camera_Longitude"]
		self.device_name = config["Paths"]["Camera_ID"]
		self.do_DHT, self.DHT_Type, self.DHT_Pin = config["Environment"].getboolean("Box_DHT"), config["Environment"]["DHT_Type"], config["Environment"]["DHT_Pin"]
		self.sensor = adafruit_dht.getattr(adafruit_dht, self.DHT_Type)(getattr(board, self.DHT_Pin))

dtstr = dt.datetime.now()
tmrw = dtstr + dt.timedelta(hours = 12)

box_temp = None
box_humidity = None

if 
while do_DHT:
	try:
		box_temp = sensor.temperature
		box_humidity = sensor.humidity
		do_DHT = False
	except:
	    continue

cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": lat,
	"longitude": lon,
#	"hourly": ["temperature_2m", "relative_humidity_2m", "dew_point_2m", "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "visibility", "temperature_80m", "temperature_120m", "temperature_180m"],
	"current": ["temperature_2m", "relative_humidity_2m", "precipitation", "cloud_cover", "visibility"],
	"start_date": dtstr.date(),
	"end_date": tmrw.date()}
responses = openmeteo.weather_api(url, params=params)
response = responses[0]

current = response.Current()
current_temperature_2m = format(current.Variables(0).Value(), '.2f')
current_relative_humidity_2m = format(current.Variables(1).Value(), '.2f')
current_precipitation = format(current.Variables(2).Value(), '.2f')
current_cloud_cover = format(current.Variables(3).Value(), '.2f')
current_visibility = format(current.Variables(4).Value(), '.2f')

exif_ccd_temp = np.nan
exif_color_temp = np.nan
candidates = glob.glob(os.path.join("/home/Archive/*/*", "*.cr?"))

#if status.byte & 0b00000010 and candidates:  # if imaging
if candidates:
    latest = max(candidates, key=os.path.getmtime)
    res = subprocess.run(["exiftool", "-j", latest], capture_output=True, text=True, check=True)
    arr = json.loads(res.stdout)
    data = arr[0]
    exif_ccd_temp = (data["CameraTemperature"]).replace(" C","")
    exif_color_temp = (data["ColorTempAsShot"])
	
cpu_temp = os.popen("vcgencmd measure_temp").readline().replace("temp=","").replace("'C\n","")

cmd = f"echo {dtstr} {box_temp} {box_humidity} {cpu_temp} {exif_ccd_temp} {exif_color_temp} {current_temperature_2m} {current_relative_humidity_2m} {current_cloud_cover} {current_precipitation} {current_visibility} >> $HOME/enviro.dat"
os.system(cmd)
  
def main():
	pass

if __name__ == "__main__":
    main()