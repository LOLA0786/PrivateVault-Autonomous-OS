import json
import threading
import time
import random
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class AgentBase(ABC):
    def __init__(self, name: str, port: int):
        self.name = name
        self.port = port
        self.goal_score = 0.0
        self.data_history = []  # For provenance/tracking
        self.running = True
        self.lock = threading.Lock()

    @abstractmethod
    def tool_fetch_data(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def tool_evaluate_trade(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def reflect(self, action_result: Any) -> str:
        """Simple reflection: Log and adjust goal."""
        with self.lock:
            self.data_history.append(action_result)
            self.goal_score = sum([d.get('value', 0) for d in self.data_history[-5:]]) / min(5, len(self.data_history))
        return f"{self.name} reflects: Goal score now {self.goal_score:.1f}"

    def autonomy_loop(self):
        """Core agent loop: Observe > Plan > Act > Reflect."""
        while self.running:
            try:
                # Observe: Fetch internal state
                observation = {"history_len": len(self.data_history), "current_score": self.goal_score}
                
                # Plan: Decide action (simple random for demo)
                action = "fetch" if random.random() > 0.5 else "trade"
                
                # Act: Use tool
                if action == "fetch":
                    result = self.tool_fetch_data()
                else:
                    # Mock trade partner for base
                    result = self.tool_evaluate_trade({"mock_offer": "data_packet"})
                
                # Reflect
                reflection = self.reflect(result)
                print(f"[{time.strftime('%H:%M:%S')}] {reflection}")
                
                time.sleep(2)  # Pace for demo
            except Exception as e:
                print(f"[{self.name}] Error in loop: {e}")
                time.sleep(1)

    def start(self):
        thread = threading.Thread(target=self.autonomy_loop, daemon=True)
        thread.start()
        print(f"[{self.name}] Started on port {self.port}")
