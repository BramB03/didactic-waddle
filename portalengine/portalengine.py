# membershipengine/portalengine.py
import os
from pathlib import Path
from typing import Any, Dict, List

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Membership portal")

baseDir = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(baseDir / "templates"))

# -----------------------------
# Portal HTML
# -----------------------------
@app.get("/", response_class=HTMLResponse)
def portalHome(request: Request):
    # Loads: portalengine/templates/portal.html
    return templates.TemplateResponse("index-portal.html", {"request": request})

# -----------------------------
# Mews config/helpers
# -----------------------------
mewsBaseUrl = os.getenv("MEWS_BASE_URL", "https://api.mews-demo.com/api/connector/v1/")
clientToken = os.getenv("DEMO_CLIENTTOKEN", "")
accessToken = os.getenv("DAVID_ACCESSTOKEN", "")
clientName = os.getenv("MEWS_CLIENT_NAME", "PortalEngine")

def mewsHeaders() -> Dict[str, str]:
    return {"Content-Type": "application/json"}

def mewsAuthBasePayload() -> Dict[str, Any]:
    if not clientToken or not accessToken:
        raise HTTPException(status_code=500, detail="Missing DEMO_CLIENTTOKEN / DAVID_ACCESSTOKEN env vars.")
    return {"ClientToken": clientToken, "AccessToken": accessToken, "Client": clientName}

def postToMews(path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{mewsBaseUrl.rstrip('/')}/{path.lstrip('/')}"
    try:
        res = requests.post(url, headers=mewsHeaders(), json=payload, timeout=30)
    except requests.RequestException as e:
        print(f"Network error calling Mews {path}: {str(e)}")
        raise HTTPException(status_code=502, detail=f"Mews network error calling {path}: {str(e)}")

    try:
        data = res.json()
    except Exception:
        data = {"raw": res.text}

    if not res.ok:
        raise HTTPException(status_code=502, detail={"message": f"Mews error calling {path}", "status": res.status_code, "response": data})

    return data

# -----------------------------
# Portal API: memberships list
# (THIS is what runs on page load via fetch)
# -----------------------------
@app.get("/api/memberships")
def listMemberships() -> Dict[str, Any]:
    payload = {
        **mewsAuthBasePayload(),
        "LoyaltyProgramId": "fa0f6c00-ab5d-4123-8baa-b3a900db98cc",
        "MembershipStates": [
            "Pending",
            "Enrolled"
        ],
        "Limitation": {"Count": 100},
    }

    # TODO: replace with your exact Mews endpoint/version
    mewsData = postToMews("loyaltyMemberships/getAll", payload)
    memberlist = []
    customerIdList = []
    for item in mewsData.get("LoyaltyMemberships", []):
        memberlist.append({
            "membershipNumber": item.get("MembershipNumber"),
            "state": item.get("State"),
            "accountId": item.get("AccountId"),
            "endDate": item.get("ExpirationDate")
        })
        customerIdList.append(item.get("AccountId"))

    payloadCustomers = {
        **mewsAuthBasePayload(),    
        "CustomerIds": customerIdList,
        "Limitation": {"Count": 1000}
    }
    mewsCustomers = postToMews("customers/getAll", payloadCustomers)
    for member in memberlist:
        for cust in mewsCustomers.get("Customers", []):
            if cust.get("Id") == member.get("accountId"):
                member["customerName"] = f"{cust.get('FirstName', '')} {cust.get('LastName', '')}".strip()
                break

    return {"memberships": memberlist}

# -----------------------------
# 2 button actions (placeholders)
# -----------------------------
@app.post("/api/membership/pause")
def pauseMembership(body: Dict[str, Any]):
    membershipId = body.get("membershipId")
    if not membershipId:
        raise HTTPException(400, "membershipId is required")
    # TODO: call Mews pause endpoint
    return {"ok": True, "action": "pause", "membershipId": membershipId}

@app.post("/api/membership/cancel")
def cancelMembership(body: Dict[str, Any]):
    membershipId = body.get("membershipId")
    if not membershipId:
        raise HTTPException(400, "membershipId is required")
    # TODO: call Mews cancel endpoint
    return {"ok": True, "action": "cancel", "membershipId": membershipId}