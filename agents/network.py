import socket
import json
import threading
import time
from typing import Optional, Dict, Any, Callable

class AgentNetwork:
    def __init__(self, host: str = 'localhost'):
        self.host = host

    def send_message(self, target_port: int, message: Dict[str, Any], timeout: int = 5) -> Optional[Dict[str, Any]]:
        """Send JSON payload to peer (MCP-like)."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                sock.connect((self.host, target_port))
                payload = json.dumps({
                    "sender": "AgentNet",
                    "timestamp": time.time(),
                    "data": message,
                    "provenance": "secure_hash"
                }).encode('utf-8')
                sock.sendall(payload)
                response = sock.recv(1024).decode('utf-8')
                return json.loads(response) if response else None
        except Exception as e:
            print(f"Network error to {target_port}: {e}")
            return None

    def listen(self, port: int, callback: Callable[[Dict[str, Any]], Dict[str, Any]]):
        """Listen for incoming messages."""
        def listener():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('localhost', port))
                sock.listen(1)
                print(f"[{port}] Listening for peers...")
                while True:
                    try:
                        conn, _ = sock.accept()
                        data = conn.recv(1024).decode('utf-8')
                        if data:
                            msg = json.loads(data)
                            response = callback(msg['data'])
                            conn.sendall(json.dumps({"response": response}).encode('utf-8'))
                    except Exception as e:
                        print(f"Listen error on {port}: {e}")
                    finally:
                        conn.close()
        threading.Thread(target=listener, daemon=True).start()
