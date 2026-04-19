from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../database'))

from db import get_db
from crud import get_transactions, add_transaction
from schema import TransactionCreate, TransactionResponse

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/", response_model=List[TransactionResponse])
def read_transactions(
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000),
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    return get_transactions(db, month=month, year=year, category=category)


@router.post("/", response_model=TransactionResponse)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    return add_transaction(
        db,
        amount=transaction.amount,
        category=transaction.category,
        type=transaction.type,
        description=transaction.description,
        transaction_date=transaction.date
    )