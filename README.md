# 🎓 Student Management System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.100.0+-009688.svg?style=flat\&logo=FastAPI\&logoColor=white)](https://fastapi.tiangolo.com)

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB.svg?style=flat\&logo=python\&logoColor=white)](https://www.python.org)

[![Vercel](https://img.shields.io/badge/Vercel-Deployed-000000.svg?style=flat\&logo=vercel\&logoColor=white)](https://student-management-system-rosy-delta.vercel.app)

[![Gemini API](https://img.shields.io/badge/Gemini-AI_Integrated-8E75B2.svg?style=flat\&logo=google\&logoColor=white)](https://deepmind.google/technologies/gemini/)

A streamlined, full-stack academic management platform engineered to manage student records, monitor academic performance, visualize grades and attendance, and provide actionable AI-driven insights through Google's Gemini LLM. 🚀

> 🌐 **[Experience the Student Management System](https://student-management-system-rosy-delta.vercel.app)**

---

## 🏗️ Architecture & Technology Stack

* **Backend Framework:** FastAPI (Python 3.12)
* **Database Engine:** SQLite / PostgreSQL
* **ORM Layer:** SQLAlchemy
* **Frontend Layer:** Vanilla HTML5, CSS3, JavaScript
* **Dashboard:** Streamlit
* **Data Processing:** Pandas, NumPy
* **Data Visualization:** Matplotlib / Chart.js
* **Intelligence Engine:** Google GenAI SDK — Gemini 2.5 Flash
* **Deployment Configuration:** Vercel / Render

---

## ✨ Core Capabilities

* **📊 Centralized Dashboard:**
  Monitor student enrollment, average class performance, top performers, grade distributions, attendance trends, and students requiring academic attention.

* **👥 Student Directory:**
  Manage student records through CRUD operations with search functionality and automated academic status evaluation.

* **🎯 Academic Status Evaluation:**
  Automatically classify students as **On Track**, **Needs Attention**, or **At Risk** based on academic performance and attendance criteria.

* **📈 Data Visualization:**
  Visualize grade distributions and course-wise attendance to make academic trends easier to understand.

* **🤖 AI-Powered Academic Assistant:**

  * **💬 Conversational Analysis:** Ask natural-language questions about available student and classroom records.
  * **📝 Automated Academic Audits:** Generate class-level reports containing highlights, concerns, and recommendations.
  * **👤 Personalized Advising:** Analyze individual student performance and generate tailored academic recommendations.
  * **📄 Report Generation:** Download generated academic reports as text files.

---

## 🧠 Academic Status Evaluation

The system uses deterministic rules to provide consistent academic classification:

| Status                 | Criteria                                                        |
| ---------------------- | --------------------------------------------------------------- |
| **🔴 At Risk**         | Attendance below 65%, numeric grade below 60, or F/Fail         |
| **🟡 Needs Attention** | Attendance below 75% or numeric grade below 70, but not At Risk |
| **🟢 On Track**        | Does not meet the above conditions                              |

The rule-based evaluation provides the initial classification, while Gemini is used for deeper analysis and recommendations.

---

## 🤖 AI Integration

The application integrates **Google Gemini 2.5 Flash** through the Google GenAI SDK.

### 💬 Ask AI

Users can ask natural-language questions about the available academic records and receive responses based on the student data provided to the model.

### 📝 Class Academic Audit

The AI analyzes class-level student records and generates a structured academic report covering:

* Highlights
* Concerns
* Recommendations

### 👤 Individual Student Advisor

Individual student records can be analyzed to generate personalized academic insights and concrete recommendations.

> **Note:** The AI functionality uses direct LLM integration with structured student data. This project does **not** use Retrieval-Augmented Generation (RAG) or a vector database.

---

## 🔄 Application Workflow

```text
Student Records
       ↓
Database
       ↓
FastAPI / SQLAlchemy
       ↓
Academic Analytics
       ↓
Rule-Based Status Evaluation
       ↓
Gemini 2.5 Flash
       ↓
Academic Insights & Recommendations
```

---

## 💻 Local Development Setup

### Prerequisites

* Python 3.12+
* Git
* Google Gemini API key

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/kinzasabir/student-management-system.git
cd student-management-system
```

**2. Create a virtual environment**

```bash
python -m venv venv
```

**Windows:**

```bash
venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Configure environment variables**

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./students.db
```

For deployments using PostgreSQL, replace `DATABASE_URL` with the appropriate PostgreSQL connection string.

**5. Start the FastAPI application**

```bash
uvicorn app.main:app --reload
```

The application will be available at:

```text
http://localhost:8000/
```

The database automatically seeds sample data when the application starts.

### Run the Streamlit Dashboard

```bash
streamlit run dashboard.py
```

---

## 📖 API Documentation

FastAPI automatically provides interactive API documentation when the application is running locally:

* **Swagger UI:** http://localhost:8000/docs
* **ReDoc:** http://localhost:8000/redoc

These interfaces can be used to explore and test the available API endpoints.

---

## 🌍 Deployment

The repository includes deployment configurations for **Vercel** and **Render**.

### ⚡ Vercel

The included `vercel.json` configures the FastAPI application for Vercel deployment.

For persistent production data, an external PostgreSQL database should be used rather than relying on local SQLite storage.

Configure the database through:

```env
DATABASE_URL=your_postgresql_connection_string
```

### 🗄️ Database Persistence

SQLite is used by default for local development.

PostgreSQL can be configured for deployments requiring persistent external database storage.

---

## 📁 Project Structure

```text
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
```

---

## 🧩 Engineering Highlights

This project demonstrates practical implementation of:

* FastAPI REST API development
* SQLAlchemy ORM and relational data management
* CRUD operations
* Pydantic data validation
* Rule-based academic evaluation
* Academic data visualization
* Google Gemini LLM integration
* Natural-language interaction with structured data
* AI-generated academic reports
* Personalized AI recommendations
* Environment-based configuration
* Cloud deployment configuration

---

## 🎯 Project Focus

The project demonstrates how generative AI can be integrated into a conventional data-driven application rather than functioning as an isolated chatbot.

It combines:

**Software Engineering + Databases + Analytics + APIs + Generative AI**

The result is a practical academic management system with both deterministic application logic and LLM-powered analysis.

---

## 📄 License
Distributed under the MIT License.

---

## 👤 Author

**Kinza Sabir**

* 💻 **GitHub:** [kinzasabir](https://github.com/kinzasabir)
* 🔗 **LinkedIn:** [Kinza Sabir](https://www.linkedin.com/in/kinzasabir/)
