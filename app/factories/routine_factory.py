from app.models.fitness import Routine, Session, Exercise

class RoutineFactory:
    @staticmethod
    def create_routine(routine_data, creator_id: int):
        routine = Routine(name=routine_data.name, creator_id=creator_id)
        
        for s in routine_data.sessions:
            session = Session(session_name=s.session_name)
            
            for e in s.exercises:
                exercise = Exercise(
                    session_id=s.session_id,
                    exercise_name=e.exercise_name,
                    target_sets=e.target_sets or 0,
                    target_reps=e.target_reps or 0,
                    target_weight=e.target_weight or 0,
                )
                session.exercises.append(exercise)
            
            routine.sessions.append(session)
  
        return routine