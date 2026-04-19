from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../database'))

from db import get_db
from crud import get_budgets, get_budget_summary
from schema import BudgetResponse, BudgetSummaryResponse

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.get("/", response_model=List[BudgetResponse])
def read_budgets(db: Session = Depends(get_db)):
    return get_budgets(db)


@router.get("/summary", response_model=List[BudgetSummaryResponse])
def read_budget_summary(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000),
    db: Session = Depends(get_db)
):
    return get_budget_summary(db, month=month, year=year)