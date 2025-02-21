# FastAPI CLI 🚀

A simple CLI tool to generate FastAPI project structures.

## Installation

```bash
pip install fastapi-cli


## Run server

```bash
uvicorn main:app --reload

```bash
myproject/
│── main.py          # Entry point for FastAPI app
│── routes.py        # Contains 'custom_routes'
│── alembic.ini
│── models.py
│── schemas.py
│── middlewares/
│   ├── middleware.py  # Global middleware logic
│── routers/         # API route modules
│── settings/
│   ├── database.py  # Database configuration
│   ├── routing.py   # Router configurations
│── alembic/
