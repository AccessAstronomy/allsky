import openmeteo_requests

import pandas as pd
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://air-quality-api.open-meteo.com/v1/air-quality"
params = {
	"latitude": 53.3838777,
	"longitude": 6.23471666,
	"current": ["dust", "aerosol_optical_depth", "pm10", "pm2_5"],
	"domains": "cams_europe",
	"timeformat": "unixtime"
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Current values. The order of variables needs to be the same as requested.
current = response.Current()
current_dust = current.Variables(0).Value()
current_aerosol_optical_depth = current.Variables(1).Value()
current_pm10 = current.Variables(2).Value()
current_pm2_5 = current.Variables(3).Value()

print(f"Current time {current.Time()}")
print(f"Current dust {current_dust}")
print(f"Current aerosol_optical_depth {current_aerosol_optical_depth}")
print(f"Current pm10 {current_pm10}")
print(f"Current pm2_5 {current_pm2_5}")

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 53.3838777,
	"longitude": 6.23471666,
	"hourly": ["temperature_2m", "relative_humidity_2m", "dew_point_2m", "cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high", "visibility", "temperature_80m", "temperature_120m", "temperature_180m"],
	"current": ["temperature_2m", "relative_humidity_2m", "precipitation", "cloud_cover"],
	"start_date": "2025-06-08",
	"end_date": "2025-06-09"}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

# Current values. The order of variables needs to be the same as requested.
current = response.Current()
current_temperature_2m = current.Variables(0).Value()
current_relative_humidity_2m = current.Variables(1).Value()
current_precipitation = current.Variables(2).Value()
current_cloud_cover = current.Variables(3).Value()

print(f"Current time {current.Time()}")
print(f"Current temperature_2m {current_temperature_2m}")
print(f"Current relative_humidity_2m {current_relative_humidity_2m}")
print(f"Current precipitation {current_precipitation}")
print(f"Current cloud_cover {current_cloud_cover}")

# Process hourly data. The order of variables needs to be the same as requested.
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
print(hourly_dataframe)