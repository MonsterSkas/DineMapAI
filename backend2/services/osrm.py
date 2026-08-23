import requests


OSRM_URL = "https://router.project-osrm.org/route/v1/driving"


def get_route(
    start_lat,
    start_lon,
    end_lat,
    end_lon
):

    url = (
        f"{OSRM_URL}/"
        f"{start_lon},{start_lat};"
        f"{end_lon},{end_lat}"
    )

    params = {
        "overview": "false"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if data["code"] != "Ok":
        return None

    route = data["routes"][0]

    return {
        "distance_km": round(
            route["distance"] / 1000,
            2
        ),
        "duration_minutes": round(
            route["duration"] / 60,
            1
        )
    }