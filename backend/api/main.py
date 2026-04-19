from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../database'))

from api.routes.transactions import router as transactions_router
from api.routes.budgets import router as budgets_router
from api.routes.bills import router as bills_router

app = FastAPI(
    title="Finance MCP Assistant API",
    description="Personal Finance Assistant with MCP integration",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions_router)
app.include_router(budgets_router)
app.include_router(bills_router)

@app.get("/")
def root():
    return {"status": "Finance MCP Assistant API is running 🚀"}