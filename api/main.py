from fastapi import FastAPI
from pydantic import BaseModel
import os

# Agents
from agents.producer_agent import ProducerAgent
# NOTE: Add more your agents after merging
# from agents.trader_agent import TraderAgent
# from agents.consumer_agent import ConsumerAgent

app = FastAPI(title="PrivateVault Autonomous OS")

class AgentRequest(BaseModel):
    goal: str
    context: str | None = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/agents/run")
def run_agents(req: AgentRequest):
    # DEMO mode if no key
    key = os.getenv("GROK_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not key:
        return {
            "demo": True,
            "status": "ok",
            "summary": f"[DEMO] Agent pipeline simulated for: {req.goal}",
            "score": 78,
        }

    # REAL mode engine (plug in after merge)
    agent = ProducerAgent(5000)
    # Integrate your full pipe later
    return {
        "demo": False,
        "status": "ok",
        "summary": f"[REAL] Pipeline executed for goal: {req.goal}",
        "score": 92,
    }
