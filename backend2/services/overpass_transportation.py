import requests


OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"


def get_transport(latitude, longitude):

    query = f"""
    [out:json][timeout:30];

    (
        // =========================
        // BUS STOPS
        // =========================

        node[
            "highway"="bus_stop"
        ](around:2000,{latitude},{longitude});


        // =========================
        // METRO STATIONS
        // =========================

        node[
            "railway"="station"
        ][
            "station"="subway"
        ](around:5000,{latitude},{longitude});


        // =========================
        // TRAIN STATIONS
        // =========================

        node[
            "railway"="station"
        ](around:5000,{latitude},{longitude});


        // =========================
        // AIRPORTS
        // =========================

        nwr[
            "aeroway"="aerodrome"
        ](around:20000,{latitude},{longitude});
    );

    out center;
    """

    headers = {
        "User-Agent": "DineMapAI/1.0"
    }

    try:

        response = requests.post(
            OVERPASS_URL,
            data=query,
            headers=headers,
            timeout=45
        )

        response.raise_for_status()

        data = response.json()

    except requests.exceptions.RequestException as e:

        print("Transportation API error:", e)

        return []


    transport = []

    # Prevent duplicate stations
    seen = set()


    for element in data.get("elements", []):

        tags = element.get("tags", {})

        element_id = (
            element.get("type"),
            element.get("id")
        )

        if element_id in seen:
            continue

        seen.add(element_id)


        # =========================
        # COORDINATES
        # =========================

        lat = element.get("lat")
        lon = element.get("lon")


        if lat is None or lon is None:

            center = element.get(
                "center",
                {}
            )

            lat = center.get("lat")
            lon = center.get("lon")


        if lat is None or lon is None:
            continue


        # =========================
        # TRANSPORT TYPE
        # =========================

        if tags.get("aeroway") == "aerodrome":

            transport_type = "airport"


        elif tags.get("highway") == "bus_stop":

            transport_type = "bus"


        elif (
            tags.get("railway") == "station"
            and tags.get("station") == "subway"
        ):

            transport_type = "metro"


        elif tags.get("railway") == "station":

            transport_type = "train"


        else:

            continue


        # =========================
        # SAVE DATA
        # =========================

        transport.append({

            "id": element["id"],

            "name": tags.get(
                "name",
                "Unnamed"
            ),

            "type": transport_type,

            "latitude": lat,

            "longitude": lon,

            "operator": tags.get(
                "operator",
                "Not available"
            ),

            "network": tags.get(
                "network",
                "Not available"
            )
        })


    return transport