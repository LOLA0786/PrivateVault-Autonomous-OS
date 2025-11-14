from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import threading
import time
import os
import json

app = FastAPI(title="PrivateVault Autonomous OS", version="1.0")

class RunRequest(BaseModel):
    context: str | None = None  # Python 3.11+ supports |

@app.post("/run")
async def run_pipeline(request: RunRequest):
    def execute():
        os.system("python main.py > /tmp/pipeline.log 2>&1")
    
    thread = threading.Thread(target=execute)
    thread.start()
    
    for _ in range(20):
        time.sleep(0.5)
        if os.path.exists("/tmp/result.json"):
            with open("/tmp/result.json") as f:
                return json.load(f)
    
    return {"error": "timeout", "log": open("/tmp/pipeline.log").read()[-500:]}
