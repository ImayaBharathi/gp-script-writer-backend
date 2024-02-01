import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Enum, Text, Identity, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID


from ..db_setup import Base
from .mixins import Timestamp
from .users_db_models import User
from .scripts_db_models import Script

class Projects(Timestamp,Base):
    __tablename__ = 'projects'
    project_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default= uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    project_name = Column(String, nullable=True)
    # project_name = Column(String, server_default=func.concat('Untitled Project ', func.cast(func.next_value(), String)), nullable=False)
    # project_name = Column(String, nullable=False, server_default=func.concat('Untitled Project ', func.cast(func.next_value(), String)))
    scripts = relationship("ProjectScripts", back_populates="project")

class ProjectScripts(Timestamp,Base):
    __tablename__ = 'project_scripts'
    project_script_id = Column(UUID(as_uuid=True), primary_key=True, index=True, default= uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.project_id'))
    script_id = Column(UUID(as_uuid=True), ForeignKey('scripts.script_id')) 
    project = relationship("Projects", back_populates="scripts")
    # script = relationship("Scripts", back_populates="projects")
