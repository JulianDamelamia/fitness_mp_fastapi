from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.routes import users, home


app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
# para desp usar CSS/js externo
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(home.router, prefix="", tags=["Home"])      # login, /me
app.include_router(users.router, prefix="/users", tags=["Users"])  # backoffice
