from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse
import os
from google import genai
from pydantic import BaseModel
from fastapi import Header
from dotenv import load_dotenv

router = APIRouter(
    prefix="/students",
    tags=["students"]
)

# Load environment variables explicitly
load_dotenv()

def get_gemini_client(override_key: Optional[str] = None):
    # Order of priority: Header API Key -> Env variables
    key = override_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key or key.strip() == "" or key == "your_gemini_api_key_here":
        return None
    try:
        return genai.Client(api_key=key)
    except Exception:
        return None

class ChatRequest(BaseModel):
    question: str
    history: Optional[List[dict]] = []

@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    try:
        # Check if student_id already exists
        db_student = db.query(Student).filter(Student.student_id == student.student_id).first()
        if db_student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Student with ID '{student.student_id}' already exists."
            )
        
        new_student = Student(
            first_name=student.first_name,
            last_name=student.last_name,
            student_id=student.student_id,
            course=student.course,
            grade=student.grade,
            attendance=student.attendance
        )
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        return new_student
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal database error occurred: {str(e)}"
        )

@router.get("", response_model=List[StudentResponse])
def read_students(
    search: Optional[str] = Query(None, description="Search by name, student ID, or course"),
    db: Session = Depends(get_db)
):
    try:
        query = db.query(Student)
        if search:
            # Simple search across fields
            search_filter = f"%{search}%"
            query = query.filter(
                (Student.first_name.ilike(search_filter)) |
                (Student.last_name.ilike(search_filter)) |
                (Student.student_id.ilike(search_filter)) |
                (Student.course.ilike(search_filter))
            )
        return query.all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error while fetching student list: {str(e)}"
        )

@router.get("/at-risk", response_model=List[StudentResponse])
def read_at_risk_students(db: Session = Depends(get_db)):
    try:
        students = db.query(Student).all()
        at_risk = []
        for s in students:
            # Check attendance below 65
            if s.attendance is not None and s.attendance < 65.0:
                at_risk.append(s)
                continue
                
            # Check grade below 60
            if s.grade:
                try:
                    # Try numeric conversion (e.g., if grade is "55.5")
                    if float(s.grade) < 60.0:
                        at_risk.append(s)
                        continue
                except ValueError:
                    # Handle letter grades/Pass-Fail case-insensitively
                    val = s.grade.strip().upper()
                    if val in ["F", "FAIL"]:
                        at_risk.append(s)
                        continue
        return at_risk
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error while analyzing risk: {str(e)}"
        )

@router.get("/gemini-status")
def get_gemini_status(x_gemini_api_key: Optional[str] = Header(None)):
    client = get_gemini_client(x_gemini_api_key)
    return {"status": "configured" if client is not None else "not_configured"}

@router.get("/{id}", response_model=StudentResponse)
def read_student(id: int, db: Session = Depends(get_db)):
    try:
        student = db.query(Student).filter(Student.id == id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student record with database ID {id} not found."
            )
        return student
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error while fetching student: {str(e)}"
        )

@router.put("/{id}", response_model=StudentResponse)
def update_student(id: int, student_update: StudentUpdate, db: Session = Depends(get_db)):
    try:
        student = db.query(Student).filter(Student.id == id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student record with database ID {id} not found."
            )
        
        update_data = student_update.model_dump(exclude_unset=True)
        
        # If student_id is being updated, verify it doesn't collide with another student
        if "student_id" in update_data and update_data["student_id"] != student.student_id:
            existing_student = db.query(Student).filter(
                Student.student_id == update_data["student_id"],
                Student.id != id
            ).first()
            if existing_student:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Student ID '{update_data['student_id']}' is already in use by another student."
                )
                
        for key, value in update_data.items():
            setattr(student, key, value)
            
        db.commit()
        db.refresh(student)
        return student
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error while updating student: {str(e)}"
        )

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(id: int, db: Session = Depends(get_db)):
    try:
        student = db.query(Student).filter(Student.id == id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Student record with database ID {id} not found."
            )
        db.delete(student)
        db.commit()
        return None
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error while deleting student: {str(e)}"
        )

@router.post("/{id}/analyze")
def analyze_student(id: int, db: Session = Depends(get_db), x_gemini_api_key: Optional[str] = Header(None)):
    client = get_gemini_client(x_gemini_api_key)
    if not client:
        raise HTTPException(status_code=533, detail="Gemini API Key is not configured.")
        
    student = db.query(Student).filter(Student.id == id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")
        
    try:
        prompt = f"""You are an expert academic advisor. Analyze the following student record:
Name: {student.first_name} {student.last_name}
Student ID: {student.student_id}
Course: {student.course}
Grade: {student.grade}
Attendance: {student.attendance}%

Provide a personalized insight (1-2 sentences) and a concrete actionable recommendation (1-2 sentences) for the teacher to help this student succeed. Format your response cleanly with markdown."""

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return {"result": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")

@router.post("/audit")
def generate_class_report(db: Session = Depends(get_db), x_gemini_api_key: Optional[str] = Header(None)):
    client = get_gemini_client(x_gemini_api_key)
    if not client:
        raise HTTPException(status_code=533, detail="Gemini API Key is not configured.")
        
    students_list = db.query(Student).all()
    if not students_list:
        raise HTTPException(status_code=400, detail="No student data available to analyze.")
        
    try:
        student_list_str = ""
        for s in students_list:
            student_list_str += f"- ID: {s.student_id}, Name: {s.first_name} {s.last_name}, Course: {s.course}, Grade: {s.grade}, Attendance: {s.attendance}%\n"
            
        prompt = f"""You are an expert educational consultant. Analyze the academic data of the following class of students:
{student_list_str}

Please generate a structured, professional report containing:
1. **Highlights**: Major positive observations, top performers, or strong trends (e.g. high attendance courses, high achievers).
2. **Concerns**: Major academic or behavioral risks, students who are struggling or at risk, low attendance areas.
3. **Recommendations**: Concrete, actionable intervention strategies and advice for the teacher to improve the overall classroom outcomes.

Format the report using Markdown headers and lists."""

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return {"result": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")

@router.post("/chat")
def ask_ai(chat_req: ChatRequest, db: Session = Depends(get_db), x_gemini_api_key: Optional[str] = Header(None)):
    client = get_gemini_client(x_gemini_api_key)
    if not client:
        raise HTTPException(status_code=533, detail="Gemini API Key is not configured.")
        
    students_list = db.query(Student).all()
    try:
        student_list_str = ""
        for s in students_list:
            student_list_str += f"- ID: {s.student_id}, Name: {s.first_name} {s.last_name}, Course: {s.course}, Grade: {s.grade}, Attendance: {s.attendance}%\n"
            
        history_str = ""
        if getattr(chat_req, 'history', None):
            history_str = "\nPrevious Conversation History:\n"
            for msg in chat_req.history:
                role = "Teacher" if msg.get("role") == "user" else "Assistant"
                history_str += f"{role}: {msg.get('content')}\n"
            
        prompt = f"""You are Gemini, an AI Assistant for teachers. You have access to the following class student data:
{student_list_str}
{history_str}
The teacher is asking the following question about their class:
"{chat_req.question}"

Answer the question clearly, concisely, and accurately based on the provided student records. Use Markdown where appropriate."""

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return {"result": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")
