from langchain_core.tools import tool, Tool
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import initialize_agent
import re


# LLM setup
llm = ChatGroq(model_name="meta-llama/llama-4-maverick-17b-128e-instruct", temperature=0)


@tool(name_or_callable="maps_tool")
def map_tool(input_text: str) -> str:
    """Use this tool to generate a Google Maps route link for multiple city names.
    Args: input_text: Prompt for route planning.
    """

    def get_lat_lng(city_name: str) -> str | None:
        """
        Uses LLM to return latitude/longitude based on a strict format.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a geo-coordinate assistant. ONLY return latitude and longitude in this format: [value, value]. For example: [34.0151, 71.5249]. Do not explain, do not add text. If the city is invalid or unclear, return 'Invalid city name'."),
            ("human", "{input}")
        ])

        chain = prompt | llm
        response = chain.invoke({"input": city_name})
        response_text = response.content.strip()

        # Extract lat/lng using regex
        match = re.match(r"\[(\-?\d+\.\d+),\s*(\-?\d+\.\d+)\]", response_text)
        if match:
            lat, lon = match.groups()
            return f"{lat},{lon}"
        else:
            return None  # Invalid or malformed response

    def generate_google_maps_directions(city_names: list[str]) -> str:
        """
        Generates a Google Maps directions link with multiple valid coordinates.
        """
        locations = []
        for city in city_names:
            coords = get_lat_lng(city.strip())
            if coords:
                locations.append(coords)

        if len(locations) < 2:
            return "At least two valid locations are required to generate a route."

        base_url = "https://www.google.com/maps/dir/"
        route_url = base_url + "/".join(locations) + "/?travelmode=driving"
        return route_url

    def route_planner_tool(query: str) -> str:
        """
        LangChain tool function: Takes comma-separated city names as input and returns a route link.
        """
        city_list = query.split(",")
        return generate_google_maps_directions(city_list)

    # Create the route generator tool
    route_tool = Tool(
        name="Google Maps Route Generator",
        description="Generates a Google Maps route link for multiple city names (comma-separated).",
        func=route_planner_tool
    )

    # Initialize agent with the tool
    trip_planner_agent = initialize_agent(
        tools=[route_tool],
        llm=llm,
        agent="structured-chat-zero-shot-react-description",
        verbose=True
    )

    # Invoke agent and return result
    response = trip_planner_agent.invoke(input_text)
    return response


# Example usage:
# if __name__ == "__main__":
#     result = map_tool.invoke("Lahore, Islamabad, Naran")
#     print("Route URL:\n", result)
