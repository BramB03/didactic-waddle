# main.py
from flask import Flask, render_template, Response
from werkzeug.middleware.dispatcher import DispatcherMiddleware

# import your other sub-apps...
import bookingengine.mainbookingengine as bookingengine_module
import webapp as webapp_module

# import the revenue portal Flask app from the package
from revenue_portal import app as revenue_portal_app

app = Flask(__name__)

# Mount sub-apps under prefixes
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    "/bookingengine": bookingengine_module.app,
    "/webapp": webapp_module.app,
    "/revenue-portal": revenue_portal_app,
})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/app1")
def app1():
    return Response("<h1>App 1</h1>", mimetype="text/html")

if __name__ == "__main__":
    app.run(debug=True)