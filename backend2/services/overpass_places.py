import requests


OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"


def get_business_area_data(latitude, longitude, radius=1000):

    query = f"""
    [out:json][timeout:30];

    (
        // Colleges
        node["amenity"="college"]
        (around:{radius},{latitude},{longitude});

        // Universities
        node["amenity"="university"]
        (around:{radius},{latitude},{longitude});

        // Shopping malls
        node["shop"="mall"]
        (around:{radius},{latitude},{longitude});

        // Supermarkets
        node["shop"="supermarket"]
        (around:{radius},{latitude},{longitude});
    );

    out;
    """

    headers = {
        "User-Agent": "DineMapAI/1.0"
    }

    try:

        response = requests.post(
            OVERPASS_URL,
            data=query,
            headers=headers,
            timeout=40
        )

        response.raise_for_status()

        data = response.json()

    except requests.exceptions.RequestException as e:

        print("Overpass Places Error:", e)

        return {
            "colleges": [],
            "universities": [],
            "malls": [],
            "supermarkets": [],
            "offices": []
        }


    colleges = []
    universities = []
    malls = []
    supermarkets = []


    for element in data.get("elements", []):

        tags = element.get("tags", {})

        latitude_value = element.get("lat")
        longitude_value = element.get("lon")

        if latitude_value is None or longitude_value is None:
            continue


        place = {
            "id": element["id"],
            "name": tags.get("name", "Unnamed"),
            "latitude": latitude_value,
            "longitude": longitude_value
        }


        # College
        if tags.get("amenity") == "college":

            colleges.append(place)


        # University
        elif tags.get("amenity") == "university":

            universities.append(place)


        # Mall
        elif tags.get("shop") == "mall":

            malls.append(place)


        # Supermarket
        elif tags.get("shop") == "supermarket":

            supermarkets.append(place)


    return {
        "colleges": colleges,
        "universities": universities,
        "malls": malls,
        "supermarkets": supermarkets,
        "offices": []
    }