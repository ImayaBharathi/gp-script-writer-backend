import enum
import uuid
from datetime import datetime

from sqlalchemy import (Boolean, Column, ForeignKey, 
                        Integer, String, Enum, Text,
                        Identity, DateTime, Numeric)

from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


from ..db_setup import Base
from .mixins import Timestamp
from .users_db_models import User

class SubscriptionPlans(Timestamp,Base):
    __tablename__ = 'subscription_plans'

    plan_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default= uuid.uuid4)
    plan_name = Column(String)
    price = Column(Numeric(precision=10, scale=2))  # Adjust precision and scale as needed
    billing_cycle = Column(String) #(e.g., 'Monthly', 'Yearly', etc.).

class Subscriptions(Timestamp,Base):
    __tablename__ = 'subscriptions'

    subscription_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default= uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    plan_id = Column(UUID(as_uuid=True), ForeignKey('subscription_plans.plan_id'))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)

    # Relationships
    user = relationship("User", backref="subscriptions")
    plan = relationship("SubscriptionPlans", backref="subscriptions")

class Payments(Timestamp,Base):
    __tablename__ = 'payments'

    payment_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default= uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey('subscriptions.subscription_id'))
    amount = Column(Numeric(precision=10, scale=2))  # Adjust precision and scale as needed
    payment_date = Column(DateTime)

    # Other payment-related fields can be added as needed

class FailedTransactions(Timestamp,Base):
    __tablename__ = 'failed_transactions'

    failed_transaction_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default= uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    transaction_date = Column(DateTime)
    error_message = Column(String)  