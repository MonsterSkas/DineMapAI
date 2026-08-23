import subprocess
"""
app.py
-----------------------------------------------------------
DineMapAI backend server (Flask).

This file implements the three endpoints the frontend already
calls from js/api.js:

    POST /login              -> loginUser()
    GET  /dashboard-data     -> getDashboardData()
    POST /analyze-location   -> analyzeLocation()

HOW TO RUN THIS:
    1. Install dependencies:
         pip install -r requirements.txt
    2. Start the server:
         python app.py
    3. It will run on http://127.0.0.1:5000
       (this matches API_BASE_URL in the frontend's js/api.js)
    4. In js/api.js, set USE_MOCK_DATA = false so the frontend
       starts talking to this server instead of using fake data.

HOW TO ADD A NEW ENDPOINT:
    1. Write a new function below and put @app.route(...) above it.
    2. Add a matching function in the frontend's js/api.js
       (using postData() or fetchData()).
    That's it — no other files need to change.
"""
import os
from flask import Flask, request, jsonify

from mock_data import get_dashboard_data, DEMO_USERS

app = Flask(__name__)


# ---------------------------------------------------------
# CORS (Cross-Origin Resource Sharing)
# -----------------------------------------------------------
# The frontend is usually opened as a plain HTML file or served
# from a different port (e.g. VS Code's "Live Server" on 5500),
# which counts as a different "origin" than this Flask server.
# Browsers block cross-origin requests by default, so this small
# function adds the headers needed to allow them.
#
# For production, replace "*" with your real frontend's URL.
# ---------------------------------------------------------
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


# ---------------------------------------------------------
# Simple health check — lets you confirm the server is running
# by visiting http://127.0.0.1:5000 in a browser.
# ---------------------------------------------------------
@app.route("/")
def health_check():
    return jsonify({
        "success": True,
        "message": "DineMapAI backend is running.",
    })


# ---------------------------------------------------------
# POST /login
# Expects JSON: { "username": "...", "password": "..." }
# Returns JSON: { "success": bool, "message": "..." }
# ---------------------------------------------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    # Basic validation — the frontend already checks this, but a
    # backend should never trust the frontend alone.
    if username == "" or password == "":
        return jsonify({
            "success": False,
            "message": "Username and password are required.",
        }), 400

    # NOTE: This is a demo-only check against a hardcoded list of
    # users in mock_data.py. Replace this with a real database
    # lookup and a proper password hash comparison (e.g. using
    # werkzeug.security.check_password_hash) before going live.
    correct_password = DEMO_USERS.get(username)

    if correct_password is not None and correct_password == password:
        return jsonify({
            "success": True,
            "message": "Login successful.",
        })

    return jsonify({
        "success": False,
        "message": "Invalid username or password.",
    }), 401


# ---------------------------------------------------------
# GET /dashboard-data
# Returns everything the dashboard page needs to render.
# ---------------------------------------------------------
@app.route("/dashboard-data", methods=["GET"])
def dashboard_data():

    try:
        data = get_dashboard_data()
        return jsonify(data)

    except Exception as e:

        print("Dashboard error:")
        print(e)

        return jsonify({
            "success": False,
            "message": "Failed to load dashboard data.",
            "error": str(e)
        }), 500


# ---------------------------------------------------------
# POST /analyze-location
# Expects JSON with the fields collected on analyze-location.html:
#   cityArea, restaurantType, targetAudience, budgetRange,
#   businessGoals, additionalPreferences, timingSlots (list)
# Returns JSON: { "success": bool, "message": "..." }
# ---------------------------------------------------------
@app.route("/analyze-location", methods=["POST"])
def analyze_location():
    data = request.get_json(silent=True) or {}

    city_area = data.get("cityArea", "").strip()
    restaurant_type = data.get("restaurantType", "").strip()

    if city_area == "" or restaurant_type == "":
        return jsonify({
            "success": False,
            "message": "City / Area and Restaurant Type are required.",
        }), 400

    # ---------------------------------------------------------
    # This is where your real analysis logic would go: querying
    # map/demand data, scoring nearby areas, saving the request
    # to a database, etc. For now we just confirm receipt.
    # ---------------------------------------------------------
    print("Received analyze-location request:", data)  # helpful while developing
    os.system(f"python D:/PROJECT/DineMapAi/Backend/backend2/main.py \"{data['cityArea']}\" \"{data['targetAudience']}\"")
    try:
        f=open("D:/PROJECT/DineMapAi/Backend/backend2/location.txt",'w')
        f.write(f"{data[city_area]}")
        f.close()
    except:
        pass
    return jsonify({
        "success": True,
        "message": f"Analysis started for {city_area} ({restaurant_type}).",
    })


# ---------------------------------------------------------
# Run the development server.
# debug=True auto-reloads the server when you edit this file.
# Turn debug off before deploying to production.
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
