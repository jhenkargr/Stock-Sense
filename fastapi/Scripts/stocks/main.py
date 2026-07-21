import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from stocks.metrics import router as router1
from stocks.cashflow import router as router2
from stocks.predict import router as router3
from stocks.suggestions import router as router4
from stocks.simplifier import router as router5
from stocks.marketstatus import router as router6

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router1, prefix="/metrics")
app.include_router(router2, prefix="/cashflow")
app.include_router(router3, prefix="/predict")
app.include_router(router4, prefix="/suggestion")
app.include_router(router5, prefix="/simplify")
app.include_router(router6, prefix="/marketstatus")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8006))
    uvicorn.run(app, host="0.0.0.0", port=port)