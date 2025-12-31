# membershipengine/mainmembershipengine.py
import os, json
from pathlib import Path
from typing import Any, Dict
from datetime import datetime, time as dt_time
from zoneinfo import ZoneInfo
import time as py_time
import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, Field
import logging

app = FastAPI(title="Membership Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

runId = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
logFile = LOG_DIR / f"mews_run_{runId}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(logFile, encoding="utf-8"),
        logging.StreamHandler()
    ],
    force=True,
)

logger = logging.getLogger("mews")

# -----------------------------
# Templates (serve HTML page)
# -----------------------------
baseDir = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(baseDir / "templates"))

@app.get("/", response_class=HTMLResponse)
def membershipIndex(request: Request):
    """
    Serves membershipengine/templates/index.html at:
    GET /membershipengine/
    """
    return templates.TemplateResponse("index-membershipengine.html", {"request": request})

# -----------------------------
# Config (ENV)
# -----------------------------
mewsBaseUrl = os.getenv("MEWS_BASE_URL", "https://api.mews-demo.com/api/connector/v1/")
MEWS_COMMANDER_BASE = "https://app.mews-demo.com/Commander/8dc59049-c9d0-4d08-a489-ae94011b28e5"
clientToken = os.getenv("DEMO_CLIENTTOKEN", "")
accessToken = os.getenv("DAVID_ACCESSTOKEN", "")
clientName = os.getenv("MEWS_CLIENT_NAME", "MemberEngineApp")
AMSTERDAM_TZ = ZoneInfo("Europe/Amsterdam")
UTC_TZ = ZoneInfo("UTC")

serviceId = os.getenv("MEWS_SERVICE_ID", "a10b3185-28a8-4a04-a8c1-b3a900d79dcd")
loyaltyProgramId = "fa0f6c00-ab5d-4123-8baa-b3a900db98cc"

def mewsHeaders() -> Dict[str, str]:
    return {"Content-Type": "application/json"}

def mewsAuthBasePayload() -> Dict[str, Any]:
    if not clientToken or not accessToken:
        raise HTTPException(
            status_code=500,
            detail="Missing DEMO_CLIENTTOKEN / DAVID_ACCESSTOKEN env vars."
        )
    return {
        "ClientToken": clientToken,
        "AccessToken": accessToken,
        "Client": clientName,
    }

# -----------------------------
# Request model (from your HTML)
# -----------------------------
class CreateRequest(BaseModel):
    firstName: str = Field(..., min_length=1)
    lastName: str = Field(..., min_length=1)
    emailAddress: EmailStr
    startDate: str  # YYYY-MM-DD
    durationMonths: int = Field(..., ge=1, le=12)
    endDate: str    # YYYY-MM-DD

# -----------------------------
# Mews API call helpers
# -----------------------------
def postToMews(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{mewsBaseUrl.rstrip('/')}/{path.lstrip('/')}"
    logger.info("REQUEST %s\n%s", url, json.dumps(payload, indent=2))

    try:
        res = requests.post(url, headers=mewsHeaders(), json=payload, timeout=30)
    except requests.RequestException as e:
        logger.error("NETWORK ERROR %s", str(e))
        raise HTTPException(status_code=502, detail=str(e))

    logger.info("RESPONSE %s\n%s", res.status_code, res.text)

    try:
        data = res.json()
    except Exception:
        logger.error("NON-JSON RESPONSE\n%s", res.text)
        raise HTTPException(status_code=502, detail="Mews returned non-JSON")

    if isinstance(data, dict) and data.get("Message"):
        logger.error("MEWS ERROR PAYLOAD\n%s", json.dumps(data, indent=2))
        raise HTTPException(status_code=502, detail=data)

    if not res.ok:
        raise HTTPException(status_code=502, detail=data)

    return data


def localEndDateToUtcIso(localDateStr: str) -> str:
    """
    Converts a local date (YYYY-MM-DD) to UTC end-of-day timestamp.
    Example: '2026-07-31' → '2026-07-31T22:00:01Z'
    """
    # Parse date
    localDate = datetime.strptime(localDateStr, "%Y-%m-%d").date()

    # Set local end-of-day (23:59:59)
    localEndDateTime = datetime.combine(localDate, dt_time(23, 59, 59), tzinfo=AMSTERDAM_TZ)

    # Convert to UTC
    utcDateTime = localEndDateTime.astimezone(UTC_TZ)

    # Add 1 second so it is exclusive (safe for Mews)
    utcDateTime = utcDateTime.replace(second=1)

    return utcDateTime.strftime("%Y-%m-%dT%H:%M:%SZ")

def getLoyaltyTierIdByDuration(monthDuration: int) -> str:
    """
    Maps membership duration to the correct Mews Loyalty Tier ID.
    """
    if monthDuration == 1:
        return "77c9ad3c-e161-426f-b3ca-b3a900ded063"
    elif monthDuration == 6:
        return "77c9ad3c-e161-426f-b3ca-b3a900ded063"
    elif monthDuration == 12:
        return "77c9ad3c-e161-426f-b3ca-b3a900ded063"  # your 12 month tier
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported membership duration: {monthDuration}")

def getRateIdByDuration(monthDuration: int) -> str:
    """
    Maps membership duration to the correct Mews Loyalty Tier ID.
    """
    if monthDuration == 1:
        return "a3c9f5ec-7246-4659-a374-b3a900fbf8bd"
    elif monthDuration == 6:
        return "e72a2796-f97f-4390-a7cb-b3a900fbc412"
    elif monthDuration == 12:
        return "5d8af13a-5d8c-4e06-a62b-b3a900d79e27"  # your 12 month tier
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported membership duration: {monthDuration}")

def addCustomer(firstName: str, lastName: str, emailAddress: str) -> str:
    payload = {
        **mewsAuthBasePayload(),
        "FirstName": firstName,
        "LastName": lastName,
        "Email": emailAddress,
        "OverwriteExisting": True
    }

    # TODO: adjust path to your real endpoint/version
    data = postToMews("customers/add", payload)

    customerId = (
        data.get("CustomerId")
        or (data.get("Customers") or [{}])[0].get("Id")
        or data.get("Id")
    )
    if not customerId:
        raise HTTPException(
            status_code=502,
            detail={"message": "Could not read CustomerId from Mews response", "response": data},
        )
    return customerId

def addLoyalty(customerId: str, endDate: str, monthdration: int) -> Dict[str, Any]:
    MembershipNumber = f"TSH-DAVID-{customerId[:8].upper()}"
    endDateIso = localEndDateToUtcIso(endDate)
    loyaltyTierId = getLoyaltyTierIdByDuration(monthdration)
    payload: Dict[str, Any] = {
        **mewsAuthBasePayload(),
        "LoyaltyMemberships": [
            {
                "AccountId": customerId,
                "LoyaltyProgramId": loyaltyProgramId,
                "IsPrimary": False,
                "State": "Enrolled",
                "MembershipNumber": MembershipNumber,
                "Points": 4,
                "ExpirationDate": endDateIso,
                "Url": "https://rewards.example.com/member/PRV-MBR-9842XKLT",
                "LoyaltyTierId": loyaltyTierId
                }
        ],
    }

    # TODO: adjust path to your real endpoint/version
    return postToMews("loyaltyMemberships/add", payload)

def addReservation(customerId: str, startDate: str, endDate: str, durationMonths: int) -> Dict[str, Any]:
    if not serviceId:
        raise HTTPException(status_code=500, detail="Missing MEWS_SERVICE_ID env var (needed for reservation add).")
    startDateIso = localEndDateToUtcIso(startDate)
    endDateIso = localEndDateToUtcIso(endDate)
    rateId = getRateIdByDuration(durationMonths)
    payload = {
        **mewsAuthBasePayload(),
        "ServiceId": serviceId,
        "SendConfirmationEmail": False,
        "Reservations": [
            {
                "Identifier": f"TSH-DAVID-RES-{customerId[:8].upper()}",
                "State": "Confirmed",
                "StartUtc": startDateIso,
                "EndUtc": endDateIso,
                "CustomerId": customerId,
                "RateId": rateId,
                "RequestedCategoryId": "cfc2df97-5545-425f-b798-b3a900f9eac6",
                "Notes": f"Duration months: {durationMonths}",
                "PersonCounts": [
                    {
                        "AgeCategoryId": "a060964f-439b-4bcf-9234-b3a900d79e23",
                        "Count": 1
                    }
                ]
            }
        ]
    }

    return postToMews("reservations/add", payload)

# -----------------------------
# Health + API
# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/create")
def create(req: CreateRequest):
    customerId = addCustomer(req.firstName, req.lastName, str(req.emailAddress))
    py_time.sleep(1)  # ensure data consistency in Mews
    loyaltyResponse = addLoyalty(customerId, req.endDate, req.durationMonths)
    print(f"Loyalty response: {loyaltyResponse}")
    py_time.sleep(1)  # ensure data consistency in Mews
    reservationResponse = addReservation(customerId, req.startDate, req.endDate, req.durationMonths)
    reservationId = (
        reservationResponse.get("ReservationId")
        or (reservationResponse.get("Reservations") or [{}])[0].get("Id")
        or reservationResponse.get("Id")
    )
    customerCommanderUrl = f"{MEWS_COMMANDER_BASE}/Customer/{customerId}/Detail"
    reservationCommanderUrl = f"{MEWS_COMMANDER_BASE}/Reservation/Detail/{reservationId}"

    return {
        "message": "Membership created successfully.",
        "customerId": customerId,
        "reservationId": reservationId,
        "customerUrl": customerCommanderUrl,
        "reservationUrl": reservationCommanderUrl,
        "loyalty": loyaltyResponse,
        "reservation": reservationResponse,
    }

@app.get("/portal", response_class=HTMLResponse)
def membershipPortal(request: Request):
    return templates.TemplateResponse("portal.html", {"request": request})