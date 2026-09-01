# Student Management System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Vercel](https://img.shields.io/badge/Vercel-Live-000000.svg?style=flat&logo=vercel&logoColor=white)](https://student-management-system-rosy-delta.vercel.app/)
[![Gemini API](https://img.shields.io/badge/Gemini-AI_Integrated-8E75B2.svg?style=flat&logo=google&logoColor=white)](https://ai.google.dev/)

A full-stack academic management portal for managing student records, tracking grades and attendance, identifying at-risk students, and generating AI-powered classroom insights with Google Gemini.

## Live Demo

Open the deployed app here:

[https://student-management-system-rosy-delta.vercel.app/](https://student-management-system-rosy-delta.vercel.app/)

## Features

- Student CRUD operations: add, view, update, and delete student records.
- Searchable student directory by name, student ID, or course.
- Academic status labels: On Track, Needs Attention, and At Risk.
- Dashboard metrics for total students, average grade, at-risk count, and top performer.
- Visual charts for grade distribution and average attendance by course.
- Gemini AI chat for asking questions about class performance.
- AI-generated class audit reports.
- Individual student advisor recommendations.
- Optional Streamlit dashboard for local data exploration.

## Tech Stack

- Backend: FastAPI
- Database: SQLite locally, PostgreSQL-ready through `DATABASE_URL`
- ORM: SQLAlchemy
- Validation: Pydantic
- Frontend: HTML, CSS, JavaScript
- Charts: Chart.js in the web app, Matplotlib in Streamlit
- AI: Google GenAI SDK with Gemini
- Deployment: Vercel, with Render configuration included

## Project Structure

```text
student-management-system/
├── app/
│   ├── models/
│   │   └── student.py
│   ├── routes/
│   │   └── students.py
│   ├── schemas/
│   │   └── student.py
│   ├── static/
│   │   ├── app.js
│   │   ├── index.html
│   │   └── style.css
│   ├── database.py
│   └── main.py
├── .env.example
├── .gitignore
├── dashboard.py
├── LICENSE
├── README.md
├── render.yaml
├── requirements.txt
├── test_chat.py
└── vercel.json
```

## File Overview

- `app/main.py`: Creates the FastAPI app, enables CORS, mounts static files, creates database tables, and seeds sample students.
- `app/database.py`: Configures the SQLAlchemy database connection and session dependency.
- `app/models/student.py`: Defines the SQLAlchemy `Student` table model.
- `app/schemas/student.py`: Defines Pydantic schemas for request validation and API responses.
- `app/routes/students.py`: Contains student CRUD routes, at-risk logic, Gemini chat, audit, and student analysis endpoints.
- `app/static/index.html`: Main deployed web interface.
- `app/static/style.css`: Styling for the web dashboard and student directory.
- `app/static/app.js`: Frontend state, API calls, charts, forms, and Gemini interactions.
- `dashboard.py`: Optional Streamlit dashboard for local use.
- `test_chat.py`: Simple script for testing the deployed Gemini chat endpoint.
- `vercel.json`: Vercel deployment configuration.
- `render.yaml`: Render deployment blueprint with PostgreSQL support.

## Academic Status Rules

| Status | Rule |
| --- | --- |
| At Risk | Attendance below 65%, numeric grade below 60, or grade equal to F/Fail |
| Needs Attention | Attendance below 75% or numeric grade below 70, but not At Risk |
| On Track | Student does not meet the risk or attention conditions |

## AI Integration

The app uses Google Gemini through the Google GenAI SDK. Gemini powers:

- Natural-language teacher questions about the class.
- Class-level academic audit reports.
- Individual student advice and academic recommendations.

The app sends structured student records to Gemini as context. It does not use RAG, embeddings, or a vector database.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Serves the frontend app |
| `GET` | `/students` | Returns all students, with optional search |
| `POST` | `/students` | Creates a new student |
| `GET` | `/students/at-risk` | Returns at-risk students |
| `GET` | `/students/gemini-status` | Checks Gemini API configuration |
| `GET` | `/students/{id}` | Returns one student by database ID |
| `PUT` | `/students/{id}` | Updates a student |
| `DELETE` | `/students/{id}` | Deletes a student |
| `POST` | `/students/{id}/analyze` | Generates AI advice for one student |
| `POST` | `/students/audit` | Generates an AI class audit report |
| `POST` | `/students/chat` | Answers teacher questions using student records |

## Local Setup

### Prerequisites

- Python 3.12+
- Git
- Google Gemini API key

### Installation

Clone the repository:

```bash
git clone https://github.com/kinza03/student-management-system.git
cd student-management-system
```

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your environment file:

```bash
copy .env.example .env
```

Update `.env` with your Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=sqlite:///./students.db
```

Start the FastAPI app:

```bash
uvicorn app.main:app --reload
```

Open the app locally:

[http://localhost:8000/](http://localhost:8000/)

## Optional Streamlit Dashboard

Run the local Streamlit dashboard:

```bash
streamlit run dashboard.py
```

## API Documentation

When the FastAPI server is running locally:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Deployment Notes

The project is currently deployed on Vercel:

[https://student-management-system-rosy-delta.vercel.app/](https://student-management-system-rosy-delta.vercel.app/)

Vercel serverless storage is temporary, so SQLite data can reset between cold starts. For persistent production data, configure a hosted PostgreSQL database and set:

```env
DATABASE_URL=your_postgresql_connection_string
```

Gemini can occasionally return a `503 UNAVAILABLE` response when the selected model is under high demand. This is a temporary provider-side error, not a project setup issue.

## Repository

GitHub:

[https://github.com/kinza03/student-management-system](https://github.com/kinza03/student-management-system)

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Author

Kinza Sabir

- GitHub: [kinza03](https://github.com/kinza03)
