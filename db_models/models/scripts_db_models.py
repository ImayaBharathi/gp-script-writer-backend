import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Enum, Text, Identity, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


from ..db_setup import Base
from .mixins import Timestamp
from .users_db_models import User


class Script(Timestamp, Base):
    __tablename__ = 'scripts'

    script_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default= uuid.uuid4)
    title = Column(String)
    genre = Column(String)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    last_modified_at = Column(DateTime, onupdate=datetime.utcnow)
    logline = Column(String)
    user = relationship("User", backref="scripts")

class ScriptVersion(Timestamp, Base):
    __tablename__ = 'script_versions'

    version_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default= uuid.uuid4)
    script_id = Column(UUID(as_uuid=True), ForeignKey('scripts.script_id'))
    version_number = Column(UUID(as_uuid=True), index=True, default= uuid.uuid4)
    content = Column(Text)
    script_file_url = Column(String)
    change_summary = Column(String)
    modified_by = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))

    # Relationships
    script = relationship("Script", backref="script_versions")
    user = relationship("User", backref="modified_versions")


class ScriptActivity(Timestamp,Base):
    __tablename__ = 'script_activity'

    script_activity_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default= uuid.uuid4)
    activity_id = Column(UUID(as_uuid=True), ForeignKey('user_activity.activity_id'))
    script_id = Column(UUID(as_uuid=True), ForeignKey('scripts.script_id'))

    # Relationships
    user_activity = relationship("UserActivity", backref="script_activities")
    script = relationship("Script", backref="script_activities")

class SharedScripts(Timestamp, Base):
    __tablename__ = 'shared_scripts'

    shared_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default= uuid.uuid4)
    script_id = Column(UUID(as_uuid=True), ForeignKey('scripts.script_id'))
    shared_with_identifier = Column(String)
    shared_by_user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    access_token = Column(String)
    expiration_date = Column(DateTime)
    permission_level = Column(String)

    # Relationships
    script = relationship("Script", backref="shared_scripts")
    shared_by_user = relationship("User", foreign_keys=[shared_by_user_id])

