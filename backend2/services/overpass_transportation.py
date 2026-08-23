import math
import time
import requests


# =========================================================
# OVERPASS SERVERS
# =========================================================
#
# Primary:
# Private.coffee is currently a global public Overpass
# instance and is the successor to the Kumi service.
#
# Fallbacks are used automatically if one server times out,
# returns 429, or returns a server-side error.
# =========================================================

OVERPASS_URLS = [
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]


# =========================================================
# REQUEST SETTINGS
# =========================================================

REQUEST_TIMEOUT = 90

MAX_RETRIES_PER_SERVER = 1

USER_AGENT = (
    "DineMapAI/1.0 "
    "(OpenStreetMap Overpass client; "
    "location-intelligence project)"
)


# =========================================================
# DISTANCE CALCULATION
# =========================================================

def calculate_distance_km(
    lat1,
    lon1,
    lat2,
    lon2
):
    """
    Calculate distance between two coordinates
    using the Haversine formula.
    """

    earth_radius_km = 6371.0

    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        +
        math.cos(lat1)
        * math.cos(lat2)
        * math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius_km * c


# =========================================================
# BUILD OVERPASS QUERY
# =========================================================

def build_query(latitude, longitude):

    query = f"""
    [out:json][timeout:80];

    (
        /* ================================================
           BUS STOPS
           ================================================ */

        node["highway"="bus_stop"]
        (around:2000,{latitude},{longitude});


        /* ================================================
           METRO / SUBWAY STATIONS
           ================================================ */

        node["railway"="station"]["station"="subway"]
        (around:5000,{latitude},{longitude});

        node["railway"="subway_entrance"]
        (around:5000,{latitude},{longitude});


        /* ================================================
           TRAIN STATIONS
           ================================================ */

        node["railway"="station"]
        (around:5000,{latitude},{longitude});

        way["railway"="station"]
        (around:5000,{latitude},{longitude});


        /* ================================================
           AIRPORTS
           ================================================ */

        nwr["aeroway"="aerodrome"]
        (around:20000,{latitude},{longitude});
    );

    out center;
    """

    return query


# =========================================================
# GET TRANSPORT DATA
# =========================================================

def get_transport(latitude, longitude):

    print("\n")
    print("=" * 60)
    print("TRANSPORT SEARCH")
    print("=" * 60)

    print(
        f"Location: {latitude}, {longitude}"
    )

    query = build_query(
        latitude,
        longitude
    )

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # =====================================================
    # TRY EACH OVERPASS SERVER
    # =====================================================

    data = None

    session = requests.Session()

    for server_number, overpass_url in enumerate(
        OVERPASS_URLS,
        start=1
    ):

        print("\n")
        print(
            f"Trying Overpass server "
            f"{server_number}/{len(OVERPASS_URLS)}:"
        )

        print(overpass_url)

        for retry in range(
            MAX_RETRIES_PER_SERVER + 1
        ):

            try:

                start_time = time.time()

                response = session.post(
                    overpass_url,
                    data=query,
                    headers=headers,
                    timeout=REQUEST_TIMEOUT
                )

                elapsed = time.time() - start_time

                print(
                    f"Response received in "
                    f"{elapsed:.2f} seconds"
                )

                # -----------------------------------------
                # Rate limited
                # -----------------------------------------

                if response.status_code == 429:

                    print(
                        "Server rate limited the request."
                    )

                    time.sleep(5)

                    break


                # -----------------------------------------
                # Server error
                # -----------------------------------------

                if response.status_code >= 500:

                    print(
                        f"Server error: "
                        f"{response.status_code}"
                    )

                    break


                # -----------------------------------------
                # Other HTTP errors
                # -----------------------------------------

                response.raise_for_status()


                # -----------------------------------------
                # Parse JSON
                # -----------------------------------------

                data = response.json()

                print(
                    "Overpass request successful."
                )

                break

            except requests.exceptions.Timeout:

                print(
                    f"TIMEOUT from "
                    f"{overpass_url}"
                )

                if retry < MAX_RETRIES_PER_SERVER:

                    print(
                        "Retrying same server..."
                    )

                    time.sleep(2)

                else:

                    print(
                        "Moving to next Overpass server..."
                    )


            except requests.exceptions.ConnectionError as e:

                print(
                    "Connection error:"
                )

                print(e)

                print(
                    "Moving to next server..."
                )

                break


            except requests.exceptions.RequestException as e:

                print(
                    "Overpass request error:"
                )

                print(e)

                print(
                    "Moving to next server..."
                )

                break


            except ValueError as e:

                print(
                    "Invalid JSON received:"
                )

                print(e)

                break


        # -------------------------------------------------
        # Stop trying servers once successful
        # -------------------------------------------------

        if data is not None:

            break


    # =====================================================
    # ALL SERVERS FAILED
    # =====================================================

    if data is None:

        print("\n")
        print("=" * 60)
        print("ALL OVERPASS SERVERS FAILED")
        print("=" * 60)

        return []


    # =====================================================
    # PROCESS RESULTS
    # =====================================================

    transport = []

    seen = set()


    for element in data.get(
        "elements",
        []
    ):

        tags = element.get(
            "tags",
            {}
        )


        # -------------------------------------------------
        # UNIQUE ELEMENT ID
        # -------------------------------------------------

        element_id = (
            element.get("type"),
            element.get("id")
        )

        if element_id in seen:

            continue

        seen.add(element_id)


        # -------------------------------------------------
        # COORDINATES
        # -------------------------------------------------

        lat = element.get("lat")
        lon = element.get("lon")


        # Ways / relations may use center coordinates

        if lat is None or lon is None:

            center = element.get(
                "center",
                {}
            )

            lat = center.get("lat")
            lon = center.get("lon")


        if lat is None or lon is None:

            continue


        # -------------------------------------------------
        # TRANSPORT TYPE
        # -------------------------------------------------

        transport_type = None


        # =================================================
        # AIRPORT
        # =================================================

        if tags.get(
            "aeroway"
        ) == "aerodrome":

            transport_type = "airport"


        # =================================================
        # BUS
        # =================================================

        elif tags.get(
            "highway"
        ) == "bus_stop":

            transport_type = "bus"


        # =================================================
        # METRO ENTRANCE
        # =================================================

        elif tags.get(
            "railway"
        ) == "subway_entrance":

            transport_type = "metro"


        # =================================================
        # METRO STATION
        # =================================================

        elif (
            tags.get("railway") == "station"
            and
            tags.get("station") == "subway"
        ):

            transport_type = "metro"


        # =================================================
        # TRAIN
        # =================================================

        elif tags.get(
            "railway"
        ) == "station":

            transport_type = "train"


        else:

            continue


        # -------------------------------------------------
        # DISTANCE FROM SEARCH LOCATION
        # -------------------------------------------------

        distance_km = calculate_distance_km(
            latitude,
            longitude,
            lat,
            lon
        )


        # -------------------------------------------------
        # NAME
        # -------------------------------------------------

        name = tags.get(
            "name",
            "Unnamed"
        )


        # -------------------------------------------------
        # SAVE TRANSPORT DATA
        # -------------------------------------------------

        transport.append({

            "id": element.get("id"),

            "name": name,

            "type": transport_type,

            "latitude": lat,

            "longitude": lon,

            "distance_km": round(
                distance_km,
                3
            ),

            "operator": tags.get(
                "operator",
                "Not available"
            ),

            "network": tags.get(
                "network",
                "Not available"
            )

        })


    # =====================================================
    # REMOVE DUPLICATE / NEAR-DUPLICATE ENTRIES
    # =====================================================

    cleaned_transport = []

    seen_locations = set()


    for item in transport:

        # Round coordinates to approximately ~10 m
        location_key = (
            item["type"],
            round(item["latitude"], 4),
            round(item["longitude"], 4)
        )

        if location_key in seen_locations:

            continue

        seen_locations.add(
            location_key
        )

        cleaned_transport.append(
            item
        )


    # =====================================================
    # SORT BY DISTANCE
    # =====================================================

    cleaned_transport.sort(
        key=lambda x: x["distance_km"]
    )


    # =====================================================
    # SUMMARY
    # =====================================================

    bus_count = sum(
        1
        for x in cleaned_transport
        if x["type"] == "bus"
    )

    metro_count = sum(
        1
        for x in cleaned_transport
        if x["type"] == "metro"
    )

    train_count = sum(
        1
        for x in cleaned_transport
        if x["type"] == "train"
    )

    airport_count = sum(
        1
        for x in cleaned_transport
        if x["type"] == "airport"
    )


    print("\n")
    print("=" * 60)
    print("TRANSPORT RESULTS")
    print("=" * 60)

    print(
        "Bus stops:",
        bus_count
    )

    print(
        "Metro stations/entrances:",
        metro_count
    )

    print(
        "Train stations:",
        train_count
    )

    print(
        "Airports:",
        airport_count
    )

    print(
        "Total:",
        len(cleaned_transport)
    )

    print("=" * 60)


    return cleaned_transport