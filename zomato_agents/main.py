from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from agent_config import agent
from tools import tools
from typing import TypedDict, Optional, List, Dict, Any

class AgentState(TypedDict):
    messages: List[Dict[str, Any]]
    action: Optional[Dict[str, Any]]
    tool_output: Optional[Any]
    intermediate_steps: List[Any]  # 🆕 Add this line



# ✅ Correct tool_router
def tool_router(state):
    action = state.get("action")
    if action:
        for tool in tools:
            if action.get("tool") == tool.name:
                return tool.name
    return END

# ✅ Build tool nodes using proper lambdas
tool_nodes = {}
for tool in tools:
    tool_nodes[tool.name] = RunnableLambda(
        lambda state, t=tool: {
            "tool_output": t.invoke(state["action"]["tool_input"]),
            "action": None,  # Clear action to prevent infinite loop
            "messages": state["messages"] + [{
                "role": "tool",
                "name": t.name,
                "content": str(t.invoke(state["action"]["tool_input"]))
            }]
        }
    )

# ✅ Use the agent as a node directly (NO RunnableLambda)
agent_node = agent.with_config(run_name="agent_node")

# Build the graph
graph = StateGraph(AgentState)

graph.add_node("agent", agent_node)

for tool_name, tool_fn in tool_nodes.items():
    graph.add_node(tool_name, tool_fn)
    graph.add_edge(tool_name, "agent")

graph.set_entry_point("agent")

graph.add_conditional_edges(
    "agent",
    tool_router,
    {tool.name: tool.name for tool in tools} | {END: END}
)

graph = graph.compile()

# ✅ Final run function
def run_agent(input_query):
    state = {
        "messages": [{"role": "user", "content": input_query}],
        "action": None,
        "tool_output": None,
        "intermediate_steps": [] 
    }

    for step in graph.stream(state):
        print(f"\n📍 Step: {step[0]}")
        print(step[1])

if __name__ == "__main__":
    run_agent("What food is trending tonight in Mumbai?")
