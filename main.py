from fastapi import FastAPI
from app.routes import users

app = FastAPI()
app.include_router(users.router)

@app.get("/")
def read_root():
	return{"message":"hola mundo"}

