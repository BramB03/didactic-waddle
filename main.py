# main.py
from flask import Flask, render_template, Response
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from a2wsgi import ASGIMiddleware  # ASGI -> WSGI adapter for mounting FastAPI into Flask

# Import your sub-apps
import bookingengine.mainbookingengine as bookingengine_module
import webapp as webapp_module
import membershipengine.mainmembershipengine as membershipengine_module

# Import revenue portal Flask app from package
from revenue_portal import app as revenue_portal_app

app = Flask(__name__)

# Wrap the FastAPI (ASGI) membership engine so WSGI DispatcherMiddleware can call it.
membershipengine_wsgi = ASGIMiddleware(membershipengine_module.app)

# Mount sub-apps under prefixes
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    "/bookingengine": bookingengine_module.app,       # Flask WSGI app
    "/webapp": webapp_module.app,                     # Flask WSGI app
    "/revenue-portal": revenue_portal_app,            # Flask WSGI app
    "/membershipengine": membershipengine_wsgi,        # FastAPI ASGI app wrapped to WSGI
})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/app1")
def app1():
    return Response("<h1>App 1</h1>", mimetype="text/html")

if __name__ == "__main__":
    # Dev only. For prod you’d use gunicorn, etc.
    app.run(debug=True, host="0.0.0.0", port=8000)