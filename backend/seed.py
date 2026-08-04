"""Seed the database with sample users, projects, and tasks for testing."""

import sys
import os

# Ensure the backend directory is on the path when run from anywhere
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine, SessionLocal, Base
from models import User, Project, Task

Base.metadata.create_all(bind=engine)


def seed():
    db = SessionLocal()

    # Check if already seeded
    if db.query(User).first():
        print("Database already has data. Clearing existing data...")
        db.query(Task).delete()
        db.query(Project).delete()
        db.query(User).delete()
        db.commit()

    # Create users
    alice = User(email="alice@blinkit.com", name="Alice Sharma")
    bob = User(email="bob@blinkit.com", name="Bob Verma")
    db.add(alice)
    db.add(bob)
    db.commit()
    db.refresh(alice)
    db.refresh(bob)

    # Create projects
    proj1 = Project(name="Dark Store Dashboard", description="Operations dashboard for dark stores", owner_id=alice.id)
    proj2 = Project(name="Inventory Sync", description="Real-time inventory sync system", owner_id=bob.id)
    db.add(proj1)
    db.add(proj2)
    db.commit()
    db.refresh(proj1)
    db.refresh(proj2)

    # Create tasks for project 1
    tasks_p1 = [
        Task(title="Design login page", priority="high", status="done", due_date="today", project_id=proj1.id),
        Task(title="Build task list component", priority="medium", status="in_progress", due_date="tomorrow", project_id=proj1.id),
        Task(title="Write API documentation", priority="low", status="pending", due_date="next friday", project_id=proj1.id),
        Task(title="Set up CI pipeline", priority="high", status="pending", due_date=None, project_id=proj1.id),
        Task(title="Database migration script", priority="medium", status="done", due_date="monday", project_id=proj1.id),
    ]

    tasks_p2 = [
        Task(title="Real-time stock sync", priority="high", status="in_progress", due_date="next monday", project_id=proj2.id),
        Task(title="Handle edge cases for missing SKUs", priority="medium", status="pending", due_date=None, project_id=proj2.id),
        Task(title="Write integration tests", priority="low", status="pending", due_date="next week", project_id=proj2.id),
    ]

    for t in tasks_p1 + tasks_p2:
        db.add(t)
    db.commit()

    print(f"Seeded {2} users, {2} projects, and {len(tasks_p1) + len(tasks_p2)} tasks.")
    print(f"  Users: Alice (id={alice.id}), Bob (id={bob.id})")
    print(f"  Projects: Dark Store Dashboard (id={proj1.id}), Inventory Sync (id={proj2.id})")
    db.close()


if __name__ == "__main__":
    seed()
