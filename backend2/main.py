import json
from datetime import datetime

from math import radians, sin, cos, sqrt, atan2

from services.osrm import get_route
from services.overpass_resturant import get_restaurants
from services.overpass_transportation import get_transport
from services.nominatim import get_coordinates
from services.overpass_places import get_business_area_data

from calculation import (
    calculate_demand,
    calculate_competition,
    calculate_accessibility,
    calculate_audience_fit,
    calculate_time_score,
    calculate_final_score
)


# ============================================================
# SETTINGS
# ============================================================

LOCATION = "saltlake, Kolkata"

TARGET_AUDIENCE = "student"

TIME_OF_DAY = "evening"

# Temporary value until weather API is connected
WEATHER_SCORE = 80


# ============================================================
# DISTANCE CALCULATION
# ============================================================

def calculate_distance_km(
    lat1,
    lon1,
    lat2,
    lon2
):

    R = 6371.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)

    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    return R * c


# ============================================================
# FIND NEAREST TRANSPORT
# ============================================================

def find_nearest_transport(
    transports,
    latitude,
    longitude,
    transport_type
):

    distances = []

    for transport in transports:

        # Your transportation function must provide
        # a "type" field for this to work.

        if transport.get("type") != transport_type:
            continue

        transport_lat = transport.get("latitude")
        transport_lon = transport.get("longitude")

        if transport_lat is None or transport_lon is None:
            continue

        distance = calculate_distance_km(
            latitude,
            longitude,
            transport_lat,
            transport_lon
        )

        distances.append(distance)

    if not distances:
        return None

    return min(distances)


# ============================================================
# GET LOCATION
# ============================================================

print("\n==========================================")
print("              DineMapAI")
print("==========================================")

print("\nSearching for location...")

result = get_coordinates(LOCATION)

print(result)

if result == None:

    print("\nLocation: failed to fetch data")
    exit()


latitude = result["latitude"]
longitude = result["longitude"]

print("------------------------------------------")

print(
    f"Location: {LOCATION}"
)

print(
    f"Latitude: {latitude}"
)

print(
    f"Longitude: {longitude}"
)


# ============================================================
# RESTAURANTS
# ============================================================

print("\nFetching restaurants...")

restaurants = get_restaurants(
    latitude,
    longitude
)

if restaurants == None:

    print("Restaurants: failed to fetch data")

    restaurants = []


print(
    "\nRestaurants:",
    len(restaurants)
)

for restaurant in restaurants[:5]:

    print(restaurant)


print("------------------------------------------")


# ============================================================
# TRANSPORTATION
# ============================================================

print("\nFetching transportation...")

transports = get_transport(
    latitude,
    longitude
)

if transports == None:

    print("Transportation: failed to fetch data")

    transports = []


print(
    "Transportation:",
    len(transports)
)

for transport in transports[:5]:

    print(transport)


print("------------------------------------------")


# ============================================================
# BUSINESS AREA DATA
# ============================================================

print("\nFetching business area data...")

places = get_business_area_data(
    latitude,
    longitude,
    radius=2000
)

if places == None:

    print(
        "Business area data: failed to fetch data"
    )

    places = {
        "colleges": [],
        "universities": [],
        "malls": [],
        "supermarkets": [],
        "offices": []
    }


print("\n========================")
print("BUSINESS AREA DATA")
print("========================")

print(
    "Colleges:",
    len(places["colleges"])
)

print(
    "Universities:",
    len(places["universities"])
)

print(
    "Malls:",
    len(places["malls"])
)

print(
    "Supermarkets:",
    len(places["supermarkets"])
)

print(
    "Offices:",
    len(places["offices"])
)


# ============================================================
# DISPLAY PLACES
# ============================================================

print("\nCOLLEGES")

for i, place in enumerate(
    places["colleges"],
    start=1
):

    print(
        f"{i}. {place['name']} | "
        f"{place['latitude']}, "
        f"{place['longitude']}"
    )


print("\nUNIVERSITIES")

for i, place in enumerate(
    places["universities"],
    start=1
):

    print(
        f"{i}. {place['name']} | "
        f"{place['latitude']}, "
        f"{place['longitude']}"
    )


print("\nMALLS")

for i, place in enumerate(
    places["malls"],
    start=1
):

    print(
        f"{i}. {place['name']} | "
        f"{place['latitude']}, "
        f"{place['longitude']}"
    )


print("\nSUPERMARKETS")

for i, place in enumerate(
    places["supermarkets"],
    start=1
):

    print(
        f"{i}. {place['name']} | "
        f"{place['latitude']}, "
        f"{place['longitude']}"
    )


print("\nOFFICES")

for i, place in enumerate(
    places["offices"],
    start=1
):

    print(
        f"{i}. {place['name']} | "
        f"{place['office_type']} | "
        f"{place['latitude']}, "
        f"{place['longitude']}"
    )


# ============================================================
# TRANSPORTATION DISTANCES
# ============================================================

metro_distance = find_nearest_transport(
    transports,
    latitude,
    longitude,
    "metro"
)

bus_distance = find_nearest_transport(
    transports,
    latitude,
    longitude,
    "bus"
)

train_distance = find_nearest_transport(
    transports,
    latitude,
    longitude,
    "train"
)


# If a particular transport type wasn't found,
# use a large distance so distance_score() gives it a low score.

if metro_distance is None:
    metro_distance = 999

if bus_distance is None:
    bus_distance = 999

if train_distance is None:
    train_distance = 999


print("\n========================")
print("TRANSPORT DISTANCES")
print("========================")

print(
    f"Nearest Metro: {metro_distance:.2f} km"
)

print(
    f"Nearest Bus:   {bus_distance:.2f} km"
)

print(
    f"Nearest Train: {train_distance:.2f} km"
)


# ============================================================
# COUNT RESTAURANTS AND CAFES
# ============================================================

restaurant_count = 0
cafe_count = 0

for restaurant in restaurants:

    # If your restaurant API returns a "type"
    # field, we can distinguish them.

    business_type = restaurant.get("type")

    if business_type == "cafe":

        cafe_count += 1

    else:

        restaurant_count += 1


# ============================================================
# PREPARE DATA FOR CALCULATION
# ============================================================

calculation_data = {

    "colleges":
        len(places["colleges"]),

    "universities":
        len(places["universities"]),

    "offices":
        len(places["offices"]),

    "malls":
        len(places["malls"]),

    "restaurants":
        restaurant_count,

    "cafes":
        cafe_count,

    "metro_distance":
        metro_distance,

    "bus_distance":
        bus_distance,

    "train_distance":
        train_distance
}


# ============================================================
# SHOW DATA GOING INTO CALCULATION
# ============================================================

print("\n==========================================")
print("       DATA SENT TO CALCULATION")
print("==========================================")

print(
    "Colleges:       ",
    calculation_data["colleges"]
)

print(
    "Universities:   ",
    calculation_data["universities"]
)

print(
    "Offices:        ",
    calculation_data["offices"]
)

print(
    "Malls:          ",
    calculation_data["malls"]
)

print(
    "Restaurants:    ",
    calculation_data["restaurants"]
)

print(
    "Cafes:          ",
    calculation_data["cafes"]
)

print(
    "Metro distance: ",
    calculation_data["metro_distance"]
)

print(
    "Bus distance:   ",
    calculation_data["bus_distance"]
)

print(
    "Train distance: ",
    calculation_data["train_distance"]
)


# ============================================================
# CALCULATIONS
# ============================================================

demand = calculate_demand(
    calculation_data
)

competition = calculate_competition(
    calculation_data
)

accessibility = calculate_accessibility(
    calculation_data
)

audience_fit = calculate_audience_fit(
    calculation_data,
    TARGET_AUDIENCE
)

time_score = calculate_time_score(
    calculation_data,
    TARGET_AUDIENCE,
    TIME_OF_DAY
)


final_score = calculate_final_score(

    demand,

    competition,

    accessibility,

    audience_fit,

    time_score,

    WEATHER_SCORE
)


# ============================================================
# FINAL RESULTS
# ============================================================

print("\n==========================================")
print("             DineMapAI SCORE")
print("==========================================")

print(
    f"Demand:          {demand:.2f}/100"
)

print(
    f"Competition:     {competition:.2f}/100"
)

print(
    f"Accessibility:   {accessibility:.2f}/100"
)

print(
    f"Audience Fit:    {audience_fit:.2f}/100"
)

print(
    f"Time Score:      {time_score:.2f}/100"
)

print(
    f"Weather:         {WEATHER_SCORE:.2f}/100"
)

print("------------------------------------------")

print(
    f"FINAL SCORE:     {final_score:.2f}/100"
)

print("==========================================")

# ============================================================
# SAVE RESULTS TO JSON (overwrites each run)
# ============================================================

OUTPUT_FILE = "results.json"

result_entry = {
    "timestamp": datetime.now().isoformat(),
    "location": LOCATION,
    "latitude": latitude,
    "longitude": longitude,
    "target_audience": TARGET_AUDIENCE,
    "time_of_day": TIME_OF_DAY,

    "data": calculation_data,

    "scores": {
        "demand": round(demand, 2),
        "competition": round(competition, 2),
        "accessibility": round(accessibility, 2),
        "audience_fit": round(audience_fit, 2),
        "time_score": round(time_score, 2),
        "weather": round(WEATHER_SCORE, 2),
        "final_score": round(final_score, 2)
    }
}

with open(OUTPUT_FILE, "w") as f:
    json.dump(result_entry, f, indent=2)

print(f"\nResults saved to {OUTPUT_FILE}")