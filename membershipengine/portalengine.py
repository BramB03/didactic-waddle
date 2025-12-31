# membershipengine/portalengine.py
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

router = APIRouter()

baseDir = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(baseDir / "templates"))

_postToMews = None
_mewsAuthBasePayload = None
MEWS_COMMANDER_BASE = None  # injected

def initPortalRouter(postToMewsFn, mewsAuthBasePayloadFn, commanderBase: str):
    global _postToMews, _mewsAuthBasePayload, MEWS_COMMANDER_BASE
    _postToMews = postToMewsFn
    _mewsAuthBasePayload = mewsAuthBasePayloadFn
    MEWS_COMMANDER_BASE = commanderBase


# ---------- PAGE ----------
@router.get("/portal", response_class=HTMLResponse)
def portalPage(request: Request):
    return templates.TemplateResponse("portal.html", {"request": request})


# ---------- MODELS ----------
class PortalItem(BaseModel):
    customerId: str
    customerName: str
    email: Optional[str] = None

    reservationId: Optional[str] = None
    startDate: Optional[str] = None  # ISO yyyy-mm-dd
    endDate: Optional[str] = None    # ISO yyyy-mm-dd

    status: str = "Unknown"          # e.g. Active / Expiring / Expired / Draft
    customerUrl: Optional[str] = None
    reservationUrl: Optional[str] = None


class PortalListResponse(BaseModel):
    items: List[PortalItem] = Field(default_factory=list)


class CancelRequest(BaseModel):
    reservationId: str
    reason: Optional[str] = None


class ExtendRequest(BaseModel):
    reservationId: str
    extraMonths: int = Field(..., ge=1, le=12)


# ---------- API ----------
@router.get("/api/portal/list", response_model=PortalListResponse)
def portalList():
    """
    Bij openen van portal.html roep je dit aan.
    Hier ga je straks jouw echte Mews query doen (bijv. memberships die bijna verlopen).
    """
    if _postToMews is None or _mewsAuthBasePayload is None:
        raise HTTPException(status_code=500, detail="Portal router not initialized.")

    # ✅ STARTER: lege lijst met juiste structuur
    # TODO: vervang door echte query (reservations/getAll + filters) en map naar PortalItem(s)
    return PortalListResponse(items=[])


@router.post("/api/portal/cancel")
def portalCancel(req: CancelRequest):
    if _postToMews is None or _mewsAuthBasePayload is None:
        raise HTTPException(status_code=500, detail="Portal router not initialized.")

    # TODO: call Mews reservation cancel/close endpoint(s)
    return {"message": "Cancel requested", "reservationId": req.reservationId, "reason": req.reason}


@router.post("/api/portal/extend")
def portalExtend(req: ExtendRequest):
    if _postToMews is None or _mewsAuthBasePayload is None:
        raise HTTPException(status_code=500, detail="Portal router not initialized.")

    # TODO: call Mews reservation update OR create follow-up reservation
    return {"message": "Extend requested", "reservationId": req.reservationId, "extraMonths": req.extraMonths}