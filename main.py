# main.py
from flask import Flask, render_template, Response
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from pathlib import Path
import importlib.util

# import your other sub-apps...
import bookingengine.mainbookingengine as bookingengine_module  # ← add this
import webapp as webapp_module  # (example of your other app)

_revenue_portal_spec = importlib.util.spec_from_file_location(
    "revenue_portal.mainrevenueportal",
    Path(__file__).parent / "revenue-portal" / "mainrevenueportal.py",
)

if _revenue_portal_spec is None or _revenue_portal_spec.loader is None:
    raise ImportError("Could not load revenue portal module.")

revenue_portal_module = importlib.util.module_from_spec(_revenue_portal_spec)
_revenue_portal_spec.loader.exec_module(revenue_portal_module)

app = Flask(__name__)

# Mount sub-apps under prefixes
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    "/bookingengine": bookingengine_module.app,  # ← mount here
    "/webapp": webapp_module.app,              # (example of your other app)
    "/revenue-portal": revenue_portal_module.app,
})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/app1")
def app1():
    return Response("<h1>App 1</h1>", mimetype="text/html")

if __name__ == "__main__":
    app.run(debug=True)
