"""Pydantic request/response models with field constraints and custom validators."""

from pydantic import BaseModel, Field, field_validator


class UserCreate(BaseModel):
    email: str
    name: str


class UserResponse(BaseModel):
    id: int
    email: str
    name: str

    model_config = {"from_attributes": True}


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    owner_id: int


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None
    owner_id: int

    model_config = {"from_attributes": True}


class TaskBase(BaseModel):
    title: str
    priority: str = Field(default="medium", pattern="^(low|medium|high)$")
    status: str = Field(default="pending", pattern="^(pending|in_progress|done)$")
    due_date: str | None = None
    project_id: int


class TaskCreate(TaskBase):
    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("title must not be blank or whitespace-only")
        return v


class TaskUpdate(BaseModel):
    title: str | None = None
    priority: str | None = Field(default=None, pattern="^(low|medium|high)$")
    status: str | None = Field(default=None, pattern="^(pending|in_progress|done)$")
    due_date: str | None = None
    project_id: int | None = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("title must not be blank or whitespace-only")
        return v


class TaskResponse(BaseModel):
    id: int
    title: str
    priority: str
    status: str
    due_date: str | None
    project_id: int

    model_config = {"from_attributes": True}


class QuickAddRequest(BaseModel):
    description: str
    project_id: int


class StatsResponse(BaseModel):
    project_id: int
    project_name: str
    total_tasks: int
    pending: int
    in_progress: int
    done: int
