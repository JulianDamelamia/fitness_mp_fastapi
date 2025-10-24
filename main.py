from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.routes import users, home
from app.schemas import UserResponse

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")
# para desp usar CSS/js externo
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(home.router, prefix="/home", tags=["Home"])      # login, /me
app.include_router(users.router, prefix="/users", tags=["Users"])  # backoffice

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    return UserResponse(username=username, message="Login successful")

@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    return UserResponse(username=username, message="Registration successful")
