import requests
import json
import sys
from datetime import datetime, timedelta


URL = "https://api.mews-demo.com/api/connector/v1/"
HEADERS = {"Content-Type": "application/json"}

def post(endpoint, payload):
    response = requests.post(URL + endpoint, data=json.dumps(payload), headers=HEADERS)
    if response.status_code != 200:
        print(f"Error at {endpoint}: {response.status_code} - {response.text}")
        sys.exit(response)
    return response.json()

def getEnterpriseConfig(payload):
    data = post("configuration/get", payload)
    return {
        "enterpriseId": data["Enterprise"]["Id"],
        "chainId": data["Enterprise"]["ChainId"],
        "currencies": [c["Currency"] for c in data["Enterprise"]["Currencies"] if c.get("IsEnabled")],
        "pricing": data["Enterprise"]["Pricing"],
        "timezone": data["Enterprise"]["TimeZoneIdentifier"],
        "nowUtc": data["NowUtc"]
    }

def getServiceBookableIds(payload):
    data = post("services/getAll", payload)
    return [
        [s['Id'], s['Data']['Value']['StartOffset'], s['Data']['Value']['EndOffset']]
        for s in data["Services"]
        if s.get('Data', {}).get('Discriminator') == 'Bookable'
        and s.get('IsActive')
        and s.get('Data', {}).get('Value', {}).get('TimeUnitPeriod') == 'Day'
    ]

def getAgeCategoryId(payload):
    data = post("ageCategories/getAll", payload)
    for age in data["AgeCategories"]:
        if age.get('MinimalAge') is None and age.get('MaximalAge') is None:
            return age['Id']
    return None

def getRatesIdEnabled(payload):
    data = post("rates/getAll", payload)
    return [r['Id'] for r in data["Rates"] if r.get('IsEnabled') and r.get('IsActive') and r.get('IsPublic')]

def getCategoryAvailabilities(payload):
    data = post("services/getAvailability", payload)
    return data["CategoryAvailabilities"]

def getDefaultGuests(payload):
    data = post("resourceCategories/getAll", payload)
    return data["ResourceCategories"][0]["Capacity"]

def getActiveProductIds(payload):
    data = post("products/getAll", payload)
    return [p['Id'] for p in data["CustomerProducts"] if p.get('IsActive')]

def createGuest(payload):
    data = post("customers/add", payload)
    return data.get("Id")

def getTaxRateCodes(payload):
    data = post("rates/getpricing", payload)
    codes = []
    for entry in data['BaseAmountPrices']:
        for item in entry['Breakdown']['Items']:
            if item['TaxRateCode']:
                codes.append(item['TaxRateCode'])
    return list(set(codes))

def createReservations(payload):
    response = requests.post(URL + "reservations/add", data=json.dumps(payload), headers=HEADERS)
    if response.status_code == 200:
        return True
    else:
        print("Failed to create reservation", response.status_code, response.text)
        return False

def getStartTimeUnitUtc(timeZoneLocation):
    # Get current UTC datetime
    nowUtcDatetime = datetime.utcnow()

    # Get current local time in specified timezone
    localTz = pytz.timezone(timeZoneLocation)
    localTime = datetime.now(localTz)
    localTime = localTz.normalize(localTime)

    # Calculate offset
    offset = localTime.strftime('%z')  # e.g., +0200
    plusMinus = offset[0]
    hoursOffset = int(offset[1:3])
    minuteOffset = int(offset[3:5])

    # Adjust UTC time to mimic the offset
    if plusMinus == '+':
        hoursOffset = 24 - hoursOffset
        if minuteOffset != 0:
            minuteOffset = 60 - minuteOffset
    nowUpdate = nowUtcDatetime.replace(hour=hoursOffset, minute=minuteOffset, second=0)

    # Return ISO format UTC timestamp
    return nowUpdate.strftime("%Y-%m-%dT%H:%M:%SZ")

    