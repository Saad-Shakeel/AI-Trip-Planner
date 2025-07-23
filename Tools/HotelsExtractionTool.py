from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from Prompts.prompts import HOTELS_PROMPT
import requests
import queue
import ast
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

hotel_queue = queue.Queue()

def get_place_details(place):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={place}&key={GOOGLE_API_KEY}"
    response = requests.get(url).json()
    print(f"GET {place} Details\n\n")
    return response.get("results", [])[:1]  # Get top result

def fetching_images(keys_list: list, values_list:list) -> queue: 
    """Use this tool to return the images of the hotels.
    
    Args:
        keys_list: list of hotel name.
        values_list: list of description of the hotel.
    """
    # print("tourist_places function called")
    # print("==================================================\n")
    # Convert string to list if needed
    places = keys_list.split(",") if isinstance(keys_list, str) else keys_list
    description = values_list.split(",") if isinstance(values_list, str) else values_list
    # print("tourist places:: ",places)
    # print("tourist description:: ",description)
    # print("==================================================\n")
    images_data = []
    for desc , place in zip(description ,places):
        # place = place.strip()  # Remove extra spaces
        place_data = get_place_details(place)
        # print("Place in Loop:: ",place)
        if place_data:
            # print("Place data:: ",place_data)
            place_info = place_data[0]
            
            # Extract image URL if available
            if "photos" in place_info and place_info["photos"]:
                photo_ref = place_info["photos"][0]["photo_reference"]
                image_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={GOOGLE_API_KEY}"
            else:
                image_url = "https://via.placeholder.com/200x130?text=No+Image"

            # Extract Google Place link if available
            place_link = place_info.get("url", f"https://www.google.com/search?q={place}")

            images_data.append({
                "name": place_info.get("name", place),  # Use `place` as fallback
                "address": desc,
                "image_url": image_url,
                "link": place_link
            })
    # print(images_data)
    return hotel_queue.put(images_data)


def display_hotel_places(hotel_dict: dict):
    """
    Display hotel places for the given landmarks.

    Args:
        hotel_dict: That contain Hotels as key and their discription as values.

    Returns:
        - List of hotel names.
        - List of hotel discriptions.
    """
    # print("display_tourist_places :: ", hotel_dict)
    # print("==================================================\n")
    keys_list = list(hotel_dict.keys())
    values_list = list(hotel_dict.values())
    # print("List of places",keys_list)
    # print("==================================================\n")
    # print("List of places",values_list)
    # print("==================================================\n")
    fetching_images(keys_list,values_list)

@tool(name_or_callable="hotel_extraction")
def hotel_extraction(query: str) -> dict:
    """Use this tool for generating hotels near the provided landmark extracting the Hotel name and description from the text."""
    model = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0)
    
    # Define prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", HOTELS_PROMPT),
        ("human", "{input}")
    ])

    # Create chain and invoke it with user input
    chain = prompt | model
    response = chain.invoke({"input": query})
    result = response.content

    try:
        hotel_dict = ast.literal_eval(result.strip())
        print("Parsed dictionary:", hotel_dict)
        print("==================================================\n")
        display_hotel_places(hotel_dict)
        return hotel_dict.keys()
    except Exception as e:
        return {"error": f"Failed to parse dictionary. Raw Output: {result}"}
    


