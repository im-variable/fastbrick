import os
import click
from jinja2 import Template

# Default template for main.py
MAIN_TEMPLATE = """\
from fastapi import FastAPI
from settings.middleware import GlobalMiddleware
from settings.routing import router

app = FastAPI()

# ✅ Add Middleware
app.add_middleware(GlobalMiddleware)

# ✅ Include API routes
app.include_router(router)

@app.get("/")
def root():
    return {"message": "Welcome to FastAPI Project"}
"""

# Default template for new app routers
APP_ROUTER_TEMPLATE = """\
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def {{ app_name }}_home():
    return {"message": "Welcome to the {{ app_name }} app"}
"""

# Default template for database settings
DATABASE_TEMPLATE = """\
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
"""

# Template for dynamic routing
ROUTING_TEMPLATE = """\
import importlib
import pkgutil
from fastapi import APIRouter
import routers

# Import custom route mappings from routes.py
from routes import app_routes

router = APIRouter()

# Dynamically import and include all routers from 'routers' package
for _, module_name, _ in pkgutil.iter_modules(routers.__path__):
    module = importlib.import_module(f"routers.{module_name}")
    
    if hasattr(module, "router"):
        prefix = app_routes.get(module_name, f"/{module_name}")
        router.include_router(module.router, prefix=prefix, tags=[module_name.capitalize()])
"""

# routes.py template (Separate file for `app_routes`)
ROUTES_TEMPLATE = """\
# Users can modify this dictionary to change route prefixes
app_routes = {}
"""

MODELS_TEMPLATE = """\
from sqlalchemy import Column, Integer, String
from settings.database import Base

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

MIDDLEWARE_TEMPLATE = """\
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("middleware")

# Define Blocked IPs
BLOCKED_IPS = {"192.168.1.1"}  # Add more IPs here

class GlobalMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = request.client.host

        # 🛑 Block Requests from Certain IPs
        if client_ip in BLOCKED_IPS:
            return Response(content="⛔ Access Denied", status_code=403)

        # ⏳ Process Request
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"❌ Exception: {e}")
            return Response(content="🚨 Internal Server Error", status_code=500)

        # ⏱️ Track Request Time
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-App-Version"] = "1.0.0"

        logger.info(f"✅ {request.method} {request.url} - {response.status_code} ({process_time:.4f}s)")
        return response
"""


@click.group()
def cli():
    """FastAPI Project Generator CLI"""
    pass

@click.command(name="create-project")
@click.argument("name")
def create_project(name):
    """Create a new FastAPI project with a clean structure."""
    
    # Create project directories
    os.makedirs(f"{name}/routers", exist_ok=True)
    os.makedirs(f"{name}/settings", exist_ok=True)
    os.makedirs(f"{name}/alembic", exist_ok=True)

    # Create main.py
    with open(f"{name}/main.py", "w") as f:
        f.write(Template(MAIN_TEMPLATE).render(project_name=name))

    # Create settings/database.py
    with open(f"{name}/settings/database.py", "w") as f:
        f.write(DATABASE_TEMPLATE)

    # Create settings/routing.py
    with open(f"{name}/settings/routing.py", "w") as f:
        f.write(ROUTING_TEMPLATE)

    # Create settings/middleware.py
    with open(f"{name}/settings/middleware.py", "w") as f:
        f.write(MIDDLEWARE_TEMPLATE)

    # Create models.py
    with open(f"{name}/models.py", "w") as f:
        f.write(MODELS_TEMPLATE)

    # Create schemas.py
    with open(f"{name}/schemas.py", "w") as f:
        f.write(SCHEMAS_TEMPLATE)

    # Create alembic.ini
    with open(f"{name}/alembic.ini", "w") as f:
        f.write(ALEMBIC_TEMPLATE)

    # Create routes.py
    with open(f"{name}/routes.py", "w") as f:
        f.write(ROUTES_TEMPLATE)

    click.echo(f"✅ FastAPI project '{name}' created successfully with structured settings!")


@click.command(name="create-app")
@click.argument("name")
def create_app(name):
    """Create a new FastAPI app (router) with database settings."""
    app_path = f"routers/{name}.py"
    settings_path = "settings/"
    routing_config_path = os.path.join(settings_path, "routing.py")

    if not os.path.exists("routers"):
        click.echo("❌ Error: No 'routers' directory found! Are you inside a FastAPI project?")
        return

    # Ensure settings folder exists
    os.makedirs(settings_path, exist_ok=True)

    # Create router file
    with open(app_path, "w") as f:
        f.write(Template(APP_ROUTER_TEMPLATE).render(app_name=name))

    # Ensure database.py exists inside settings/
    db_config_path = os.path.join(settings_path, "database.py")
    if not os.path.exists(db_config_path):
        with open(db_config_path, "w") as f:
            f.write(DATABASE_TEMPLATE)

    # Ensure routing.py exists inside settings/
    if not os.path.exists(routing_config_path):
        with open(routing_config_path, "w") as f:
            f.write(ROUTING_TEMPLATE)

    # Ensure routes.py exists outside settings/
    if not os.path.exists("routes.py"):
        with open("routes.py", "w") as f:
            f.write(ROUTING_TEMPLATE)

    # Update `settings/routing.py` with the new default prefix
    with open("routes.py", "r+") as f:
        content = f.read()
        if "app_routes = {" in content:
            new_entry = f'    "{name}": "/{name}",\n'
            if f'"{name}":' not in content:  # Prevent duplicate entries
                updated_content = content.replace("app_routes = {", f"app_routes = {{\n{new_entry}")
                f.seek(0)
                f.write(updated_content)
                f.truncate()

    click.echo(f"✅ App '{name}' created successfully! All routes will be auto-detected.")


cli.add_command(create_project)
cli.add_command(create_app)

if __name__ == "__main__":
    cli()
