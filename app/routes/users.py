from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.auth import verify_password, create_access_token, get_password_hash
from datetime import timedelta

router = APIRouter()


fake_user_db = {
    "julian": {
        "username": "julian",
        "hashed_password": get_password_hash("secret123"),
    }
}

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_user_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Credenciales inválidas")

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
