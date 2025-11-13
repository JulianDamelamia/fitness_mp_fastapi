from sqlalchemy.orm import Session
from typing import Any

from app.interfaces.observer import Observer, Subject
from app.models.user import User
from app.models.business import Plan
from app.models.notification import Notification


class NotificationService(Observer):
    """
    ConcreteObserver, implementa la lógica de crear notificaciones
    en la base de datos cuando un Sujeto lo notifica.
    """

    def update(self, subject: Subject, event_data: Any) -> None:
        """
        El método 'update' es llamado por el Sujeto (notifyObservers).
        """
        
        # Extraemos los datos del evento
        try:
            db: Session = event_data["db"]
            event_type: str = event_data["event_type"]
            plan: Plan = event_data["plan"]
        except KeyError:
            print("Error de Notificación: Faltan datos en event_data.")
            return

        # Notificar a los seguidores
        if event_type == "NEW_PLAN" and isinstance(subject, User):
            trainer: User = subject
            message = f"{trainer.username} ha publicado un nuevo plan: {plan.title}"
            
            # Buscamos a los seguidores del entrenador
            followers = trainer.followed_by
            
            for follower in followers:
                new_notification = Notification(
                    message=message,
                    user_id=follower.id
                )
                db.add(new_notification)

        # Notificar a los compradores
        if event_type == "UPDATED_PLAN":
            message = f"El plan '{plan.title}' que compraste ha sido actualizado."
            
            # Buscamos a los compradores del plan
            buyers = plan.buyers
            
            for buyer in buyers:
                new_notification = Notification(
                    message=message,
                    user_id=buyer.id
                )
                db.add(new_notification)
        
        try:
            db.commit()
        except Exception as e:
            print(f"Error al guardar notificaciones: {e}")
            db.rollback()