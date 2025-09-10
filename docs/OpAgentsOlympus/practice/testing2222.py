from dotenv import load_dotenv
from agents import (
    Agent,
    Runner,
    function_tool,
    RunConfig,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
)

load_dotenv()
import os

# Load environment variables
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please define it in your .env file.")

# Setup Gemini client
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Preferred Gemini model setup
model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash", openai_client=external_client
)

# Runner config (you can export this)
config = RunConfig(
    model=model,
    model_provider=external_client,
    # tracing_disabled=True
)


# --------------------------------------------------------
# Enhanced Tool Functions
@function_tool
def get_weather_info(city: str = "Karachi") -> str:
    """Get detailed weather information for a specific city"""
    weather_data = {
        "Karachi": "Temperature: 40°C, Condition: Sunny, Humidity: 65%, Wind: 15 km/h",
        "Lahore": "Temperature: 35°C, Condition: Partly Cloudy, Humidity: 70%, Wind: 10 km/h",
        "Islamabad": "Temperature: 28°C, Condition: Clear, Humidity: 55%, Wind: 8 km/h",
    }
    return weather_data.get(city, f"Weather data not available for {city}")


@function_tool
def get_location_info() -> str:
    """Get current location and timezone information"""
    return "Location: Karachi, Pakistan | Timezone: PKT (UTC+5) | Coordinates: 24.8607° N, 67.0011° E"


@function_tool
def get_medical_info(topic: str) -> str:
    """Provide general medical information about a specific topic (educational purposes only)"""
    medical_info = {
        "diabetes": "Diabetes is a chronic condition affecting blood sugar levels. Common symptoms include increased thirst, frequent urination, and fatigue. Always consult a healthcare provider for diagnosis and treatment.",
        "hypertension": "Hypertension (high blood pressure) is a common condition that can lead to heart disease. Symptoms may include headaches, shortness of breath, and nosebleeds. Regular check-ups are important.",
        "asthma": "Asthma is a respiratory condition causing airway inflammation. Symptoms include wheezing, coughing, and chest tightness. Avoid triggers and follow prescribed treatment plans.",
        "headache": "Headaches can have various causes including stress, dehydration, or underlying conditions. Rest, hydration, and pain relievers may help. Seek medical attention for severe or persistent headaches.",
    }
    return medical_info.get(
        topic.lower(),
        f"General information about {topic}: This is for educational purposes only. Please consult a healthcare professional for medical advice.",
    )


@function_tool
def get_general_knowledge(topic: str) -> str:
    """Provide general knowledge information about various topics"""
    knowledge_base = {
        "photosynthesis": "Photosynthesis is the process by which plants convert sunlight, water, and carbon dioxide into glucose and oxygen. This process is essential for life on Earth as it produces oxygen and serves as the foundation of the food chain.",
        "gravity": "Gravity is a fundamental force that attracts objects with mass toward each other. On Earth, it's approximately 9.8 m/s² and keeps us grounded to the planet's surface.",
        "solar_system": "The Solar System consists of the Sun and the objects that orbit it, including 8 planets, dwarf planets, moons, asteroids, and comets. Earth is the third planet from the Sun.",
        "internet": "The Internet is a global network of connected computers that allows information sharing and communication worldwide. It was developed from ARPANET in the 1960s and has revolutionized modern communication.",
    }
    return knowledge_base.get(
        topic.lower(),
        f"General information about {topic}: This is a broad topic that covers various aspects. For specific information, please provide more details.",
    )


# ---------------------------------------------------------------
# Specialized Agents
medicine_agent = Agent(
    model=config.model,
    name="medical-info-agent",
    instructions=(
        "You are a medical information assistant. "
        "You can provide general information about health topics, but do not give medical advice. "
        "Always recommend consulting healthcare professionals for medical decisions. "
        "Use the get_medical_info tool to provide educational information about health topics."
    ),
    tools=[get_medical_info],
)

weather_agent = Agent(
    model=config.model,
    name="weather-agent",
    instructions=(
        "You are a weather information assistant. "
        "Use the get_weather_info and get_location_info tools to provide comprehensive weather information. "
        "Always provide current weather data and location context when available."
    ),
    tools=[get_weather_info, get_location_info],
)

general_knowledge_agent = Agent(
    model=config.model,
    name="general-knowledge-agent",
    instructions=(
        "You are a general knowledge assistant. "
        "You can answer questions about various topics including science, history, geography, and general facts. "
        "Use the get_general_knowledge tool to provide accurate information."
    ),
    tools=[get_general_knowledge],
)

# --------------------------------------------------------
# Main Coordinator Agent
coordinator_agent = Agent(
    model=config.model,
    name="coordinator-agent",
    instructions=(
        "You are a smart coordinator that routes user queries to the most appropriate specialized agent. "
        "Your job is to analyze the user's query and determine which agent should handle it:\n"
        "- For weather-related questions (weather, temperature, climate, location), route to weather_agent\n"
        "- For medical/health questions (symptoms, diseases, medications, health advice), route to medicine_agent\n"
        "- For general knowledge questions (science, history, facts, explanations), route to general_knowledge_agent\n"
        "- For other queries, answer directly if you can, or route to the most appropriate agent\n"
        "Always explain which agent you're routing to and why."
    ),
    handoffs=[weather_agent, medicine_agent, general_knowledge_agent],
)

# -----------------------------------------------------------------------
# Interactive Query System
query = input("Enter your query: ")

result = Runner.run_sync(
    coordinator_agent,
    query,
    # run_config=config
)
print(f"🎯 Agent Used: {result.last_agent.name}")
print(f"📝 Response: {result.final_output}")
print("=" * 60)
