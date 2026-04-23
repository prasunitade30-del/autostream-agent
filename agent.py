import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_groq import ChatGroq
from rag import retrieve_context
from tools import mock_lead_capture

load_dotenv()

#LLM Setup 
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3,
)

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    intent: str
    lead_name: str
    lead_email: str
    lead_platform: str
    lead_captured: bool
    awaiting: str

#Intent detection 
def detect_intent(state: AgentState) -> AgentState:
    last_msg = state["messages"][-1].content.lower()

    high_intent_keywords = [
        "sign up", "sign me up", "i want to try", "i want to buy", "subscribe",
        "get started", "let's go", "i'm in", "sign up for", "purchase",
        "i want the pro", "i want the basic", "how do i start", "register"
    ]
    product_keywords = [
        "price", "pricing", "cost", "plan", "feature", "how much", "refund",
        "support", "caption", "4k", "resolution", "basic", "pro", "video",
        "tell me about", "what is", "autostream", "subscription"
    ]

    if any(kw in last_msg for kw in high_intent_keywords):
        intent = "high_intent"
    elif any(kw in last_msg for kw in product_keywords):
        intent = "product_inquiry"
    else:
        intent = "casual_greeting"

    return {**state, "intent": intent}

def router(state: AgentState) -> str:
    if state.get("lead_captured"):
        return "end"
    if state.get("awaiting"):
        return "collect_lead_info"
    if state["intent"] == "high_intent":
        return "collect_lead_info"
    if state["intent"] == "product_inquiry":
        return "rag_response"
    return "greet"

#Greeting
def greet(state: AgentState) -> AgentState:
    system = SystemMessage(content=(
        "You are an enthusiastic sales assistant for AutoStream, a SaaS platform "
        "for automated video editing. Keep responses short, warm, and helpful. "
        "Don't mention pricing unless asked."
    ))
    response = llm.invoke([system] + state["messages"])
    return {**state, "messages": state["messages"] + [AIMessage(content=response.content)]}

#RAG response
def rag_response(state: AgentState) -> AgentState:
    last_msg = state["messages"][-1].content
    context = retrieve_context(last_msg)

    system = SystemMessage(content=(
        "You are a knowledgeable sales assistant for AutoStream. "
        "Use ONLY the context below to answer the user's question accurately. "
        "Be concise and friendly. End with a soft CTA encouraging them to try the Pro plan.\n\n"
        f"CONTEXT:\n{context}"
    ))
    response = llm.invoke([system] + state["messages"])
    return {**state, "messages": state["messages"] + [AIMessage(content=response.content)]}

#Lead collection
def collect_lead_info(state: AgentState) -> AgentState:
    last_msg = state["messages"][-1].content.strip()
    awaiting = state.get("awaiting", "")
    name = state.get("lead_name", "")
    email = state.get("lead_email", "")
    platform = state.get("lead_platform", "")

    if awaiting == "name":
        name = last_msg
        awaiting = "email"
    elif awaiting == "email":
        email = last_msg
        awaiting = "platform"
    elif awaiting == "platform":
        platform = last_msg
        awaiting = "done"
    else:
        awaiting = "name"

    if awaiting == "done" and name and email and platform:
        result = mock_lead_capture(name, email, platform)
        reply = (
            f" You're all set, {name}! I've registered your interest in AutoStream Pro.\n"
            f"We'll reach out to {email} shortly with your trial access.\n"
            f"Can't wait to see what you create on {platform}! "
        )
        return {
            **state,
            "lead_name": name,
            "lead_email": email,
            "lead_platform": platform,
            "lead_captured": True,
            "awaiting": "",
            "messages": state["messages"] + [AIMessage(content=reply)],
        }

    prompts = {
        "name": "Awesome! I'd love to get you started. What's your name?",
        "email": f"Great to meet you, {name}! What's your email address so we can send you access details?",
        "platform": f"Perfect! And which platform do you mainly create content for? (e.g., YouTube, Instagram, TikTok)",
    }
    reply = prompts[awaiting]

    return {
        **state,
        "lead_name": name,
        "lead_email": email,
        "lead_platform": platform,
        "awaiting": awaiting,
        "messages": state["messages"] + [AIMessage(content=reply)],
    }


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("detect_intent", detect_intent)
    graph.add_node("greet", greet)
    graph.add_node("rag_response", rag_response)
    graph.add_node("collect_lead_info", collect_lead_info)

    graph.set_entry_point("detect_intent")

    graph.add_conditional_edges("detect_intent", router, {
        "greet": "greet",
        "rag_response": "rag_response",
        "collect_lead_info": "collect_lead_info",
        "end": END,
    })

    graph.add_edge("greet", END)
    graph.add_edge("rag_response", END)
    graph.add_edge("collect_lead_info", END)

    return graph.compile()

#Chat
def main():
    app = build_graph()
    print("\n AutoStream AI Agent")
    print("Type 'quit' to exit\n")
    print("-" * 40)

    state: AgentState = {
        "messages": [],
        "intent": "",
        "lead_name": "",
        "lead_email": "",
        "lead_platform": "",
        "lead_captured": False,
        "awaiting": "",
    }

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Agent: Thanks for visiting AutoStream! Goodbye! ")
            break
        if not user_input:
            continue

        state["messages"] = state["messages"] + [HumanMessage(content=user_input)]
        state = app.invoke(state)

        last_ai_msg = next(
            (m for m in reversed(state["messages"]) if isinstance(m, AIMessage)), None
        )
        if last_ai_msg:
            print(f"Agent: {last_ai_msg.content}\n")

        if state.get("lead_captured"):
            print("Agent: It was great talking to you! Our team will follow up soon. Goodbye! ")
            break

if __name__ == "__main__":
    main()