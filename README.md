# AutoStream AI Agent 

A production-grade conversational AI agent built for AutoStream, a SaaS video editing platform.


## How to run locally

Prerequisites: Python 3.9+, Groq API Key

```bash
1. Cloning the repo
git clone https://github.com/prasunitade30_del/autostream-agent.git
cd autostream-agent

2. Creating and activating virtual environment
python -m venv venv
venv\Scripts\activate          

3. Installing dependencies
pip install -r requirements.txt

4. Adding API key
echo "GROQ_API_KEY=your_groq_api_key_here" > .env

5. Running the agent
python agent.py
```

---

## Architecture 

This agent is built using LangGraph, a stateful graph execution framework built on top of LangChain. LangGraph was chosen over AutoGen because it provides explicit, deterministic control over multi-step agentic workflows through a directed graph structure making it easier to reason about state transitions, debug conversation flow, and avoid uncontrolled agent loops.

State Management: A typed `AgentState` dictionary persists across all graph nodes. It stores the full conversation history (via LangGraph's `add_messages` reducer), the detected intent, lead collection fields (`name`, `email`, `platform`), a flag for whether the lead was captured, and an `awaiting` field that tracks which piece of information the agent is currently collecting. This state is passed through every node and updated immutably.

Graph Flow: Every user message enters the `detect_intent` node, which classifies intent as `casual_greeting`, `product_inquiry`, or `high_intent`. A conditional router then directs flow to the appropriate node: `greet`, `rag_response`, or `collect_lead_info`. The RAG node retrieves relevant content from a local JSON knowledge base using keyword matching. The lead collection node uses the `awaiting` state field to collect name → email → platform sequentially before calling `mock_lead_capture()`.



## WhatsApp Deployment via Webhooks

To deploy this agent on WhatsApp:

1. Register with Meta for Developers — create a WhatsApp Business App and get a phone number + access token.
2. Set up a Webhook endpoint — build a FastAPI or Flask server with two routes:
   - `GET /webhook` — for Meta's verification challenge (returns the hub challenge token).
   - `POST /webhook` — receives incoming messages from WhatsApp users as JSON payloads.
3. Session state management — use a dictionary (or Redis in production) keyed by the user's WhatsApp phone number to persist `AgentState` across webhook calls, since each message arrives as a separate HTTP request.
4. Process and reply — on each `POST`, extract the user's message, look up their session state, call `app.invoke(state)`, and send the agent's response back via the WhatsApp Cloud API (`POST https://graph.facebook.com/v17.0/{phone_id}/messages`).
5. Deploy — host the webhook server on Railway, Render, or AWS Lambda with a public HTTPS URL registered in the Meta dashboard.


## Link to the project demonstration video
https://drive.google.com/drive/folders/148QGIywqE6Nz4XAnkFm_NOEW0IBsdYke?usp=drive_link