import os
import click
from jinja2 import Template

PROJECT_TEMPLATE = """\
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
"""

APP_TEMPLATE = """\
from fastapi import APIRouter

router = APIRouter()

@router.get("/")

def read_items():
    return {"message": "Hello from {{ app_name }}"}
"""

APP_ROUTER_TEMPLATE = """\
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_{{ app_name }}():
    return {"message": "Hello from {{ app_name }}"}
"""

ROUTES_TEMPLATE = """\
import importlib
import pkgutil
from fastapi import APIRouter
import routers

router = APIRouter()

# Dynamically import and include all routers from 'routers' package
for _, module_name, _ in pkgutil.iter_modules(routers.__path__):
    module = importlib.import_module(f"routers.{module_name}")
    if hasattr(module, "router"):
        router.include_router(module.router, prefix=f"/{module_name}", tags=[module_name.capitalize()])
"""

DATABASE_TEMPLATE = """\
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
"""

MODELS_TEMPLATE = """\
from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
"""

SCHEMAS_TEMPLATE = """\
from pydantic import BaseModel

class UserBase(BaseModel):
    email: str
    hashed_password: str

"""

ALEMBIC_TEMPLATE = """\
# Alembic placeholder
"""


@click.group()
def cli():
    """FastAPI Project Generator CLI"""
    pass

@click.command()
@click.argument("name")
def startproject(name):
    """Create a new FastAPI project."""
    os.makedirs(f"{name}/routers", exist_ok=True)

    with open(f"{name}/main.py", "w") as f:
        f.write('from fastapi import FastAPI\nfrom routes import router\n\napp = FastAPI()\napp.include_router(router)\n\n@app.get("/")\ndef root():\n    return {"message": "Welcome to FastAPI Project"}\n')

    with open(f"{name}/database.py", "w") as f:
        f.write(DATABASE_TEMPLATE)

    with open(f"{name}/models.py", "w") as f:
        f.write(MODELS_TEMPLATE)

    with open(f"{name}/schemas.py", "w") as f:
        f.write(SCHEMAS_TEMPLATE)

    with open(f"{name}/routes.py", "w") as f:
        f.write(ROUTES_TEMPLATE)

    with open(f"{name}/alembic.ini", "w") as f:
        f.write(ALEMBIC_TEMPLATE)

    click.echo(f"FastAPI project '{name}' created successfully!")


@click.command()
@click.argument("name")
def startapp(name):
    """Create a new FastAPI app (router)."""
    app_path = f"routers/{name}.py"

    if not os.path.exists("routers"):
        click.echo("Error: No 'routers' directory found! Are you inside a FastAPI project?")
        return

    # Create router file
    with open(app_path, "w") as f:
        f.write(Template(APP_ROUTER_TEMPLATE).render(app_name=name))

    # Ensure routes.py exists
    if not os.path.exists("routes.py"):
        with open("routes.py", "w") as f:
            f.write(ROUTES_TEMPLATE)

    click.echo(f"App '{name}' created successfully! All routes will be auto-detected.")


cli.add_command(startproject)
cli.add_command(startapp)

if __name__ == "__main__":
    cli()
