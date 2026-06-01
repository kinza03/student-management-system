import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server environments
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

# Try to import DB session for direct database access fallback (useful for Streamlit Cloud deployment)
try:
    from app.database import SessionLocal, engine, Base
    from app.models.student import Student
    db_fallback_available = True
    # Automatically initialize tables in fallback database (e.g. SQLite / Cloud PostgreSQL)
    Base.metadata.create_all(bind=engine)
except Exception as e:
    db_fallback_available = False

# Set page config
st.set_page_config(
    page_title="Student Management Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Backend API URL
API_URL = "http://127.0.0.1:8000/students"

# Inject Custom CSS for premium styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .title-container {
        padding: 0.5rem 0rem;
        margin-bottom: 1.5rem;
    }
    
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.25rem;
    }
    
    .subtitle {
        font-size: 1.05rem;
        color: #64748b;
        font-weight: 400;
    }
    
    /* Premium Glassmorphic Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 16px;
        padding: 1.25rem;
        text-align: center;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 20px 0 rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(99, 102, 241, 0.3);
        box-shadow: 0 8px 25px 0 rgba(99, 102, 241, 0.1);
    }
    
    .metric-val {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-val-risk {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
        background: linear-gradient(135deg, #ef4444 0%, #f43f5e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-val-perf {
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
        color: #10b981;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .metric-label {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        color: #64748b;
    }
    
    /* HTML Badges for quick reference */
    .badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.75rem;
        border: 1px solid;
    }
    .badge-ontrack {
        background-color: #d1fae5;
        color: #065f46;
        border-color: #a7f3d0;
    }
    .badge-attention {
        background-color: #fef3c7;
        color: #92400e;
        border-color: #fde68a;
    }
    .badge-risk {
        background-color: #fee2e2;
        color: #991b1b;
        border-color: #fecaca;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions to talk to backend API
# Mock response helper to mimic requests.Response behavior in fallback mode
class MockResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json = json_data
    def json(self):
        return self._json

def check_backend():
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=2)
        return response.status_code == 200
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False

def get_all_students(search_query=None):
    if backend_online:
        params = {}
        if search_query:
            params["search"] = search_query
        try:
            response = requests.get(API_URL, params=params)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            st.error(f"Error fetching students: {e}")
            return []
    elif db_fallback_available:
        db = SessionLocal()
        try:
            query = db.query(Student)
            if search_query:
                search_filter = f"%{search_query}%"
                query = query.filter(
                    (Student.first_name.ilike(search_filter)) |
                    (Student.last_name.ilike(search_filter)) |
                    (Student.student_id.ilike(search_filter)) |
                    (Student.course.ilike(search_filter))
                )
            results = query.all()
            return [
                {
                    "id": s.id,
                    "first_name": s.first_name,
                    "last_name": s.last_name,
                    "student_id": s.student_id,
                    "course": s.course,
                    "grade": s.grade,
                    "attendance": s.attendance
                }
                for s in results
            ]
        except Exception as e:
            st.error(f"Database error: {e}")
            return []
        finally:
            db.close()
    else:
        return []

def get_at_risk_students():
    if backend_online:
        try:
            response = requests.get(f"{API_URL}/at-risk")
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            st.error(f"Error fetching at-risk students: {e}")
            return []
    elif db_fallback_available:
        db = SessionLocal()
        try:
            students = db.query(Student).all()
            at_risk = []
            for s in students:
                is_at_risk = False
                if s.attendance is not None and s.attendance < 65.0:
                    is_at_risk = True
                elif s.grade:
                    try:
                        if float(s.grade) < 60.0:
                            is_at_risk = True
                    except ValueError:
                        val = s.grade.strip().upper()
                        if val in ["F", "FAIL"]:
                            is_at_risk = True
                if is_at_risk:
                    at_risk.append({
                        "id": s.id,
                        "first_name": s.first_name,
                        "last_name": s.last_name,
                        "student_id": s.student_id,
                        "course": s.course,
                        "grade": s.grade,
                        "attendance": s.attendance
                    })
            return at_risk
        except Exception as e:
            st.error(f"Database error: {e}")
            return []
        finally:
            db.close()
    else:
        return []

def create_student(first_name, last_name, student_id, course, grade, attendance):
    if backend_online:
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "student_id": student_id,
            "course": course,
            "grade": grade,
            "attendance": float(attendance)
        }
        try:
            response = requests.post(API_URL, json=payload)
            return response
        except Exception as e:
            st.error(f"Error connecting to server: {e}")
            return None
    elif db_fallback_available:
        db = SessionLocal()
        try:
            existing = db.query(Student).filter(Student.student_id == student_id).first()
            if existing:
                return MockResponse(400, {"detail": f"Student with ID '{student_id}' already exists."})
            
            new_student = Student(
                first_name=first_name,
                last_name=last_name,
                student_id=student_id,
                course=course,
                grade=grade,
                attendance=float(attendance)
            )
            db.add(new_student)
            db.commit()
            return MockResponse(201, {})
        except Exception as e:
            db.rollback()
            return MockResponse(500, {"detail": f"Database error: {e}"})
        finally:
            db.close()
    else:
        return None

def update_student(db_id, first_name, last_name, student_id, course, grade, attendance):
    if backend_online:
        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "student_id": student_id,
            "course": course,
            "grade": grade,
            "attendance": float(attendance)
        }
        try:
            response = requests.put(f"{API_URL}/{db_id}", json=payload)
            return response
        except Exception as e:
            st.error(f"Error connecting to server: {e}")
            return None
    elif db_fallback_available:
        db = SessionLocal()
        try:
            student = db.query(Student).filter(Student.id == db_id).first()
            if not student:
                return MockResponse(404, {"detail": "Student not found."})
            
            if student_id != student.student_id:
                existing = db.query(Student).filter(Student.student_id == student_id, Student.id != db_id).first()
                if existing:
                    return MockResponse(400, {"detail": f"Student ID '{student_id}' is already in use by another student."})
            
            student.first_name = first_name
            student.last_name = last_name
            student.student_id = student_id
            student.course = course
            student.grade = grade
            student.attendance = float(attendance)
            db.commit()
            return MockResponse(200, {})
        except Exception as e:
            db.rollback()
            return MockResponse(500, {"detail": f"Database error: {e}"})
        finally:
            db.close()
    else:
        return None

def delete_student(db_id):
    if backend_online:
        try:
            response = requests.delete(f"{API_URL}/{db_id}")
            return response
        except Exception as e:
            st.error(f"Error connecting to server: {e}")
            return None
    elif db_fallback_available:
        db = SessionLocal()
        try:
            student = db.query(Student).filter(Student.id == db_id).first()
            if not student:
                return MockResponse(404, {"detail": "Student not found."})
            db.delete(student)
            db.commit()
            return MockResponse(204, {})
        except Exception as e:
            db.rollback()
            return MockResponse(500, {"detail": f"Database error: {e}"})
        finally:
            db.close()
    else:
        return None

# Grade parsing & conversion helpers
def grade_to_numeric(grade):
    if not grade:
        return 75.0
    try:
        return float(grade)
    except ValueError:
        pass
    
    grade_map = {
        "A+": 97.0, "A": 93.0, "B+": 87.0, "B": 83.0,
        "C+": 77.0, "C": 73.0, "D": 65.0, "F": 50.0,
        "Pass": 80.0, "Fail": 50.0
    }
    return grade_map.get(grade.strip(), 75.0)

def numeric_to_grade(score):
    if score >= 95.0: return "A+"
    if score >= 90.0: return "A"
    if score >= 85.0: return "B+"
    if score >= 80.0: return "B"
    if score >= 75.0: return "C+"
    if score >= 70.0: return "C"
    if score >= 60.0: return "D"
    return "F"

# Status badge calculator
def calculate_status(student):
    attendance = student.get("attendance")
    if attendance is None or pd.isna(attendance):
        attendance = 0.0
    else:
        try:
            attendance = float(attendance)
        except (ValueError, TypeError):
            attendance = 0.0
            
    grade = student.get("grade")
    has_grade = grade is not None and not pd.isna(grade)
    
    is_at_risk = False
    if attendance < 65.0:
        is_at_risk = True
    elif has_grade:
        grade_str = str(grade).strip()
        try:
            if float(grade_str) < 60.0:
                is_at_risk = True
        except ValueError:
            val = grade_str.upper()
            if val in ["F", "FAIL"]:
                is_at_risk = True
                
    if is_at_risk:
        return "At Risk"
        
    is_needs_attention = False
    if attendance < 75.0:
        is_needs_attention = True
    elif has_grade:
        grade_str = str(grade).strip()
        try:
            if float(grade_str) < 70.0:
                is_needs_attention = True
        except ValueError:
            val = grade_str.upper()
            if val in ["D", "C-"]:
                is_needs_attention = True
                
    if is_needs_attention:
        return "Needs Attention"
        
    return "On Track"

def get_status_emoji(status):
    if status == "At Risk":
        return "🔴 At Risk"
    elif status == "Needs Attention":
        return "🟡 Needs Attention"
    return "🟢 On Track"

# Matplotlib plotting functions
def plot_grade_distribution(df):
    fig, ax = plt.subplots(figsize=(5, 3.5))
    grade_order = ["A+", "A", "B+", "B", "C+", "C", "D", "F", "Pass", "Fail"]
    counts = df["grade"].value_counts()
    
    counts_aligned = [counts.get(g, 0) for g in grade_order]
    active_grades = [g for g, c in zip(grade_order, counts_aligned) if c > 0]
    active_counts = [c for c in counts_aligned if c > 0]
    
    if not active_counts:
        ax.text(0.5, 0.5, "No grade data", ha='center', va='center', color="#64748b")
        ax.axis('off')
        return fig
        
    bars = ax.bar(active_grades, active_counts, color="#6366f1", edgecolor="none", width=0.5)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cccccc')
    ax.spines['bottom'].set_color('#cccccc')
    ax.tick_params(colors='#64748b', labelsize=9)
    ax.set_ylabel("Students", color='#64748b', fontweight='semibold', fontsize=9)
    ax.set_title("Grade Distribution", color='#334155', fontweight='bold', pad=10, fontsize=11)
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 2),
                    textcoords="offset points",
                    ha='center', va='bottom', color='#475569', fontweight='semibold', fontsize=8)
                    
    fig.patch.set_alpha(0.0)
    ax.set_facecolor('none')
    plt.tight_layout()
    return fig

def plot_attendance_by_course(df):
    fig, ax = plt.subplots(figsize=(5, 3.5))
    course_attendance = df.groupby('course')['attendance'].mean().reset_index()
    
    if course_attendance.empty:
        ax.text(0.5, 0.5, "No attendance data", ha='center', va='center', color="#64748b")
        ax.axis('off')
        return fig
        
    bars = ax.bar(course_attendance['course'], course_attendance['attendance'], color="#a855f7", edgecolor="none", width=0.4)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cccccc')
    ax.spines['bottom'].set_color('#cccccc')
    ax.tick_params(colors='#64748b', labelsize=9)
    ax.set_ylabel("Avg Attendance (%)", color='#64748b', fontweight='semibold', fontsize=9)
    ax.set_title("Average Attendance by Course", color='#334155', fontweight='bold', pad=10, fontsize=11)
    plt.xticks(rotation=15, ha='right')
    
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 2),
                    textcoords="offset points",
                    ha='center', va='bottom', color='#475569', fontweight='semibold', fontsize=8)
                    
    fig.patch.set_alpha(0.0)
    ax.set_facecolor('none')
    plt.tight_layout()
    return fig

# Gemini API Functions
def get_gemini_client():
    if not gemini_key or gemini_key.strip() == "" or gemini_key == "your_gemini_api_key_here":
        return None
    try:
        from google import genai
        return genai.Client(api_key=gemini_key)
    except Exception as e:
        st.error(f"Error initializing Gemini SDK: {e}")
        return None

def analyze_student(student):
    client = get_gemini_client()
    if not client:
        return "API Key not configured. Please add your Gemini API Key in the sidebar or in the `.env` file."
    
    try:
        prompt = f"""You are an expert academic advisor. Analyze the following student record:
Name: {student['first_name']} {student['last_name']}
Student ID: {student['student_id']}
Course: {student['course']}
Grade: {student['grade']}
Attendance: {student['attendance']}%

Provide a personalized insight (1-2 sentences) and a concrete actionable recommendation (1-2 sentences) for the teacher to help this student succeed. Format your response cleanly with markdown."""

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Error analyzing student: {e}"

def generate_class_report(students_list):
    client = get_gemini_client()
    if not client:
        return "API Key not configured. Please add your Gemini API Key in the sidebar or in the `.env` file."
    
    try:
        student_list_str = ""
        for s in students_list:
            student_list_str += f"- ID: {s['student_id']}, Name: {s['first_name']} {s['last_name']}, Course: {s['course']}, Grade: {s['grade']}, Attendance: {s['attendance']}%\n"
            
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
        return response.text
    except Exception as e:
        return f"Error generating class report: {e}"

def ask_ai(question, students_list):
    client = get_gemini_client()
    if not client:
        return "API Key not configured. Please add your Gemini API Key in the sidebar or in the `.env` file."
    
    try:
        student_list_str = ""
        for s in students_list:
            student_list_str += f"- ID: {s['student_id']}, Name: {s['first_name']} {s['last_name']}, Course: {s['course']}, Grade: {s['grade']}, Attendance: {s['attendance']}%\n"
            
        prompt = f"""You are Gemini, an AI Assistant for teachers. You have access to the following class student data:
{student_list_str}

The teacher is asking the following question about their class:
"{question}"

Answer the question clearly, concisely, and accurately based on the provided student records. Use Markdown where appropriate."""

        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Error talking to Gemini: {e}"

# Check backend status
backend_online = check_backend()

# Sidebar Navigation
with st.sidebar:
    st.image("https://img.icons8.com/color/144/graduation-cap.png", width=70)
    st.markdown("### Navigation")
    menu = st.radio(
        "Go to",
        ["Dashboard", "Students", "Add Student", "AI Assistant"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # API key override section
    if not gemini_key or gemini_key.strip() == "" or gemini_key == "your_gemini_api_key_here":
        st.warning("🔑 Gemini API key is not configured.")
        sidebar_key = st.text_input("Enter Gemini API Key:", type="password")
        if sidebar_key:
            gemini_key = sidebar_key
            st.success("API key loaded temporarily!")
    else:
        st.success("🔑 API Key: Loaded from .env")

    st.markdown("---")
    if backend_online:
        st.success("🟢 API Server: Connected")
        st.info("⚡ Mode: FastAPI Server Backend")
    elif db_fallback_available:
        st.warning("🟡 API Server: Offline")
        st.success("🟢 Mode: Direct Database (Local/Cloud)")
    else:
        st.error("🔴 Connection Error")
        st.warning("FastAPI Server is offline and database fallback is unavailable.")
        st.code("uvicorn app.main:app --reload")

# Title Header
st.markdown("""
<div class="title-container">
    <h1 class="main-title">🎓 Student Management Portal</h1>
    <p class="subtitle">Real-time educational monitoring, tracking, and student performance insights.</p>
</div>
""", unsafe_allow_html=True)

if not backend_online and not db_fallback_available:
    st.warning("⚠️ Connection Error: The backend API server is offline and database fallback is unavailable. Please run the server or configure your database.")
else:
    # Fetch student data
    students = get_all_students()
    
    if "Dashboard" in menu:
        if not students:
            st.info("No student records found. Head to 'Add Student' in the sidebar to register a new student!")
        else:
            df = pd.DataFrame(students)
            df['numeric_grade'] = df['grade'].apply(grade_to_numeric)
            df['status'] = df.apply(calculate_status, axis=1)
            
            # Metrics computations
            total_students = len(df)
            avg_grade_numeric = df['numeric_grade'].mean()
            avg_grade_letter = numeric_to_grade(avg_grade_numeric)
            
            at_risk_list = get_at_risk_students()
            at_risk_count = len(at_risk_list)
            
            # Find Top Performer
            top_student = df.sort_values(by=['numeric_grade', 'attendance'], ascending=False).iloc[0]
            top_performer_name = f"{top_student['first_name']} {top_student['last_name']}"
            top_performer_display = f"{top_performer_name} ({top_student['grade']})"
            
            # Metric Columns
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Total Students</div>
                    <div class="metric-val">{total_students}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Average Class Grade</div>
                    <div class="metric-val">{avg_grade_numeric:.1f}% ({avg_grade_letter})</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">At-Risk Count</div>
                    <div class="metric-val-risk">{at_risk_count}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Top Performer</div>
                    <div class="metric-val-perf" title="{top_performer_display}">{top_performer_display}</div>
                </div>
                """, unsafe_allow_html=True)
                
            st.write("")
            st.write("")
            
            # Chart Columns
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                fig1 = plot_grade_distribution(df)
                st.pyplot(fig1)
                plt.close(fig1)
                
            with chart_col2:
                fig2 = plot_attendance_by_course(df)
                st.pyplot(fig2)
                plt.close(fig2)
                
            st.markdown("---")
            
            # Dashboard Bottom Section
            bot_col1, bot_col2 = st.columns(2)
            
            with bot_col1:
                st.subheader("🏆 Top Performers")
                top_performers = df.sort_values(by=['numeric_grade', 'attendance'], ascending=False).head(3)
                for index, s in top_performers.iterrows():
                    st.markdown(f"""
                    <div style="padding: 10px; border-radius: 8px; background: rgba(16, 185, 129, 0.05); border: 1px solid rgba(16, 185, 129, 0.15); margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <b>{s['first_name']} {s['last_name']}</b> ({s['student_id']})<br>
                            <span style="font-size: 0.8rem; color: #64748b;">Course: {s['course']}</span>
                        </div>
                        <div style="text-align: right;">
                            <span class="badge badge-ontrack">Grade: {s['grade']}</span><br>
                            <span style="font-size: 0.8rem; color: #64748b;">Attend: {s['attendance']}%</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
            with bot_col2:
                st.subheader("⚠️ At-Risk Alert List")
                if at_risk_count == 0:
                    st.success("🎉 Excellent! There are no students currently marked at risk.")
                else:
                    for s in at_risk_list:
                        # compute issues
                        reasons = []
                        if s.get("attendance", 0) < 65.0:
                            reasons.append(f"low attendance ({s['attendance']}%)")
                        grade = s.get("grade")
                        try:
                            if grade and float(grade) < 60.0:
                                reasons.append(f"low grade ({grade})")
                        except ValueError:
                            if grade and grade.strip().upper() in ["F", "FAIL"]:
                                reasons.append("failing grade (F/FAIL)")
                        
                        st.markdown(f"""
                        <div style="padding: 10px; border-radius: 8px; background: rgba(239, 68, 68, 0.05); border: 1px solid rgba(239, 68, 68, 0.15); margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <b>{s['first_name']} {s['last_name']}</b> ({s['student_id']})<br>
                                <span style="font-size: 0.8rem; color: #ef4444; font-weight: 500;">Reason: {', '.join(reasons)}</span>
                            </div>
                            <div style="text-align: right;">
                                <span class="badge badge-risk">At Risk</span><br>
                                <span style="font-size: 0.8rem; color: #64748b;">Course: {s['course']}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

    elif "Students" in menu:
        st.subheader("👥 Registered Students Directory")
        
        # Search panel
        search_query = st.text_input("🔍 Search Database", placeholder="Type name, student ID, or course to search...")
        
        # Fetch matching students
        db_students = get_all_students(search_query)
        
        if not db_students:
            st.write("No matching student records found.")
        else:
            df = pd.DataFrame(db_students)
            df['status'] = df.apply(calculate_status, axis=1)
            df['Status Badge'] = df['status'].apply(get_status_emoji)
            
            # Rearrange columns for display
            display_df = df[['id', 'student_id', 'first_name', 'last_name', 'course', 'grade', 'attendance', 'Status Badge']].copy()
            display_df.columns = ['DB ID', 'Student ID', 'First Name', 'Last Name', 'Course', 'Grade', 'Attendance (%)', 'Academic Status']
            
            # Show Table
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            st.markdown("---")
            
            # Actions Panel (Update / Delete)
            st.markdown("### ⚙️ Student Management Actions")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Edit Student Record")
                selected_db_id = st.selectbox(
                    "Select Student to Edit",
                    options=df['id'].tolist(),
                    index=None,
                    placeholder="Choose student to edit...",
                    format_func=lambda x: f"{df[df['id'] == x]['first_name'].values[0]} {df[df['id'] == x]['last_name'].values[0]} ({df[df['id'] == x]['student_id'].values[0]})" if x is not None and not df[df['id'] == x].empty else "",
                    key="edit_select"
                )
                
                if selected_db_id:
                    student_data = df[df['id'] == selected_db_id].iloc[0]
                    status_val = calculate_status(student_data)
                    
                    if status_val == "At Risk":
                        badge_html = '<span class="badge badge-risk">At Risk</span>'
                    elif status_val == "Needs Attention":
                        badge_html = '<span class="badge badge-attention">Needs Attention</span>'
                    else:
                        badge_html = '<span class="badge badge-ontrack">On Track</span>'
                        
                    st.markdown(f"Current Status: {badge_html}", unsafe_allow_html=True)
                    
                    with st.form(key=f"edit_student_form_{selected_db_id}"):
                        edit_fn = st.text_input("First Name", value=student_data['first_name'])
                        edit_ln = st.text_input("Last Name", value=student_data['last_name'])
                        edit_sid = st.text_input("Student ID", value=student_data['student_id'])
                        edit_course = st.text_input("Course", value=student_data['course'])
                        
                        grade_options = ["A+", "A", "B+", "B", "C+", "C", "D", "F", "Pass", "Fail"]
                        current_grade = student_data['grade']
                        if current_grade not in grade_options:
                            grade_options.insert(0, current_grade)
                        edit_grade = st.selectbox("Grade", grade_options, index=grade_options.index(current_grade))
                        
                        edit_attend = st.slider("Attendance (%)", 0.0, 100.0, float(student_data['attendance']), step=0.5)
                        
                        submit_update = st.form_submit_button("Update Student Record", use_container_width=True)
                        
                        if submit_update:
                            if not edit_fn or not edit_ln or not edit_sid or not edit_course:
                                st.error("Please fill in all required fields.")
                            else:
                                update_resp = update_student(
                                    selected_db_id, edit_fn, edit_ln, edit_sid, edit_course, edit_grade, edit_attend
                                )
                                if update_resp and update_resp.status_code == 200:
                                    st.success("Successfully updated record!")
                                    st.rerun()
                                elif update_resp:
                                    err_detail = update_resp.json().get('detail', 'Unknown error.')
                                    st.error(f"Failed to update: {err_detail}")
            
            with col2:
                st.markdown("#### Delete Student Record")
                delete_db_id = st.selectbox(
                    "Select Student to Delete",
                    options=df['id'].tolist(),
                    index=None,
                    placeholder="Choose student to delete...",
                    format_func=lambda x: f"{df[df['id'] == x]['first_name'].values[0]} {df[df['id'] == x]['last_name'].values[0]} ({df[df['id'] == x]['student_id'].values[0]})" if x is not None and not df[df['id'] == x].empty else "",
                    key="delete_select"
                )
                
                if delete_db_id:
                    to_delete = df[df['id'] == delete_db_id].iloc[0]
                    st.warning(f"Are you sure you want to permanently delete student **{to_delete['first_name']} {to_delete['last_name']}** ({to_delete['student_id']})?")
                    
                    delete_btn = st.button("❌ Confirm Delete Permanently", use_container_width=True, type="primary")
                    if delete_btn:
                        del_resp = delete_student(delete_db_id)
                        if del_resp and del_resp.status_code == 204:
                            st.success("Student successfully deleted!")
                            st.rerun()
                        else:
                            st.error("Failed to delete student record.")

    elif "Add Student" in menu:
        st.subheader("➕ Register a New Student")
        st.write("Complete the form below to add a new student record to the system.")
        
        col1, col2 = st.columns(2)
        with col1:
            with st.form(key="register_form", clear_on_submit=True):
                fn = st.text_input("First Name*", placeholder="e.g. Liam")
                ln = st.text_input("Last Name*", placeholder="e.g. Anderson")
                sid = st.text_input("Student ID*", placeholder="e.g. S10243")
                course = st.text_input("Enrolled Course*", placeholder="e.g. Data Structures")
                
                grade = st.selectbox("Current Grade", ["A+", "A", "B+", "B", "C+", "C", "D", "F", "Pass", "Fail"])
                attendance = st.slider("Attendance Percentage (%)", 0.0, 100.0, 95.0, step=0.5)
                
                st.markdown("<small>*Required fields</small>", unsafe_allow_html=True)
                submit_btn = st.form_submit_button("Add Student Record", use_container_width=True)
                
                if submit_btn:
                    if not fn or not ln or not sid or not course:
                        st.error("Please fill in all required fields.")
                    else:
                        resp = create_student(fn, ln, sid, course, grade, attendance)
                        if resp and resp.status_code == 201:
                            st.success(f"🎉 Student {fn} {ln} added successfully!")
                        elif resp:
                            err_detail = resp.json().get('detail', 'Unknown error.')
                            st.error(f"Failed to add student: {err_detail}")
                        else:
                            st.error("Could not reach backend API server.")
                            
        with col2:
            st.markdown("### Instructions")
            st.markdown("""
            - **Student ID**: Must be entirely unique. The API server will reject records with duplicate IDs.
            - **Attendance**: Input the current attendance rate. E.g., `95.0%` indicates solid class participation.
            - **Grade**: Select the grade representing the student's current academic status.
            - **Status Badges**: Added students are automatically color-coded on the Students directory:
              - **On Track** (green): Attendance >= 75% and Grade >= 70
              - **Needs Attention** (amber): Attendance < 75% or Grade < 70 (but not yet At Risk)
              - **At Risk** (red): Attendance < 65% or Grade < 60 ('F'/'Fail')
            """)
            st.image("https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=500&auto=format&fit=crop&q=60", caption="Student Academic Portal", use_container_width=True)

    elif "AI Assistant" in menu:
        st.subheader("🤖 AI Classroom Assistant (Gemini)")
        st.write("Leverage advanced AI capabilities powered by Google Gemini to ask questions, analyze individual student performance, or generate detailed academic reports.")
        
        if not students:
            st.info("No student data available. Please register student records first.")
        else:
            # Create tabs for the 3 requested AI functions
            tab_chat, tab_report, tab_advisor = st.tabs([
                "💬 Ask AI (Chat)", 
                "📊 Class Academic Audit", 
                "👤 Individual Student Advisor"
            ])
            
            # TAB 1: Chat interface (ask_ai)
            with tab_chat:
                st.markdown("#### Ask Gemini about your class")
                st.write("You can ask any natural language questions about students, courses, overall attendance, or performance patterns.")
                
                # Chat layout session state setup
                if "messages" not in st.session_state:
                    st.session_state.messages = []
                
                # Clear chat history button
                if st.button("🗑️ Clear Chat History", key="clear_chat"):
                    st.session_state.messages = []
                    st.rerun()
                
                st.markdown("---")
                
                # Display messages from history
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                
                # Capture chat input
                if prompt := st.chat_input("Ask a question about the class..."):
                    # Show user query
                    with st.chat_message("user"):
                        st.markdown(prompt)
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    
                    # Generate and show assistant response
                    with st.chat_message("assistant"):
                        with st.spinner("Gemini is analyzing student records..."):
                            response = ask_ai(prompt, students)
                            st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
            
            # TAB 2: Class Academic Audit (generate_class_report)
            with tab_report:
                st.markdown("#### Generate Class-Wide AI Evaluation Report")
                st.write("Request Gemini to compile a complete report outlining class highlights, academic concerns, and strategic intervention recommendations.")
                
                generate_report = st.button("📊 Generate AI Analysis Report", use_container_width=True, key="btn_gen_report")
                
                if generate_report:
                    with st.spinner("Analyzing student records with Gemini..."):
                        report_content = generate_class_report(students)
                        
                        st.markdown("---")
                        st.markdown("### Generated Report")
                        st.markdown(f"""
                        <div style="padding: 20px; border-radius: 12px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 20px;">
                            {report_content}
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.download_button(
                            label="📥 Download Full Report as Text File",
                            data=report_content,
                            file_name="student_ai_analysis_report.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
            
            # TAB 3: Student Advisor (analyze_student)
            with tab_advisor:
                st.markdown("#### Personalized Student Advisor")
                st.write("Select an individual student from the dropdown below to receive personalized insight and a recommended roadmap.")
                
                # Format options for dropdown
                student_options = []
                student_map = {}
                for s in students:
                    label = f"{s['first_name']} {s['last_name']} ({s['student_id']}) - {s['course']}"
                    student_options.append(label)
                    student_map[label] = s
                
                selected_label = st.selectbox("Select Student to Analyze", options=student_options)
                
                if selected_label:
                    selected_student = student_map[selected_label]
                    
                    # Display quick student card
                    status_val = calculate_status(selected_student)
                    if status_val == "At Risk":
                        badge_html = '<span class="badge badge-risk">At Risk</span>'
                    elif status_val == "Needs Attention":
                        badge_html = '<span class="badge badge-attention">Needs Attention</span>'
                    else:
                        badge_html = '<span class="badge badge-ontrack">On Track</span>'
                        
                    st.markdown(f"""
                    <div style="padding: 15px; border-radius: 12px; background: rgba(255, 255, 255, 0.04); border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 15px;">
                        <h4>Student Profile: {selected_student['first_name']} {selected_student['last_name']}</h4>
                        <b>Student ID</b>: {selected_student['student_id']}<br>
                        <b>Course</b>: {selected_student['course']}<br>
                        <b>Current Grade</b>: {selected_student['grade']}<br>
                        <b>Attendance Rate</b>: {selected_student['attendance']}%<br>
                        <b>Academic Standing</b>: {badge_html}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    analyze_btn = st.button("🤖 Get Advisor Recommendations", use_container_width=True)
                    
                    if analyze_btn:
                        with st.spinner("Consulting Gemini..."):
                            insight = analyze_student(selected_student)
                            st.markdown("---")
                            st.markdown("### Gemini's Insight & Recommendations")
                            st.markdown(f"""
                            <div style="padding: 20px; border-radius: 12px; background: rgba(99, 102, 241, 0.05); border: 1px solid rgba(99, 102, 241, 0.2); margin-bottom: 20px;">
                                {insight}
                            </div>
                            """, unsafe_allow_html=True)
