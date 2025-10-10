from datetime import datetime, timedelta, timezone

# Get the current UTC time
now_utc = datetime.now(timezone.utc)

# Adjust to the start to midnight UTC by setting hours, minutes and seconds to zero.
# Adjust the hours incase of a difference bewteen due to the timezone
endUtc = now_utc.replace(hour=0,minute=0, second=0, microsecond=0)

# Calculate the start of the timeframe by setting minutes to 59 and seconds to 59
startUtc = endUtc - timedelta(days=1)
endUtc = endUtc - timedelta(seconds=1)

# Format both times in ISO 8601 format
output = {
    'start_utc': startUtc.isoformat(),
    'end_utc': endUtc.isoformat()
}
