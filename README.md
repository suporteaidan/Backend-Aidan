# Aidan API

Backend API built with FastAPI for the Aidan application.

---

## 🚀 Tech Stack

- Python 3.12+
- FastAPI
- Async SQLAlchemy
- PostgreSQL
- Poetry

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/aidan-api.git
cd aidan-api
Install dependencies:

poetry install

Activate environment:

poetry env activate

⚙️ Environment Variables

Create a .env file in the project root:

DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DATABASE

▶️ Run the Application

poetry run uvicorn app.main:app --reload

Swagger documentation:

http://localhost:8000/docs