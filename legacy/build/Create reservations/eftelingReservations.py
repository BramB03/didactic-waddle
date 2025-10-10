from randomNames import firstName
from randomNames import lastName
import sys
import requests
import json
from datetime import datetime, timedelta
import random
import math
import pytz
import time

headers = {
"Content-Type": "application/json"
}

'''
ClientToken = "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D"
Efteling hotel test = "D546E3C64E3640D1AEA2B1C50094DCEF-999B7AA0C1471EBC8D7140DBAD8232A"
'''


ClientToken = "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D"
AccessToken = "D546E3C64E3640D1AEA2B1C50094DCEF-999B7AA0C1471EBC8D7140DBAD8232A"
Client = "Test"

payloadBase = {
"ClientToken": ClientToken,
"AccessToken": AccessToken,
"Client": Client
}

# Number of minutes to sleep
minutes = 0
#change number to add days into future
weekOffset = 18

for minute in range(minutes, 0, -1):
    print(f"{minute} more minute(s)...")
    time.sleep(60)

print("Initiating...")


json_payloadBase = json.dumps(payloadBase) # Convert the payload to JSON format
getConfig = requests.post("https://api.mews-demo.com/api/connector/v1/configuration/get", data=json_payloadBase, headers=headers) # Send the POST request
if getConfig.status_code != 200:
    Error = "Getconfig" + str(getConfig)
    sys.exit(Error)
getConfig_data = getConfig.json() # Parse the JSON response
# Get ID's from getConfig
enterprise_id = getConfig_data["Enterprise"]["Id"]
chain_id = getConfig_data["Enterprise"]["ChainId"]
currencies_ids_list = getConfig_data["Enterprise"]["Currencies"]
currency_active_ids = [currency['Currency'] for currency in currencies_ids_list if currency.get('IsEnabled')]
TaxEnv = getConfig_data["Enterprise"]["Pricing"]    
NowUtc = getConfig_data.get("NowUtc")
nowJson = json.dumps(NowUtc)
TimeZoneLocation = getConfig_data["Enterprise"]["TimeZoneIdentifier"]

NowUtc = json.loads(nowJson)
NowUtc += timedelta(days=weekOffset)
now_utc_datetime = datetime.strptime(NowUtc, "%Y-%m-%dT%H:%M:%SZ")
local_tz = pytz.timezone(TimeZoneLocation)
localTime = datetime.now(local_tz)
localTime = local_tz.normalize(localTime)
offset = localTime.strftime('%z')
plusMinus = offset[0:1]
hoursOffset = int(offset[1:3])
minuteOffset = int(offset[3:5])
if plusMinus == '+':
    hoursOffset = 24 - hoursOffset
    if minuteOffset != 0:
        minuteOffset = 60 - minuteOffset
    nowUpdate = now_utc_datetime.replace(hour=hoursOffset, minute=minuteOffset, second=0)
else:
    nowUpdate = now_utc_datetime.replace(hour=hoursOffset, minute=minuteOffset, second=0)
StartTimeUnitUtc = nowUpdate.strftime("%Y-%m-%dT%H:%M:%SZ")

if TaxEnv == 'Net':
    GrossNet = 'NetValue'
else:
    GrossNet = 'GrossValue'

createdReservations = 0

headers = {
    "Content-Type": "application/json"
}

# JSON payload to be sent in the POST request
payload1 = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "Client": Client,
    "EnterpriseId": enterprise_id,
    "Limitation":{ "Count": 50 }
}

json_payload1 = json.dumps(payload1) # Convert the payload to JSON format
getService = requests.post("https://api.mews-demo.com/api/connector/v1/services/getAll", data=json_payload1, headers=headers) # Send the POST request
if getService.status_code != 200:
    print(getService)
    sys.exit(getService)
getService_data = getService.json() # Parse the JSON response
time.sleep(0.2)
service_ids_list = getService_data["Services"]
bookable_active_ids = [[service['Id'], service['Data']['Value']['StartOffset'], service['Data']['Value']['EndOffset']] for service in service_ids_list if service.get('Data', {}).get('Discriminator') == 'Bookable' and service.get('IsActive')]
for serviceId in bookable_active_ids:
#   get rates active list for random
    payload0 = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "Client": Client,
    "EnterpriseId": enterprise_id,
    "ServiceIds": [
    serviceId[0]
    ],
    "ActivityStates": [ "Active" ],
    "Limitation": { "Count": 5 }
    }
    json_payload0 = json.dumps(payload0) # Convert the payload to JSON format
    getAge = requests.post("https://api.mews-demo.com/api/connector/v1/ageCategories/getAll", data=json_payload0, headers=headers) # Send the POST request
    if getAge.status_code != 200:
        print(getAge)
        sys.exit(getAge)
    getAge_data = getAge.json() # Parse the JSON response
    time.sleep(0.2)
    ageCatrgoryIds = getAge_data["AgeCategories"]
    ageCategory = [age['Id'] for age in ageCatrgoryIds if age.get('MinimalAge') is None and age.get('MaximalAge') is None]
    ageCategoryString = ''.join(ageCategory)
    payload2 = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "Client": Client,
    "EnterpriseId": enterprise_id,
    "ServiceIds": [
    serviceId[0]
    ],
    "ActivityState": "Active",
    "Extent": {
        "Rates": "true",
    },
    "Limitation": { "Count": 80 }
    }
    json_payload2 = json.dumps(payload2) # Convert the payload to JSON format
    getRates = requests.post("https://api.mews-demo.com/api/connector/v1/rates/getAll", data=json_payload2, headers=headers) # Send the POST request
    if getRates.status_code != 200:
        Error = "GetRates" + str(getRates)
        sys.exit(Error)
    getRates_data = getRates.json() # Parse the JSON response
    rate_ids_data = getRates_data["Rates"]
    time.sleep(0.2)
    rate_active_ids = [rate['Id'] for rate in rate_ids_data if rate.get('IsEnabled') and rate.get('IsActive') and rate.get('IsPublic')]
    payload3 = {
        "ClientToken": ClientToken,
        "AccessToken": AccessToken,
        "Client": Client,
        "EnterpriseId": enterprise_id,
        "ServiceId": serviceId[0],
        "FirstTimeUnitStartUtc": StartTimeUnitUtc,
        "LastTimeUnitStartUtc": StartTimeUnitUtc
    }
    json_payload3 = json.dumps(payload3) # Convert the payload to JSON format
    getAvailability = requests.post("https://api.mews-demo.com/api/connector/v1/services/getAvailability", data=json_payload3, headers=headers) # Send the POST request
    getAvailability_data = getAvailability.json() # Parse the JSON response
    if getAvailability.status_code != 200:
        print(getAvailability_data)
        continue
    category_availabilities = getAvailability_data["CategoryAvailabilities"]
    #category_availabilities.reverse()
    time.sleep(0.2)  
    category_id =[]
    Counter250 = 0
    for category in category_availabilities:
        Counter400 = 0
        categoryId = category['CategoryId']
        availabilities = category["Availabilities"]
        if availabilities == 0:
            break
        mean = sum(availabilities) / len(availabilities)
        availabilityAdjusted = math.ceil(mean * 1.6)
        payload5 = {
        "ClientToken": ClientToken,
        "AccessToken": AccessToken,
        "Client": Client,
        "EnterpriseId": enterprise_id,
        "ServiceIds": [
        serviceId[0]
        ],
        "ResourceId": categoryId,
        "Limitation":{
        "Count": 1
        }
        }
        json_payload5 = json.dumps(payload5) # Convert the payload to JSON format
        getGuests = requests.post("https://api.mews-demo.com/api/connector/v1/resourceCategories/getAll", data=json_payload5, headers=headers) # Send the POST request
        if getGuests.status_code != 200:
            Error = "getGuests" + str(getGuests)
            continue
        getGuests_data = getGuests.json()
        defaultGuests = getGuests_data["ResourceCategories"][0]["Capacity"]
        
        payload13 = {
        "ClientToken": ClientToken,
        "AccessToken": AccessToken,
        "Client": Client,
        "EnterpriseId": enterprise_id,
        "ServiceIds": [
        serviceId[0]
        ],
        "Limitation":{
        "Count": 50
        }
        }
        json_payload13 = json.dumps(payload13) # Convert the payload to JSON format
        getProd = requests.post("https://api.mews-demo.com/api/connector/v1/products/getAll", data=json_payload13, headers=headers) # Send the POST request
        if getProd.status_code != 200:
            Error = "getProd" + str(getProd)
            continue
        getProd_data = getProd.json() # Parse the JSON response
        prodList = getProd_data["CustomerProducts"]
        activeProdList = [product['Id'] for product in prodList if product.get('IsActive')]
        #change 1 to availabilities if succes
        for i in range(availabilityAdjusted):
            Counter250 = Counter250 + 1
            if Counter250 == 125:
                Error = "Reaching max posts"
                SystemExit(Error)
            firstNameId = random.choice(lastName)
            lastNameId = random.choice(firstName)
            emailId = firstNameId + "." + lastNameId + "@demo.com"
            payload6 = {
                "ClientToken": ClientToken,
                "AccessToken": AccessToken,
                "Client": Client,
                "ChainId": chain_id,
                "OverwriteExisting": 'true',
                "LastName": firstNameId,
                "FirstName": lastNameId,
                "Email": emailId,
            }
            json_payload6 = json.dumps(payload6) # Convert the payload to JSON format
            getGuest_data = requests.post("https://api.mews-demo.com/api/connector/v1/customers/add", data=json_payload6, headers=headers) # Send the POST request
            if getGuest_data.status_code != 200:
                Error = "getGuest_data" + str(getGuest_data)
                continue
            getGuestIdPlural = getGuest_data.json()
            GuestId = getGuestIdPlural.get('Id')
            payload11 = {
                "ClientToken": ClientToken,
                "AccessToken": AccessToken,
                "Client": Client,
                "EnterpriseId": enterprise_id,
                "CustomerId": GuestId,
            }
            #bookingengine api: hotels/getAll, store publickey van sandbox pci proxy, 
            #json_payload11 = json.dumps(payload11) # Convert the payload to JSON format
            #getCCconfirmation = requests.post("https://api.mews-demo.com/api/connector/v1/creditCards/addTokenized", data=json_payload11, headers=headers) # Send the POST request
            #getCCconfirmationtext = getCCconfirmation.json()
            #print(getCCconfirmationtext)
            randomNumbersIn =[ 0, 0, 0, 0, 0,0, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3]
            randomNumberIn = random.choice(randomNumbersIn)

            randomDayDeltaIn = timedelta(days=randomNumberIn) #weghalen
            randomNumbersOut = [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4, 5]
            randomNumberOut = random.randint(1, 5)
            randomDayDeltaOut = timedelta(days=randomNumberOut)
            num_times = randomNumberOut
            startOffsetData = serviceId[1]
            endOffsetData = serviceId[2]
            startOffset = int(startOffsetData[-7:-5])
            endOffset = int(endOffsetData[-7:-5])
            CheckInUpdate = nowUpdate + timedelta(hours=startOffset)
            CheckOutUpdate = nowUpdate + timedelta(hours=endOffset)
            checkInUpdate = CheckInUpdate + randomDayDeltaIn
            checkOutUpdate = CheckOutUpdate + randomDayDeltaOut + randomDayDeltaIn
            checkInTime = checkInUpdate.strftime("%Y-%m-%dT%H:%M:%SZ")
            checkOutTime = checkOutUpdate.strftime("%Y-%m-%dT%H:%M:%SZ")
            payloads = []
            payloadRes =[]
            index = 0
            rateId = random.choice(rate_active_ids)
            payload14 = {
                "ClientToken": ClientToken,
                "AccessToken": AccessToken,
                "Client": Client,
                "RateId": rateId,
                "FirstTimeUnitStartUtc": StartTimeUnitUtc,
                "LastTimeUnitStartUtC": StartTimeUnitUtc
            }
            json_payload14 = json.dumps(payload14) # Convert the payload to JSON format
            getPricingJson = requests.post("https://api.mews-demo.com/api/connector/v1/rates/getpricing", data=json_payload14, headers=headers) # Send the POST request
            getPricingData = getPricingJson.json()
            taxRateCodes = []
            for entry in getPricingData['BaseAmountPrices']:
                items = entry['Breakdown']['Items']
                for item in items:
                    taxRateCodes.append(item['TaxRateCode'])
            if taxRateCodes == [None]:
                continue
            for index in range(num_times):
                payload10 = {
                    "Index": index,
                    "Amount": {
                        "Currency": currency_active_ids[0],
                        GrossNet: random.randint(100, 200),
                        "TaxCodes": taxRateCodes
                    }
                }
                payloads.append(payload10)
            ranThree = [1, 1, 3, 2, 2, 2, 3, 5, 3, 4]
            numRes = random.choice(ranThree)
            if availabilityAdjusted < numRes:
                numRes = 1 
            
            for index in range(numRes):
                if activeProdList != []:
                    payload12 = {
                        "State" : "Confirmed",
                        "StartUtc": checkInTime, 
                        "EndUtc": checkOutTime,
                        "CustomerId": GuestId,
                        "RequestedCategoryId": categoryId,
                        "RateId": rateId,
                        "Notes": "Test reservation",
                        "PersonCounts": [
                            {
                            "AgeCategoryId": ageCategoryString,
                            "Count": defaultGuests
                        },
                        ],
                        "TimeUnitPrices": payloads,
                        "ProductOrders": [
                            {
                                "ProductId": random.choice(activeProdList)
                            }
                        ]
                    }
                    payloadRes.append(payload12)
                else:
                    payload12 = {
                        "State" : "Confirmed",
                        "StartUtc": checkInTime, 
                        "EndUtc": checkOutTime,
                        "CustomerId": GuestId,
                        "RequestedCategoryId": categoryId,
                        "RateId": rateId,
                        "Notes": "Test reservation",
                        "PersonCounts": [
                            {
                            "AgeCategoryId": ageCategoryString,
                            "Count": defaultGuests
                        },
                        ],
                        "TimeUnitPrices": payloads
                    }
                    payloadRes.append(payload12)
            payload4 = {
                "ClientToken": ClientToken,
                "AccessToken": AccessToken,
                "Client": Client,
                "EnterpriseId": enterprise_id,
                "ServiceId": serviceId[0],
                "CheckRateApplicability": "false",
                "GroupName": "Demo Push",
                "Reservations": payloadRes
            }
            json_payload4 = json.dumps(payload4) # Convert the payload to JSON format
            ResponseJson = requests.post("https://api.mews-demo.com/api/connector/v1/reservations/add", data=json_payload4, headers=headers) # Send the POST request
            
            if ResponseJson.status_code == 200:
                print(ResponseJson)
                createdReservations = createdReservations + 1
                time.sleep(0.2)
            else:
                Counter400 = Counter400 + 1
                Response = ResponseJson.json()
                print(Response)
                
            if Counter400 == 3:
                print("Moving to next space category")
                Counter400 = 0
                break

print(createdReservations)