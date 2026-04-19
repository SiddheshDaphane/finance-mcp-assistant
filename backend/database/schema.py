from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
from decimal import Decimal


# ─── Transaction Schemas ──────────────────────────────────────

class TransactionCreate(BaseModel):
    amount: float
    category: str
    type: str
    description: Optional[str] = None
    date: date


class TransactionResponse(BaseModel):
    id: int
    amount: Decimal
    category: str
    type: str
    description: Optional[str] = None
    date: date
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Budget Schemas ───────────────────────────────────────────

class BudgetResponse(BaseModel):
    id: int
    category: str
    monthly_limit: Decimal
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BudgetSummaryResponse(BaseModel):
    category: str
    monthly_limit: float
    spent: float
    remaining: float


# ─── Bill Schemas ─────────────────────────────────────────────

class BillCreate(BaseModel):
    name: str
    amount: float
    due_date: date
    is_recurring: bool = False
    category: Optional[str] = None


class BillResponse(BaseModel):
    id: int
    name: str
    amount: Decimal
    due_date: date
    status: str
    is_recurring: bool
    category: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── Chat Schema ──────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str