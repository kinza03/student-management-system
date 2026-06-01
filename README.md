# 🎓 Student Management System with Gemini AI Assistant

A comprehensive full-stack academic monitoring portal. The application consists of a **FastAPI backend REST API** (running SQLite with SQLAlchemy ORM) and a **Streamlit dashboard frontend** integrated with **Google Gemini AI** (`gemini-2.5-flash`) for classroom insight queries, student-level roadmap recommendations, and automatic academic audit reporting.

---

## 🚀 Quick Start & Installation

Follow these steps to set up and run the application locally on Windows (Python 3.12+):

### 0. Create Your Environment File
Copy the example environment file:
```bash
copy .env.example .env
```

Then open `.env` and add your real Gemini API key.

### 1. Install Dependencies
Install all required Python packages:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a file named `.env` in the root project directory and configure your Gemini API Key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
> **Note**: If you don't configure this, you can still temporarily paste your API key directly inside the dashboard's sidebar interface to test the AI capabilities.

### 3. Start the Backend API Server
Launch the FastAPI server using Uvicorn. This initializes the SQLite database and automatically seeds it with **8 sample students** on startup:
```bash
uvicorn app.main:app --reload
```
- API Docs (Swagger UI): http://127.0.0.1:8000/docs
- API Root: http://127.0.0.1:8000/

### 4. Start the Streamlit Dashboard
Launch the dashboard interface in a separate terminal:
```bash
streamlit run dashboard.py
```
- Local URL: http://localhost:8501/ (or the port specified in terminal)

---

## 🌐 Deploy as a Live App

This repository includes `render.yaml`, which can deploy the FastAPI app and static frontend to Render with a managed PostgreSQL database.

### Deploy on Render
1. Push this project to GitHub.
2. Go to [Render](https://render.com/), choose **New +** → **Blueprint**.
3. Connect your GitHub repository.
4. Render will detect `render.yaml` and create:
   - A web service for the FastAPI app.
   - A PostgreSQL database for live student records.
5. Add your `GEMINI_API_KEY` when Render asks for the synced secret value.
6. Deploy.

After deployment, Render will give you a public URL that people can open in their browser.

> Note: The included `vercel.json` can run the FastAPI app on Vercel, but SQLite data is not persistent in serverless environments. For a real shared live app, use Render/Railway/Fly.io with PostgreSQL.

---

## 🐙 Push to GitHub

From the project folder:

```bash
git init
git add .
git commit -m "Initial student management system"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/student-management-system.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username. Make sure `.env` is not committed; this project includes `.gitignore` to protect it.

---

## 📂 Project Directory Structure

```
student-management-system/
├── app/
│   ├── models/
│   │   └── student.py       # SQLAlchemy Student database model
│   ├── routes/
│   │   └── students.py      # CRUD and custom logic routes with try-catch
│   ├── schemas/
│   │   └── student.py       # Pydantic models for validation
│   ├── database.py          # SQLAlchemy database setup and session injection
│   └── main.py              # FastAPI app creation & DB auto-seeding
├── .env                     # Environment configuration (Gemini API Key)
├── dashboard.py             # Streamlit visual dashboard & Gemini integration
├── requirements.txt         # Project dependencies manifest
├── students.db              # SQLite Database (generated on startup)
└── README.md                # Documentation
```

---

## 🛠️ Key Features

### 1. Backend REST API Endpoints
- `GET /students`: Retrieves all students (supports query search by name/course/ID).
- `POST /students`: Registers a new student (validates unique ID).
- `GET /students/{id}`: Retrieves a single student by primary database ID.
- `PUT /students/{id}`: Updates student details.
- `DELETE /students/{id}`: Deletes a student record.
- `GET /students/at-risk`: Returns students with attendance below 65% or grade below 60.

### 2. Streamlit Visual Dashboard
- **Dashboard Overview**: Key metrics cards (Enrollment, average grade, at-risk count, and top performers) paired with custom-styled Matplotlib graphs for grade distribution and attendance analytics.
- **Searchable Students Directory**: Directory featuring search-as-you-type filtering, color-coded academic status badges (**🟢 On Track**, **🟡 Needs Attention**, and **🔴 At Risk**), and management forms to update or delete records.
- **Add Student Registration**: Quick-add student entry form with slide inputs and validation.

### 3. Gemini AI Assistant
- **Ask AI (Chat)**: A teacher assistant chatbot allowing natural language queries regarding class performance trends.
- **Class Academic Audit**: Generates an audit highlighting top courses, at-risk trends, class health breakdowns, and downloadable text reports.
- **Student Advisor**: Displays student profiles and returns a personalized insight and concrete recommendation roadmap.
