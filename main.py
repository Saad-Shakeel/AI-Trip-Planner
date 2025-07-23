import streamlit as st
from streamlit.components.v1 import html
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
import queue
import time
from dotenv import load_dotenv
import os

# Tools
from Tools.LandmarksExtractionTool import landmarks_extraction, image_queue
from Tools.HotelsExtractionTool import hotel_extraction, hotel_queue
from Tools.MapTool import map_tool
from Tools.GoogleGmailTool import gmail_tool
from Tools.RestaurantsTool import get_top_food_spots_near_place
from Prompts.prompts import SYSTEM_PROMPT

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize memory for conversation context.
memory = MemorySaver()

st.set_page_config(
    page_title="Trip Planner Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)
  

# # Initialize the LLM using Google’s Generative AI.
# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.0-flash",
#     temperature=0,
#     max_retries=1,
#     api_key= GEMINI_API_KEY,
# )

llm = ChatGroq(model="deepseek-r1-distill-llama-70b", temperature = 0)
# List of tools available to the agent.
tools = [
    landmarks_extraction,
    get_top_food_spots_near_place,
    map_tool,
    gmail_tool,
    hotel_extraction,
]

# Create the agent executor with the system prompt and memory.
agent_executor = create_react_agent(
    prompt=SYSTEM_PROMPT,
    model=llm,
    tools=tools,
    debug=True,
    checkpointer=memory,
)

# ===== Streamlit Interface =====

st.markdown("""
    <style>
        .title { font-size: 42px; font-weight: bold; color: #defcf9; text-align: center; margin-bottom: 10px; }
        .subtitle { font-size: 22px; color: #e5eaf5; text-align: center; margin-bottom: 20px;}
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🌍 AI Trip Planner</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Your smart travel assistant for a perfect journey ✈️🏨🌎</div>', unsafe_allow_html=True)

# Initialize conversation history in session state.
if "messages" not in st.session_state:
    st.session_state.messages = []  # List of dicts: {"role": "user"/"assistant", "content": message_text}


with st.chat_message("assistant"):
    st.write("Hey there! Ready to plan your next adventure? 🌍✈️ Tell me where you want to go, and I'll craft the perfect itinerary just for you!")


# Display previous chat messages.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("images"):
            cols = st.columns(min(5, len(message["images"])))
            for idx, image in enumerate(message["images"]):
                with cols[idx % len(cols)]:
                    st.markdown(
                        f"""
                        <div class="place-card">
                            <img src="{image['image_url']}" class="place-img">
                            <p class="place-name">{image['name']}</p>
                            <p class="place-details">
                                {image['address']}<br>
                                <a href="{image['link']}" target="_blank" class="more-info">More Details</a>
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
# Accept user input.
if user_input := st.chat_input("What trip planning details do you need?"):
    # Display and store the user message.
    st.session_state.messages.append({"role": "user", "content": user_input, "images": []})
        
    with st.chat_message("user"):
        st.markdown(user_input)
    
    conversation = [(msg["role"], msg["content"]) for msg in st.session_state.messages if msg["role"] in ("user", "assistant")]
    
    # Call the agent executor and stream the response.
    config = {"configurable": {"thread_id": "1"}}
    events = agent_executor.stream(
        {"messages": conversation},
        stream_mode="values",
        config=config
    )
    
    final_response = ""
    streamed = ""
    images_data = []
    with st.spinner("🔍 Analyzing your request..."):
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            for event in events:
                final_response = event["messages"][-1].content  
                        
            # response_placeholder.markdown(final_response + "▌")
            # time.sleep(0.05)
        for word in final_response.split(" "):
                streamed += word + " "
                response_placeholder.markdown(streamed + "▌")
                time.sleep(0.03)
        
        # Display the images in the main thread
        st.markdown("""
                        <style>
                            .place-card {
                                position: relative;
                                width: 220px;
                                text-align: center;
                                padding: 10px;
                                background-color: #1e1e1e;
                                border-radius: 12px;
                                box-shadow: 0px 4px 10px rgba(255, 255, 255, 0.1);
                                transition: transform 0.3s ease-in-out;
                                display: flex;
                                flex-direction: column;
                                align-items: center;
                                justify-content: flex-start;
                            }
                            .place-card:hover {
                                transform: scale(1.05);
                            }
                            .place-img {
                                width: 100%;
                                height: 140px;
                                border-radius: 10px;
                                object-fit: cover;
                                margin-bottom: 10px;
                            }
                            .place-info {
                                width: 100%;
                                text-align: center;
                            }
                            .place-name {
                                color: white;
                                font-size: 14px;
                                font-weight: bold;
                            }
                            .place-details {
                                font-size: 12px;
                                color: #ddd;
                                margin-top: 5px;
                            }
                            .more-info {
                                font-size: 11px;
                                color: #1e90ff;
                                text-decoration: none;
                                font-weight: bold;
                            }
                            .more-info:hover {
                                text-decoration: underline;
                            }
                        </style>
                        """, unsafe_allow_html=True)
        
        while True:
            try:
                try:
                    images = image_queue.get(timeout=1)
                    print("Got data from image_queue")
                except queue.Empty:
                    images = hotel_queue.get(timeout=1)
                    print("Got data from hotel_queue")
                if images:
                    print("Fetching...")
                    images_data.extend(images)
                    cols = st.columns(min(5, len(images)))
                    for idx, image in enumerate(images):
                        with cols[idx % len(cols)]:
                            st.markdown(
                                f"""
                                <div class="place-card">
                                    <img src="{image['image_url']}" class="place-img">
                                    <p class="place-name">{image['name']}</p>
                                    <p class="place-details">
                                        {image['address']}<br>
                                        <a href="{image['link']}" target="_blank" class="more-info">More Details</a>
                                    </p>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )  
                    print("Images Generated")                    
                else:
                    st.warning("No place data available.")
            except queue.Empty:
                print("Loop Break")
                break
        
    # Store the assistant's response in the conversation history.
    st.session_state.messages.append({"role": "assistant", "content": final_response, "images": images_data})