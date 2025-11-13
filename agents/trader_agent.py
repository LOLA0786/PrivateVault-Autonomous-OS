from agent_base import AgentBase
from typing import Dict, Any
import random
import time
import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class TraderAgent(AgentBase):
    def __init__(self, port: int):
        super().__init__("Trader", port)
        from network import AgentNetwork
        self.net = AgentNetwork()
        self.net.listen(port, self.handle_incoming)
        self.client = OpenAI(
            api_key=os.getenv("GROK_API_KEY"),
            base_url="https://api.x.ai/v1"
        )

    def tool_fetch_data(self) -> Dict[str, Any]:
        if self.data_history:
            total = sum(d.get("value", 0) for d in self.data_history[-3:])
            return {"type": "aggregated", "value": total / 3}
        return {"type": "empty", "value": 0}

    def tool_evaluate_trade(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        base_value = offer.get("value", 0)
        try:
            response = self.client.chat.completions.create(
                model="grok-4",
                messages=[{"role": "user", "content": f"Evaluate trade offer value {base_value}. Is it fair? Respond as JSON: {{'accepted': true/false, 'final_value': number, 'reason': 'brief explanation'}}"}],
                max_tokens=80
            )
            grok_eval = json.loads(response.choices[0].message.content)
            final_value = grok_eval.get("final_value", base_value * random.uniform(0.9, 1.1))
            reason = grok_eval.get("reason", "Grok-evaluated")
            print(f"[Grok] Trader reason: {reason}")
            return {"accepted": grok_eval.get("accepted", True), "final_value": final_value}
        except Exception as e:
            print(f"[Grok Error] Fallback: {e}")
            return {"accepted": True, "final_value": base_value * random.uniform(0.9, 1.1)}

    def handle_incoming(self, incoming_data: Dict[str, Any]) -> Dict[str, Any]:
        if incoming_data.get("type") == "data_packet":
            value = incoming_data.get("value", 0)
            if value > 0:
                forwarded = self.net.send_message(5002, incoming_data)
                if forwarded:
                    self.reflect(forwarded)
                return {"brokered": True, "value": value}
        return {"status": "no_deal"}
