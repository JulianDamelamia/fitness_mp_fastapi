from app.models.tracker import SessionLog, ExerciseLog
from app.models.fitness import Exercise

class SessionFactory:
    def __init__(self, db):
        self.db = db

    def create_session(self, data):
        session_log = SessionLog(session_id=data.session_id, date=data.date)

        for ex in data.exercises:
            exercise = self.db.query(Exercise).filter(Exercise.id == ex.exercise_id).first()
            if not exercise:
                raise ValueError(f"Exercise with id {ex.exercise_id} not found")

            log = ExerciseLog(
                weight=ex.weight,
                reps=str(ex.reps),  
                set_n=len(ex.reps),
                exercise_id=exercise.id,
            )
            session_log.exercise_logs.append(log)


        return session_log