import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, UUID, JSON, BigInteger, Date, CheckConstraint
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    status = Column(Text, CheckConstraint("status IN ('active','suspended','deleted')"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    retention_days = Column(Integer)
    metadata_json = Column(JSON)


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    email = Column(Text, nullable=False)
    hashed_password = Column(Text, nullable=False)
    role = Column(Text, CheckConstraint("role IN ('admin','user','viewer')"))
    status = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime)


class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    hashed_key = Column(Text, nullable=False)
    scope = Column(Text)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    actor_id = Column(UUID(as_uuid=True))
    action = Column(Text)
    resource_type = Column(Text)
    resource_id = Column(UUID(as_uuid=True))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class DataSource(Base):
    __tablename__ = "data_sources"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    name = Column(Text)
    type = Column(Text, CheckConstraint("type IN ('text','image','audio','video')"))
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata_json = Column(JSON)


class IngestedObject(Base):
    __tablename__ = "ingested_objects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    data_source_id = Column(UUID(as_uuid=True), ForeignKey("data_sources.id"))
    cloudfront_url = Column(Text)
    content_type = Column(Text)
    size_bytes = Column(BigInteger)
    checksum = Column(Text)
    ingestion_status = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)


class ChatSession(Base):
    __tablename__ = "chat_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    system_prompt = Column(Text)
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"))
    role = Column(Text, CheckConstraint("role IN ('user','assistant','system','tool')"))
    content = Column(Text)
    references = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    ingested_object_id = Column(UUID(as_uuid=True), ForeignKey("ingested_objects.id"))
    content = Column(Text, nullable=False)
    embedding = Column(JSON) # Placeholder for PGVector column type if using custom libs
    metadata_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
