# app.py
import os
from typing import Any, Dict, Optional
import requests
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

app = FastAPI()

# If you serve the HTML from a different domain/port, set CORS.
# For same-origin (same host), you can remove this.
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
mewsBaseUrl = os.getenv("MEWS_BASE_URL", "https://api.mews-demo.com")  # adjust if needed
clientToken = os.getenv("DEMO_CLIENTTOKEN", "")
accessToken = os.getenv("DAVID_ACCESSTOKEN", "")
clientName = os.getenv("MEWS_CLIENT_NAME", "MemberEngineApp")

# Optional service / resource IDs you may need for reservation creation
serviceId = "a10b3185-28a8-4a04-a8c1-b3a900d79dcd"  # e.g. your hotel/service
loyaltyProgramId = "fa0f6c00-ab5d-4123-8baa-b3a900db98cc"  # if required by your loyalty endpoint

def mewsHeaders() -> Dict[str, str]:
    return {"Content-Type": "application/json"}

def mewsAuthBasePayload() -> Dict[str, Any]:
    if not clientToken or not accessToken:
        # fail fast if env is missing
        raise HTTPException(status_code=500, detail="Missing MEWS_CLIENT_TOKEN / MEWS_ACCESS_TOKEN env vars.")
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
    startDate: str  # "YYYY-MM-DD"
    durationMonths: int = Field(..., ge=1, le=12)
    endDate: str  # "YYYY-MM-DD" (computed in browser)

# -----------------------------
# Mews API call helpers
# (keep each request in its own function)
# -----------------------------
def postToMews(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{mewsBaseUrl.rstrip('/')}/{path.lstrip('/')}"
    try:
        res = requests.post(url, headers=mewsHeaders(), json=payload, timeout=30)
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Mews network error calling {path}: {str(e)}")

    # Try parse JSON either way
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
    """
    Returns created CustomerId.
    Replace the endpoint version/path + payload shape to match your Mews Connector API.
    """
    payload = {
        **mewsAuthBasePayload(),
        # ---- TODO: adjust to real Customer/Add contract ----
        "Customer": {
            "FirstName": firstName,
            "LastName": lastName,
            "Email": emailAddress,
        },
    }

    # ---- TODO: set correct path ----
    data = postToMews("customers/add", payload)

    # ---- TODO: extract according to response ----
    # Example patterns you might need:
    # customerId = data["CustomerId"]
    # customerId = data["Customers"][0]["Id"]
    customerId = (
        data.get("CustomerId")
        or (data.get("Customers") or [{}])[0].get("Id")
        or data.get("Id")
    )

    if not customerId:
        raise HTTPException(status_code=502, detail={"message": "Could not read CustomerId from Mews response", "response": data})

    return customerId

def addLoyalty(customerId: str) -> Dict[str, Any]:
    """
    Returns loyalty object / loyaltyId.
    Replace endpoint/path + payload to match your loyalty/membership flow.
    """
    payload = {
        **mewsAuthBasePayload(),
        # ---- TODO: adjust to real Loyalty/Add contract ----
        "CustomerId": customerId,
    }

    # If a program ID is required:
    if loyaltyProgramId:
        payload["LoyaltyProgramId"] = loyaltyProgramId

    # ---- TODO: set correct path ----
    data = postToMews("loyalty/add", payload)

    # Return the whole response so you can inspect/store details
    return data

def addReservation(
    customerId: str,
    startDate: str,
    endDate: str,
    durationMonths: int,
) -> Dict[str, Any]:
    """
    Creates a reservation for the customer.
    startDate/endDate are YYYY-MM-DD. If Mews wants UTC date-times, convert here.
    """
    if not serviceId:
        raise HTTPException(status_code=500, detail="Missing MEWS_SERVICE_ID env var (needed for reservation add).")

    payload = {
        **mewsAuthBasePayload(),
        # ---- TODO: adjust to real Reservation/Add contract ----
        "ServiceId": serviceId,
        "CustomerId": customerId,

        # Many Mews endpoints prefer UTC timestamps; adapt if needed:
        # "StartUtc": f"{startDate}T00:00:00Z",
        # "EndUtc": f"{endDate}T00:00:00Z",
        "StartDate": startDate,
        "EndDate": endDate,

        # Optional: keep what the user picked for your own logic
        "Notes": f"Duration months: {durationMonths}",
    }

    # ---- TODO: set correct path ----
    data = postToMews("reservations/add", payload)
    return data

# -----------------------------
# Your endpoint the HTML calls
# -----------------------------
@app.post("/api/create")
def create(req: CreateRequest):
    # 1) customer
    customerId = addCustomer(req.firstName, req.lastName, str(req.emailAddress))

    # 2) loyalty/membership (optional but you said you want it)
    loyaltyResponse = addLoyalty(customerId)

    # 3) reservation
    reservationResponse = addReservation(
        customerId=customerId,
        startDate=req.startDate,
        endDate=req.endDate,
        durationMonths=req.durationMonths,
    )

    return {
        "message": "Created customer, loyalty, and reservation.",
        "customerId": customerId,
        "loyalty": loyaltyResponse,
        "reservation": reservationResponse,
    }

# Run:
#   pip install fastapi uvicorn requests
#   export MEWS_CLIENT_TOKEN="..."
#   export MEWS_ACCESS_TOKEN="..."
#   export MEWS_SERVICE_ID="..."
#   uvicorn app:app --reload --port 8000
#
# Then open your HTML (served from same host or set allow_origins appropriately)