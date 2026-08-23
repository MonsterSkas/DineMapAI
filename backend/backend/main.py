from services.osrm import get_route
from services.overpass_resturant import get_restaurants
from services.overpass_transportation import get_transport

from services.nominatim import get_coordinates
from services.overpass_places import get_business_area_data

result = get_coordinates("Salt Lake, Kolkata")

print(result)

lat= 22.590425
long=88.41692

print("-------------------------------------")

restaurants = get_restaurants(
    lat,
    long
)

print("Restaurants:", len(restaurants))
for restaurant in restaurants[:5]:
    print(restaurant)

print("------------------------------------")

transports = get_transport(
    lat,
    long
)
print("Transportation:", len(transports))
for transport in transports[:5]:
    print(transport)

print("------------------------------------")

data = get_business_area_data(
    lat,
    long,
    radius=1000
)


print("\n========================")
print("BUSINESS AREA DATA")
print("========================")

print("Colleges:", len(data["colleges"]))
print("Universities:", len(data["universities"]))
print("Malls:", len(data["malls"]))
print("Supermarkets:", len(data["supermarkets"]))
print("Offices:", len(data["offices"]))


print("\nCOLLEGES")

for i, place in enumerate(data["colleges"], start=1):
    print(
        f"{i}. {place['name']} | "
        f"{place['latitude']}, "
        f"{place['longitude']}"
    )


print("\nUNIVERSITIES")

for i, place in enumerate(data["universities"], start=1):
    print(
        f"{i}. {place['name']} | "
        f"{place['latitude']}, "
        f"{place['longitude']}"
    )


print("\nMALLS")

for i, place in enumerate(data["malls"], start=1):
    print(
        f"{i}. {place['name']} | "
        f"{place['latitude']}, "
        f"{place['longitude']}"
    )


print("\nSUPERMARKETS")

for i, place in enumerate(data["supermarkets"], start=1):
    print(
        f"{i}. {place['name']} | "
        f"{place['latitude']}, "
        f"{place['longitude']}"
    )


print("\nOFFICES")

for i, place in enumerate(data["offices"], start=1):
    print(
        f"{i}. {place['name']} | "
        f"{place['office_type']} | "
        f"{place['latitude']}, "
        f"{place['longitude']}"
    )



### Distances 


"""
result = get_route(
    22.5958,
    88.4497,
    22.5904,
    88.4169
)

print(result)
"""
