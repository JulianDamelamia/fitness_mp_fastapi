from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter()

@router.get("/", response_model=list[str])
def list_users(db: Session = Depends(get_db)):
    """
    Lista los nombres de usuario de todos los usuarios en la base de datos real.
    """
    users = db.query(User).all()
    return [user.username for user in users]


@router.delete("/{username}", response_model=UserResponse)
def delete_user(
    username: str,
    db: Session = Depends(get_db)
    # TODO que solo un admin pueda borrar usuarios.
):
    """
    Elimina un usuario de la base de datos real.
    """
    user_to_delete = db.query(User).filter(User.username == username).first()
    
    if not user_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    
    db.delete(user_to_delete)
    db.commit()
    
    return UserResponse(username=username, message="Usuario eliminado exitosamente")