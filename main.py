# main.py
from flask import Flask, render_template, Response
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import webapp as webapp_module  # ← imports webapp.py's Flask app

app = Flask(__name__)

# Mount the sub-app at /webapp
# All routes defined at "/" inside webapp.py will appear under "/webapp"
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    "/webapp": webapp_module.app
})

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/app1")
def app1():
    return Response("<h1>App 1</h1>", mimetype="text/html")

if __name__ == "__main__":
    app.run(debug=True)