from datetime import timedelta

DOMAIN = "rainbow_weather"
CONF_API_KEY = "api_key"
CONF_LATITUDE = "latitude"
CONF_LONGITUDE = "longitude"

PLATFORMS = ["sensor", "binary_sensor", "button"]
SCAN_INTERVAL = timedelta(minutes=5)
API_URL = "https://api.rainbow.ai/nowcast/v1/precip/{longitude}/{latitude}"

ATTR_FORECAST = "forecast"
ATTR_SUMMARY = "summary"
