from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../database'))

from db import get_db
from crud import get_bills, get_overdue_bills, mark_bill_paid, schedule_bill
from schema import BillCreate, BillResponse

router = APIRouter(prefix="/bills", tags=["Bills"])


@router.get("/", response_model=List[BillResponse])
def read_bills(
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    return get_bills(db, status=status)


@router.get("/overdue", response_model=List[BillResponse])
def read_overdue_bills(db: Session = Depends(get_db)):
    return get_overdue_bills(db)


@router.patch("/{bill_id}/pay", response_model=BillResponse)
def pay_bill(bill_id: int, db: Session = Depends(get_db)):
    bill = mark_bill_paid(db, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    return bill


@router.post("/", response_model=BillResponse)
def create_bill(bill: BillCreate, db: Session = Depends(get_db)):
    return schedule_bill(
        db,
        name=bill.name,
        amount=bill.amount,
        due_date=bill.due_date,
        is_recurring=bill.is_recurring,
        category=bill.category
    )