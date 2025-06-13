# tools.py

from langchain_core.tools import tool
from datetime import datetime
import random

@tool
def get_current_weather(city: str) -> str:
    """Mock tool: returns current weather in a city"""
    return random.choice(["Sunny", "Rainy", "Cloudy", "Humid", "Cool"])

@tool
def get_current_time() -> str:
    """Returns current time and day"""
    return datetime.now().strftime("%A %I:%M %p")

@tool
def get_trending_dishes(city: str) -> list:
    """Returns trending dishes for a city"""
    trends = {
        "Mumbai": ["Pav Bhaji", "Vada Pav", "Misal", "Falooda"],
        "Delhi": ["Chole Bhature", "Momos", "Rajma Chawal"],
        "Bangalore": ["Dosa", "Bisi Bele Bath", "Momos"]
    }
    return random.sample(trends.get(city, []), 3)

# Ensure tool names are explicitly set for LangGraph routing
get_current_weather.name = "get_current_weather"
get_current_time.name = "get_current_time"
get_trending_dishes.name = "get_trending_dishes"

# Export all tools in a list
tools = [get_current_weather, get_current_time, get_trending_dishes]
