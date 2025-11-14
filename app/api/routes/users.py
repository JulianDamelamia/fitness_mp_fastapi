from fastapi import APIRouter, HTTPException, Depends, status, Header, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db, get_current_user, get_current_admin
from app.models.user import User, UserRole
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


@router.post("/request-trainer", response_model=UserResponse)
def request_trainer_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # <-- Usuario logueado
):
    """
    El usuario logueado solicita convertirse en entrenador.
    """
    if current_user.role == UserRole.TRAINER:
        raise HTTPException(status_code=400, detail="Ya eres un entrenador")
    if current_user.is_pending_trainer:
        raise HTTPException(status_code=400, detail="Ya tienes una solicitud pendiente")

    current_user.is_pending_trainer = True
    db.commit()
    
    return UserResponse(
        username=current_user.username, 
        message="Solicitud para ser entrenador enviada. Pendiente de aprobación."
    )


@router.get("/admin/pending-trainers", response_model=List[str])
def get_pending_trainers(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    (Admin) Lista los usuarios pendientes de aprobación como entrenadores.
    """
    pending_users = db.query(User).filter(
        User.is_pending_trainer == True
    ).all()
    
    return [user.username for user in pending_users]


@router.post("/admin/approve-trainer/{username}", response_model=UserResponse)
def approve_trainer(
    username: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """
    (Admin) Aprueba a un usuario como entrenador.
    """
    user_to_approve = db.query(User).filter(User.username == username).first()
    
    if not user_to_approve:
        raise HTTPException(status_code=4.04, detail="Usuario no encontrado")
    if not user_to_approve.is_pending_trainer:
        raise HTTPException(status_code=400, detail="El usuario no tiene una solicitud pendiente")

    user_to_approve.role = UserRole.TRAINER
    user_to_approve.is_pending_trainer = False
    db.commit()
    
    return UserResponse(
        username=username, 
        message="Usuario aprobado como entrenador exitosamente"
    )

@router.post("/follow/{user_id}")
def follow_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_to_follow = db.query(User).filter(User.id == user_id).first()
    if not user_to_follow:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Evitar auto-seguirse
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="No puedes seguirte a ti mismo")

    # Añadir a la lista de 'following'
    if user_to_follow not in current_user.following:
        current_user.following.append(user_to_follow)
        db.commit()

    # Redirigimos al usuario a la página donde estaba
    referer_url = request.headers.get("referer", "/")
    return RedirectResponse(url=referer_url, status_code=303)


@router.post("/unfollow/{user_id}")
def unfollow_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_to_unfollow = db.query(User).filter(User.id == user_id).first()
    if not user_to_unfollow:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Quitar de la lista de 'following'
    if user_to_unfollow in current_user.following:
        current_user.following.remove(user_to_unfollow)
        db.commit()

    referer_url = request.headers.get("referer", "/")
    return RedirectResponse(url=referer_url, status_code=303)