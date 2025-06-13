import os
import json
from datetime import datetime, timedelta
from typing import TypedDict, List, Dict
from langgraph.graph import StateGraph, END
import cohere
import random
from dotenv import load_dotenv

load_dotenv()

# Initialize Cohere
co = cohere.Client(os.getenv('COHERE_API_KEY', '1iiAhGbTpnAgRzMZSXk25pwXEovJW0N8a3P9QlTY'))  # Fallback for testing

# Restaurant Database
RESTAURANTS = [
    {
        "id": "resto_5",
        "name": "Tandoori Tales",
        "cuisine": "Indian",
        "inventory": {
            "Paneer Tikka": {"cost": 150, "quantity": 5},
            "Roti": {"cost": 20, "quantity": 12}
        },
        "hours": {"open": 11, "close": 23},
        "rating": 4.0,
        "last_hour_sales": 3
    },
    {
        "id": "resto_6",
        "name": "Dragon Bowl",
        "cuisine": "Chinese",
        "inventory": {
            "Hakka Noodles": {"cost": 130, "quantity": 22},
            "Manchurian": {"cost": 140, "quantity": 7}
        },
        "hours": {"open": 12, "close": 22},
        "rating": 4.3,
        "last_hour_sales": 4
    },
    {
        "id": "resto_7",
        "name": "Wrap & Roll",
        "cuisine": "Mexican",
        "inventory": {
            "Burrito": {"cost": 160, "quantity": 18},
            "Nachos": {"cost": 90, "quantity": 9}
        },
        "hours": {"open": 13, "close": 23},
        "rating": 3.7,
        "last_hour_sales": 2
    },
    {
        "id": "resto_8",
        "name": "Desi Biryani House",
        "cuisine": "Indian",
        "inventory": {
            "Hyderabadi Biryani": {"cost": 180, "quantity": 25},
            "Raita": {"cost": 30, "quantity": 2}
        },
        "hours": {"open": 10, "close": 22},
        "rating": 4.1,
        "last_hour_sales": 6
    },
    {
        "id": "resto_9",
        "name": "Veggie Vibe",
        "cuisine": "Vegan",
        "inventory": {
            "Quinoa Bowl": {"cost": 140, "quantity": 5},
            "Smoothie": {"cost": 110, "quantity": 1}
        },
        "hours": {"open": 9, "close": 21},
        "rating": 4.6,
        "last_hour_sales": 0
    },
    {
        "id": "resto_10",
        "name": "Pizza & Co.",
        "cuisine": "Italian",
        "inventory": {
            "Pepperoni Pizza": {"cost": 220, "quantity": 10},
            "Garlic Bread": {"cost": 60, "quantity": 20}
        },
        "hours": {"open": 11, "close": 23},
        "rating": 4.4,
        "last_hour_sales": 7
    },
    {
        "id": "resto_11",
        "name": "The Curry Club",
        "cuisine": "Indian",
        "inventory": {
            "Chicken Curry": {"cost": 170, "quantity": 6},
            "Rice": {"cost": 40, "quantity": 3}
        },
        "hours": {"open": 10, "close": 22},
        "rating": 3.9,
        "last_hour_sales": 1
    },
    {
        "id": "resto_12",
        "name": "Sambar & Chutney",
        "cuisine": "South Indian",
        "inventory": {
            "Dosa": {"cost": 70, "quantity": 15},
            "Idli": {"cost": 40, "quantity": 20}
        },
        "hours": {"open": 8, "close": 21},
        "rating": 4.0,
        "last_hour_sales": 2
    },
    {
        "id": "resto_13",
        "name": "Fry & Grill",
        "cuisine": "American",
        "inventory": {
            "Grilled Chicken": {"cost": 190, "quantity": 4},
            "Onion Rings": {"cost": 50, "quantity": 10}
        },
        "hours": {"open": 12, "close": 24},
        "rating": 3.6,
        "last_hour_sales": 1
    },
    {
        "id": "resto_14",
        "name": "Taste of Thailand",
        "cuisine": "Thai",
        "inventory": {
            "Pad Thai": {"cost": 160, "quantity": 8},
            "Tom Yum Soup": {"cost": 100, "quantity": 2}
        },
        "hours": {"open": 13, "close": 23},
        "rating": 4.3,
        "last_hour_sales": 3
    },
    {
        "id": "resto_15",
        "name": "Roller Roti",
        "cuisine": "North Indian",
        "inventory": {
            "Paneer Roll": {"cost": 100, "quantity": 12},
            "Aloo Roll": {"cost": 80, "quantity": 20}
        },
        "hours": {"open": 11, "close": 22},
        "rating": 3.8,
        "last_hour_sales": 4
    },
    {
        "id": "resto_16",
        "name": "Chaat Corner",
        "cuisine": "Street Food",
        "inventory": {
            "Pani Puri": {"cost": 30, "quantity": 50},
            "Bhel Puri": {"cost": 40, "quantity": 25}
        },
        "hours": {"open": 15, "close": 22},
        "rating": 4.2,
        "last_hour_sales": 9
    },
    {
        "id": "resto_17",
        "name": "Sizzling Tandoor",
        "cuisine": "Indian",
        "inventory": {
            "Seekh Kebab": {"cost": 160, "quantity": 7},
            "Butter Naan": {"cost": 40, "quantity": 2}
        },
        "hours": {"open": 12, "close": 23},
        "rating": 4.0,
        "last_hour_sales": 2
    },
    {
        "id": "resto_18",
        "name": "Bento Box",
        "cuisine": "Japanese",
        "inventory": {
            "Tempura": {"cost": 180, "quantity": 6},
            "Sushi Roll": {"cost": 200, "quantity": 3}
        },
        "hours": {"open": 11, "close": 22},
        "rating": 4.7,
        "last_hour_sales": 5
    },
    {
        "id": "resto_19",
        "name": "Kebab Express",
        "cuisine": "Mughlai",
        "inventory": {
            "Mutton Kebab": {"cost": 200, "quantity": 5},
            "Paratha": {"cost": 30, "quantity": 10}
        },
        "hours": {"open": 13, "close": 23},
        "rating": 3.5,
        "last_hour_sales": 1
    },
    {
        "id": "resto_20",
        "name": "Hearty Greens",
        "cuisine": "Salads & Health",
        "inventory": {
            "Caesar Salad": {"cost": 120, "quantity": 4},
            "Detox Juice": {"cost": 90, "quantity": 2}
        },
        "hours": {"open": 9, "close": 20},
        "rating": 4.5,
        "last_hour_sales": 0
    },
    {
        "id": "resto_21",
        "name": "Momo Station",
        "cuisine": "Tibetan",
        "inventory": {
            "Veg Momos": {"cost": 80, "quantity": 30},
            "Chicken Momos": {"cost": 100, "quantity": 25}
        },
        "hours": {"open": 11, "close": 22},
        "rating": 4.3,
        "last_hour_sales": 6
    },
    {
        "id": "resto_22",
        "name": "Punjab Express",
        "cuisine": "Punjabi",
        "inventory": {
            "Amritsari Kulcha": {"cost": 100, "quantity": 6},
            "Dal Makhani": {"cost": 130, "quantity": 3}
        },
        "hours": {"open": 10, "close": 23},
        "rating": 4.0,
        "last_hour_sales": 3
    },
    {
        "id": "resto_23",
        "name": "Desert Dreams",
        "cuisine": "Desserts",
        "inventory": {
            "Gulab Jamun": {"cost": 60, "quantity": 15},
            "Ice Cream": {"cost": 70, "quantity": 12}
        },
        "hours": {"open": 12, "close": 24},
        "rating": 4.6,
        "last_hour_sales": 8
    },
    {
        "id": "resto_24",
        "name": "BBQ Blaze",
        "cuisine": "Barbecue",
        "inventory": {
            "BBQ Chicken": {"cost": 220, "quantity": 10},
            "BBQ Veg Platter": {"cost": 200, "quantity": 4}
        },
        "hours": {"open": 16, "close": 23},
        "rating": 4.1,
        "last_hour_sales": 2
    }
]


class AgentState(TypedDict):
    restaurants: List[Dict]
    current_time: datetime
    detected_opportunities: List[Dict]
    generated_deals: List[Dict]
    user_request: Dict
    llm_insights: Dict
    final_deals: List[Dict]  # Added this to ensure the key exists

class DealAgent:
    def __init__(self):
        self.workflow = self._build_workflow()
    
    def _build_workflow(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("check_status", self.check_restaurant_status)
        workflow.add_node("analyze_ops", self.analyze_opportunities)
        workflow.add_node("llm_strategy", self.llm_analysis)
        workflow.add_node("create_deals", self.generate_deals)
        workflow.add_node("personalize", self.personalize_recommendations)
        
        workflow.set_entry_point("check_status")
        workflow.add_edge("check_status", "analyze_ops")
        workflow.add_edge("analyze_ops", "llm_strategy")
        workflow.add_edge("llm_strategy", "create_deals")
        workflow.add_edge("create_deals", "personalize")
        workflow.add_edge("personalize", END)
        
        return workflow.compile()

    def check_restaurant_status(self, state: AgentState) -> AgentState:
        """Gather restaurant data"""
        print("🔍 Checking restaurant status...")
        state["restaurants"] = RESTAURANTS
        state["current_time"] = datetime.now()
        state["detected_opportunities"] = []
        state["generated_deals"] = []
        state["llm_insights"] = {}
        state["final_deals"] = []  # Initialize here
        return state

    def analyze_opportunities(self, state: AgentState) -> AgentState:
        """Identify deal opportunities"""
        print("🤖 Analyzing patterns...")
        opportunities = []
        
        for resto in state["restaurants"]:
            current_hour = state["current_time"].hour
            
            if current_hour >= resto["hours"]["close"] - 2:
                opportunities.append({
                    "restaurant_id": resto["id"],
                    "restaurant_name": resto["name"],
                    "type": "closing_soon",
                    "urgency": "high"
                })
            
            if resto["last_hour_sales"] < 3:
                opportunities.append({
                    "restaurant_id": resto["id"],
                    "restaurant_name": resto["name"],
                    "type": "slow_sales",
                    "urgency": "medium"
                })
                
            for item, details in resto["inventory"].items():
                if details["quantity"] < 5:
                    opportunities.append({
                        "restaurant_id": resto["id"],
                        "restaurant_name": resto["name"],
                        "type": "clear_stock",
                        "item": item,
                        "urgency": "high"
                    })
        
        state["detected_opportunities"] = opportunities
        return state

    def llm_analysis(self, state: AgentState) -> AgentState:
        """Cohere-powered strategic insights"""
        print("🧠 Running LLM analysis...")
        opportunities_text = "\n".join(
            f"{o['restaurant_name']}: {o['type']} (urgency: {o['urgency']})"
            for o in state["detected_opportunities"]
        )
        
        prompt = f"""Analyze these restaurant opportunities:
{opportunities_text}

Current time: {state["current_time"].strftime("%H:%M")}

Suggest creative deals in JSON format with these keys:
- "critical" (list of restaurant names that need attention)
- "creative_deals" (list of deal ideas with 'type', 'target', 'rationale')
- "marketing" (list of marketing angle ideas)"""
        
        try:
            response = co.generate(
                model="command",
                prompt=prompt,
                max_tokens=800,
                temperature=0.7
            )
            response_text = response.generations[0].text
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0]
            state["llm_insights"] = json.loads(response_text)
        except Exception as e:
            print(f"LLM Error: {e}")
            state["llm_insights"] = {
                "critical": [],
                "creative_deals": [],
                "marketing": []
            }
        return state

    def generate_deals(self, state: AgentState) -> AgentState:
        """Generate deals with hybrid logic"""
        print("💡 Creating deals...")
        deals = []
        
        # Rule-based deals
        for opp in state["detected_opportunities"]:
            resto = next(r for r in state["restaurants"] if r["id"] == opp["restaurant_id"])
            discount = 20 + (10 if opp["urgency"] == "high" else 0)
            
            if opp["type"] == "clear_stock":
                item = opp["item"]
                deals.append({
                    "restaurant": resto["name"],
                    "deal": f"{discount}% off {item}",
                    "type": "clearance",
                    "urgency": opp["urgency"],
                    "original_price": resto["inventory"][item]["cost"],
                    "discounted_price": round(resto["inventory"][item]["cost"] * (1 - discount/100))
                })
            else:
                deals.append({
                    "restaurant": resto["name"],
                    "deal": f"{discount}% off all menu",
                    "type": opp["type"],
                    "urgency": opp["urgency"]
                })
        
        # LLM-enhanced deals
        if state["llm_insights"].get("creative_deals"):
            for idea in state["llm_insights"]["creative_deals"]:
                if isinstance(idea, dict) and "target" in idea:
                    deals.append({
                        "restaurant": idea["target"],
                        "deal": idea.get("type", "Special Offer"),
                        "type": "innovative",
                        "rationale": idea.get("rationale", ""),
                        "urgency": "high"
                    })
        
        state["generated_deals"] = deals
        return state

    def personalize_recommendations(self, state: AgentState) -> AgentState:
        """Tailor recommendations to user"""
        print("🎯 Personalizing...")
        user_prefs = state.get("user_request", {})
        
        if user_prefs.get("cuisine"):
            filtered_deals = [
                d for d in state["generated_deals"]
                if any(r["cuisine"] == user_prefs["cuisine"] 
                     for r in state["restaurants"] 
                     if r["name"] == d["restaurant"])
            ]
        else:
            filtered_deals = state["generated_deals"]
        
        # Sort by urgency + LLM priority
        critical_restaurants = [c for c in state["llm_insights"].get("critical", [])]
        state["final_deals"] = sorted(
            filtered_deals,
            key=lambda x: (
                x["urgency"] == "high",
                x["restaurant"] in critical_restaurants,
                random.random()
            ),
            reverse=True
        )
        return state

if __name__ == "__main__":
    agent = DealAgent()
    
    # Initialize all required state keys
    initial_state = AgentState(
        restaurants=[],
        current_time=datetime.now(),
        detected_opportunities=[],
        generated_deals=[],
        user_request={"cuisine": "Indian"},
        llm_insights={},
        final_deals=[]
    )
    
    # Run agent
    result = agent.workflow.invoke(initial_state)
    
    # Display results
    print("\n🍽️  SMART DEAL RECOMMENDATIONS")
    print("=" * 40)
    if result.get("final_deals"):
        for i, deal in enumerate(result["final_deals"][:5], 1):
            print(f"\n{i}. {deal['restaurant']}")
            print(f"   🎁 {deal['deal']}")
            if 'discounted_price' in deal:
                print(f"   💰 Price: ₹{deal['discounted_price']} (was ₹{deal['original_price']})")
            print(f"   ⚡ Urgency: {deal['urgency'].upper()}")
            if deal.get("rationale"):
                print(f"   💡 Reason: {deal['rationale']}")
        
        if result["llm_insights"].get("marketing"):
            print("\n📢 MARKETING IDEAS:")
            for idea in result["llm_insights"]["marketing"][:3]:
                print(f"- {idea}")
    else:
        print("No deals available at this time.")