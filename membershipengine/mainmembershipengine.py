# membershipengine/mainmembershipengine.py
import os
from typing import Any, Dict
import requests

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

app = FastAPI(title="Membership Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Config (ENV)
# -----------------------------
mewsBaseUrl = os.getenv("MEWS_BASE_URL", "https://api.mews-demo.com")
clientToken = os.getenv("DEMO_CLIENTTOKEN", "")
accessToken = os.getenv("DAVID_ACCESSTOKEN", "")
clientName = os.getenv("MEWS_CLIENT_NAME", "MemberEngineApp")

serviceId = os.getenv("MEWS_SERVICE_ID", "a10b3185-28a8-4a04-a8c1-b3a900d79dcd")
loyaltyProgramId = os.getenv("MEWS_LOYALTY_PROGRAM_ID", "fa0f6c00-ab5d-4123-8baa-b3a900db98cc")

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

class CreateRequest(BaseModel):
    firstName: str = Field(..., min_length=1)
    lastName: str = Field(..., min_length=1)
    emailAddress: EmailStr
    startDate: str  # YYYY-MM-DD
    durationMonths: int = Field(..., ge=1, le=12)
    endDate: str    # YYYY-MM-DD

def postToMews(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{mewsBaseUrl.rstrip('/')}/{path.lstrip('/')}"
    try:
        res = requests.post(url, headers=mewsHeaders(), json=payload, timeout=30)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Mews network error calling {path}: {str(e)}")

    try:
        data = res.json()
    except Exception:
        data = {"raw": res.text}

    if not res.ok:
        raise HTTPException(
            status_code=502,
            detail={
                "message": f"Mews error calling {path}",
                "status": res.status_code,
                "response": data,
            },
        )
    return data

def addCustomer(firstName: str, lastName: str, emailAddress: str) -> str:
    payload = {
        **mewsAuthBasePayload(),
        "Customer": {
            "FirstName": firstName,
            "LastName": lastName,
            "Email": emailAddress,
        },
    }
    data = postToMews("customers/add", payload)

    customerId = (
        data.get("CustomerId")
        or (data.get("Customers") or [{}])[0].get("Id")
        or data.get("Id")
    )
    if not customerId:
        raise HTTPException(status_code=502, detail={"message": "Could not read CustomerId from Mews response", "response": data})
    return customerId

def addLoyalty(customerId: str) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        **mewsAuthBasePayload(),
        "CustomerId": customerId,
    }
    if loyaltyProgramId:
        payload["LoyaltyProgramId"] = loyaltyProgramId

    return postToMews("loyalty/add", payload)

def addReservation(customerId: str, startDate: str, endDate: str, durationMonths: int) -> Dict[str, Any]:
    if not serviceId:
        raise HTTPException(status_code=500, detail="Missing MEWS_SERVICE_ID env var (needed for reservation add).")

    payload = {
        **mewsAuthBasePayload(),
        "ServiceId": serviceId,
        "CustomerId": customerId,

        # Replace with StartUtc/EndUtc if Mews endpoint expects it:
        "StartDate": startDate,
        "EndDate": endDate,

        "Notes": f"Duration months: {durationMonths}",
    }
    return postToMews("reservations/add", payload)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/create")
def create(req: CreateRequest):
    customerId = addCustomer(req.firstName, req.lastName, str(req.emailAddress))
    loyaltyResponse = addLoyalty(customerId)
    reservationResponse = addReservation(customerId, req.startDate, req.endDate, req.durationMonths)

    return {
        "message": "Created customer, loyalty, and reservation.",
        "customerId": customerId,
        "loyalty": loyaltyResponse,
        "reservation": reservationResponse,
    }