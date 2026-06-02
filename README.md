# 🎓 Student Management System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Vercel](https://img.shields.io/badge/Vercel-Deployed-000000.svg?style=flat&logo=vercel&logoColor=white)](https://vercel.com/)
[![Gemini API](https://img.shields.io/badge/Gemini-AI_Integrated-8E75B2.svg?style=flat&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)

A streamlined, full-stack academic monitoring portal engineered to track student performance, analyze attendance metrics, and provide actionable, AI-driven insights via Google's Gemini LLM. 🚀

## 🏗️ Architecture & Technology Stack

- **Backend Framework**: FastAPI (Python 3.12)
- **Database Engine**: SQLite / PostgreSQL (Production deployment ready)
- **ORM Layer**: SQLAlchemy
- **Frontend Layer**: Vanilla HTML5, CSS3, JavaScript
- **Data Visualization**: Chart.js
- **Intelligence Engine**: Google GenAI SDK (Gemini)
- **Deployment Platform**: Vercel (Serverless)

## ✨ Core Capabilities

- **📊 Centralized Dashboard**: Real-time analytics on student enrollment, average academic scores, and early-warning detection mechanisms for at-risk individuals.
- **👥 Intelligent Directory**: A frictionless CRUD interface offering dynamic search capabilities and automated student status evaluation.
- **📈 Data Visualization**: Interactive rendering of classroom grade distributions and overarching attendance trends.
- **🤖 AI-Powered Academic Assistant**:
  - **💬 Conversational Analysis**: Interrogate classroom data using natural language queries.
  - **📝 Automated Audits**: Generate deep-dive analytical reports highlighting institutional strengths, weaknesses, and necessary interventions.
  - **👤 Personalized Advising**: Obtain tailored academic roadmaps for specific students instantly.

## 💻 Local Development Setup

### Prerequisites
- Python 3.12+
- Git

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/kinza03/student-management-system.git
   cd student-management-system
   ```

2. **Environment Configuration**
   Create a `.env` file in the root directory and add your Google Gemini API key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```
   *(Note: For security, the system also supports injecting the API key directly via the frontend UI).*

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Server**
   ```bash
   uvicorn app.main:app --reload
   ```
   The backend API and the static frontend will be served at `http://localhost:8000/`. The database auto-seeds sample data upon initial startup.

## 📖 API Documentation

FastAPI automatically provisions interactive API documentation when running locally:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🌍 Vercel Deployment

This application is strictly optimized for **Vercel Serverless Deployment** ⚡. 
The included `vercel.json` configuration file seamlessly maps the FastAPI endpoints to Vercel's serverless functions while serving the static frontend assets.

> **Important Data Persistence Note**: Because Vercel serverless functions use an ephemeral `/tmp` filesystem, local SQLite databases will be wiped between cold starts. For persistent production data on Vercel, it is highly recommended to configure a remote PostgreSQL database (such as Neon or Supabase) via the `DATABASE_URL` environment variable.

## 📄 License
Distributed under the MIT License.
