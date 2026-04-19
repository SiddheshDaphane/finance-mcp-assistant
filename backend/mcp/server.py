import sys
import os
import json
from datetime import date

sys.path.append(os.path.join(os.path.dirname(__file__), '../database'))

from mcp.server.fastmcp import FastMCP
from db import SessionLocal
from crud import (
    get_transactions,
    add_transaction,
    get_budgets,
    get_budget_summary,
    get_bills,
    get_overdue_bills,
    mark_bill_paid,
    schedule_bill
)

# ─── Initialize MCP Server ────────────────────────────────────
mcp = FastMCP("Finance Assistant")


# ─── Helper ───────────────────────────────────────────────────
def get_db():
    return SessionLocal()


# ═══════════════════════════════════════════════════════════════
# TOOLS — Gemini can call these to perform actions
# ═══════════════════════════════════════════════════════════════

@mcp.tool()
def fetch_transactions(month: int, year: int, category: str = None) -> str:
    """
    Fetch transactions for a given month and year.
    Optionally filter by category.
    Returns a list of transactions as JSON.
    """
    db = get_db()
    try:
        transactions = get_transactions(db, month=month, year=year, category=category)
        result = [
            {
                "id": t.id,
                "amount": float(t.amount),
                "category": t.category,
                "type": t.type,
                "description": t.description,
                "date": str(t.date)
            }
            for t in transactions
        ]
        return json.dumps(result)
    finally:
        db.close()


@mcp.tool()
def create_transaction(
    amount: float,
    category: str,
    type: str,
    description: str,
    transaction_date: str
) -> str:
    """
    Add a new transaction to the database.
    type must be either 'income' or 'expense'.
    transaction_date must be in YYYY-MM-DD format.
    Returns the created transaction as JSON.
    """
    db = get_db()
    try:
        transaction = add_transaction(
            db,
            amount=amount,
            category=category,
            type=type,
            description=description,
            transaction_date=transaction_date
        )
        return json.dumps({
            "id": transaction.id,
            "amount": float(transaction.amount),
            "category": transaction.category,
            "type": transaction.type,
            "description": transaction.description,
            "date": str(transaction.date)
        })
    finally:
        db.close()


@mcp.tool()
def fetch_budget_summary(month: int, year: int) -> str:
    """
    Get budget summary for a given month and year.
    Shows how much was spent vs the limit for each category.
    Returns list of categories with spent and remaining amounts.
    """
    db = get_db()
    try:
        summary = get_budget_summary(db, month=month, year=year)
        return json.dumps(summary)
    finally:
        db.close()


@mcp.tool()
def fetch_spending_alerts(month: int, year: int) -> str:
    """
    Get categories where spending has exceeded the monthly budget limit.
    Returns a list of overspent categories with how much they went over.
    """
    db = get_db()
    try:
        summary = get_budget_summary(db, month=month, year=year)
        alerts = [
            {
                "category": s["category"],
                "monthly_limit": s["monthly_limit"],
                "spent": s["spent"],
                "overspent_by": round(s["spent"] - s["monthly_limit"], 2)
            }
            for s in summary
            if s["spent"] > s["monthly_limit"]
        ]
        if not alerts:
            return json.dumps({"message": "No overspending detected. Great job!"})
        return json.dumps(alerts)
    finally:
        db.close()


@mcp.tool()
def fetch_bills(status: str = None) -> str:
    """
    Fetch all bills. Optionally filter by status: 'paid' or 'unpaid'.
    Returns a list of bills as JSON.
    """
    db = get_db()
    try:
        bills = get_bills(db, status=status)
        result = [
            {
                "id": b.id,
                "name": b.name,
                "amount": float(b.amount),
                "due_date": str(b.due_date),
                "status": b.status,
                "is_recurring": b.is_recurring,
                "category": b.category
            }
            for b in bills
        ]
        return json.dumps(result)
    finally:
        db.close()


@mcp.tool()
def fetch_overdue_bills() -> str:
    """
    Get all bills that are unpaid and past their due date.
    Returns a list of overdue bills as JSON.
    """
    db = get_db()
    try:
        bills = get_overdue_bills(db)
        result = [
            {
                "id": b.id,
                "name": b.name,
                "amount": float(b.amount),
                "due_date": str(b.due_date),
                "category": b.category
            }
            for b in bills
        ]
        if not result:
            return json.dumps({"message": "No overdue bills. You are all caught up!"})
        return json.dumps(result)
    finally:
        db.close()


@mcp.tool()
def pay_bill(bill_id: int) -> str:
    """
    Mark a bill as paid by its ID.
    Returns the updated bill as JSON.
    """
    db = get_db()
    try:
        bill = mark_bill_paid(db, bill_id)
        if not bill:
            return json.dumps({"error": f"Bill with id {bill_id} not found"})
        return json.dumps({
            "id": bill.id,
            "name": bill.name,
            "amount": float(bill.amount),
            "due_date": str(bill.due_date),
            "status": bill.status
        })
    finally:
        db.close()


@mcp.tool()
def add_bill(
    name: str,
    amount: float,
    due_date: str,
    is_recurring: bool,
    category: str
) -> str:
    """
    Schedule a new bill.
    due_date must be in YYYY-MM-DD format.
    Returns the created bill as JSON.
    """
    db = get_db()
    try:
        bill = schedule_bill(
            db,
            name=name,
            amount=amount,
            due_date=due_date,
            is_recurring=is_recurring,
            category=category
        )
        return json.dumps({
            "id": bill.id,
            "name": bill.name,
            "amount": float(bill.amount),
            "due_date": str(bill.due_date),
            "status": bill.status,
            "is_recurring": bill.is_recurring,
            "category": bill.category
        })
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════
# RESOURCES — Read-only data the app can access directly
# ═══════════════════════════════════════════════════════════════

@mcp.resource("finance://budgets")
def budget_rules() -> str:
    """
    Read-only resource exposing all budget limits per category.
    Use this to understand what the spending limits are.
    """
    db = get_db()
    try:
        budgets = get_budgets(db)
        result = [
            {
                "category": b.category,
                "monthly_limit": float(b.monthly_limit)
            }
            for b in budgets
        ]
        return json.dumps(result)
    finally:
        db.close()


@mcp.resource("finance://transactions/recent")
def recent_transactions() -> str:
    """
    Read-only resource exposing the last 30 days of transactions.
    Use this to get a quick snapshot of recent spending.
    """
    db = get_db()
    try:
        today = date.today()
        transactions = get_transactions(
            db,
            month=today.month,
            year=today.year
        )
        result = [
            {
                "id": t.id,
                "amount": float(t.amount),
                "category": t.category,
                "type": t.type,
                "description": t.description,
                "date": str(t.date)
            }
            for t in transactions
        ]
        return json.dumps(result)
    finally:
        db.close()


@mcp.resource("finance://monthly-report/{month}/{year}")
def monthly_report(month: str, year: str) -> str:
    """
    Templated resource that returns a full monthly report
    for the given month and year.
    Includes transactions, budget summary and unpaid bills.
    """
    db = get_db()
    try:
        transactions = get_transactions(db, month=int(month), year=int(year))
        summary = get_budget_summary(db, month=int(month), year=int(year))
        bills = get_bills(db, status='unpaid')

        report = {
            "month": month,
            "year": year,
            "total_transactions": len(transactions),
            "total_spent": sum(
                float(t.amount) for t in transactions if t.type == 'expense'
            ),
            "total_income": sum(
                float(t.amount) for t in transactions if t.type == 'income'
            ),
            "budget_summary": summary,
            "unpaid_bills": [
                {
                    "name": b.name,
                    "amount": float(b.amount),
                    "due_date": str(b.due_date)
                }
                for b in bills
            ]
        }
        return json.dumps(report)
    finally:
        db.close()


# ═══════════════════════════════════════════════════════════════
# PROMPTS — Pre-crafted instructions for common workflows
# ═══════════════════════════════════════════════════════════════

@mcp.prompt()
def analyze_spending(month: str, year: str) -> str:
    """
    Prompt that instructs the AI to analyze spending
    for a given month and provide actionable advice.
    """
    return f"""
    You are a personal finance advisor. Analyze the user's spending for {month}/{year}.

    Follow these steps:
    1. Use fetch_transactions to get all transactions for {month}/{year}
    2. Use fetch_budget_summary to get spending vs limits for each category
    3. Use fetch_spending_alerts to identify overspent categories
    4. Use fetch_overdue_bills to check for any overdue bills

    Then provide:
    - A summary of total income vs total expenses
    - Top 3 spending categories
    - Any categories where the user overspent and by how much
    - Any overdue bills that need immediate attention
    - 3 specific, actionable tips to improve their finances next month

    Be friendly, specific, and use actual numbers from the data.
    """


@mcp.prompt()
def create_budget_plan(monthly_income: str) -> str:
    """
    Prompt that instructs the AI to create a personalized
    budget plan based on income and current spending patterns.
    """
    return f"""
    You are a personal finance advisor. Create a budget plan for someone
    with a monthly income of ${monthly_income}.

    Follow these steps:
    1. Use fetch_budget_summary for the current month to understand current spending
    2. Use resource finance://budgets to see current budget limits

    Then create a budget plan that:
    - Follows the 50/30/20 rule (50% needs, 30% wants, 20% savings)
    - Compares current spending against the recommended amounts
    - Suggests specific adjustments per category
    - Highlights which categories need immediate reduction
    - Sets realistic targets for next month

    Present the plan in a clear, structured way with specific dollar amounts.
    """


@mcp.prompt()
def payment_planning() -> str:
    """
    Prompt that instructs the AI to review upcoming bills
    and create a payment priority plan.
    """
    return f"""
    You are a personal finance advisor helping with bill payment planning.

    Follow these steps:
    1. Use fetch_overdue_bills to get all overdue bills
    2. Use fetch_bills with status='unpaid' to get all upcoming unpaid bills
    3. Use fetch_budget_summary for the current month to check available funds

    Then provide:
    - List of overdue bills that need IMMEDIATE payment
    - Upcoming bills sorted by due date
    - Total amount needed to clear all unpaid bills
    - Recommended payment order based on due date and amount
    - Warning if total unpaid bills exceed available budget

    Be direct and urgent about overdue items.
    """


# ═══════════════════════════════════════════════════════════════
# Run the server
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    mcp.run()