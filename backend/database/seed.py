import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import engine, Base, SessionLocal
from models import Transaction, Budget, Bill


def seed():
    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Clear existing data
    db.query(Bill).delete()
    db.query(Transaction).delete()
    db.query(Budget).delete()
    db.commit()

    # ─── Budgets ──────────────────────────────────────────────
    budgets = [
        Budget(category='Food', monthly_limit=500.00),
        Budget(category='Rent', monthly_limit=1500.00),
        Budget(category='Entertainment', monthly_limit=200.00),
        Budget(category='Transport', monthly_limit=150.00),
        Budget(category='Utilities', monthly_limit=200.00),
        Budget(category='Shopping', monthly_limit=300.00),
        Budget(category='Health', monthly_limit=150.00),
        Budget(category='Savings', monthly_limit=500.00),
    ]
    db.add_all(budgets)
    db.commit()

    # ─── Transactions ─────────────────────────────────────────
    transactions = [
        # Income
        Transaction(amount=5000.00, category='Salary', type='income', description='Monthly salary', date='2025-02-01'),
        Transaction(amount=5000.00, category='Salary', type='income', description='Monthly salary', date='2025-03-01'),
        Transaction(amount=5000.00, category='Salary', type='income', description='Monthly salary', date='2025-04-01'),
        # Food
        Transaction(amount=120.00, category='Food', type='expense', description='Grocery shopping', date='2025-02-05'),
        Transaction(amount=45.00, category='Food', type='expense', description='Restaurant dinner', date='2025-02-12'),
        Transaction(amount=85.00, category='Food', type='expense', description='Weekly groceries', date='2025-02-20'),
        Transaction(amount=200.00, category='Food', type='expense', description='Grocery shopping', date='2025-03-03'),
        Transaction(amount=150.00, category='Food', type='expense', description='Dinner party supplies', date='2025-03-15'),
        Transaction(amount=210.00, category='Food', type='expense', description='Weekly groceries', date='2025-03-25'),
        Transaction(amount=95.00, category='Food', type='expense', description='Grocery shopping', date='2025-04-04'),
        Transaction(amount=60.00, category='Food', type='expense', description='Restaurant lunch', date='2025-04-10'),
        # Rent
        Transaction(amount=1500.00, category='Rent', type='expense', description='Monthly rent', date='2025-02-01'),
        Transaction(amount=1500.00, category='Rent', type='expense', description='Monthly rent', date='2025-03-01'),
        Transaction(amount=1500.00, category='Rent', type='expense', description='Monthly rent', date='2025-04-01'),
        # Entertainment
        Transaction(amount=15.00, category='Entertainment', type='expense', description='Netflix subscription', date='2025-02-08'),
        Transaction(amount=60.00, category='Entertainment', type='expense', description='Movie night', date='2025-02-14'),
        Transaction(amount=15.00, category='Entertainment', type='expense', description='Netflix subscription', date='2025-03-08'),
        Transaction(amount=120.00, category='Entertainment', type='expense', description='Concert tickets', date='2025-03-20'),
        Transaction(amount=15.00, category='Entertainment', type='expense', description='Netflix subscription', date='2025-04-08'),
        Transaction(amount=80.00, category='Entertainment', type='expense', description='Sports event', date='2025-04-12'),
        # Transport
        Transaction(amount=50.00, category='Transport', type='expense', description='Gas', date='2025-02-10'),
        Transaction(amount=30.00, category='Transport', type='expense', description='Uber rides', date='2025-02-22'),
        Transaction(amount=50.00, category='Transport', type='expense', description='Gas', date='2025-03-10'),
        Transaction(amount=45.00, category='Transport', type='expense', description='Uber rides', date='2025-03-18'),
        Transaction(amount=50.00, category='Transport', type='expense', description='Gas', date='2025-04-10'),
        # Utilities
        Transaction(amount=100.00, category='Utilities', type='expense', description='Electricity bill', date='2025-02-15'),
        Transaction(amount=80.00, category='Utilities', type='expense', description='Internet bill', date='2025-02-15'),
        Transaction(amount=105.00, category='Utilities', type='expense', description='Electricity bill', date='2025-03-15'),
        Transaction(amount=80.00, category='Utilities', type='expense', description='Internet bill', date='2025-03-15'),
        Transaction(amount=98.00, category='Utilities', type='expense', description='Electricity bill', date='2025-04-15'),
        # Shopping
        Transaction(amount=250.00, category='Shopping', type='expense', description='Clothes', date='2025-02-18'),
        Transaction(amount=180.00, category='Shopping', type='expense', description='Electronics accessories', date='2025-03-22'),
        Transaction(amount=90.00, category='Shopping', type='expense', description='Home supplies', date='2025-04-05'),
        # Health
        Transaction(amount=100.00, category='Health', type='expense', description='Gym membership', date='2025-02-01'),
        Transaction(amount=100.00, category='Health', type='expense', description='Gym membership', date='2025-03-01'),
        Transaction(amount=100.00, category='Health', type='expense', description='Gym membership', date='2025-04-01'),
        # Savings
        Transaction(amount=500.00, category='Savings', type='expense', description='Monthly savings transfer', date='2025-02-28'),
        Transaction(amount=500.00, category='Savings', type='expense', description='Monthly savings transfer', date='2025-03-31'),
        Transaction(amount=500.00, category='Savings', type='expense', description='Monthly savings transfer', date='2025-04-30'),
    ]
    db.add_all(transactions)
    db.commit()

    # ─── Bills ────────────────────────────────────────────────
    bills = [
        Bill(name='Netflix', amount=15.00, due_date='2025-04-08', status='paid', is_recurring=True, category='Entertainment'),
        Bill(name='Electricity', amount=98.00, due_date='2025-04-15', status='unpaid', is_recurring=True, category='Utilities'),
        Bill(name='Internet', amount=80.00, due_date='2025-04-15', status='unpaid', is_recurring=True, category='Utilities'),
        Bill(name='Gym Membership', amount=100.00, due_date='2025-04-01', status='paid', is_recurring=True, category='Health'),
        Bill(name='Rent', amount=1500.00, due_date='2025-04-01', status='paid', is_recurring=True, category='Rent'),
        Bill(name='Car Insurance', amount=120.00, due_date='2025-04-20', status='unpaid', is_recurring=False, category='Transport'),
        Bill(name='Phone Bill', amount=60.00, due_date='2025-04-18', status='unpaid', is_recurring=True, category='Utilities'),
        Bill(name='Spotify', amount=10.00, due_date='2025-04-10', status='unpaid', is_recurring=True, category='Entertainment'),
    ]
    db.add_all(bills)
    db.commit()

    db.close()
    print("✅ Database seeded successfully!")


if __name__ == "__main__":
    seed()