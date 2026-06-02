# 🎓 Student Management System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
[![Vercel](https://img.shields.io/badge/Vercel-Deployed-000000.svg?style=flat&logo=vercel&logoColor=white)](https://vercel.com/)
[![Gemini API](https://img.shields.io/badge/Gemini-AI_Integrated-8E75B2.svg?style=flat&logo=google&logoColor=white)](https://deepmind.google/technologies/gemini/)

A robust, full-stack academic monitoring and management portal designed to track student performance, analyze attendance metrics, and provide actionable, AI-driven insights using Google's Gemini LLM.

## Architecture & Technology Stack

- **Backend**: FastAPI (Python 3.12)
- **Database**: SQLite (Local development) / PostgreSQL (Production deployment ready)
- **ORM**: SQLAlchemy
- **Frontend**: Vanilla HTML5, CSS3, JavaScript
- **Data Visualization**: Chart.js
- **AI Integration**: Google GenAI SDK (Gemini)
- **Deployment**: Vercel (Serverless) / Render

## Key Features ✨

- **Comprehensive Dashboard**: Real-time analytics on student enrollment, average grades, and early-warning detection for at-risk students.
- **Student Directory**: A complete CRUD (Create, Read, Update, Delete) interface with intelligent search capabilities and automated academic status evaluation.
- **Interactive Visualizations**: Dynamic rendering of grade distributions and course attendance metrics.
- **AI-Powered Assistant**:
  - **Conversational Queries**: Query the database using natural language to extract specific classroom trends.
  - **Classroom Audit**: Generate extensive automated reports highlighting class strengths, weaknesses, and intervention strategies.
  - **Individual Student Advisor**: Obtain personalized roadmaps and recommendations for specific students.

## Local Development Setup

### Prerequisites
- Python 3.12 or higher
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kinza03/student-management-system.git
   cd student-management-system
   ```

2. **Configure Environment Variables**
   ```bash
   cp .env.example .env
   ```
   Add your Google Gemini API key to the `.env` file:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```
   *(Note: The application also supports securely passing the API key directly via the frontend UI during runtime).*

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Application**
   ```bash
   uvicorn app.main:app --reload
   ```
   The backend API and the static frontend will be served at `http://localhost:8000/`. The database is automatically seeded with sample data upon initialization.

## API Documentation

When running locally, FastAPI automatically generates interactive API documentation.
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Production Deployment 🚀

### Vercel (Serverless)
The project includes a `vercel.json` configuration file, optimizing the FastAPI application and static assets for Vercel's serverless environment. 
*Note: Due to the ephemeral nature of serverless environments, it is highly recommended to configure a remote PostgreSQL database (e.g., Neon or Supabase) via the `DATABASE_URL` environment variable to ensure data persistence.*

### Render (Stateful)
A `render.yaml` Blueprint is provided for deploying the application alongside a managed, persistent PostgreSQL database.

## License
Distributed under the MIT License.
