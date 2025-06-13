from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
from agent_01 import SmartFoodAgent, FoodChatBot, Config
from agent_02 import DealAgent, AgentState
import os
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize agents
config = Config()
food_agent = SmartFoodAgent()
food_chatbot = FoodChatBot()
deal_agent = DealAgent()

def run_async(coro):
    """Helper function to run async coroutines in Flask"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

@app.route('/api/food/recommendations', methods=['POST'])
def get_food_recommendations():
    """
    Endpoint for food recommendations (from agent_01)
    Now using sync wrapper for async function
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'default_user')
        location = data.get('location', 'Mumbai')
        
        result = run_async(food_agent.recommend_food(user_id, location))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/food/chat', methods=['POST'])
def chat_about_food():
    """
    Enhanced endpoint for food chat with better demo mode handling
    """
    try:
        data = request.get_json()
        message = data.get('message', '')
        location = data.get('location', 'Mumbai')
        
        # Create a simple response if in demo mode
        if config.is_demo_mode():
            sample_responses = [
                f"In {location}, people are loving North Indian cuisine today. Try butter chicken!",
                f"Based on weather in {location}, I recommend light salads or fresh juices.",
                f"Popular in {location} right now: street food like pani puri and bhel puri.",
                f"For {location}, spicy options are trending today - how about some biryani?",
                f"In {location}, healthy options like quinoa bowls are getting great reviews."
            ]
            return jsonify({
                "response": random.choice(sample_responses),
                "demo_mode": True
            })
        
        # Use the actual chatbot if API keys are configured
        response = run_async(food_chatbot.chat_about_food(message, location))
        return jsonify({
            "response": response,
            "demo_mode": False
        })
        
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({
            "error": str(e),
            "response": "I'm having trouble answering right now. Please try again later.",
            "demo_mode": True
        }), 500

@app.route('/api/deals/recommendations', methods=['POST'])
def get_deal_recommendations():
    """
    Endpoint for deal recommendations (from agent_02)
    """
    try:
        data = request.get_json()
        cuisine = data.get('cuisine', None)
        location = data.get('location', 'Mumbai')  # Added location parameter

        # Initialize state with user preferences
        initial_state = AgentState(
            restaurants=[],
            current_time=datetime.now(),
            detected_opportunities=[],
            generated_deals=[],
            user_request={
                "cuisine": cuisine,
                "location": location
            } if cuisine else {"location": location},
            llm_insights={},
            final_deals=[]
        )

        # Run the deal agent workflow
        result = deal_agent.workflow.invoke(initial_state)

        # Prepare response with enhanced data
        response = {
            "deals": result.get("final_deals", []),
            "marketing_ideas": result.get("llm_insights", {}).get("marketing", []),
            "total_savings": sum(
                deal.get("original_price", 0) - deal.get("discounted_price", 0)
                for deal in result.get("final_deals", [])
                if "original_price" in deal and "discounted_price" in deal
            ),
            "high_priority_count": len([
                deal for deal in result.get("final_deals", [])
                if deal.get("urgency") == "high"
            ]),
            "average_rating": (
                sum(deal.get("rating", 0) for deal in result.get("final_deals", [])) /
                len(result.get("final_deals", []))
                if result.get("final_deals") else 0
            ),
            "timestamp": datetime.now().isoformat()
        }

        return jsonify(response)
    except Exception as e:
        print(f"Error in deals endpoint: {str(e)}")
        return jsonify({
            "error": str(e),
            "deals": [],
            "total_savings": 0,
            "high_priority_count": 0,
            "average_rating": 0
        }), 500

@app.route('/api/system/status', methods=['GET'])
def system_status():
    """
    Endpoint to check system status and API keys
    """
    status = {
        "cohere_api_available": bool(config.COHERE_API_KEY != "demo-key-replace-with-real"),
        "weather_api_available": bool(config.OPENWEATHER_API_KEY != "demo-key-replace-with-real"),
        "demo_mode": config.is_demo_mode(),
        "status": "operational"
    }
    return jsonify(status)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)