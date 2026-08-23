import math
import time
import requests


# =========================================================
# OVERPASS SERVERS
# =========================================================
#
# The first server is tried first.
# If it times out / fails / is rate limited,
# the next server is automatically tried.
#
# =========================================================

OVERPASS_URLS = [
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]


# =========================================================
# SETTINGS
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
    Calculate straight-line distance between
    two latitude/longitude coordinates.
    """

    earth_radius_km = 6371.0

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)

    delta_lat = math.radians(
        lat2 - lat1
    )

    delta_lon = math.radians(
        lon2 - lon1
    )

    a = (
        math.sin(delta_lat / 2) ** 2
        +
        math.cos(lat1_rad)
        *
        math.cos(lat2_rad)
        *
        math.sin(delta_lon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius_km * c


# =========================================================
# BUILD OVERPASS QUERY
# =========================================================

def build_query(
    latitude,
    longitude,
    radius
):

    query = f"""
    [out:json][timeout:80];

    (
        /* ================================================
           COLLEGES
           ================================================ */

        nwr["amenity"="college"]
        (around:{radius},{latitude},{longitude});


        /* ================================================
           UNIVERSITIES
           ================================================ */

        nwr["amenity"="university"]
        (around:{radius},{latitude},{longitude});


        /* ================================================
           SHOPPING MALLS
           ================================================ */

        nwr["shop"="mall"]
        (around:{radius},{latitude},{longitude});


        /* ================================================
           SUPERMARKETS
           ================================================ */

        nwr["shop"="supermarket"]
        (around:{radius},{latitude},{longitude});


        /* ================================================
           OFFICES
           ================================================ */

        nwr["office"]
        (around:{radius},{latitude},{longitude});
    );

    out center;
    """

    return query


# =========================================================
# GET BUSINESS AREA DATA
# =========================================================

def get_business_area_data(
    latitude,
    longitude,
    radius=1000
):

    print("\n")
    print("=" * 60)
    print("BUSINESS / AREA DATA SEARCH")
    print("=" * 60)

    print(
        f"Latitude: {latitude}"
    )

    print(
        f"Longitude: {longitude}"
    )

    print(
        f"Search radius: {radius} meters"
    )

    # =====================================================
    # BUILD QUERY
    # =====================================================

    query = build_query(
        latitude,
        longitude,
        radius
    )


    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }


    # =====================================================
    # RESULT CONTAINERS
    # =====================================================

    empty_result = {
        "colleges": [],
        "universities": [],
        "malls": [],
        "supermarkets": [],
        "offices": []
    }


    # =====================================================
    # REQUEST DATA
    # =====================================================

    data = None

    session = requests.Session()


    # =====================================================
    # TRY MULTIPLE OVERPASS SERVERS
    # =====================================================

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

                elapsed = (
                    time.time()
                    -
                    start_time
                )

                print(
                    f"Response received in "
                    f"{elapsed:.2f} seconds"
                )


                # -----------------------------------------
                # RATE LIMIT
                # -----------------------------------------

                if response.status_code == 429:

                    print(
                        "Server rate limited the request."
                    )

                    time.sleep(5)

                    break


                # -----------------------------------------
                # SERVER ERROR
                # -----------------------------------------

                if response.status_code >= 500:

                    print(
                        f"Overpass server error: "
                        f"{response.status_code}"
                    )

                    break


                # -----------------------------------------
                # OTHER HTTP ERRORS
                # -----------------------------------------

                response.raise_for_status()


                # -----------------------------------------
                # JSON
                # -----------------------------------------

                data = response.json()

                print(
                    "Overpass request successful."
                )

                break


            except requests.exceptions.Timeout:

                print(
                    "Overpass request timed out."
                )

                if retry < MAX_RETRIES_PER_SERVER:

                    print(
                        "Retrying same server..."
                    )

                    time.sleep(2)

                else:

                    print(
                        "Trying next Overpass server..."
                    )


            except requests.exceptions.ConnectionError as e:

                print(
                    "Connection error:"
                )

                print(e)

                print(
                    "Trying next Overpass server..."
                )

                break


            except requests.exceptions.RequestException as e:

                print(
                    "Overpass request error:"
                )

                print(e)

                print(
                    "Trying next Overpass server..."
                )

                break


            except ValueError as e:

                print(
                    "Invalid JSON received:"
                )

                print(e)

                break


        # -------------------------------------------------
        # Stop once a server succeeds
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

        return empty_result


    # =====================================================
    # RESULT ARRAYS
    # =====================================================

    colleges = []

    universities = []

    malls = []

    supermarkets = []

    offices = []


    # =====================================================
    # DUPLICATE TRACKING
    # =====================================================

    seen = set()


    # =====================================================
    # PROCESS OSM ELEMENTS
    # =====================================================

    for element in data.get(
        "elements",
        []
    ):

        tags = element.get(
            "tags",
            {}
        )


        # -------------------------------------------------
        # UNIQUE OSM ID
        # -------------------------------------------------

        element_id = (
            element.get("type"),
            element.get("id")
        )

        if element_id in seen:

            continue

        seen.add(
            element_id
        )


        # =================================================
        # GET COORDINATES
        # =================================================

        latitude_value = element.get(
            "lat"
        )

        longitude_value = element.get(
            "lon"
        )


        # Ways and relations normally use "center"
        if (
            latitude_value is None
            or
            longitude_value is None
        ):

            center = element.get(
                "center",
                {}
            )

            latitude_value = center.get(
                "lat"
            )

            longitude_value = center.get(
                "lon"
            )


        if (
            latitude_value is None
            or
            longitude_value is None
        ):

            continue


        # =================================================
        # DISTANCE
        # =================================================

        distance_km = calculate_distance_km(
            latitude,
            longitude,
            latitude_value,
            longitude_value
        )


        # =================================================
        # COMMON PLACE OBJECT
        # =================================================

        place = {

            "id": element.get(
                "id"
            ),

            "name": tags.get(
                "name",
                "Unnamed"
            ),

            "latitude": latitude_value,

            "longitude": longitude_value,

            "distance_km": round(
                distance_km,
                3
            ),

            "operator": tags.get(
                "operator",
                "Not available"
            )

        }


        # =================================================
        # COLLEGE
        # =================================================

        if tags.get(
            "amenity"
        ) == "college":

            place["type"] = "college"

            colleges.append(
                place
            )


        # =================================================
        # UNIVERSITY
        # =================================================

        elif tags.get(
            "amenity"
        ) == "university":

            place["type"] = "university"

            universities.append(
                place
            )


        # =================================================
        # SHOPPING MALL
        # =================================================

        elif tags.get(
            "shop"
        ) == "mall":

            place["type"] = "mall"

            malls.append(
                place
            )


        # =================================================
        # SUPERMARKET
        # =================================================

        elif tags.get(
            "shop"
        ) == "supermarket":

            place["type"] = "supermarket"

            supermarkets.append(
                place
            )


        # =================================================
        # OFFICES
        # =================================================

        elif tags.get(
            "office"
        ):

            place["type"] = "office"

            offices.append(
                place
            )


    # =====================================================
    # SORT BY DISTANCE
    # =====================================================

    colleges.sort(
        key=lambda x: x["distance_km"]
    )

    universities.sort(
        key=lambda x: x["distance_km"]
    )

    malls.sort(
        key=lambda x: x["distance_km"]
    )

    supermarkets.sort(
        key=lambda x: x["distance_km"]
    )

    offices.sort(
        key=lambda x: x["distance_km"]
    )


    # =====================================================
    # SUMMARY
    # =====================================================

    print("\n")
    print("=" * 60)
    print("BUSINESS / AREA RESULTS")
    print("=" * 60)

    print(
        "Colleges:",
        len(colleges)
    )

    print(
        "Universities:",
        len(universities)
    )

    print(
        "Malls:",
        len(malls)
    )

    print(
        "Supermarkets:",
        len(supermarkets)
    )

    print(
        "Offices:",
        len(offices)
    )

    print(
        "Total:",
        (
            len(colleges)
            +
            len(universities)
            +
            len(malls)
            +
            len(supermarkets)
            +
            len(offices)
        )
    )

    print("=" * 60)


    # =====================================================
    # RETURN
    # =====================================================

    return {

        "colleges": colleges,

        "universities": universities,

        "malls": malls,

        "supermarkets": supermarkets,

        "offices": offices

    }