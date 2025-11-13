from agent_base import AgentBase
from typing import Dict, Any
import random
import time
import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class ConsumerAgent(AgentBase):
    def __init__(self, port: int):
        super().__init__("Consumer", port)
        from network import AgentNetwork
        self.net = AgentNetwork()
        self.net.listen(port, self.handle_incoming)
        self.client = OpenAI(
            api_key=os.getenv("GROK_API_KEY"),
            base_url="https://api.x.ai/v1"
        )

    def tool_fetch_data(self) -> Dict[str, Any]:
        try:
            response = self.client.chat.completions.create(
                model="grok-4",
                messages=[{"role": "user", "content": "Suggest a score boost for consumed data. Respond as JSON: {'value': number between 5-30, 'optimization': 'brief tip'}"}],
                max_tokens=50
            )
            grok_boost = json.loads(response.choices[0].message.content)
            value = grok_boost.get("value", random.uniform(5, 30))
            tip = grok_boost.get("optimization", "Grok-optimized")
            print(f"[Grok] Consumer tip: {tip}")
            return {"type": "consumed", "value": value}
        except Exception as e:
            print(f"[Grok Error] Fallback: {e}")
            return {"type": "consumed", "value": random.uniform(5, 30)}

    def tool_evaluate_trade(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        score_boost = offer.get("value", 0) * 1.5
        return {"optimized": True, "boost": score_boost}

    def handle_incoming(self, incoming_data: Dict[str, Any]) -> Dict[str, Any]:
        if incoming_data.get("brokered"):
            self.reflect(incoming_data)
            if self.goal_score > 80:
                print(f"\n[{self.name}] Shared goal achieved! Final score: {self.goal_score:.1f}")
                self.running = False
            return {"consumed": True}
        return {"status": "pending"}
