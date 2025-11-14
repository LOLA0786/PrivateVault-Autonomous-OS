from fastapi import FastAPI
from pydantic import BaseModel
from agents.producer_agent import ProducerAgent

app = FastAPI(title="PrivateVault Autonomous OS")

# Initialize agent with Base64 API key
import os, base64
ENCODED_KEY = os.getenv("OPENAI_KEY_BASE64", "")
API_KEY = base64.b64decode(ENCODED_KEY).decode() if ENCODED_KEY else None

producer_agent = ProducerAgent(api_key=API_KEY)

class AgentRequest(BaseModel):
    goal: str
    context: str | None = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/agent/run")
def run_agent(req: AgentRequest):
    result = producer_agent.run_task(req.goal, req.context)
    return {"goal": req.goal, "context": req.context, "result": result}
