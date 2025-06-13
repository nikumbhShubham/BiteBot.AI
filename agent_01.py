import json
import asyncio
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import requests
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import cohere
from typing_extensions import TypedDict
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration class for API keys and settings
class Config:
    def __init__(self):
        # Load from environment variables for security
        self.COHERE_API_KEY = os.getenv('COHERE_API_KEY')
        self.OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')  # Get free key from openweathermap.org
        
        # Validate required API keys
        if not self.COHERE_API_KEY:
            logger.warning("COHERE_API_KEY not found in environment variables")
            self.COHERE_API_KEY = "demo-key-replace-with-real"
        
        if not self.OPENWEATHER_API_KEY:
            logger.warning("OPENWEATHER_API_KEY not found in environment variables")
            self.OPENWEATHER_API_KEY = "demo-key-replace-with-real"
    
    def is_demo_mode(self) -> bool:
        """Check if we're running in demo mode with fake keys"""
        return (self.COHERE_API_KEY == "demo-key-replace-with-real" or 
                self.OPENWEATHER_API_KEY == "demo-key-replace-with-real")

# Initialize configuration
config = Config()

# Initialize Cohere client with error handling
try:
    if not config.is_demo_mode():
        co = cohere.Client(config.COHERE_API_KEY)
    else:
        co = None
        logger.info("Running in demo mode - AI features will use fallback data")
except Exception as e:
    logger.error(f"Failed to initialize Cohere client: {e}")
    co = None

# Data Models
@dataclass
class UserProfile:
    user_id: str
    location: str
    dietary_preferences: List[str]
    cuisine_history: List[str]
    price_range: str

class AgentState(TypedDict):
    """State for the recommendation agent"""
    user_id: str
    location: str
    weather: Optional[Dict[str, Any]]
    festivals: Optional[Dict[str, Any]]
    trends: Optional[Dict[str, Any]]
    recommendations: Optional[List[Dict[str, Any]]]
    final_recommendations: Optional[List[Dict[str, Any]]]
    current_month: Optional[str]
    error_messages: Optional[List[str]]

# Weather API Integration
class WeatherService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    def get_weather_data(self, location: str) -> Dict[str, Any]:
        """Get real weather data from OpenWeatherMap API"""
        if config.is_demo_mode():
            return self._get_demo_weather_data()
        
        try:
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant weather information
            weather_info = {
                "condition": data['weather'][0]['main'].lower(),
                "description": data['weather'][0]['description'],
                "temperature": round(data['main']['temp']),
                "feels_like": round(data['main']['feels_like']),
                "humidity": data['main']['humidity'],
                "city": data['name'],
                "country": data['sys']['country']
            }
            
            # Add food suggestions based on weather
            weather_info["food_suggestions"] = self._get_weather_based_suggestions(
                weather_info["condition"], 
                weather_info["temperature"]
            )
            
            logger.info(f"Successfully fetched weather for {location}: {weather_info['condition']}, {weather_info['temperature']}°C")
            return weather_info
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch weather data: {e}")
            return self._get_fallback_weather_data(location)
        except KeyError as e:
            logger.error(f"Unexpected weather API response format: {e}")
            return self._get_fallback_weather_data(location)
    
    def _get_weather_based_suggestions(self, condition: str, temperature: int) -> List[str]:
        """Get food suggestions based on weather conditions"""
        suggestions = []
        
        # Temperature-based suggestions
        if temperature < 15:
            suggestions.extend(["hot soup", "tea", "warm beverages", "comfort food"])
        elif temperature > 30:
            suggestions.extend(["cold drinks", "ice cream", "light salads", "fresh juices"])
        else:
            suggestions.extend(["balanced meals", "fresh food"])
        
        # Condition-based suggestions
        condition_map = {
            "rain": ["pakoras", "chai", "hot snacks", "soup"],
            "drizzle": ["hot beverages", "fried snacks"],
            "clear": ["fresh juice", "salads", "grilled items"],
            "clouds": ["comfort food", "warm meals"],
            "snow": ["hot chocolate", "warm soup", "hearty meals"],
            "thunderstorm": ["comfort food", "hot beverages"]
        }
        
        if condition in condition_map:
            suggestions.extend(condition_map[condition])
        
        return list(set(suggestions))  # Remove duplicates
    
    def _get_demo_weather_data(self) -> Dict[str, Any]:
        """Demo weather data for testing"""
        return {
            "condition": "clear",
            "description": "clear sky",
            "temperature": 28,
            "feels_like": 30,
            "humidity": 65,
            "city": "Mumbai",
            "country": "IN",
            "food_suggestions": ["fresh juice", "salads", "grilled items"]
        }
    
    def _get_fallback_weather_data(self, location: str) -> Dict[str, Any]:
        """Fallback weather data when API fails"""
        return {
            "condition": "pleasant",
            "description": "pleasant weather",
            "temperature": 25,
            "feels_like": 27,
            "humidity": 70,
            "city": location,
            "country": "Unknown",
            "food_suggestions": ["balanced meals", "seasonal favorites"]
        }

# Enhanced AI Service with better error handling
class AIService:
    def __init__(self, cohere_client):
        self.co = cohere_client
    
    def get_festival_foods(self, month: str, location: str = "India") -> Dict[str, Any]:
        """Get festival foods using AI with proper error handling"""
        if not self.co:
            return self._get_fallback_festival_data(month, location)
        
        prompt = f"""
        List the major festivals celebrated in {location} during {month}. 
        For each festival, provide traditional foods that are commonly ordered online.
        
        Return ONLY valid JSON in this exact format:
        {{
            "festivals": [
                {{
                    "name": "festival_name",
                    "date_range": "approximate dates",
                    "foods": ["food1", "food2", "food3"],
                    "popular_orders": ["dish1", "dish2"],
                    "significance": "brief description"
                }}
            ]
        }}
        
        Focus only on major festivals that significantly impact food ordering patterns.
        If no major festivals in {month}, return empty festivals array.
        """
        
        try:
            response = self.co.generate(
                model='command',
                prompt=prompt,
                max_tokens=600,
                temperature=0.2
            )
            
            text = response.generations[0].text.strip()
            # Add this before the JSON parsing to see what the API is actually returning
            logger.debug(f"Raw API response: {response.generations[0].text}")
            
            # Clean up the response to extract JSON
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            elif text.startswith('{') or text.startswith('['):
                # Already looks like JSON
                pass
            else:
        # Try to find JSON within the text
                try:
                    start = text.find('{')
                    end = text.rfind('}') + 1
                    if start != -1 and end != -1:
                        text = text[start:end]
                except:
                    pass
            
            # Try to parse JSON
            result = json.loads(text)
            
            # Validate structure
            if 'festivals' in result and isinstance(result['festivals'], list):
                logger.info(f"Successfully fetched {len(result['festivals'])} festivals for {month}")
                return result
            else:
                raise ValueError("Invalid festival data structure")
                
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse festival data: {e}")
            return self._get_fallback_festival_data(month, location)
        except Exception as e:
            logger.error(f"Cohere API error for festivals: {e}")
            return self._get_fallback_festival_data(month, location)
    
    def analyze_food_trends(self, location: str, season: str, weather: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze food trends using AI"""
        if not self.co:
            return self._get_fallback_trends_data()
    
        weather_desc = f"{weather.get('condition', 'pleasant')} weather, {weather.get('temperature', 25)}°C"
    
        prompt = f"""You are an expert food trend analyst. Analyze current food ordering trends for {location} during {season} season with {weather_desc}.

        Return ONLY valid JSON in this exact format:
        {{
        "trending_cuisines": ["cuisine1", "cuisine2", "cuisine3"],
        "weather_foods": ["food1", "food2", "food3"],
        "seasonal_specialties": ["dish1", "dish2", "dish3"],
        "order_patterns": {{
            "breakfast": ["item1", "item2"],
            "lunch": ["item1", "item2"],
            "dinner": ["item1", "item2"],
            "snacks": ["item1", "item2"]
        }},
        "trending_reasons": {{
            "weather": "brief explanation",
            "season": "brief explanation"
        }}
    }}

        Example valid response:
        {{
            "trending_cuisines": ["Indian", "Italian", "Chinese"],
            "weather_foods": ["soup", "hot beverages", "comfort food"],
            "seasonal_specialties": ["monsoon thali", "pakoras", "masala chai"],
            "order_patterns": {{
                "breakfast": ["poha", "upma"],
                "lunch": ["thali", "biriyani"],
                "dinner": ["curry", "naan"],
                "snacks": ["pakoras", "samosa"]
            }},
            "trending_reasons": {{
                "weather": "People prefer warm comfort food during rainy season",
                "season": "Monsoon brings cravings for fried snacks and hot beverages"
            }}
        }}

        Focus on realistic, popular food items available in {location}. Return ONLY the JSON object, no additional text or commentary.
        """
    
        try:
            response = self.co.generate(
                model='command',
                prompt=prompt,
                max_tokens=800,
                temperature=0.3
            )
        
            text = response.generations[0].text.strip()
            logger.debug(f"Raw trends API response: {text}")  # Debug logging
        
        # Enhanced JSON extraction
            try:
                # Try to find JSON in the response
                start = text.find('{')
                end = text.rfind('}') + 1
                if start != -1 and end != -1:
                    json_text = text[start:end]
                    result = json.loads(json_text)
                else:
                    raise ValueError("No JSON found in response")
                
            # Validate structure
                required_keys = ['trending_cuisines', 'weather_foods', 'seasonal_specialties', 'order_patterns']
                if not all(key in result for key in required_keys):
                    raise ValueError("Missing required keys in response")
                
                logger.info(f"Successfully analyzed trends for {location}")
                return result
            
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse trends data: {e}\nResponse was: {text}")
                return self._get_fallback_trends_data()
            
        except Exception as e:
            logger.error(f"Cohere API error for trends: {e}")
            return self._get_fallback_trends_data()
    
    def generate_personalized_recommendations(self, user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate personalized recommendations using AI"""
        if not self.co:
            return self._get_fallback_recommendations()
    
        prompt = f"""You are an expert food recommendation system. Generate 5 personalized food recommendations for {user_context.get('location', 'Mumbai')} based on:

        Weather: {user_context.get('weather', {}).get('description', 'pleasant')}, {user_context.get('weather', {}).get ('temperature', 25)}°C
        Current trends: {json.dumps(user_context.get('trends', {}), indent=2)}
        Festivals: {json.dumps(user_context.get('festivals', {}), indent=2)}
        Time: {user_context.get('time_of_day', 'afternoon')}

    Return ONLY a valid JSON array in this exact format:
    [
        {{
            "dish_name": "specific dish name",
            "cuisine": "cuisine type",
            "reason": "why this recommendation fits the context",
            "confidence": 0.85,
            "tags": ["tag1", "tag2", "tag3"],
            "price_range": "budget/mid/premium",
            "meal_type": "breakfast/lunch/dinner/snack"
        }}
    ]

    Example valid response:
    [
        {{
            "dish_name": "Butter Chicken",
            "cuisine": "North Indian",
            "reason": "Rich and flavorful, perfect for the current weather",
            "confidence": 0.9,
            "tags": ["non-veg", "comfort-food", "popular"],
            "price_range": "mid",
            "meal_type": "dinner"
        }},
        {{
            "dish_name": "Masala Dosa",
            "cuisine": "South Indian",
            "reason": "Light yet satisfying, great for the current time of day",
            "confidence": 0.85,
            "tags": ["vegetarian", "breakfast", "popular"],
            "price_range": "budget",
            "meal_type": "breakfast"
        }}
    ]

    Make recommendations specific, realistic, and available for food delivery. Consider weather, local preferences, and current trends. Return ONLY the JSON array, no additional text or commentary.
    """
    
        try:
            response = self.co.generate(
                model='command',
                prompt=prompt,
                max_tokens=1000,
                temperature=0.4
            )
        
            text = response.generations[0].text.strip()
            logger.debug(f"Raw recommendations API response: {text}")  # Debug logging
        
        # Enhanced JSON extraction
            try:
            # Try to find JSON array in the response
                start = text.find('[')
                end = text.rfind(']') + 1
                if start != -1 and end != -1:
                    json_text = text[start:end]
                    result = json.loads(json_text)
                else:
                    raise ValueError("No JSON array found in response")
                
            # Validate structure
                if not isinstance(result, list):
                    raise ValueError("Expected array but got something else")
                if len(result) == 0:
                    raise ValueError("Empty recommendations array")
                
                logger.info(f"Generated {len(result)} personalized recommendations")
                return result
            
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse recommendations: {e}\nResponse was: {text}")
                return self._get_fallback_recommendations()
            
        except Exception as e:
            logger.error(f"Cohere API error for recommendations: {e}")
            return self._get_fallback_recommendations()
        
    
    def explain_recommendation(self, recommendation: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate explanation for a recommendation"""
        if not self.co:
            return self._get_fallback_explanation(recommendation)
        
        prompt = f"""
        Explain why we recommended "{recommendation.get('dish_name', 'this dish')}" to the user.
        
        Context:
        - Weather: {context.get('weather', {}).get('description', 'pleasant')}
        - Location: {context.get('location', 'your area')}
        - Current trends: {context.get('trends', {}).get('trending_cuisines', [])}
        - Festivals: {[f['name'] for f in context.get('festivals', {}).get('festivals', [])]}
        
        Provide a friendly, 1-2 sentence explanation that helps the user understand 
        why this food item is perfect for them right now.
        
        Start with "Perfect choice because..." and keep it conversational and specific.
        """
        
        try:
            response = self.co.generate(
                model='command',
                prompt=prompt,
                max_tokens=150,
                temperature=0.3
            )
            
            explanation = response.generations[0].text.strip()
            return explanation if explanation else self._get_fallback_explanation(recommendation)
            
        except Exception as e:
            logger.error(f"Failed to generate explanation: {e}")
            return self._get_fallback_explanation(recommendation)
    
    def _get_fallback_festival_data(self, month: str, location: str) -> Dict[str, Any]:
        """Fallback festival data"""
        # Simple month-based festival mapping for India
        festival_map = {
            "January": [{"name": "Makar Sankranti", "foods": ["til gur", "kheer", "pongal"], "popular_orders": ["sweet boxes", "traditional meals"]}],
            "February": [{"name": "Vasant Panchami", "foods": ["yellow sweets", "saffron dishes"], "popular_orders": ["mithai", "festive meals"]}],
            "March": [{"name": "Holi", "foods": ["gujiya", "thandai", "sweets"], "popular_orders": ["holi sweets", "festive snacks"]}],
            "April": [{"name": "Ram Navami", "foods": ["prasad", "fruits", "vegetarian meals"], "popular_orders": ["satvik food", "fruits"]}],
            "August": [{"name": "Krishna Janmashtami", "foods": ["makhan", "sweets", "fruits"], "popular_orders": ["festive sweets", "milk products"]}],
            "September": [{"name": "Ganesh Chaturthi", "foods": ["modak", "laddu", "sweets"], "popular_orders": ["modak", "festive sweets"]}],
            "October": [{"name": "Dussehra", "foods": ["sweets", "festive meals"], "popular_orders": ["celebration meals", "sweets"]}],
            "November": [{"name": "Diwali", "foods": ["mithai", "dry fruits", "festive meals"], "popular_orders": ["diwali sweets", "gift boxes"]}]
        }
        
        return {
            "festivals": festival_map.get(month, [])
        }
    
    def _get_fallback_trends_data(self) -> Dict[str, Any]:
        """Fallback trends data"""
        return {
            "trending_cuisines": ["Indian", "Chinese", "Italian", "South Indian"],
            "weather_foods": ["comfort food", "seasonal favorites"],
            "seasonal_specialties": ["local dishes", "traditional meals"],
            "order_patterns": {
                "breakfast": ["paratha", "idli", "poha"],
                "lunch": ["rice meals", "roti sabzi", "biryani"],
                "dinner": ["dal rice", "noodles", "pizza"],
                "snacks": ["samosa", "pakora", "chai"]
            }
        }
    
    def _get_fallback_recommendations(self) -> List[Dict[str, Any]]:
        """Fallback recommendations"""
        return [
            {
                "dish_name": "Butter Chicken with Naan",
                "cuisine": "North Indian",
                "reason": "Popular comfort food perfect for any weather",
                "confidence": 0.85,
                "tags": ["comfort", "popular", "non-veg"],
                "price_range": "mid",
                "meal_type": "dinner"
            },
            {
                "dish_name": "Vegetable Biryani",
                "cuisine": "Indian",
                "reason": "Aromatic rice dish loved by everyone",
                "confidence": 0.80,
                "tags": ["vegetarian", "aromatic", "filling"],
                "price_range": "mid",
                "meal_type": "lunch"
            },
            {
                "dish_name": "Margherita Pizza",
                "cuisine": "Italian",
                "reason": "Classic favorite that never disappoints",
                "confidence": 0.75,
                "tags": ["vegetarian", "cheesy", "popular"],
                "price_range": "mid",
                "meal_type": "dinner"
            }
        ]
    
    def _get_fallback_explanation(self, recommendation: Dict[str, Any]) -> str:
        """Fallback explanation"""
        dish_name = recommendation.get('dish_name', 'this dish')
        return f"Perfect choice because {dish_name} is a popular favorite that matches current preferences and trends!"

# Main Smart Food Agent
class SmartFoodAgent:
    def __init__(self):
        self.weather_service = WeatherService(config.OPENWEATHER_API_KEY)
        self.ai_service = AIService(co)
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build the recommendation workflow graph"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("gather_data", self._gather_data)
        workflow.add_node("analyze_trends", self._analyze_trends)
        workflow.add_node("generate_recommendations", self._generate_recommendations)
        workflow.add_node("add_explanations", self._add_explanations)
        
        # Set entry point and edges
        workflow.set_entry_point("gather_data")
        workflow.add_edge("gather_data", "analyze_trends")
        workflow.add_edge("analyze_trends", "generate_recommendations")
        workflow.add_edge("generate_recommendations", "add_explanations")
        workflow.add_edge("add_explanations", END)
        
        return workflow.compile()
    
    def _gather_data(self, state: AgentState) -> AgentState:
        """Gather weather and festival data"""
        logger.info("📊 Gathering contextual data...")
        
        location = state.get("location", "Mumbai")
        current_month = datetime.now().strftime("%B")
        errors = []
        
        # Get weather data
        try:
            weather = self.weather_service.get_weather_data(location)
            logger.info(f"🌤️ Weather: {weather.get('condition')} at {weather.get('temperature')}°C")
        except Exception as e:
            logger.error(f"Failed to fetch weather: {e}")
            weather = self.weather_service._get_fallback_weather_data(location)
            errors.append("Weather data unavailable")
        
        # Get festival data
        try:
            festivals = self.ai_service.get_festival_foods(current_month, location)
            festival_count = len(festivals.get('festivals', []))
            logger.info(f"🎉 Found {festival_count} festivals for {current_month}")
        except Exception as e:
            logger.error(f"Failed to fetch festivals: {e}")
            festivals = {"festivals": []}
            errors.append("Festival data unavailable")
        
        # Update state
        state.update({
            "weather": weather,
            "festivals": festivals,
            "current_month": current_month,
            "error_messages": errors
        })
        
        return state
    
    def _analyze_trends(self, state: AgentState) -> AgentState:
        """Analyze food trends"""
        logger.info("📈 Analyzing food trends...")
        
        location = state.get("location", "Mumbai")
        weather = state.get("weather", {})
        season = self._get_season()
        
        try:
            trends = self.ai_service.analyze_food_trends(location, season, weather)
            trending_cuisines = trends.get('trending_cuisines', [])
            logger.info(f"🔥 Trending cuisines: {', '.join(trending_cuisines[:3])}")
        except Exception as e:
            logger.error(f"Failed to analyze trends: {e}")
            trends = self.ai_service._get_fallback_trends_data()
            if state.get("error_messages"):
                state["error_messages"].append("Trend analysis unavailable")
        
        state["trends"] = trends
        return state
    
    def _generate_recommendations(self, state: AgentState) -> AgentState:
        """Generate personalized recommendations"""
        logger.info("🎯 Generating personalized recommendations...")
        
        # Prepare context for AI
        context = {
            "location": state.get("location", "Mumbai"),
            "weather": state.get("weather", {}),
            "festivals": state.get("festivals", {}),
            "trends": state.get("trends", {}),
            "time_of_day": self._get_time_of_day()
        }
        
        try:
            recommendations = self.ai_service.generate_personalized_recommendations(context)
            logger.info(f"✨ Generated {len(recommendations)} recommendations")
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {e}")
            recommendations = self.ai_service._get_fallback_recommendations()
            if state.get("error_messages"):
                state["error_messages"].append("AI recommendations unavailable")
        
        state["recommendations"] = recommendations
        return state
    
    def _add_explanations(self, state: AgentState) -> AgentState:
        """Add explanations to recommendations"""
        logger.info("💡 Adding explanations...")
        
        recommendations = state.get("recommendations", [])
        context = {
            "weather": state.get("weather", {}),
            "festivals": state.get("festivals", {}),
            "trends": state.get("trends", {}),
            "location": state.get("location", "Mumbai")
        }
        
        for rec in recommendations:
            try:
                explanation = self.ai_service.explain_recommendation(rec, context)
                rec["explanation"] = explanation
            except Exception as e:
                logger.error(f"Failed to generate explanation for {rec.get('dish_name', 'unknown')}: {e}")
                rec["explanation"] = self.ai_service._get_fallback_explanation(rec)
        
        state["final_recommendations"] = recommendations
        logger.info("✅ Processing completed successfully")
        return state
    
    def _get_season(self) -> str:
        """Get current season"""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"  
        elif month in [6, 7, 8, 9]:
            return "monsoon"
        else:
            return "autumn"
    
    def _get_time_of_day(self) -> str:
        """Get current time period"""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    async def recommend_food(self, user_id: str, location: str = "Mumbai",user_message: str = "") -> Dict[str, Any]:
        """Main method to get food recommendations"""
        initial_state: AgentState = {
            "user_id": user_id,
            "location": location or "Mumbai",
            "user_message": user_message, 
            "weather": None,
            "festivals": None,
            "trends": None,
            "recommendations": None,
            "final_recommendations": None,
            "current_month": None,
            "error_messages": []
        }
        
        try:
            logger.info("🔄 Starting recommendation pipeline...")
            result = await self.graph.ainvoke(initial_state)
            
            # Prepare response
            response = {
                "recommendations": result.get("final_recommendations", []),
                "context": {
                    "location": result.get("location"),
                    "weather": result.get("weather"),
                    "festivals": result.get("festivals"),
                    "current_month": result.get("current_month")
                },
                "errors": result.get("error_messages", []),
                "timestamp": datetime.now().isoformat(),
                "demo_mode": config.is_demo_mode()
            }
            
            logger.info("✅ Recommendation pipeline completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"❌ Critical error in recommendation pipeline: {e}")
            import traceback
            traceback.print_exc()
            
            # Return emergency fallback
            return {
                "recommendations": self.ai_service._get_fallback_recommendations()[:3],
                "context": {"location": location},
                "errors": [f"System error: {str(e)}"],
                "timestamp": datetime.now().isoformat(),
                "demo_mode": True
            }

# Chat Interface
class FoodChatBot:
    def __init__(self):
        self.agent = SmartFoodAgent()
        self.ai_service = AIService(co)
    
   # In FoodChatBot class
async def chat_about_food(self, user_message: str, location: str = "Mumbai") -> str:
    """Enhanced chat interface with emotional awareness"""
    result = await self.agent.recommend_food(
        user_id="user",
        location=location,
        user_message=user_message  # Critical for context
    )
    
    recommendations = result.get("recommendations", [])
    
    # Build empathetic response
    response = "🍽️ **Here's what I recommend to brighten your day:**\n\n" if any(
        word in user_message.lower() for word in ["sad", "depressed", "lonely"]
    ) else "🍽️ **Here are my recommendations:**\n\n"
    
    for i, rec in enumerate(recommendations[:3], 1):
        response += f"{i}. {rec.get('emoji', '🍛')} **{rec['dish_name']}** ({rec['cuisine']})\n"
        response += f"   💡 {rec.get('reason', 'Perfect for you!')}\n"
        if "comfort" in rec.get("tags", []):
            response += "   🧡 Great for mood boosting\n"
    
    return response

# Usage Examples
async def main():
    """Example usage of the recommendation system"""
    print("🤖 Smart Food Recommendation Agent")
    print("=" * 50)
    
    if config.is_demo_mode():
        print("⚠️  DEMO MODE - Set environment variables for full features:")
        print("   export COHERE_API_KEY='your-cohere-key'")
        print("   export OPENWEATHER_API_KEY='your-weather-key'")
        print()
    
    agent = SmartFoodAgent()
    
    # Get recommendations
    print("Getting recommendations for Mumbai...")
    result = await agent.recommend_food(
        user_id="demo_user",
        location="Mumbai"
    )
    
    # Display results
    recommendations = result.get("recommendations", [])
    context = result.get("context", {})
    
    print(f"\n📍 Location: {context.get('location', 'Unknown')}")
    
    weather = context.get("weather", {})
    if weather:
        print(f"🌤️  Weather: {weather.get('description', 'pleasant')}, {weather.get('temperature', 'comfortable')}°C")
    
    festivals = context.get("festivals", {}).get("festivals", [])
    if festivals:
        print(f"🎉 Festivals: {', '.join([f['name'] for f in festivals])}")
    
    print(f"\n🍽️  **Top Recommendations:**")
    print("-" * 40)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. **{rec['dish_name']}** ({rec['cuisine']})")
        print(f"   💡 {rec.get('explanation', rec.get('reason', ''))}")
        print(f"   🎯 Confidence: {rec.get('confidence', 0.8):.0%}")
        print(f"   💰 Price Range: {rec.get('price_range', 'mid').title()}")
        print(f"   🏷️  Tags: {', '.join(rec.get('tags', []))}")
    
    # Show any errors
    errors = result.get("errors", [])
    if errors:
        print(f"\n⚠️  Notices: {', '.join(errors)}")

async def chat_example():
    """Example of the chat interface"""
    print("\n" + "=" * 50)
    print("🗣️  Food Chat Interface Demo")
    print("=" * 50)
    
    chatbot = FoodChatBot()
    
    test_messages = [
        "I'm hungry, what should I eat?",
        "Something spicy for this weather",
        "What's good for a rainy day?",
        "Tell me about Indian street food",
        "Suggest something healthy"
    ]
    
    for msg in test_messages:
        print(f"\n👤 User: {msg}")
        response = await chatbot.chat_about_food(msg, "Mumbai")
        print(f"🤖 Bot: {response}")
        print("-" * 30)

async def interactive_chat():
    """Interactive chat session"""
    print("\n" + "=" * 50)
    print("🗣️  Interactive Food Chat")
    print("=" * 50)
    print("Type 'quit' to exit, 'help' for commands")
    
    chatbot = FoodChatBot()
    location = "Mumbai"
    
    while True:
        try:
            user_input = input(f"\n👤 You ({location}): ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Thanks for using Smart Food Agent!")
                break
            elif user_input.lower() == 'help':
                print("""
🔧 Available commands:
- Ask for food recommendations: "I'm hungry", "suggest something"
- Change location: "set location Delhi"
- Ask about food: "tell me about pizza"
- General chat about food topics
- 'quit' to exit
                """)
                continue
            elif user_input.lower().startswith('set location'):
                new_location = user_input[12:].strip()
                if new_location:
                    location = new_location
                    print(f"📍 Location updated to: {location}")
                continue
            
            if not user_input:
                continue
            
            response = await chatbot.chat_about_food(user_input, location)
            print(f"🤖 Bot: {response}")
            
        except KeyboardInterrupt:
            print("\n👋 Thanks for using Smart Food Agent!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

# Configuration setup helper
def setup_environment():
    """Helper function to set up environment variables"""
    print("🔧 Environment Setup Helper")
    print("=" * 40)
    
    print("""
To get the most out of this food recommendation system, you'll need API keys:

1. **Cohere API Key** (for AI recommendations):
   - Visit: https://cohere.ai/
   - Sign up for free account
   - Get your API key from dashboard
   - Set: export COHERE_API_KEY='your-key-here'

2. **OpenWeatherMap API Key** (for real weather data):
   - Visit: https://openweathermap.org/api
   - Sign up for free account  
   - Get your API key
   - Set: export OPENWEATHER_API_KEY='your-key-here'

3. **Linux/Mac setup:**
   echo 'export COHERE_API_KEY="your-cohere-key"' >> ~/.bashrc
   echo 'export OPENWEATHER_API_KEY="your-weather-key"' >> ~/.bashrc
   source ~/.bashrc

4. **Windows setup:**
   set COHERE_API_KEY=your-cohere-key
   set OPENWEATHER_API_KEY=your-weather-key

The system will work in demo mode without these keys, but with limited features.
    """)

# Enhanced error handling and monitoring
class SystemMonitor:
    def __init__(self):
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "api_errors": 0,
            "average_response_time": 0
        }
    
    def log_request(self, success: bool, response_time: float, error_type: str = None):
        """Log request metrics"""
        self.metrics["total_requests"] += 1
        
        if success:
            self.metrics["successful_requests"] += 1
        else:
            self.metrics["failed_requests"] += 1
            if error_type:
                self.metrics["api_errors"] += 1
        
        # Update average response time
        current_avg = self.metrics["average_response_time"]
        total = self.metrics["total_requests"]
        self.metrics["average_response_time"] = (
            (current_avg * (total - 1) + response_time) / total
        )
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        total = self.metrics["total_requests"]
        if total == 0:
            return {"status": "ready", "success_rate": 1.0}
        
        success_rate = self.metrics["successful_requests"] / total
        
        return {
            "status": "healthy" if success_rate > 0.8 else "degraded",
            "success_rate": success_rate,
            "total_requests": total,
            "average_response_time": self.metrics["average_response_time"],
            "demo_mode": config.is_demo_mode()
        }

# Global monitor instance
monitor = SystemMonitor()

# Main execution
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart Food Recommendation Agent")
    parser.add_argument("--mode", choices=["demo", "chat", "interactive", "setup"], 
                       default="demo", help="Run mode")
    parser.add_argument("--location", default="Mumbai", help="Default location")
    
    args = parser.parse_args()
    
    if args.mode == "setup":
        setup_environment()
    elif args.mode == "demo":
        asyncio.run(main())
        asyncio.run(chat_example())
    elif args.mode == "chat":
        asyncio.run(chat_example())
    elif args.mode == "interactive":
        asyncio.run(interactive_chat())
    else:
        print("Use --help to see available options")

