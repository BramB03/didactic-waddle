from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.middleware.wsgi import WSGIMiddleware
from fastapi.templating import Jinja2Templates

import bookingengine.mainbookingengine as bookingengine_module
import webapp as webapp_module
from revenue_portal import app as revenue_portal_app
from membershipengine.mainmembershipengine import app as membershipengine_app
from portalengine.portalengine import app as portalengine_app

hub = FastAPI(title="ASGI Hub")

templates = Jinja2Templates(directory="templates")

@hub.get("/", response_class=HTMLResponse)
def index(request: Request):
    # Renders /templates/index.html
    return templates.TemplateResponse("index.html", {"request": request})

@hub.get("/health")
def health():
    return {"status": "ok"}

# Mount apps
hub.mount("/membershipengine", membershipengine_app)
hub.mount("/bookingengine", WSGIMiddleware(bookingengine_module.app))
hub.mount("/webapp", WSGIMiddleware(webapp_module.app))
hub.mount("/revenue-portal", WSGIMiddleware(revenue_portal_app))
hub.mount("/portalengine", portalengine_app)
