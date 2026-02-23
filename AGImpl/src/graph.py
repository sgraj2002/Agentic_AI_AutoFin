from langgraph.graph import StateGraph, END
from .models import Briefcase
from .agents import node_screener, node_miner, node_calculator

def create_graph():
    workflow = StateGraph(Briefcase)
    
    workflow.add_node("screener", node_screener)
    workflow.add_node("miner", node_miner)
    workflow.add_node("calculator", node_calculator)
    
    workflow.set_entry_point("screener")
    workflow.add_edge("screener", "miner")
    workflow.add_edge("miner", "calculator")
    workflow.add_edge("calculator", END)
    
    return workflow.compile()
