from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Enum, Text, Date, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum
from datetime import datetime, date

class UserRole(str, enum.Enum):
    ADMIN = "admin"; PM = "pm"; CREATIVE = "creative"; CLIENT = "client"
class ProjectStatus(str, enum.Enum):
    ACTIVE = "active"; ARCHIVED = "archived"
class MilestoneStatus(str, enum.Enum):
    PENDING = "pending"; IN_PROGRESS = "in_progress"; IN_REVIEW = "in_review"; COMPLETED = "completed"; APPROVED = "approved"
class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"; SENT = "sent"; PAID = "paid"; OVERDUE = "overdue"; CANCELLED = "cancelled"
class DeliverableStatus(str, enum.Enum):
    DRAFT = "draft"; IN_REVIEW = "in_review"; APPROVED = "approved"
class AITaskStatus(str, enum.Enum):
    PENDING = "pending"; PROCESSING = "processing"; COMPLETED = "completed"; FAILED = "failed"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    workspace_memberships: Mapped[list["WorkspaceMember"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    owned_workspaces: Mapped[list["Workspace"]] = relationship(back_populates="owner")

class Workspace(Base):
    __tablename__ = "workspaces"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    owner: Mapped["User"] = relationship(back_populates="owned_workspaces")
    members: Mapped[list["WorkspaceMember"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")
    projects: Mapped[list["Project"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")
    clients: Mapped[list["Client"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")

class WorkspaceMember(Base):
    __tablename__ = "workspace_members"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.CREATIVE, nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    workspace: Mapped["Workspace"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="workspace_memberships")

class Client(Base):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True) # NEW
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    workspace: Mapped["Workspace"] = relationship(back_populates="clients")
    projects: Mapped[list["Project"]] = relationship(back_populates="client")

class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(Integer, ForeignKey("workspaces.id", ondelete="CASCADE"), nullable=False)
    client_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("clients.id", ondelete="SET NULL"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    workspace: Mapped["Workspace"] = relationship(back_populates="projects")
    client: Mapped["Client | None"] = relationship(back_populates="projects")
    milestones: Mapped[list["Milestone"]] = relationship(back_populates="project", cascade="all, delete-orphan")

class Milestone(Base):
    __tablename__ = "milestones"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[MilestoneStatus] = mapped_column(Enum(MilestoneStatus), default=MilestoneStatus.PENDING, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    project: Mapped["Project"] = relationship(back_populates="milestones")
    invoice: Mapped["Invoice | None"] = relationship(back_populates="milestone", uselist=False, cascade="all, delete-orphan")
    deliverables: Mapped[list["Deliverable"]] = relationship(back_populates="milestone", cascade="all, delete-orphan")

class Invoice(Base):
    __tablename__ = "invoices"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    milestone_id: Mapped[int] = mapped_column(Integer, ForeignKey("milestones.id", ondelete="CASCADE"), unique=True, nullable=False)
    stripe_invoice_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    hosted_invoice_url: Mapped[str | None] = mapped_column(String(500), nullable=True) # NEW
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[InvoiceStatus] = mapped_column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    milestone: Mapped["Milestone"] = relationship(back_populates="invoice")

class Deliverable(Base):
    __tablename__ = "deliverables"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    milestone_id: Mapped[int] = mapped_column(Integer, ForeignKey("milestones.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[DeliverableStatus] = mapped_column(Enum(DeliverableStatus), default=DeliverableStatus.DRAFT, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    milestone: Mapped["Milestone"] = relationship(back_populates="deliverables")
    comments: Mapped[list["Comment"]] = relationship(back_populates="deliverable", cascade="all, delete-orphan")
    ai_tasks: Mapped[list["AITask"]] = relationship(back_populates="deliverable", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    deliverable_id: Mapped[int] = mapped_column(Integer, ForeignKey("deliverables.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    x_coord: Mapped[float | None] = mapped_column(Float, nullable=True)
    y_coord: Mapped[float | None] = mapped_column(Float, nullable=True)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    deliverable: Mapped["Deliverable"] = relationship(back_populates="comments")
    user: Mapped["User"] = relationship()
    parent: Mapped["Comment | None"] = relationship(remote_side=[id], back_populates="replies")
    replies: Mapped[list["Comment"]] = relationship(back_populates="parent", cascade="all, delete-orphan")

class AITask(Base):
    __tablename__ = "ai_tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    deliverable_id: Mapped[int] = mapped_column(Integer, ForeignKey("deliverables.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[AITaskStatus] = mapped_column(Enum(AITaskStatus), default=AITaskStatus.PENDING, nullable=False)
    result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    deliverable: Mapped["Deliverable"] = relationship(back_populates="ai_tasks")