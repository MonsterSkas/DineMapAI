import json
import os

from services.overpass_resturant import get_restaurants
from services.overpass_transportation import get_transport
from services.nominatim import get_coordinates
from services.overpass_places import get_business_area_data


# ============================================================
# CONFIGURATION
# ============================================================

LOCATION_QUERY = "Salt Lake, Kolkata"

# Keep this small for faster Overpass response
PLACES_RADIUS = 1000


# ============================================================
# LOCATION
# ============================================================

print("\nGetting location...")

result = get_coordinates(LOCATION_QUERY)

if not result:
    print("ERROR: Could not get location.")
    exit()

print("Location:", result["display_name"])

lat = result["latitude"]
longitude = result["longitude"]


# ============================================================
# RESTAURANTS
# ============================================================

print("\nGetting restaurants...")

try:

    restaurants = get_restaurants(
        lat,
        longitude
    )

    print(
        "Restaurants:",
        len(restaurants)
    )

except Exception as e:

    print(
        "Restaurant API failed:",
        e
    )

    restaurants = []


# ============================================================
# TRANSPORTATION
# ============================================================

print("\nGetting transportation...")

try:

    transports = get_transport(
        lat,
        longitude
    )

    print(
        "Transportation:",
        len(transports)
    )

except Exception as e:

    print(
        "Transportation API failed:",
        e
    )

    transports = []


# ============================================================
# PLACES
# ============================================================

print("\nGetting nearby places...")

try:

    data = get_business_area_data(
        lat,
        longitude,
        radius=PLACES_RADIUS
    )

    print(
        "Colleges:",
        len(data.get("colleges", []))
    )

    print(
        "Universities:",
        len(data.get("universities", []))
    )

    print(
        "Malls:",
        len(data.get("malls", []))
    )

    print(
        "Supermarkets:",
        len(data.get("supermarkets", []))
    )

    print(
        "Offices:",
        len(data.get("offices", []))
    )


except Exception as e:

    print(
        "Places API failed/skipped:",
        e
    )

    # Don't stop the entire program
    data = {
        "colleges": [],
        "universities": [],
        "malls": [],
        "supermarkets": [],
        "offices": []
    }


# ============================================================
# COMBINE EVERYTHING
# ============================================================

location_data = {

    "location": {

        "query": LOCATION_QUERY,

        "latitude": lat,

        "longitude": longitude,

        "display_name": result.get(
            "display_name",
            ""
        )
    },


    "restaurants": restaurants,


    "transportation": transports,


    "business_area": {

        "colleges": data.get(
            "colleges",
            []
        ),

        "universities": data.get(
            "universities",
            []
        ),

        "malls": data.get(
            "malls",
            []
        ),

        "supermarkets": data.get(
            "supermarkets",
            []
        ),

        "offices": data.get(
            "offices",
            []
        )
    }
}


# ============================================================
# SAVE JSON
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

os.makedirs(
    DATA_DIR,
    exist_ok=True
)


FILE_PATH = os.path.join(
    DATA_DIR,
    "location_data.json"
)


with open(
    FILE_PATH,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        location_data,
        file,
        indent=4,
        ensure_ascii=False
    )


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n=====================================")
print("       DINEMAPAI DATA COLLECTION")
print("=====================================")

print(
    "Restaurants:",
    len(restaurants)
)

print(
    "Transportation:",
    len(transports)
)

print(
    "Colleges:",
    len(data["colleges"])
)

print(
    "Universities:",
    len(data["universities"])
)

print(
    "Malls:",
    len(data["malls"])
)

print(
    "Supermarkets:",
    len(data["supermarkets"])
)

print(
    "Offices:",
    len(data["offices"])
)

print("-------------------------------------")

print(
    "JSON saved successfully:"
)

print(FILE_PATH)

print("=====================================")