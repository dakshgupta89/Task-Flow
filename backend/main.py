"""TaskFlow — FastAPI backend with CRUD, statistics, sort/search, and AI quick-add."""

import os
import time
import logging

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import engine, Base, get_db
from models import User, Project, Task
from schemas import (
    UserCreate,
    UserResponse,
    ProjectCreate,
    ProjectResponse,
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    QuickAddRequest,
    StatsResponse,
)
from algorithms import insertion_sort, binary_search, linear_search
from ai_parser import parse_task_from_description

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - MIDDLEWARE - %(message)s",
)
logger = logging.getLogger("taskflow")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskFlow", version="1.0.0")

# CORS — explicit origin matching the frontend's local server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# ---------------------------------------------------------------------------
# Custom middleware — logs method, path, and processing time on every request
# ---------------------------------------------------------------------------

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000
    logger.info(f"{request.method} {request.url.path} - {duration_ms:.2f}ms")
    return response


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(email=user.email, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

@app.post("/projects", response_model=ProjectResponse, status_code=201)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == project.owner_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Owner user not found")
    db_project = Project(
        name=project.name,
        description=project.description,
        owner_id=project.owner_id,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@app.get("/projects", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()


@app.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


# ---------------------------------------------------------------------------
# Tasks — CRUD
# ---------------------------------------------------------------------------

PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}


@app.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == task.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db_task = Task(
        title=task.title,
        priority=task.priority,
        status=task.status,
        due_date=task.due_date,
        project_id=task.project_id,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks(
    sort: str | None = Query(None, description="Sort by: priority or due_date"),
    db: Session = Depends(get_db),
):
    tasks = db.query(Task).all()

    if sort == "priority":
        records = [
            {
                "id": t.id,
                "title": t.title,
                "priority": t.priority,
                "priority_rank": PRIORITY_RANK.get(t.priority, 2),
                "status": t.status,
                "due_date": t.due_date,
                "project_id": t.project_id,
            }
            for t in tasks
        ]
        insertion_sort(records, "priority_rank")
        return records

    elif sort == "due_date":
        records = [
            {
                "id": t.id,
                "title": t.title,
                "priority": t.priority,
                "status": t.status,
                "due_date": t.due_date if t.due_date is not None else "~~~",
                "project_id": t.project_id,
            }
            for t in tasks
        ]
        insertion_sort(records, "due_date")
        return records

    return tasks


# Search endpoint must be declared before /tasks/{task_id} to avoid route conflict.
@app.get("/tasks/search", response_model=TaskResponse)
def search_task(
    title: str = Query(..., description="Exact title text to search"),
    algo: str = Query("binary", description="Search algorithm: binary or linear"),
    db: Session = Depends(get_db),
):
    tasks = db.query(Task).all()
    index = [{"id": t.id, "title": t.title} for t in tasks]

    if algo == "linear":
        idx = linear_search(index, title, "title")
    else:
        insertion_sort(index, "title")
        idx = binary_search(index, title, "title")

    if idx == -1:
        raise HTTPException(status_code=404, detail="Task not found")

    task_id = index[idx]["id"]
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return None


# ---------------------------------------------------------------------------
# Statistics — SQL aggregate (COUNT + GROUP BY) across projects↔tasks join
# ---------------------------------------------------------------------------

@app.get("/projects/{project_id}/stats", response_model=StatsResponse)
def project_stats(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    total = (
        db.query(func.count(Task.id))
        .filter(Task.project_id == project_id)
        .scalar()
    )

    status_counts = (
        db.query(Task.status, func.count(Task.id))
        .filter(Task.project_id == project_id)
        .group_by(Task.status)
        .all()
    )
    counts_map = {row[0]: row[1] for row in status_counts}

    return StatsResponse(
        project_id=project_id,
        project_name=project.name,
        total_tasks=total or 0,
        pending=counts_map.get("pending", 0),
        in_progress=counts_map.get("in_progress", 0),
        done=counts_map.get("done", 0),
    )


# ---------------------------------------------------------------------------
# AI Quick-Add (Section 3)
# ---------------------------------------------------------------------------

@app.post("/tasks/quick-add", response_model=TaskResponse, status_code=201)
def quick_add_task(body: QuickAddRequest, db: Session = Depends(get_db)):
    # Validate project exists
    project = db.query(Project).filter(Project.id == body.project_id).first()
    if not project:
        raise HTTPException(status_code=422, detail="project_id does not reference an existing project")

    # Parse the free-text description using the mock parser
    parsed = parse_task_from_description(body.description)

    # Validate parsed fields against the Pydantic model before persisting
    try:
        validated = TaskCreate(
            title=parsed["title"],
            priority=parsed["priority"],
            status="pending",
            due_date=parsed["due_date"],
            project_id=body.project_id,
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Validation failed: {str(e)}")

    db_task = Task(
        title=validated.title,
        priority=validated.priority,
        status=validated.status,
        due_date=validated.due_date,
        project_id=validated.project_id,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.get("/")
def root():
    return {"message": "TaskFlow API is running", "docs": "/docs"}
