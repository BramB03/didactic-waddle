import sys
import requests
import json
from datetime import datetime, timedelta, timezone
import random
import math
import subprocess
import time
import pytz

#prem onboarding tool
ClientToken = "83C9ED289A8D4E29823BB17F00F944FD-54EF3E61C88BBEA362EB90C2CC0BC80"
Client = "Mews Import Application"

#TheDavidTokenZuid
AccessTokenOne = "3865AA3369A24F18A95AB23300F4485B-4771FB299B0C950D7EA9CDE78F891D5"
#theDavidTokenSouth
AccessTokenTwo = "BB06E1EEA5AC40C792CAB23300F4CD77-04FFDDF48B0EB1D61A110EBCD728D80"
AccessTokens = [AccessTokenOne, AccessTokenTwo]

headers = {
    "Content-Type": "application/json"
}

utc_now = datetime.now(pytz.utc)
amsterdam_tz = pytz.timezone('Europe/Amsterdam')
amsterdam_now = utc_now.astimezone(amsterdam_tz)
time_difference = amsterdam_now - utc_now
Amsterdam_offset = amsterdam_now.utcoffset()

ServiceIds = {}
EnterpriseIds = []
rateIds = {}
productIds = {}
index = 0

for token in AccessTokens:
    payloadServicesGetAll = {
        "ClientToken": ClientToken,
        "AccessToken": token,
        "Client": Client,
        "Limitation":{ "Count": 20 }
    }
    json_payloadServicesGetAll = json.dumps(payloadServicesGetAll) # Convert the payload to JSON format
    getService = requests.post("https://api.mews-demo.com/api/connector/v1/services/getAll", data=json_payloadServicesGetAll, headers=headers) # Send the POST request
    getService_data = getService.json() # Parse the JSON response
    service_ids_list = getService_data["Services"]
    getEnterpriseId = getService_data["Services"][0]["EnterpriseId"]
    if getEnterpriseId not in EnterpriseIds:
        EnterpriseIds.append(getEnterpriseId)
    bookable_active_id_old = [
        (service["ExternalIdentifier"], service["Id"]) 
        for service in service_ids_list 
        if service.get('Data', {}).get('Discriminator') == 'Bookable' 
        and service.get('IsActive') 
        and service.get('ExternalIdentifier') == 'STAY'
    ]

    for external_id, service_id in bookable_active_id_old:
        if external_id not in ServiceIds:
            ServiceIds[external_id] = []
        ServiceIds[external_id].append(service_id)
    ServiceIdsPayload = [values[index] for values in ServiceIds.values() if len(values) > index]

    payloadRatesGetAll = {
        "ClientToken": ClientToken,
        "AccessToken": token,
        "EnterpriseIds": [
            EnterpriseIds[index]
        ],
        "ServiceIds": ServiceIdsPayload,
        
        "ActivityStates": [
            "Active"
        ],
        "Extent": {
            "Rates": True,
            "RateGroups": False,
            "AvailabilityBlockAssignments": False
        },
        "Limitation": {
            "Count": 100
        }
    }
    
    json_payloadRatesGetAll = json.dumps(payloadRatesGetAll) # Convert the payload to JSON format
    getRates = requests.post("https://api.mews-demo.com/api/connector/v1/rates/getAll", data=json_payloadRatesGetAll, headers=headers) # Send the POST request
    getRates_data = getRates.json() # Parse the JSON response
    rates_ids_list = getRates_data["Rates"]
    ratesIdsFiltered = [
        (rates["Name"], rates["Id"]) 
        for rates in rates_ids_list 
        if rates.get('IsActive')
        and rates.get('Type') != "AvailabilityB/lock"
    ]

    for external_id, rate_id in ratesIdsFiltered:
        if external_id not in rateIds:
            if index == 0:
                rateIds[external_id] = [rate_id, 'Missing']
            else:
                rateIds[external_id] = ['Missing', rate_id]
        else:
            if rateIds[external_id][0] == 'Missing':  # Check the first slot
                rateIds[external_id][0] = rate_id
            elif rateIds[external_id][1] == 'Missing':  # Check the second slot
                rateIds[external_id][1] = rate_id

    payloadProductsGetAll = {
        "ClientToken": ClientToken,
        "AccessToken": token,
        "EnterpriseIds": [
            EnterpriseIds[index]
        ],
        "ServiceIds": ServiceIdsPayload,
        "Limitation": {
            "Count": 100
        }
    }
    
    json_payloadProductsGetAll = json.dumps(payloadProductsGetAll) # Convert the payload to JSON format
    getProducts = requests.post("https://api.mews-demo.com/api/connector/v1/products/getAll", data=json_payloadProductsGetAll, headers=headers)
    getProducts_data = getProducts.json() 
    products_ids_list = getProducts_data["Products"]
    productsIdsFiltered = [
        (products["Name"], products["Id"], products["Price"]["GrossValue"], products["ChargingMode"], products["PostingMode"]) 
        for products in products_ids_list 
        if products.get('IsActive')
        and products.get('Name')
    ]

    for external_id, products_id, gross_value, charging_mode, posting_mode in productsIdsFiltered:
        if external_id not in productIds:
            # Create a new entry for this external_id
            if index == 0:
                productIds[external_id] = [products_id, 'Missing', gross_value, charging_mode, posting_mode]
            else:
                productIds[external_id] = ['Missing', products_id, gross_value, charging_mode, posting_mode]
        else:
            # Update the existing entry
            if productIds[external_id][0] == 'Missing':  # Check the first slot for products_id
                productIds[external_id][0] = products_id
            elif productIds[external_id][1] == 'Missing':  # Check the second slot for products_id
                productIds[external_id][1] = products_id

            # Ensure that the other fields (gross_value, charging_mode, posting_mode) are unique
            if gross_value not in productIds[external_id][2:]:
                productIds[external_id].append(gross_value)
            if charging_mode not in productIds[external_id][2:]:
                productIds[external_id].append(charging_mode)
            if posting_mode not in productIds[external_id][2:]:
                productIds[external_id].append(posting_mode)
    index = index + 1

print(productIds)
'''





payload6 = {
    "ClientToken": ClientToken,
    "AccessToken": AccessTokenTwo,
    "Client": Client,
    "Limitation":{ "Count": 20 }
}

json_payload6 = json.dumps(payload6) # Convert the payload to JSON format
getServiceNew = requests.post("https://api.mews-demo.com/api/connector/v1/services/getAll", data=json_payload6, headers=headers) # Send the POST request
getService_dataNew = getServiceNew.json() # Parse the JSON response
service_ids_listNew = getService_dataNew["Services"]
enterpriseIdNew = getService_dataNew["Services"][0]["EnterpriseId"]
bookable_active_id_new = [(serviceNew['ExternalIdentifier'], serviceNew["Id"]) for serviceNew in service_ids_listNew if serviceNew.get('Data', {}).get('Discriminator') == 'Bookable' and serviceNew.get('IsActive')]

dict1 = dict(bookable_active_id_old)
dict2 = dict(bookable_active_id_new)
CombinedServiceIds = []
for key in dict1.keys():
    if key in dict2:
        combined_tuple = (key, dict1[key], dict2[key])
        CombinedServiceIds.append(combined_tuple)

    #Get all restrictions ID's
for NewService in bookable_active_id_new:
    payload10 = {
        "ClientToken": ClientToken,
        "AccessToken": AccessTokenTwo,
        "Client": Client,
        "EnterpriseIds": [
            enterpriseIdNew
        ],
        "ServiceIds": [
            NewService[1]
        ],
        "Limitation": { "Count": 500 }
    }
    json_payload10 = json.dumps(payload10) # Convert the payload to JSON format
    DeleteRestrictions = requests.post("https://api.mews-demo.com/api/connector/v1/restrictions/getAll", data=json_payload10, headers=headers) # Send the POST request
    DeleteRestrictionsData = DeleteRestrictions.json() # Parse the JSON response
    ToDeleteRestrictions = [id['Id'] for id in DeleteRestrictionsData['Restrictions']]
#remove all restrictions based on ID
    payload11 = {
        "ClientToken": ClientToken,
        "AccessToken": AccessTokenTwo,
        "Client": Client,
        "RestrictionIds": ToDeleteRestrictions
    }
    json_payload11 = json.dumps(payload11) # Convert the payload to JSON format
    DeleteRestrictions = requests.post("https://api.mews-demo.com/api/connector/v1/restrictions/delete", data=json_payload11, headers=headers) # Send the POST request


for ExternalServiceId in ExternalServiceIds:
    payloads =[]
    restrictionsNotPosted = []
    for item in CombinedServiceIds:
        if item[0] == ExternalServiceId:
            serviceIdOld = item[1]
    for item in CombinedServiceIds:
        if item[0] == ExternalServiceId:
            serviceIdNew = item[2]    
    rateIdsOld = []
    payload2 = {
        "ClientToken": ClientToken,
        "AccessToken": AccessTokenOne,
        "Client": Client,
        "EnterpriseId": enterpriseIdOld,
        "ServiceIds": [
            serviceIdOld
        ],
        "ActivityStates": [
            "Active"
        ],
        "Extent": {
            "Rates": "true"
        },
        "Limitation": { "Count": 300 }
    }
    json_payload2 = json.dumps(payload2) # Convert the payload to JSON format
    getRates = requests.post("https://api.mews-demo.com/api/connector/v1/rates/getAll", data=json_payload2, headers=headers) # Send the POST request
    getRates_data = getRates.json() # Parse the JSON response
    getRatesList = getRates_data["Rates"]
    rateIdsOld = [(rates['ExternalIdentifier'], rates['Id']) for rates in getRatesList]
    payload5 = {
        "ClientToken": ClientToken,
        "AccessToken": AccessTokenTwo,
        "Client": Client,
        "EnterpriseId": enterpriseIdNew,
        "ServiceIds": [
            serviceIdNew
        ],
        "ActivityStates": [
            "Active"
        ],
        "Extent": {
            "Rates": "true"
        },
        "Limitation": { "Count": 300 }
    }
    json_payload5 = json.dumps(payload5) # Convert the payload to JSON format
    getRatesNew = requests.post("https://api.mews-demo.com/api/connector/v1/rates/getAll", data=json_payload5, headers=headers) # Send the POST request
    getRates_dataNew = getRatesNew.json() # Parse the JSON response
    getRatesListNew = getRates_dataNew["Rates"]
    RateIdsNew = [(rates["ExternalIdentifier"], rates["Id"]) for rates in getRatesListNew]
    dict1 = dict(rateIdsOld)
    dict2 = dict(RateIdsNew)
    CombinedRateIds = []
    for key in dict1.keys():
        if key in dict2:
            combined_tuple = (key, dict1[key], dict2[key])
            CombinedRateIds.append(combined_tuple)
        #store ID's, store EX identifier
    resourceIdsOld = []
    payload3 = {
    "ClientToken": ClientToken,
    "AccessToken": AccessTokenOne,
    "Client": Client,
    "EnterpriseIds": [
        enterpriseIdOld
    ],
    "ServiceIds": [
        serviceIdOld
    ],
    "ActivityStates": [ "Active" ],
        "Limitation":{
        "Count": 100
    }
    }
    json_payload3 = json.dumps(payload3) # Convert the payload to JSON format
    getResourceJson = requests.post("https://api.mews-demo.com/api/connector/v1/resourceCategories/getAll", data=json_payload3, headers=headers) # Send the POST request
    getResourceData = getResourceJson.json() # Parse the JSON response
    getResourceListOld = getResourceData["ResourceCategories"]
    resourceIdsOld = [(resource["ExternalIdentifier"], resource["Id"]) for resource in getResourceListOld]

    payload4 = {
    "ClientToken": ClientToken,
    "AccessToken": AccessTokenTwo,
    "Client": Client,
    "EnterpriseIds": [
        enterpriseIdNew
    ],
    "ServiceIds": [
        serviceIdNew
    ],
    "ActivityStates": [ "Active" ],
        "Limitation":{
        "Count": 100
    }
    }
    json_payload4 = json.dumps(payload4) # Convert the payload to JSON format
    getResourceJson = requests.post("https://api.mews-demo.com/api/connector/v1/resourceCategories/getAll", data=json_payload4, headers=headers) # Send the POST request
    getResourceData = getResourceJson.json() # Parse the JSON response
    getResourceListNew = getResourceData["ResourceCategories"]
    getResourceType = [(type["Type"]) for type in getResourceListNew]
    resourceIdsNew = [(resource["ExternalIdentifier"], resource["Id"]) for resource in getResourceListNew]
    dict1 = dict(resourceIdsOld)
    dict2 = dict(resourceIdsNew)
    CombinedResourceIds = []
    for key in dict1.keys():
        if key in dict2:
            combined_tuple = (key, dict1[key], dict2[key])
            CombinedResourceIds.append(combined_tuple)
    if not CombinedResourceIds:
        CombinedResourceIds = None
    #rategroups
    rateGroupOld = []
    payload5 = {
    "ClientToken": ClientToken,
    "AccessToken": AccessTokenOne,
    "Client": Client,
    "EnterpriseIds": [
        enterpriseIdOld
    ],
    "ServiceIds": [
        serviceIdOld
    ],
    "ActivityStates": [ "Active" ],
        "Limitation":{
        "Count": 25
    }
    }
    json_payload5 = json.dumps(payload5) # Convert the payload to JSON format
    getRateGroupJson = requests.post("https://api.mews-demo.com/api/connector/v1/rateGroups/getAll", data=json_payload5, headers=headers) # Send the POST request
    getRateGroupData = getRateGroupJson.json() # Parse the JSON response
    getRateGroupListOld = getRateGroupData["RateGroups"]
    RateGroupIdsOld = [(RateGroup["ExternalIdentifier"], RateGroup["Id"]) for RateGroup in getRateGroupListOld]

    payload6 = {
    "ClientToken": ClientToken,
    "AccessToken": AccessTokenTwo,
    "Client": Client,
    "EnterpriseIds": [
        enterpriseIdNew
    ],
    "ServiceIds": [
        serviceIdNew
    ],
    "ActivityStates": [ "Active" ],
        "Limitation":{
        "Count": 25
    }
    }
    json_payload6 = json.dumps(payload6) # Convert the payload to JSON format
    getRateGroupJsonNew = requests.post("https://api.mews-demo.com/api/connector/v1/rateGroups/getAll", data=json_payload6, headers=headers) # Send the POST request
    getRateGroupDataNew = getRateGroupJsonNew.json() # Parse the JSON response
    getRateGroupListNew = getRateGroupDataNew["RateGroups"]
    RateGroupIdsNew = [(RateGroup["ExternalIdentifier"], RateGroup["Id"]) for RateGroup in getRateGroupListNew]
    dict1 = dict(RateGroupIdsOld)
    dict2 = dict(RateGroupIdsNew)
    CombinedRateGroupIds = []
    for key in dict1.keys():
        if key in dict2:
            combined_tuple = (key, dict1[key], dict2[key])
            CombinedRateGroupIds.append(combined_tuple)

    payload7 = {
        "ClientToken": ClientToken,
        "AccessToken": AccessTokenOne,
        "Client": Client,
        "EnterpriseIds": [
            enterpriseIdOld
        ],
        "ServiceIds": [
            serviceIdOld
        ],
        "Limitation": { "Count": 500 }
    }
    json_payload7 = json.dumps(payload7) # Convert the payload to JSON format
    getRestrictionsOld = requests.post("https://api.mews-demo.com/api/connector/v1/restrictions/getAll", data=json_payload7, headers=headers) # Send the POST request
    Restrictions_dataOld = getRestrictionsOld.json() # Parse the JSON response
    restrictionList = Restrictions_dataOld["Restrictions"]
    
    #i = 0
    for restriction in restrictionList:
        RestrictionServiceId = restriction["ServiceId"]
        RestrictionId = restriction["Id"]
        ExactRateId = restriction["Conditions"]["ExactRateId"]
        BaseRateId = restriction["Conditions"]["BaseRateId"]
        RateGroupId = restriction["Conditions"]["RateGroupId"]
        ResourceCategoryId = restriction["Conditions"]["ResourceCategoryId"]
        #Copy data 
        ResourceCategoryType = restriction["Conditions"]["ResourceCategoryType"]
        StartUtc = restriction["Conditions"]["StartUtc"]
        EndUtc = restriction["Conditions"]["EndUtc"]
        Days = restriction["Conditions"]["Days"]
        daysOption = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        days_dict = {day: (day in Days) for day in daysOption}       
        RestrictionType = restriction["Conditions"]["Type"]
        MinAdvance, MaxAdvance, MinLength, MaxLength, MinPrice, MaxPrice, MinReservationCount, MaxReservationCount = None, None, None, None, None, None, None, None 
        MinAdvance = restriction["Exceptions"]["MinAdvance"]
        MaxAdvance = restriction["Exceptions"]["MaxAdvance"]
        MinLength = restriction["Exceptions"]["MinLength"]
        MaxLength = restriction["Exceptions"]["MaxLength"]
        MinPrice = restriction["Exceptions"]["MinPrice"]
        MaxPrice = restriction["Exceptions"]["MaxPrice"]
        MinReservationCount = restriction["Exceptions"]["MinReservationCount"]
        MaxReservationCount = restriction["Exceptions"]["MaxReservationCount"]
        #Morph data
        RestrictionServiceIdNew = None 
        ExactRateIdNew = None
        BaseRateIdNew = None
        RateGroupIdNew = None
        ResourceCategoryIdNew = None
        token = 0
        for item in CombinedServiceIds:
            if item[1] == RestrictionServiceId:
                RestrictionServiceIdNew = item[2]
                break
            
        if ExactRateId is None:
            token = token + 1
        else:
            for item in CombinedRateIds:
                if item[1] == ExactRateId:
                    ExactRateIdNew = item[2]
                    break        
            else:
                ExactRateIdNew = "NO MATCH FOUND!"
        
        if BaseRateId is None:
            token = token + 1
        else:
            for item in CombinedRateIds:
                if item[1] == BaseRateId:
                    BaseRateIdNew = item[2]
                    break        
            else:
                BaseRateIdNew = "NO MATCH FOUND!"
        
        if RateGroupId is None:
            token = token + 1
        else:
            for item in CombinedRateGroupIds:
                if item[1] == RateGroupId:
                    RateGroupIdNew = item[2]
                    break        
            else:
                RateGroupIdNew = "NO MATCH FOUND!"
                print(item)
                
        if ResourceCategoryId is None:
            token = token + 1
        else:
            for item in CombinedResourceIds:
                if item[1] == ResourceCategoryId:
                    RateGroupIdNew = item[2]
                    break        
            else:
                RateGroupIdNew = "NO MATCH FOUND!"
        
        if ResourceCategoryType is None:
            token = token + 1

        payload9 = {
            "Id": RestrictionId,
            "Type": RestrictionType,
            "ExactRateId": ExactRateIdNew,
            "BaseRateId": BaseRateIdNew,
            "RateGroupId": RateGroupIdNew,
            "ResourceCategoryId": ResourceCategoryIdNew,
            "ResourceCategoryType": ResourceCategoryType,
            "StartUtc": StartUtc,
            "EndUtc": EndUtc,    
            "Days": days_dict,
        }
        if MinAdvance != None:
            payload9["MinAdvance"] = MinAdvance
        if MaxAdvance != None:
            payload9["MaxAdvance"] = MaxAdvance
        if MinLength != None:
            payload9["MinLength"] = MinLength
        if MaxLength != None:
            payload9["MaxLength"] = MaxLength
        if MinPrice != None:
            payload9["MinPrice"] = MinPrice
        if MaxPrice != None:
            payload9["MaxPrice"] = MaxPrice
        if MinReservationCount != None:
            payload9["MinReservationCount"] = MinReservationCount
        if MaxReservationCount != None:
            payload9["MaxReservationCount"] = MaxReservationCount
        
        MatchCheck = [ExactRateIdNew, BaseRateIdNew, RateGroupIdNew, ResourceCategoryIdNew, ResourceCategoryType]
        
        if token == 5:
            text = 'Restriction applies to all, please check and add manually'
            restrictionsNotPosted.append(text)
            restrictionsNotPosted.append(restriction)
        elif "NO MATCH FOUND!" in MatchCheck:
            for var_name, var_value in payload9.items():
                if var_value == "NO MATCH FOUND!":
                    text2 = var_name + ' is not matching between environments'
                    restrictionsNotPosted.append(text2)
            restrictionsNotPosted.append(restriction)
        else: 
            payloads.append(payload9)
        #    i = i + 1
        #if 1 == 10:
        #    break
    payload8 = {
        "ClientToken": ClientToken,
        "AccessToken": AccessTokenTwo,
        "Client": Client, 
        "ServiceId": RestrictionServiceIdNew,
        "Data": payloads
    }
    json_payload8 = json.dumps(payload8, indent=4)
    restrictions_NotPosted = json.dumps(restrictionsNotPosted, indent=4)
    with open('Not posted restrictions.txt', 'w') as file:
        file.write(restrictions_NotPosted)
    PushRestrictions = requests.post("https://api.mews-demo.com/api/connector/v1/restrictions/set", data=json_payload8, headers=headers) # Send the POST request
    print('Done')
    
    '''