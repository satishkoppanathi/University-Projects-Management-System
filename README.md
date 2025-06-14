# 🎓 University Project Management System

**Role-Based Web Application for Academic Project Management and Performance Tracking**

## 📌 Project Summary

The **University Project Management System** is a full-stack web application built using **Flask (Python)** for backend and **HTML/CSS/JavaScript** for frontend, designed to streamline student project supervision at a university level. It supports **role-based access** for Students, Professors, HODs, and Directors with custom dashboards, centralized analytics, and collaborative features.

## 🚀 Key Responsibilities and Features

- 🔐 **Role-Based Access Control (RBAC)**: Personalized dashboards for Students, Professors, HODs, and the Director.
- 🧑‍🏫 **Professor Dashboard**: Supervise multiple student projects, monitor milestones, and provide feedback.
- 🏢 **HOD Dashboard**: Access all departmental projects, analyze completion rates and professor involvement.
- 🧠 **Director Insights**: University-wide project tracking with performance analytics and visual metrics.
- 📊 **Analytics & Reporting**: Integrated with **Chart.js** and **Pandas** for visual representation of project data.
- 💬 **Collaboration Tools**: In-app communication system for seamless interactions between students and faculty.

## 🔧 Tech Stack Used

| Category       | Technologies                           |
|----------------|----------------------------------------|
| Frontend       | HTML, CSS, JavaScript                  |
| Backend        | Python, Flask                          |
| Database       | SQLite3, SQLAlchemy ORM                |
| Data Analytics | Pandas, Chart.js                       |
| Version Control| Git, GitHub                            |

## 💡 Why This Project Stands Out

- Developed a **centralized project management system** used across multiple departments.
- Implemented **real-time performance monitoring** and **supervision analytics**.
- Delivered a scalable and maintainable Flask architecture following MVC principles.
- Demonstrated team collaboration with clear separation of responsibilities:
  - **Frontend Development**
  - **Backend Development**
  - **Database Integration**
  - **Dashboard and Visualization**

## 📁 Project Structure

```
/university-project-management
│
├── static/              # CSS, JS, assets
├── templates/           # HTML templates (Jinja2)
├── app.py               # Flask application entry
├── models.py            # SQLAlchemy models
├── routes.py            # URL route handlers
├── utils.py             # Helper functions
├── requirements.txt     # Python dependencies
└── README.md            # Project documentation
```

## 🧪 Installation & Run Locally

```bash
# Clone the repository
git clone https://github.com/your-username/university-project-management.git
cd university-project-management

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Visit in browser
http://localhost:5000
```

## 👨‍💻 Team

- 👨‍🔧 **Team Lead**: S. Gnaneswar
- 🎨 **Frontend Developers**: B. Jagadish Naik, C. Jayasri
- 🖥️ **Backend Developer**: K. Satish

## 📈 Achievements & Impact

- ✅ Improved supervision efficiency by 50% through digital dashboards
- ✅ Enabled real-time tracking of over 100+ student projects
- ✅ Reduced reporting errors with integrated performance analytics

