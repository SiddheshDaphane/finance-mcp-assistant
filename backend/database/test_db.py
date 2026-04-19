import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import SessionLocal
from crud import get_transactions, get_budgets, get_budget_summary, get_bills, get_overdue_bills

db = SessionLocal()

print("=== Transactions (April 2025) ===")
transactions = get_transactions(db, month=4, year=2025)
for t in transactions:
    print(f"{t.date} | {t.category} | {t.type} | ${t.amount} | {t.description}")

print("\n=== Budgets ===")
budgets = get_budgets(db)
for b in budgets:
    print(f"{b.category} — limit: ${b.monthly_limit}")

print("\n=== Budget Summary (April 2025) ===")
summary = get_budget_summary(db, month=4, year=2025)
for s in summary:
    print(s)

print("\n=== Unpaid Bills ===")
bills = get_bills(db, status='unpaid')
for b in bills:
    print(f"{b.name} — ${b.amount} — due: {b.due_date}")

print("\n=== Overdue Bills ===")
overdue = get_overdue_bills(db)
for b in overdue:
    print(f"{b.name} — ${b.amount} — due: {b.due_date}")

db.close()