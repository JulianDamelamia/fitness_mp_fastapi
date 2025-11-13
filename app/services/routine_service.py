from typing import List
from sqlalchemy.orm import Session as db_Session
from sqlalchemy import and_

from app.models.fitness import Routine, Session, Exercise
from app.models.associations import routines_sessions
from app.builders.routine_builder import RoutineBuilder, SessionBuilder
from app.errors.errors import EntityNotFoundError,ValidationError 
class RoutineService:
    """Servicio para gestionar operaciones relacionadas con rutinas de ejercicio
    vinculando los builders con las acciones sobre la base de datos
    Proporciona métodos estáticos para crear y actualizar rutinas, validando
    datos de entrada y gestionando la persistencia en base de datos.
    """

    @staticmethod
    def create_routine(routine_data, db: db_Session, current_user_id: int):
        """Crea una nueva rutina de ejercicio.
        Args:
            routine_data: Objeto con datos de la rutina (name, sessions).
            db: Sesión de base de datos.
            current_user_id: ID del usuario creador.
        Returns:
            Routine: Rutina creada y persistida.
        Raises:
            ValidationError: Si falta nombre, sesiones o datos requeridos en sesiones/ejercicios.
        """
        if not getattr(routine_data, "name", None):
            raise ValidationError("La rutina requiere un nombre")
        
        if not getattr(routine_data, "sessions", None):
            raise ValidationError("La rutina debe incluir al menos una sesión")
        
        routine = RoutineBuilder.create_routine(
            routine_data=routine_data, creator_id=current_user_id, db=db)

        for s_data in routine_data.sessions:
            if not getattr(s_data, "session_name", None):
                raise ValidationError("Las sesiones nuevas requieren un nombre")

            for e_data in getattr(s_data, "exercises", []):
                if not getattr(e_data, "exercise_name", None):
                    raise ValidationError("Los ejercicios nuevos requieren un nombre")

        db.add(routine)
        db.commit()
        db.refresh(routine)
        return routine
    
    @staticmethod
    def update_routine(routine_id, routine_data, db, current_user_id):
        """Actualiza una rutina existente.
        Args:
            routine_id: ID de la rutina a actualizar.
            routine_data: Objeto con datos actualizados (name, sessions).
            db: Sesión de base de datos.
            current_user_id: ID del usuario (debe ser el creador).
        Returns:
            Routine: Rutina actualizada.
        Raises:
            EntityNotFoundError: Si la rutina o sesiones no existen.
            ValidationError: Si el usuario no está autorizado.
        """
        routine = db.query(Routine).filter(Routine.id == routine_id).first()
        if not routine:
            raise EntityNotFoundError(f"Rutina ID {routine_id} no encontrada")

        if routine.creator_id != current_user_id:
            raise ValidationError("No autorizado para modificar esta rutina")

        if getattr(routine_data, "name", None):
            routine.name = routine_data.name
 
        if not getattr(routine_data, "sessions", None):
            db.commit()
            db.refresh(routine)
            return routine

        updated_sessions = []
        for session_data in routine_data.sessions:
            if getattr(session_data, "id", None):
                session = db.query(Session).filter(Session.id == session_data.id).first()
                if not session:
                    raise EntityNotFoundError(f"Session ID {session_data.id} no encontrada")
                session = SessionBuilder.update_session(session, session_data, db)
            else:
                # Nueva sesión
                session = SessionBuilder.create_session(session_data.session_name, session_data.exercises, db)

            updated_sessions.append(session)
        
        for s in updated_sessions:
            if s not in routine.sessions:
                routine.sessions.append(s)
        db.commit()
        db.refresh(routine)
        return routine
    
    @staticmethod
    def delete_sessions(routine: Routine, session_ids: List[int], db):
        """Elimina de una rutina las sesiones cuyos IDs se indiquen."""
        if not session_ids:
            raise ValidationError("Debe especificar al menos un ID de sesión a eliminar")

        deleted = []
        for sid in session_ids:
            # query:
            # SELECT s.* FROM sessions AS s
            # JOIN routines_session AS rs ON s.id = rs.session_id
            # WHERE rs.routine_id = :routine_ids AND s.id = :session_id
            session = (
                    db.query(Session)
                    .join(routines_sessions, Session.id == routines_sessions.c.session_id)
                    .filter(
                        and_(
                            routines_sessions.c.routine_id == routine.id,
                            Session.id == sid
                        )
                    )
            .first()
        )
            if not session:
                raise EntityNotFoundError(f"La sesión con ID {sid} no existe en esta rutina")
            db.delete(session)
            deleted.append(sid)
        return deleted
    
    @staticmethod
    def update_exercise(db, ex_data):
        """Actualiza un ejercicio existente según los datos recibidos."""
        exercise = db.query(Exercise).filter(Exercise.id == ex_data.id).first()
        if not exercise:
            raise EntityNotFoundError(f"Exercise ID {ex_data.id} no encontrado")
        if getattr(ex_data, "exercise_name", None):
            exercise.exercise_name = ex_data.exercise_name
        if getattr(ex_data, "target_sets", None) is not None:
            exercise.target_sets = ex_data.target_sets
        if getattr(ex_data, "target_reps", None) is not None:
            exercise.target_reps = ex_data.target_reps
        return exercise