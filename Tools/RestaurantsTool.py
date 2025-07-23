import requests
from langchain.tools import tool
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_coordinates_from_place(spot_name):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": spot_name,
        "key": GOOGLE_API_KEY
    }
    response = requests.get(url, params=params).json()
    if response["results"]:
        location = response["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    return None, None

def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,rating,vicinity,user_ratings_total,opening_hours,reviews,url",
        "key": GOOGLE_API_KEY
    }
    response = requests.get(url, params=params).json()
    return response.get("result", {})

@tool(name_or_callable="get_top_food_spots_near_place")
def get_top_food_spots_near_place(spot_name : str) -> list:
    """ Use this tool to get the nearby footspot, their address and Google Map link of top 2 food spot near places
    Args:
        spot_name (str): Name of spot
    Returns:
        list : [name, address, google_map_link]
    """
    radius = 5000
    top_n = 4
    lat, lng = get_coordinates_from_place(spot_name)
    if lat is None:
        print(f"Could not find location for '{spot_name}'")
        return []

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": "restaurant",
        "key": GOOGLE_API_KEY
    }

    response = requests.get(url, params=params).json()
    results = response.get("results", [])
    sorted_results = sorted(results, key=lambda x: x.get("rating", 0), reverse=True)

    top_places = []

    for place in sorted_results[:top_n]:
        place_id = place.get("place_id")
        details = get_place_details(place_id)
        hours = details.get("opening_hours", {}).get("weekday_text", [])

        top_places.append({
            "name": details.get("name"),
            "address": details.get("vicinity"),
            "google_maps_url": details.get("url"),
        })

    return top_places



# spot = "Lok Virsa Museum"
# top_restaurants = get_top_food_spots_near_place(spot)

