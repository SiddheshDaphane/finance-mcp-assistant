from sqlalchemy import Column, Integer, String, Numeric, Date, Boolean, Text, TIMESTAMP, CheckConstraint
from sqlalchemy.sql import func
from database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    category = Column(String(50), nullable=False)
    type = Column(String(10), nullable=False)
    description = Column(Text)
    date = Column(Date, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        CheckConstraint("type IN ('income', 'expense')", name="check_transaction_type"),
    )


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), unique=True, nullable=False)
    monthly_limit = Column(Numeric(10, 2), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())


class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    due_date = Column(Date, nullable=False)
    status = Column(String(10), nullable=False, default="unpaid")
    is_recurring = Column(Boolean, default=False)
    category = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (
        CheckConstraint("status IN ('paid', 'unpaid')", name="check_bill_status"),
    )