import requests
from typing import Dict, List

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def get_nearby_places(lat: float, lon: float, radius: int = 1000) -> Dict[str, List[str]]:
    """
    Fetch nearby amenities using OpenStreetMap's Overpass API.
    """
    # Fix 1: Properly check for None instead of falsy values (0.0 is a valid coordinate)
    if lat is None or lon is None:
        return {"hospitals": [], "schools": [], "shopping_centers": []}

    # Fix 2: Use `nwr` (Node, Way, Relation) for compact Overpass queries
    query = f"""
    [out:json][timeout:10];
    (
      nwr["amenity"="hospital"](around:{radius},{lat},{lon});
      nwr["amenity"="school"](around:{radius},{lat},{lon});
      nwr["shop"~"supermarket|mall|department_store"](around:{radius},{lat},{lon});
    );
    out tags center;
    """

    try:
        response = requests.post(OVERPASS_URL, data={"data": query}, timeout=12)
        response.raise_for_status()
        data = response.json()

        hospitals, schools, shopping = set(), set(), set()

        for element in data.get("elements", []):
            tags = element.get("tags", {})
            name = tags.get("name")
            if not name:
                continue

            amenity = tags.get("amenity")
            shop = tags.get("shop")

            if amenity == "hospital":
                hospitals.add(name)
            elif amenity == "school":
                schools.add(name)
            elif shop in ["supermarket", "mall", "department_store"]:
                shopping.add(name)

        return {
            "hospitals": sorted(list(hospitals)),
            "schools": sorted(list(schools)),
            "shopping_centers": sorted(list(shopping))
        }

    except Exception as e:
        print(f"Error fetching OSM data: {e}")
        return {"hospitals": [], "schools": [], "shopping_centers": []}