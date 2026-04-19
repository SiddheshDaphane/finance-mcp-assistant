from db import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from models import Transaction, Budget, Bill
from datetime import date


# ─── Transactions ─────────────────────────────────────────────

def get_transactions(db: Session, month: int = None, year: int = None, category: str = None):
    query = db.query(Transaction)

    if month:
        query = query.filter(extract('month', Transaction.date) == month)
    if year:
        query = query.filter(extract('year', Transaction.date) == year)
    if category:
        query = query.filter(Transaction.category.ilike(category))

    return query.order_by(Transaction.date.desc()).all()


def add_transaction(db: Session, amount: float, category: str, type: str, description: str, transaction_date: str):
    transaction = Transaction(
        amount=amount,
        category=category,
        type=type,
        description=description,
        date=transaction_date
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


# ─── Budgets ──────────────────────────────────────────────────

def get_budgets(db: Session):
    return db.query(Budget).order_by(Budget.category).all()


def get_budget_summary(db: Session, month: int, year: int):
    budgets = db.query(Budget).all()
    summary = []

    for budget in budgets:
        spent = db.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
            Transaction.category == budget.category,
            Transaction.type == 'expense',
            extract('month', Transaction.date) == month,
            extract('year', Transaction.date) == year
        ).scalar()

        summary.append({
            "category": budget.category,
            "monthly_limit": float(budget.monthly_limit),
            "spent": float(spent),
            "remaining": float(budget.monthly_limit) - float(spent)
        })

    return summary


# ─── Bills ────────────────────────────────────────────────────

def get_bills(db: Session, status: str = None):
    query = db.query(Bill)
    if status:
        query = query.filter(Bill.status == status)
    return query.order_by(Bill.due_date.asc()).all()


def get_overdue_bills(db: Session):
    return db.query(Bill).filter(
        Bill.status == 'unpaid',
        Bill.due_date < date.today()
    ).order_by(Bill.due_date.asc()).all()


def mark_bill_paid(db: Session, bill_id: int):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if bill:
        bill.status = 'paid'
        db.commit()
        db.refresh(bill)
    return bill


def schedule_bill(db: Session, name: str, amount: float, due_date: str, is_recurring: bool, category: str):
    bill = Bill(
        name=name,
        amount=amount,
        due_date=due_date,
        is_recurring=is_recurring,
        category=category
    )
    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill