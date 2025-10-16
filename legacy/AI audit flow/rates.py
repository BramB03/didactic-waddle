import json, requests, pprint, os

clientToken = os.getenv("DEMO_CLIENTTOKEN")
accessToken = os.getenv("DAVID_ACCESSTOKEN")
client = "Mews Audit Application"
url = "https://api.mews-demo.com/api/connector/v1/" 
headers = {
    "Content-Type": "application/json"
}
payloadRates = {
    "ClientToken": clientToken,
    "AccessToken": accessToken,
    "Client": client,
    "ServiceIds": [
        "5291ecd7-c75f-4281-bca0-ae94011b2f3a"
    ],
    "ActivityStates": [
        "Active"
    ],
    "Extent": {
        "Rates": True,
        "RateGroups": True,
        "AvailabilityBlockAssignments": False
    }, 
   "Limitation": {
        "Count": 1000,
    }
}

responseRates = requests.post(url + "rates/getAll", data=json.dumps(payloadRates), headers=headers)
ratesData = responseRates.json()
rates = ratesData.get("Rates", [])
filteredRates = [
    item for item in rates if item.get("Type") != "AvailabilityBlock" 
    ]
rateGroups = ratesData.get("RateGroups", [])

ratePassThrough = []
for item in filteredRates:
    if item.get("IsBaseRate") == True:
        tarief = "BaseRate"
    elif item.get("IsBaseRate") == False:
        tarief = "DependentRate"
        if item.get("DependentRatePricing"):
            tariefKortingRelatief = item.get("DependentRatePricing").get("RelativeAdjustment")
            tariefKortingAbsoluut = item.get("DependentRatePricing").get("AbsoluteAdjustment")
        else:
            tariefKortingRelatief = "n/a"
            tariefKortingAbsoluut = "n/a"
        tarief = f'{tarief} with relative adjustment of {tariefKortingRelatief} and/or absolute adjustment of {tariefKortingAbsoluut}'

    ratePassThrough.append({
        "rateId": item.get("Id"),
        "name": item.get("Name"),
        "description": item.get("Description"),
        "currency": item.get("Currency"),
        "rateType": item.get("Type"),
        "ratePricing": tarief,
        "rateGroupId": item.get("RateGroupId"),
        "BusinessSegmentId": item.get("BusinessSegmentId")
    })

