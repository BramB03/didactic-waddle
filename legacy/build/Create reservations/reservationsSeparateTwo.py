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

credentialOptions = [
    {
        "label": "The David AZ - Demo",
        "clientToken": "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D",
        "accessToken": "BEC33DAD4C57410C9E6DB09600C7FB9B-310471532A30162E5B6F0EB4F4AD2BF",
        "clientId": "prod_client_id"
    },
    {
        "label": "Efteling Hotel - Demo",
        "clientToken": "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D",
        "accessToken": "D546E3C64E3640D1AEA2B1C50094DCEF-999B7AA0C1471EBC8D7140DBAD8232A",
        "clientId": "sandbox_client_id"
    },
    {
        "label": "St Clement - Demo",
        "clientToken": "E0D439EE522F44368DC78E1BFB03710C-D24FB11DBE31D4621C4817E028D9E1D",
        "accessToken": "FA313B35B0AA44F9A985B2DE0076DC0D-B2ED620854C06E840EA6857E5306661",
        "clientId": "dev_client_id"
    }
]

# Prompt the user to choose
print("Select a credential set:")
for idx, option in enumerate(credentialOptions, start=1):
    print(f"{idx}. {option['label']}")

while True:
    try:
        choice = int(input("Enter number (1–{}): ".format(len(credentialOptions))))
        if 1 <= choice <= len(credentialOptions):
            selected = credentialOptions[choice - 1]
            break
        else:
            print("Invalid number. Try again.")
    except ValueError:
        print("Invalid input. Please enter a number.")

# Assign selected credentials
ClientToken = selected["clientToken"]
AccessToken = selected["accessToken"]
Client = selected["clientId"]

ExtraDays = 13
#time.sleep(900)
payloadBase = {
    "ClientToken": ClientToken,
    "AccessToken": AccessToken,
    "Client": Client
}

from createResDef import (
    getEnterpriseConfig,
    getServiceBookableIds,
    getAgeCategoryId,
    getRatesIdEnabled,
    getCategoryAvailabilities,
    getDefaultGuests,
    getActiveProductIds,
    createGuest,
    getTaxRateCodes,
    createReservations,
    getStartTimeUnitUtc
)

resState = ["Confirmed", "Confirmed"]  # Could also be: ["Confirmed", "Optional"]


# Step 1: Fetch base enterprise config
config = getEnterpriseConfig(ClientToken, AccessToken, Client)
enterpriseId = config["enterpriseId"]
chainId = config["chainId"]
StartTimeUnitUtc = config["startTimeUtc"]
GrossNet = config["grossNet"]
currency = config["currency"]
nowUpdate = getStartTimeUnitUtc(config["timezone"])

# Step 2: Get bookable service IDs
bookableServices = getServiceBookableIds(ClientToken, AccessToken, Client, enterpriseId)

createdReservations = 0
reservationCap = 250

for serviceId, startOffsetData, endOffsetData in bookableServices:
    for _ in range(10):  # Attempt up to 10 service rounds
        ageCategoryId = getAgeCategoryId(ClientToken, AccessToken, Client, enterpriseId, serviceId)
        rateIds = getRatesIdEnabled(ClientToken, AccessToken, Client, enterpriseId, serviceId)

        if not rateIds:
            continue

        categories = getCategoryAvailabilities(ClientToken, AccessToken, Client, enterpriseId, serviceId, StartTimeUnitUtc)
        if not categories:
            continue

        for categoryId, availabilities in categories:
            mean = sum(availabilities) / len(availabilities)
            availabilityAdjusted = math.ceil(mean * 0.2)

            defaultGuests = getDefaultGuests(ClientToken, AccessToken, Client, enterpriseId, serviceId, categoryId)
            productIds = getActiveProductIds(ClientToken, AccessToken, Client, enterpriseId, serviceId)

            for _ in range(availabilityAdjusted):
                if createdReservations >= reservationCap:
                    sys.exit("Reached reservation limit")

                guestFirst = random.choice(firstName)
                guestLast = random.choice(lastName)
                guestEmail = f"{guestFirst}.{guestLast}@demo.com"

                guestId = createGuest(ClientToken, AccessToken, Client, chainId, guestFirst, guestLast, guestEmail)
                if not guestId:
                    continue

                # Random check-in/out time generation
                randomCheckInOffset = timedelta(days=random.choices([0, 1, 2, 3, 4, 5, 6, 7], weights=[0.4, 0.3, 0.1, 0.1, 0.05, 0.03, 0.01, 0.01])[0])
                randomCheckOutOffset = timedelta(days=random.randint(1, 7))
                checkInUpdate = nowUpdate + timedelta(hours=int(startOffsetData[-7:-5])) + randomCheckInOffset
                checkOutUpdate = nowUpdate + timedelta(hours=int(endOffsetData[-7:-5])) + randomCheckInOffset + randomCheckOutOffset
                checkInTime = checkInUpdate.strftime("%Y-%m-%dT%H:%M:%SZ")
                checkOutTime = checkOutUpdate.strftime("%Y-%m-%dT%H:%M:%SZ")

                # Pricing
                rateId = random.choice(rateIds)
                taxCodes = getTaxRateCodes(ClientToken, AccessToken, Client, rateId, StartTimeUnitUtc, GrossNet, currency)
                if not taxCodes:
                    continue

                nights = (checkOutUpdate - checkInUpdate).days
                prices = [{
                    "Index": i,
                    "Amount": {
                        "Currency": currency,
                        GrossNet: random.randint(100, 200),
                        "TaxCodes": taxCodes
                    }
                } for i in range(nights)]

                numReservations = random.choice([1, 1, 1, 1, 2, 2, 3])
                reservationsPayload = []
                for _ in range(numReservations):
                    res = {
                        "State": random.choice(resState),
                        "StartUtc": checkInTime,
                        "EndUtc": checkOutTime,
                        "CustomerId": guestId,
                        "RequestedCategoryId": categoryId,
                        "RateId": rateId,
                        "Notes": "Test reservation",
                        "PersonCounts": [{
                            "AgeCategoryId": ageCategoryId,
                            "Count": defaultGuests
                        }],
                        "TimeUnitPrices": prices
                    }
                    if productIds:
                        res["ProductOrders"] = [{"ProductId": random.choice(productIds)}]
                    reservationsPayload.append(res)

                # Final POST
                success = createReservations(ClientToken, AccessToken, Client, enterpriseId, serviceId, reservationsPayload)
                if success:
                    print("Reservation created")
                    createdReservations += 1
                    time.sleep(0.1)
                else:
                    print("Reservation failed")
                    break  # After 3 failures, skip to next category
        print(f"Total reservations created: {createdReservations}")
