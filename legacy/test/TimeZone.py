from datetime import datetime, timedelta
import pytz

def adjust_timezone(FirstDayUTC, NextDayUTC, CheckInTime, CheckOutTime, TimeZoneLocation="Europe/Amsterdam"):
    local_timezone = pytz.timezone(TimeZoneLocation)
    
    # Get initial timezone offset for FirstDayUTC
    initial_local_time_first = FirstDayUTC.astimezone(local_timezone)
    initial_offset_first = initial_local_time_first.utcoffset().total_seconds() // 3600

    # Get initial timezone offset for NextDayUTC
    initial_local_time_next = NextDayUTC.astimezone(local_timezone)
    initial_offset_next = initial_local_time_next.utcoffset().total_seconds() // 3600
    
    # Check for timezone difference for FirstDayUTC
    current_local_time_first = FirstDayUTC.astimezone(local_timezone)
    current_offset_first = current_local_time_first.utcoffset().total_seconds() // 3600
    
    # Adjust FirstDayUTC if the offset has changed
    if current_offset_first != initial_offset_first:
        print(f"Timezone difference changed for FirstDayUTC! Updating from {initial_offset_first} to {current_offset_first}")
        updated_hour_first = CheckInTime - (initial_offset_first - current_offset_first)
        FirstDayUTC = FirstDayUTC.replace(hour=int(updated_hour_first))
        initial_offset_first = current_offset_first  # Update the initial offset for FirstDayUTC
    
    # Check for timezone difference for NextDayUTC
    current_local_time_next = NextDayUTC.astimezone(local_timezone)
    current_offset_next = current_local_time_next.utcoffset().total_seconds() // 3600
    
    # Adjust NextDayUTC if the offset has changed
    if current_offset_next != initial_offset_next:
        print(f"Timezone difference changed for NextDayUTC! Updating from {initial_offset_next} to {current_offset_next}")
        updated_hour_next = CheckOutTime - (initial_offset_next - current_offset_next)
        NextDayUTC = NextDayUTC.replace(hour=int(updated_hour_next))
        initial_offset_next = current_offset_next  # Update the initial offset for NextDayUTC

    FirstDayUTC = datetime.fromisoformat(str(FirstDayUTC))
    FirstDayUTC = FirstDayUTC.strftime('%Y-%m-%d %H:%M:%S')
    NextDayUTC = datetime.fromisoformat(str(NextDayUTC))
    NextDayUTC = NextDayUTC.strftime('%Y-%m-%d %H:%M:%S')
    
    return FirstDayUTC, NextDayUTC
