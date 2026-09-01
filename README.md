# 🎓 Student Management System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Vercel](https://img.shields.io/badge/Vercel-Deployed-000000.svg?style=flat&logo=vercel&logoColor=white)](https://student-management-system-rosy-delta.vercel.app)
[![Gemini API](https://img.shields.io/badge/Gemini-AI_Integrated-8E75B2.svg?style=flat&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)

A full-stack academic management platform engineered to manage student records, monitor academic performance, visualize grades and attendance, and provide AI-powered academic insights using Google's Gemini LLM. 🚀

🌐 Live Demo: Experience the Student Management System

🏗️ Architecture & Technology Stack
⚙️ Backend Framework: FastAPI (Python 3.12)
🗄️ Database Engine: SQLite / PostgreSQL
🔗 ORM Layer: SQLAlchemy
🎨 Frontend Layer: Vanilla HTML5, CSS3, JavaScript
📊 Data Processing: Pandas, NumPy
📈 Data Visualization: Matplotlib / Chart.js
🤖 Intelligence Engine: Google GenAI SDK — Gemini 2.5 Flash
☁️ Deployment: Vercel / Render configuration
✨ Core Capabilities
📊 Centralized Dashboard:
Provides an overview of student enrollment, average class performance, top performers, grade distribution, attendance trends, and students requiring academic attention.
👥 Student Directory:
Full CRUD functionality for managing student records, with search capabilities and automated academic status evaluation.
🎯 Academic Status Evaluation:
Automatically categorizes students as On Track, Needs Attention, or At Risk based on attendance and academic performance thresholds.
📈 Data Visualization:
Presents grade distributions and course-wise attendance through visual analytics for easier academic monitoring.
🤖 AI-Powered Academic Assistant:
💬 Conversational Analysis: Ask natural-language questions about available student and class records.
📝 Automated Academic Audits: Generate class-level reports containing highlights, concerns, and recommendations.
👤 Personalized Advising: Analyze an individual student's academic performance and generate tailored recommendations.
📄 Report Generation: Download AI-generated class reports as text files.
🧠 Academic Status Logic

The system uses deterministic rules to identify students who may require intervention:

Status	Evaluation
🔴 At Risk	Attendance < 65%, grade < 60, or F/Fail
🟡 Needs Attention	Attendance < 75% or grade < 70, but not At Risk
🟢 On Track	Does not meet the above conditions

This rule-based evaluation works alongside the Gemini-powered analysis layer, keeping core academic classification deterministic while using AI for interpretation and recommendations.

🤖 AI Integration

The system integrates Google Gemini 2.5 Flash through the Google GenAI SDK.

The AI layer supports three primary workflows:

💬 Ask AI

Users can ask questions about the available classroom records using natural language. The system provides answers based on the student data supplied to the model.

📝 Class Academic Audit

The system sends class-level records to Gemini to generate an academic report containing:

Highlights
Concerns
Recommendations
👤 Individual Student Advisor

Individual student records can be analyzed to generate personalized academic insights and concrete recommendations.

Note: This project uses direct LLM integration with structured student data. It does not use a Retrieval-Augmented Generation (RAG) or vector-database architecture.

💻 Local Development Setup
Prerequisites
Python 3.12+
Git
Google Gemini API key
Installation

1. Clone the repository

git clone https://github.com/kinzasabir/student-management-system.git
cd student-management-system

2. Create and activate a virtual environment

python -m venv venv

Windows:

venv\Scripts\activate

3. Install dependencies

pip install -r requirements.txt

4. Configure environment variables

Create a .env file in the project root:

GEMINI_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./students.db

DATABASE_URL can be configured for PostgreSQL when using an external database.

5. Start the FastAPI application

uvicorn app.main:app --reload

The application will be available at:

http://localhost:8000/

The database automatically seeds sample data when the application starts.

📊 Run the Streamlit Dashboard
streamlit run dashboard.py
📖 API Documentation

FastAPI automatically provides interactive API documentation when running locally:

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

These interfaces can be used to explore and test the available API endpoints.

🌍 Deployment

The repository includes deployment configurations for Vercel and Render.

⚡ Vercel

The included vercel.json configures the FastAPI application for deployment through Vercel.

For persistent production data, an external PostgreSQL database should be used rather than relying on the local SQLite filesystem.

Configure the database through:

DATABASE_URL=your_postgresql_connection_string
🗄️ Database Persistence

SQLite is convenient for local development, while PostgreSQL is supported for deployments requiring persistent external storage.

📁 Project Structure
student-management-system/
│
├── app/
│   ├── main.py
│   └── routes/
│
├── dashboard.py
├── test_chat.py
├── requirements.txt
├── .env.example
├── .gitignore
├── vercel.json
├── render.yaml
├── LICENSE
└── README.md
🧩 Engineering Highlights

This project demonstrates practical implementation of:

FastAPI REST API architecture
SQLAlchemy ORM and relational data management
CRUD operations and data validation
Rule-based academic evaluation
Academic data visualization
Google Gemini LLM integration
Natural-language interaction with structured data
AI-generated academic reports
Personalized AI recommendations
Environment-based configuration
Cloud deployment configuration
🎯 Project Focus

The goal of this project is to demonstrate how traditional academic management functionality can be combined with modern AI capabilities.

Instead of using AI as a standalone chatbot, the system integrates an LLM into a data-driven application where:

Structured Data → Backend → Analytics & Rules → AI Analysis → Actionable Insights

This creates a practical example of combining software engineering, databases, data analytics, APIs, and generative AI within a single application.

## 📄 License
Distributed under the MIT License.

👤 Author

Kinza Sabir

GitHub: kinzasabir
LinkedIn: kinzasabir

