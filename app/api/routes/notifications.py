from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.notification import Notification

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def get_my_notifications(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Muestra las notificaciones del usuario, ordenadas por fecha.
    Usa la relación 'notifications' que ya definimos en el modelo User.
    """
    notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).all()
    
    return templates.TemplateResponse("notifications.html", {
        "request": request,
        "notifications": notifications
    })

@router.post("/mark_as_read")
def mark_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Marca todas las notificaciones no leídas del usuario como leídas.
    """
    # Busca todas las notificaciones del usuario que no estén leídas
    unread_notifications = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    )
    
    # Actualiza el campo 'is_read' a True
    unread_notifications.update({"is_read": True})
    
    db.commit()
    
    # Redirige de vuelta a la lista de notificaciones
    return RedirectResponse(url="/notifications/", status_code=303)