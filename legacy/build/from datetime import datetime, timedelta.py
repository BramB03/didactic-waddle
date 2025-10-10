from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def get_utc_time(timezone_name, date):
    tz = ZoneInfo(timezone_name)
    dt = datetime(date.year, date.month, date.day, 0, 0, 0, tzinfo=tz)
    utc_dt = dt.astimezone(ZoneInfo('UTC'))
    formatted_time = utc_dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    formatted_time = formatted_time[:-3] + 'Z'
    return formatted_time

# Define the timezone and current date
timezone_name = 'Europe/Amsterdam'
current_date = datetime.now()

# Calculate future dates
date_90_days = current_date + timedelta(days=90)
date_180_days = current_date + timedelta(days=180)

# Get UTC times
utc_time_now = get_utc_time(timezone_name, current_date)
utc_time_90_days = get_utc_time(timezone_name, date_90_days)
utc_time_180_days = get_utc_time(timezone_name, date_180_days)

print(f"UTC time now: {utc_time_now}")
print(f"UTC time in 90 days: {utc_time_90_days}")
print(f"UTC time in 180 days: {utc_time_180_days}")
