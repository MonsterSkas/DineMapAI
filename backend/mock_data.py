"""
mock_data.py
-----------------------------------------------------------
DineMapAI dashboard data provider.

IMPORTANT:
    results.json is READ FROM DISK EVERY TIME
    get_dashboard_data() is called.

This means:
    1. results.json changes
    2. User refreshes dashboard
    3. Flask calls get_dashboard_data()
    4. Latest results.json is loaded
    5. Dashboard receives the new values

NO Flask restart is required.
"""

import json
import os


# =========================================================
# CONFIGURATION
# =========================================================

JSON_FILE = r"D:/PROJECT/DineMapAi/New folder/backend/results.json"


# =========================================================
# LOAD JSON
# =========================================================

def load_results():

    """
    Read the latest results.json from disk.

    This function is intentionally called every time
    get_dashboard_data() runs.
    """

    print("\n========================================")
    print("Loading latest results.json...")
    print("========================================")

    if not os.path.exists(JSON_FILE):

        raise FileNotFoundError(
            f"results.json not found:\n{JSON_FILE}"
        )

    with open(
        JSON_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    print("JSON loaded successfully.")
    print("Location:", data.get("location"))
    print("Final Score:", data.get("scores", {}).get("final_score"))

    return data


# =========================================================
# DASHBOARD DATA
# =========================================================

def get_dashboard_data():

    """
    Returns everything the dashboard page needs to render.

    IMPORTANT:
        The JSON is loaded HERE, not when this module is
        imported.

    Therefore every call gets the latest results.json.
    """

    # -----------------------------------------------------
    # READ FRESH JSON
    # -----------------------------------------------------

    data = load_results()


    # =====================================================
    # BASIC INFORMATION
    # =====================================================

    timestamp = data.get("timestamp")
    location = data.get("location")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    target_audience = data.get(
        "target_audience"
    )

    time_of_day = data.get(
        "time_of_day"
    )


    # =====================================================
    # LOCATION DATA
    # =====================================================

    location_data = data.get(
        "data",
        {}
    )

    colleges = location_data.get(
        "colleges",
        0
    )

    universities = location_data.get(
        "universities",
        0
    )

    offices = location_data.get(
        "offices",
        0
    )

    malls = location_data.get(
        "malls",
        0
    )

    restaurants = location_data.get(
        "restaurants",
        0
    )

    cafes = location_data.get(
        "cafes",
        0
    )

    metro_distance = location_data.get(
        "metro_distance",
        0
    )

    bus_distance = location_data.get(
        "bus_distance",
        0
    )

    train_distance = location_data.get(
        "train_distance",
        0
    )


    # =====================================================
    # SCORES
    # =====================================================

    scores = data.get(
        "scores",
        {}
    )

    demand = scores.get(
        "demand",
        0
    )

    competition = scores.get(
        "competition",
        0
    )

    accessibility = scores.get(
        "accessibility",
        0
    )

    audience_fit = scores.get(
        "audience_fit",
        0
    )

    time_score = scores.get(
        "time_score",
        0
    )

    weather = scores.get(
        "weather",
        0
    )

    final_score = scores.get(
        "final_score",
        0
    )


    # =====================================================
    # DEBUG OUTPUT
    # =====================================================

    print("\n========== CURRENT DASHBOARD DATA ==========")

    print("Timestamp:", timestamp)

    print("Location:", location)

    print("Latitude:", latitude)

    print("Longitude:", longitude)

    print("Target Audience:", target_audience)

    print("Time:", time_of_day)

    print("Restaurants:", restaurants)

    print("Cafes:", cafes)

    print("Colleges:", colleges)

    print("Universities:", universities)

    print("Offices:", offices)

    print("Malls:", malls)

    print("Metro Distance:", metro_distance)

    print("Bus Distance:", bus_distance)

    print("Train Distance:", train_distance)

    print("Demand:", demand)

    print("Competition:", competition)

    print("Accessibility:", accessibility)

    print("Audience Fit:", audience_fit)

    print("Time Score:", time_score)

    print("Weather:", weather)

    print("Final Score:", final_score)

    print("============================================\n")


    # =====================================================
    # RETURN DASHBOARD OBJECT
    # =====================================================

    return {

        "success": True,

        # -------------------------------------------------
        # USER
        # -------------------------------------------------

        "user": {
            "name": "Angshu"
        },


        # -------------------------------------------------
        # BASIC LOCATION INFORMATION
        # -------------------------------------------------

        "location": {
            "name": location,
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": timestamp,
            "targetAudience": target_audience,
            "timeOfDay": time_of_day
        },


        # -------------------------------------------------
        # TIMING PERFORMANCE
        # -------------------------------------------------

        "timingPerformance": [

            {
                "label": "Final Score",
                "time": "",
                "score": final_score,
                "status": "--",
                "color": "green"
            },

            {
                "label": "Weather",
                "time": "",
                "score": weather,
                "status": "Very Good",
                "color": "blue"
            }

        ],


        # -------------------------------------------------
        # DEMAND TREND
        # -------------------------------------------------

        "demandTrend": [

            {
                "hour": "12 AM",
                "value": 8
            },

            {
                "hour": "4 AM",
                "value": 4
            },

            {
                "hour": "8 AM",
                "value": 52
            },

            {
                "hour": "12 PM",
                "value": 48
            },

            {
                "hour": "4 PM",
                "value": 78
            },

            {
                "hour": "8 PM",
                "value": 92
            },

            {
                "hour": "12 AM",
                "value": 30
            }

        ],


        # -------------------------------------------------
        # TOP LOCATIONS
        # -------------------------------------------------

        "topLocations": [],


        # -------------------------------------------------
        # SCORE BREAKDOWN
        # -------------------------------------------------

        "scoreBreakdown": {

            "locationName": location,

            "axes": [

                {
                    "label": "Demand",
                    "value": demand
                },

                {
                    "label": "Accessibility",
                    "value": accessibility
                },

                {
                    "label": "Target Audience",
                    "value": audience_fit
                },

                {
                    "label": "Competition (Inverted)",
                    "value": competition
                },

                {
                    "label": "Nearby Facilities",
                    "value": 60
                }

            ]

        },


        # -------------------------------------------------
        # KEY INSIGHTS
        # -------------------------------------------------

        "keyInsights": [

            {
                "icon": "fa-arrow-trend-up",
                "color": "green",
                "text":
                    "Evening performance is strongest "
                    "(4 PM - 10 PM). Ideal for dinner "
                    "& hangout crowds."
            },

            {
                "icon": "fa-circle-info",
                "color": "blue",
                "text":
                    "College proximity is a major "
                    "demand driver in this area."
            },

            {
                "icon": "fa-triangle-exclamation",
                "color": "orange",
                "text":
                    "Competition is moderate compared "
                    "to popular commercial zones."
            },

            {
                "icon": "fa-subway",
                "color": "purple",
                "text":
                    "Areas near metro stations show "
                    "18% higher footfall potential."
            }

        ],


        # -------------------------------------------------
        # DATA OVERVIEW
        # -------------------------------------------------

        "dataOverview": [

            {
                "label": "Total Restaurants",
                "value": restaurants
            },

            {
                "label": "Cafés",
                "value": cafes
            },

            {
                "label": "Colleges",
                "value": colleges
            },

            {
                "label": "Metro Stations",
                "value": metro_distance
            },

            {
                "label": "Avg. Population",
                "value": "12.4 L"
            }

        ]

    }


# =========================================================
# DEMO USERS
# =========================================================

DEMO_USERS = {

    "demo": "demo123",

    "admin": "admin123"

}