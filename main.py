from typing import List
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI()

# Add CORSMiddleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup (using SQLite for simplicity)
DATABASE_URL = "sqlite:///./tasks.db"

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Task model for database
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    date = Column(String)  # Store the date
    time = Column(String)  # Store the time
    completed = Column(Boolean, default=False)


# Create the tables in the database
Base.metadata.create_all(bind=engine)

# Pydantic model for task input validation (used for creating a task)
class TaskCreate(BaseModel):
    name: str
    date: str
    time: str
    completed: bool = False


# Pydantic model for task response (includes id)
class TaskResponse(BaseModel):
    id: int
    name: str
    date: str
    time: str
    completed: bool

    class Config:
        orm_mode = True


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# GET endpoint to retrieve all tasks
@app.get("/tasks")
def get_tasks(db: Session = Depends(get_db)):
    try:
        tasks = db.query(Task).all()  # Query all tasks
        return tasks  # Return the tasks list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  # Catch the error and return it


# POST endpoint to create a new task
@app.post("/tasks", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(
        name=task.name,
        date=task.date,
        time=task.time,
        completed=task.completed,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


# PUT endpoint to update an existing task
@app.put("/tasks/{task_id}", response_model=TaskResponse)
def put_task(task_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    db_task = db.query(Task).filter(Task.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.name = task.name
    db_task.date = task.date
    db_task.time = task.time
    db_task.completed = task.completed
    db.commit()
    db.refresh(db_task)
    return db_task


# from sqlalchemy.orm import Session
# from fastapi import Depends
# from main import Task, SessionLocal

# db = SessionLocal()
# new_task = Task(name="Test Task", date="2025-01-01", time="10:00", completed=False)
# db.add(new_task)
# db.commit()
# db.refresh(new_task)
# print(new_task.id)  # Prints the ID of the inserted task
# db.close()

