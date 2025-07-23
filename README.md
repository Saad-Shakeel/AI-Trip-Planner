# AI-Trip-Planner

![AI Trip Planner Demo](demo.gif)

## Description

**AI-Trip-Planner** is an intelligent, agentic travel assistant that helps users plan their trips efficiently. Leveraging advanced LLMs (via GROQ and Google APIs) and a suite of specialized tools, it guides users through city selection, itinerary generation, hotel and restaurant recommendations, map route planning, and even shares itineraries via email—all through a conversational, user-friendly Streamlit interface.

---

## Features

- **Conversational Trip Planning**: Interact with an AI agent to plan your trip step-by-step.
- **Smart City & Landmark Selection**: Suggests top tourist places in any city.
- **Personalized Itinerary Generation**: Creates day-wise itineraries with optimal sequencing and meal breaks.
- **Hotel & Restaurant Recommendations**: Finds top-rated hotels and food spots near your destinations.
- **Google Maps Route Planning**: Generates optimized routes and Google Maps links for your trip.
- **Itinerary Sharing via Email**: Sends your itinerary as a professional HTML email using Gmail integration.
- **Visual Experience**: Displays images and details of places and hotels.
- **Agentic Framework**: Modular, tool-based agent using LangGraph and LangChain for robust, extensible reasoning.

---

## How It Works

1. **User starts a conversation** with the AI agent via the Streamlit web interface.
2. The agent collects:
   - City of interest
   - Preferred places to visit
   - Trip duration
3. **Itinerary Generation**: The agent creates a detailed, day-wise plan, including meal breaks and local food recommendations.
4. **Hotel & Restaurant Suggestions**: For each place, the agent can suggest nearby hotels and restaurants.
5. **Route Planning**: Generates Google Maps links for daily routes.
6. **Itinerary Sharing**: Optionally, the agent can send the itinerary to your email using the Gmail tool.

---

## Agentic Framework

This project uses an **agentic framework** built on [LangGraph](https://github.com/langchain-ai/langgraph) and [LangChain](https://github.com/langchain-ai/langchain):
- **Agent Executor**: Orchestrates the conversation, memory, and tool usage.
- **Tools**: Each major function (landmarks, hotels, maps, Gmail, restaurants) is a modular tool, invoked as needed.
- **Memory**: Maintains conversation context for a seamless, multi-turn experience.
- **LLMs**: Uses GROQ-hosted models and optionally Google Gemini for reasoning and content generation.

---

## Project Structure

```
AI-Trip-Planner/
├── main.py                  # Streamlit app and agent orchestration
├── requirements.txt         # Python dependencies
├── demo.gif                 # Demo video
├── Prompts/
│   └── prompts.py           # System and tool prompt templates
├── Tools/
│   ├── GoogleGmailTool.py   # Gmail tool for sending emails
│   ├── HotelsExtractionTool.py # Hotel search and image fetching
│   ├── LandmarksExtractionTool.py # Landmark search and image fetching
│   ├── MapTool.py           # Google Maps route generation
│   └── RestaurantsTool.py   # Restaurant/food spot search
└── .streamlit/
    └── config.toml          # Streamlit UI theme config
```

---

## Prerequisites

- Python 3.8+
- [pip](https://pip.pypa.io/en/stable/)
- [GROQ API Key](https://console.groq.com/keys)
- [Google Cloud Platform Project & API Key](https://console.cloud.google.com/)
- Gmail API credentials (OAuth 2.0 client)

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Saad-Shakeel/AI-Trip-Planner.git
   cd AI-Trip-Planner
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up environment variables:**
   - Create a `.env` file in the root directory:
     ```env
     GROQ_API_KEY=your_groq_api_key_here
     GOOGLE_API_KEY=your_google_api_key_here
     ```

---

## API Key Setup

### 1. GROQ API Key
- Sign up at [GROQ Console](https://console.groq.com/).
- Go to **API Keys** and create a new key.
- Add it to your `.env` file as `GROQ_API_KEY`.

### 2. Google API Key (for Maps, Places, Gmail)
- Go to [Google Cloud Console](https://console.cloud.google.com/).
- Create a new project (or use an existing one).
- Enable the following APIs:
  - **Maps JavaScript API**
  - **Places API**
  - **Gmail API**
- Go to **APIs & Services > Credentials** and create an **API Key**.
- Add it to your `.env` file as `GOOGLE_API_KEY`.

---

## Gmail Tool Setup

To send emails, you need OAuth 2.0 credentials for the Gmail API:

1. In [Google Cloud Console](https://console.cloud.google.com/):
   - Go to **APIs & Services > Credentials**.
   - Click **Create Credentials > OAuth client ID**.
   - Choose **Desktop app**.
   - Download the `credentials.json` file and place it in `Tools/Credentials.json`.

2. **First-time Gmail Tool Use:**
   - When you use the Gmail tool for the first time, a link will be printed in the console.
   - Open the link in your browser, log in to your Gmail account, and grant access.
   - This will generate a `token.json` file in the `Tools/` directory for future use.

**Note:** The Gmail tool is only used when you choose to share your itinerary via email.

---

## Running the App

```bash
streamlit run main.py
```

- Open the provided local URL in your browser.
- Start chatting with the AI Trip Planner!

---

## Acknowledgments

This work is a part of [ATS](https://atsailab.com)'s projects catalog.

