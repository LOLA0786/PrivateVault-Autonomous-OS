import time
import signal
import sys
from producer_agent import ProducerAgent
from trader_agent import TraderAgent
from consumer_agent import ConsumerAgent

def signal_handler(sig, frame):
    print("\n🛑 Stopping agents...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    print("🚀 Launching Grok-Powered AgentNet: Internet of Agents")
    print("Agents using Grok-4 for smart data/trading. Get your API key: https://console.x.ai\n")

    # Init agents
    producer = ProducerAgent(5000)
    trader = TraderAgent(5001)
    consumer = ConsumerAgent(5002)

    # Start all
    producer.start()
    trader.start()
    consumer.start()

    try:
        time.sleep(60)  # Run for 60s to see Grok magic
    except KeyboardInterrupt:
        pass
    finally:
        producer.running = trader.running = consumer.running = False
        print("Demo complete! Agents powered by Grok-4 🚀 Check GitHub.")
