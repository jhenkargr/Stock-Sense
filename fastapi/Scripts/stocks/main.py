import subprocess
import sys
import uvicorn
import time
import socket
from fastapi import FastAPI, Query
from typing import Annotated
from stocks.metrics import router as router1, get_stocks as metrics_stocks, rowone as metrics_live
from stocks.cashflow import router as router2
from stocks.predict import router as router3
from stocks.suggestions import router as router4
from stocks.simplifier import router as router5
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
PORT = 8006
SERVICE_PORTS = {
	"stocks.cashflow:app": 8001,
    "stocks.simplifier:app": 8002,
	"stocks.metrics:app": 8003,
	"stocks.predict:app": 8007,
	"stocks.suggestions:app": 8009,
}

app.include_router(router1, prefix="/metrics")
app.include_router(router2, prefix="/cashflow")
app.include_router(router3, prefix="/predict")
app.include_router(router4, prefix="/suggestion")
app.include_router(router5, prefix="/simplify")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def wait_for_port(port: int, host="127.0.0.1", timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                print(f"  ✓ Port {port} is ready")
                return True
        except OSError:
            time.sleep(0.5)
    raise RuntimeError(f"Service on port {port} did not start within {timeout}s")

if __name__ == "__main__":
    for app_path, port in SERVICE_PORTS.items():
        print(f"Starting {app_path} on http://127.0.0.1:{port}/docs ...")
        subprocess.Popen([sys.executable, "-m", "uvicorn", app_path,
                          "--host", "127.0.0.1", "--port", str(port)])
        wait_for_port(port)

    print(f"Starting main app on http://127.0.0.1:{PORT}/docs")
    uvicorn.run(app, host="127.0.0.1", port=PORT)
		

#python -m stocks.main