from langgraph.graph import StateGraph, START, END
from .agents import ResearchAgents
from .state import ResearchState


def create_graph(agents: ResearchAgents):
    graph = StateGraph(ResearchState)
    graph.add_node("researcher", agents.researcher_node)
    graph.add_node("analyst", agents.analyst_node)
    graph.add_node("fact_checker", agents.fact_checker_node)
    graph.add_node("writer", agents.writer_node)

    graph.add_edge(START, "researcher")
    graph.add_edge("researcher", "analyst")
    graph.add_edge("analyst", "fact_checker")
    graph.add_edge("fact_checker", "writer")
    graph.add_edge("writer", END)
    return graph.compile()
