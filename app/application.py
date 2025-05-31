from flask import Flask, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="static", static_url_path="")
CORS(app)


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


# Add a route to serve static files
@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory("static", path)
