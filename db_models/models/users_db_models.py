import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Enum, Text, Identity, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


from ..db_setup import Base
from .mixins import Timestamp


class User(Timestamp, Base):
    __tablename__ = 'users'

    user_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default= uuid.uuid4)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    other_info = Column(String)
    is_active = Column(Boolean, default=True)

class GoogleAuth(Timestamp, Base):
    __tablename__ = 'google_auth'

    google_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default= uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    google_unique_id_for_user = Column(UUID(as_uuid=True))
    other_google_data = Column(String)

    user = relationship("User", backref="google_auth")

class AppleAuth(Timestamp, Base):
    __tablename__ = 'apple_auth'

    apple_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default= uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    other_apple_data = Column(String)

    user = relationship("User", backref="apple_auth")

class UserDetails(Timestamp, Base):
    __tablename__ = 'user_details'

    user_details_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default= uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    other_info = Column(String)
    
    user = relationship("User", backref="user_details")

class UserActivity(Timestamp,Base):
    __tablename__ = 'user_activity'

    activity_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default= uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    activity_type = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="user_activities")

