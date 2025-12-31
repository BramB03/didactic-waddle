# membershipengine/portalengine.py
import os
from pathlib import Path
from typing import Any, Dict, List
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import calendar
import json

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
AMSTERDAM_TZ = ZoneInfo("Europe/Amsterdam")
UTC_TZ = ZoneInfo("UTC")

def parseInputDateToLocal(dateStr: str, tzName: str = "Europe/Amsterdam") -> datetime:
    """
    Accepts:
      - "YYYY-MM-DD"
      - "YYYY-MM-DDTHH:MM:SSZ" (or with +00:00)
      - "DD/MM/YYYY"
    Returns timezone-aware datetime in tzName.
    """
    if not dateStr or str(dateStr).strip() in ("—", "", "null", "None"):
        raise ValueError(f"Invalid date input: {dateStr}")

    s = str(dateStr).strip()
    tz = ZoneInfo(tzName)

    # DD/MM/YYYY
    if "/" in s:
        d, m, y = s.split("/")
        return datetime(int(y), int(m), int(d), 0, 0, 0, tzinfo=tz)

    # ISO 8601
    # Handle trailing Z
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"

    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        # treat naive as local date/time
        dt = dt.replace(tzinfo=tz)
        return dt

    return dt.astimezone(tz)

def addMonths(year: int, month: int, monthsToAdd: int) -> tuple[int, int]:
    total = (year * 12 + (month - 1)) + monthsToAdd
    newYear = total // 12
    newMonth = (total % 12) + 1
    return newYear, newMonth

def toUtcZ(dtLocal: datetime) -> str:
    return dtLocal.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def computePauseWindowUtc(endDateInput: str, tzName: str = "Europe/Amsterdam") -> tuple[str, str]:
    """
    Pause is always +1 month from the provided endDateInput's month.
    Outputs:
      - membershipExpirationUtc: last day of pause month at 23:59 local -> UTC Z
      - reservationEndUtc: first day of next month at 00:01 local -> UTC Z
    """
    local = parseInputDateToLocal(endDateInput, tzName=tzName)
    year, month = local.year, local.month

    # pause month = +1 month
    pauseYear, pauseMonth = addMonths(year, month, 1)
    lastDay = calendar.monthrange(pauseYear, pauseMonth)[1]

    tz = ZoneInfo(tzName)

    # 23:59 on last day of pause month
    membershipLocal = datetime(pauseYear, pauseMonth, lastDay, 23, 59, 0, tzinfo=tz)

    # 00:01 on first day of month AFTER pause month
    nextYear, nextMonth = addMonths(pauseYear, pauseMonth, 1)
    reservationLocal = datetime(nextYear, nextMonth, 1, 0, 1, 0, tzinfo=tz)

    return toUtcZ(membershipLocal), toUtcZ(reservationLocal)

def parseIsoZ(iso: str) -> datetime:
    # supports "2026-03-31T21:59:00Z"
    if iso.endswith("Z"):
        iso = iso[:-1] + "+00:00"
    return datetime.fromisoformat(iso)

def monthIndexForDate(startUtcIso: str, targetUtcIso: str, tzName: str = "Europe/Amsterdam") -> int:
    """
    Returns 0-based month index relative to reservation start month,
    using LOCAL calendar months (tzName).
    """
    tz = ZoneInfo(tzName)
    startLocal = parseIsoZ(startUtcIso).astimezone(tz)
    targetLocal = parseIsoZ(targetUtcIso).astimezone(tz)

    return (targetLocal.year - startLocal.year) * 12 + (targetLocal.month - startLocal.month)

def nextMonthIndex(startUtcIso: str, tzName: str = "Europe/Amsterdam") -> int:
    """
    Index for the month AFTER the start month. Always 1.
    Included for clarity / readability.
    """
    _ = tzName
    return 1

def nextMonthIndexWithinReservation(startUtcIso: str, endUtcIso: str, tzName: str = "Europe/Amsterdam") -> int:
    """
    Returns the next month index that is still inside [start, end).
    If the reservation doesn't span into the next calendar month, raises.
    """
    tz = ZoneInfo(tzName)
    startLocal = parseIsoZ(startUtcIso).astimezone(tz)
    endLocal = parseIsoZ(endUtcIso).astimezone(tz)

    # next month start (local)
    nextMonthYear = startLocal.year + (1 if startLocal.month == 12 else 0)
    nextMonth = 1 if startLocal.month == 12 else startLocal.month + 1
    nextMonthStartLocal = datetime(nextMonthYear, nextMonth, 1, 0, 0, 0, tzinfo=tz)

    # Check if reservation actually reaches into the next month
    if endLocal <= nextMonthStartLocal:
        raise ValueError("Reservation does not extend into the next calendar month.")

    return 1

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
            "membershipId": item.get("Id"),
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
class PauseRequest(BaseModel):
    accountId: str
    membershipId: str
    endDate: str

@app.post("/api/membership/pause")
def pause(req: PauseRequest):
    membershipId = req.membershipId
    accountId = req.accountId
    endDate = req.endDate
    newEndDateMembership, newEndDateReservation = computePauseWindowUtc(endDate)
    payloadMembership = {
        **mewsAuthBasePayload(),
        "LoyaltyMembershipUpdates": [
            {
                "LoyaltyMembershipId": membershipId,
                "ExpirationDate": {"Value": newEndDateMembership}
            }
        ]
    }
    extendedMembership = postToMews("loyaltyMemberships/update", payloadMembership)

    payloadGetReservations = {
        **mewsAuthBasePayload(),
        "ServiceIds": ["a10b3185-28a8-4a04-a8c1-b3a900d79dcd"],
        "AccountIds": [accountId],
        "Limitation": {"Count": 1}
    }
    reservationsData = postToMews("reservations/getAll/2023-06-06", payloadGetReservations)
    reservationId = None
    if not reservationsData.get("Reservations"):
        raise HTTPException(502, "Failed to fetch reservations for account")
    else:
        for resv in reservationsData.get("Reservations", []):
            reservationId = resv.get("Id")
            originalStart = resv.get("StartUtc")
            originalEnd = resv.get("EndUtc")
            break

    payloadReservation = {
        **mewsAuthBasePayload(),
        "Reason": "Pausing membership via portal",
        "ReservationUpdates": [
            {
                "ReservationId": reservationId,
                "EndUtc": { "Value": newEndDateReservation },
                "TimeUnitPrices": {
                    "Value": [
                        {
                            "Index": int(monthIndexForDate(originalStart, originalEnd)),
                            "Amount": {
                                "Currency": "EUR",
                                "GrossValue": 0,
                                "TaxCodes": [
                                    "NL-2019-R"
                                ]
                            }
                        }
                    ]
                }
            }
        ]
    }
    print("Reservation update payload:", json.dumps(payloadReservation, indent=2))
    pausedReservation = postToMews("reservations/update", payloadReservation)
    if not pausedReservation.get("Ok"):
        raise HTTPException(502, "Failed to extend reservation")

    return {"ok": True, "action": "pause", "membershipId": membershipId}

@app.post("/api/membership/cancel")
def cancelMembership(body: Dict[str, Any]):
    membershipId = body.get("membershipId")
    if not membershipId:
        raise HTTPException(400, "membershipId is required")
    # TODO: call Mews cancel endpoint
    return {"ok": True, "action": "cancel", "membershipId": membershipId}