import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from configparser import ConfigParser
import datetime
import os
from slack_sdk import WebClient
from configparser import ConfigParser
import json

config_file = "allsky.ini"
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

config = ConfigParser()
config.read(config_file)
lat, lon = config["Location"]["Camera_Latitude"], config["Location"]["Camera_Longitude"]
token = config["Slack"]["Key"]
device_name = config["Paths"]["Camera_ID"]

date = datetime.datetime.utcnow() 
tmrw = date + datetime.timedelta(hours = 12)

url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": lat,
	"longitude": lon,
	"hourly": ["temperature_2m", "relative_humidity_2m", "dew_point_2m", "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "visibility", "temperature_80m", "temperature_120m", "temperature_180m"],
	"current": ["temperature_2m", "relative_humidity_2m", "precipitation", "cloud_cover"],
	"start_date": date.date(),
	"end_date": tmrw.date()}
responses = openmeteo.weather_api(url, params=params)
response = responses[0]

hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
hourly_dew_point_2m = hourly.Variables(2).ValuesAsNumpy()
hourly_cloud_cover = hourly.Variables(3).ValuesAsNumpy()
hourly_cloud_cover_low = hourly.Variables(4).ValuesAsNumpy()
hourly_cloud_cover_mid = hourly.Variables(5).ValuesAsNumpy()
hourly_cloud_cover_high = hourly.Variables(6).ValuesAsNumpy()
hourly_visibility = hourly.Variables(7).ValuesAsNumpy()
hourly_temperature_80m = hourly.Variables(8).ValuesAsNumpy()
hourly_temperature_120m = hourly.Variables(9).ValuesAsNumpy()
hourly_temperature_180m = hourly.Variables(10).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
hourly_data["dew_point_2m"] = hourly_dew_point_2m
hourly_data["cloud_cover"] = hourly_cloud_cover
hourly_data["cloud_cover_low"] = hourly_cloud_cover_low
hourly_data["cloud_cover_mid"] = hourly_cloud_cover_mid
hourly_data["cloud_cover_high"] = hourly_cloud_cover_high
hourly_data["visibility"] = hourly_visibility
hourly_data["temperature_80m"] = hourly_temperature_80m
hourly_data["temperature_120m"] = hourly_temperature_120m
hourly_data["temperature_180m"] = hourly_temperature_180m

hourly_dataframe = pd.DataFrame(data = hourly_data)

wx = [hourly_dataframe[17:29]["cloud_cover"].min(),hourly_dataframe[17:29]["cloud_cover"].max(),hourly_dataframe[17:29]["cloud_cover"].mean(),
      hourly_dataframe[17:29]["cloud_cover"].quantile(0.25),hourly_dataframe[17:29]["cloud_cover"].quantile(0.5),hourly_dataframe[17:29]["cloud_cover"].quantile(0.75),
      hourly_dataframe[17:29]["relative_humidity_2m"].mean(),hourly_dataframe[17:29]["relative_humidity_2m"].min(),hourly_dataframe[17:29]["relative_humidity_2m"].max()]

weather_out = f"My night's forecast: Cloud Cover from {wx[0]:.0f}% to {wx[1]:.0f}% Mean: {wx[2]:.0f}% (1stQ {wx[3]:.0f}%, Med {wx[4]:.0f}%, 3rdQ {wx[5]:.0f}%). Humidty {wx[6]:.0f}% (from {wx[7]:.0f}% to {wx[8]:.0f}%)."

emoji = "cloud"
colour = "#a9a9a9"

if wx[2] < 80: 
    emoji = "partly_sunny"
    colour = "#444444"
if wx[2] < 40: 
    emoji = "moon"
    colour = "#7b679a"
if wx[2] < 20: 
    emoji = "night_with_stars"
    colour = "#4b0082"

blocks_json = [
		{
			"type": "divider"
		},
		{
			"type": "rich_text",
			"elements": [
				{
					"type": "rich_text_section",
					"elements": [
						{
							"type": "emoji",
							"name": f"{emoji}"
						},
						{
							"type": "text",
							"text": f" {device_name} Overnight Weather Forecast:"
						}
					]
				}
			]
		}
	]

attachments_json = [
    {
        "mrkdwn_in": ["text"],
        "color": colour,
        "fields":
        [
            {
                "title": "Mean Cloud",
                "value": f"{wx[2]:.0f}%",
                "short": True
            },
            {
                "title": "Cloud Range",
                "value": f"{wx[0]:.0f}% .. {wx[1]:.0f}%",
                "short": True
            },
            {
                "title": "Cloud Cover Quartiles",
                "value": f"{wx[3]:.0f}% .. {wx[4]:.0f}% .. {wx[5]:.0f}%",
                "short": False
            },
            {
                "title": "Mean Humidity",
                "value": f"{wx[6]:.0f}%",
                "short": True
            },
            {
                "title": "Humidity Range",
                "value": f"{wx[7]:.0f}% .. {wx[8]:.0f}%",
                "short": True
            }
        ]
    }
]

client = WebClient(token=token)
channel_id = "C06729CNQKC" #system-monitor
#channel_id = "C06AK1ZFKBR" #bottest
result = client.chat_postMessage(
    channel=channel_id,
    blocks=json.dumps(blocks_json),
    attachments=json.dumps(attachments_json)
)
