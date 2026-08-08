import requests


OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def get_restaurants(latitude, longitude, radius=5000):          #5km

    query = f"""
    [out:json][timeout:30];

    nwr["amenity"="restaurant"]
    (around:{radius},{latitude},{longitude});

    out center;
    """

    headers = {
        "User-Agent": "DineMapAI/1.0 (hackathon project)"
    }

    response = requests.post(
        OVERPASS_URL,
        data=query,
        headers=headers,
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    restaurants = []

    for element in data.get("elements", []):

        tags = element.get("tags", {})

        lat = element.get("lat")
        lon = element.get("lon")

        if lat is None or lon is None:
            center = element.get("center", {})
            lat = center.get("lat")
            lon = center.get("lon")

        if lat is not None and lon is not None:
            restaurants.append({
                "id": element["id"],
                "name": tags.get("name", "Unnamed Restaurant"),
                "latitude": lat,
                "longitude": lon,
                "tags": tags
            })

    return restaurants