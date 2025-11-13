from agent_base import AgentBase
from typing import Dict, Any
import random
import time
import threading
import json
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class ProducerAgent(AgentBase):
    def __init__(self, port: int):
        super().__init__("Producer", port)
        from network import AgentNetwork
        self.net = AgentNetwork()
        self.net.listen(port, self.handle_incoming)
        # Grok API setup from .env
        self.client = OpenAI(
            api_key=os.getenv("GROK_API_KEY"),
            base_url="https://api.x.ai/v1"
        )
        # Auto-send data to Trader every 5 sec
        threading.Thread(target=self.auto_produce, daemon=True).start()

    def tool_fetch_data(self) -> Dict[str, Any]:
        """Tool: Use Grok-4 to generate smart data."""
        try:
            response = self.client.chat.completions.create(
                model="grok-4",
                messages=[{"role": "user", "content": "Generate a realistic tech stock market insight as a JSON: {'insight': 'brief text', 'value': number between 20-60 representing predicted growth score}"}],
                max_tokens=100
            )
            grok_output = json.loads(response.choices[0].message.content)
            value = grok_output.get("value", random.uniform(20, 60))
            insight = grok_output.get("insight", "Grok-generated insight")
            print(f"[Grok] Producer insight: {insight}")
            return {
                "type": "data_packet",
                "value": value,
                "metadata": {"source": self.name, "timestamp": time.time(), "powered_by": "Grok-4"}
            }
        except Exception as e:
            print(f"[Grok Error] Fallback to random: {e}")
            value = random.uniform(20, 60)
            return {"type": "data_packet", "value": value, "metadata": {"source": self.name}}

    def tool_evaluate_trade(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        return {"accepted": True, "counter": offer.get("value", 0) * 1.1}

    def auto_produce(self):
        while self.running:
            time.sleep(5)
            data = self.tool_fetch_data()
            print(f"[{time.strftime('%H:%M:%S')}] Producer sending Grok-powered data to Trader: {data['value']:.1f}")
            response = self.net.send_message(5001, data)
            if response:
                self.reflect(response)

    def handle_incoming(self, incoming_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "received"}
