import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from app.database import engine, Base
from app.routes import students

# Create the SQLite database tables (if they don't exist)
Base.metadata.create_all(bind=engine)

# Seed database if it is empty
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.student import Student

db = SessionLocal()
try:
    if db.query(Student).count() == 0:
        sample_students = [
            Student(first_name="Jane", last_name="Smith", student_id="S1001", course="FastAPI Development", grade="A+", attendance=98.0),
            Student(first_name="John", last_name="Doe", student_id="S1002", course="Python Basics", grade="C+", attendance=85.0),
            Student(first_name="Emily", last_name="Johnson", student_id="S1003", course="Data Science", grade="B", attendance=92.5),
            Student(first_name="Michael", last_name="Brown", student_id="S1004", course="FastAPI Development", grade="F", attendance=58.0),
            Student(first_name="Sarah", last_name="Davis", student_id="S1005", course="Data Science", grade="D", attendance=70.0),
            Student(first_name="William", last_name="Wilson", student_id="S1006", course="Python Basics", grade="Pass", attendance=90.0),
            Student(first_name="Olivia", last_name="Taylor", student_id="S1007", course="Machine Learning", grade="A", attendance=96.0),
            Student(first_name="James", last_name="Martinez", student_id="S1008", course="Machine Learning", grade="Fail", attendance=62.0)
        ]
        db.add_all(sample_students)
        db.commit()
finally:
    db.close()

app = FastAPI(
    title="Student Management System API",
    description="A FastAPI backend for managing student records using SQLAlchemy and SQLite.",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(students.router)

# Mount static directory for JS/CSS assets
# We resolve the path relative to this file to prevent issues on Vercel
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/", response_class=HTMLResponse)
def read_root():
    index_path = os.path.join(static_dir, "index.html")
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Frontend index.html not found! Please make sure app/static/index.html is created.</h1>", 
            status_code=404
        )
