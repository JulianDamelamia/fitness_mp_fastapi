from typing import List
from app.models.fitness import Routine, Session, Exercise
from app.errors.errors import EntityNotFoundError, ValidationError


class ExerciseBuilder:
    """Gestiona la creación y actualización de ejercicios."""

    @staticmethod
    def create_exercise(db, session, ex_data):
        """Crea un ejercicio nuevo o retorna uno existente según el id."""
        if getattr(ex_data, "id", None):
            existing = db.query(Exercise).filter_by(id=ex_data.id).first()
            if not existing:
                raise ValidationError(f"Ejercicio con ID {ex_data.id} no encontrado")
            return existing

        required_fields = ["exercise_name", "target_sets", "target_reps"]
        for field in required_fields:
            if getattr(ex_data, field, None) is None:
                raise ValidationError(
                    f"El campo '{field}' es obligatorio para ejercicios nuevos"
                )

        return Exercise(
            exercise_name=ex_data.exercise_name,
            target_sets=ex_data.target_sets,
            target_reps=ex_data.target_reps,
            target_weight=getattr(ex_data, "target_weight", 0),
            session=session,
        )

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


class SessionBuilder:
    """Gestiona la creación y actualización de sesiones."""

    @staticmethod
    def create_session(session_name: str, exercise_list: List, db):
        """Crea una sesión con su lista de ejercicios."""
        if not session_name or not session_name.strip():
            raise ValidationError(
                "El campo 'session_name' es obligatorio y no puede estar vacío"
            )

        session = Session(session_name=session_name)
        for e in exercise_list:
            exercise = ExerciseBuilder.create_exercise(
                db=db, session=session, ex_data=e
            )
            session.exercises.append(exercise)
        return session

    @staticmethod
    def update_session(session: Session, session_data, db):
        """Actualiza una sesión existente, agregando ejercicios nuevos si los hay."""
        if getattr(session_data, "session_name", None):
            session.session_name = session_data.session_name

        if getattr(session_data, "exercises", None) is not None:
            for ex_data in session_data.exercises:
                if getattr(ex_data, "id", None):
                    exercise = ExerciseBuilder.update_exercise(db, ex_data)
                else:
                    exercise = ExerciseBuilder.create_exercise(db, session, ex_data)
                    session.exercises.append(exercise)
        return session


class RoutineBuilder:
    """Construye y actualiza rutinas con sus sesiones y ejercicios."""

    @staticmethod
    def create_routine(routine_data, creator_id: int, db):
        """Crea una rutina nueva con las sesiones indicadas."""
        if not routine_data.name or not routine_data.name.strip():
            raise ValidationError(
                "El campo 'name' es obligatorio y no puede estar vacío"
            )

        routine = Routine(name=routine_data.name, creator_id=creator_id)

        for s in routine_data.sessions:
            session_to_add = None

            # CASO 1: El usuario seleccionó una sesión existente
            if getattr(s, "id", None):
                session_to_add = db.query(Session).filter_by(id=s.id).first()
                if not session_to_add:
                    raise EntityNotFoundError(f"Sesión con ID {s.id} no encontrada")

            # CASO 2: El usuario está creando una sesión nueva
            else:
                session_to_add = SessionBuilder.create_session(
                    session_name=s.session_name, exercise_list=s.exercises, db=db
                )

            if session_to_add:
                routine.sessions.append(session_to_add)

        return routine
