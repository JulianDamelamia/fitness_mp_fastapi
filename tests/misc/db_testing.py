from sqlalchemy.orm import Session as dbSession
from sqlalchemy.dialects.postgresql import insert
from app.database import engine, Base
from app.models import User, Plan, Routine, SessionTemplate, ExerciseTemplate, Purchase, Session, PerformedExercise

# Crear las tablas
Base.metadata.drop_all(bind=engine)

# Vuelve a crear todas las tablas
Base.metadata.create_all(bind=engine)

db = dbSession(bind=engine)

user = User(username="julian", email="julian@mail.com", hashed_password="hashed_pw")
db.add(user)
db.commit()
db.refresh(user)

# Crear un plan
plan = Plan(title="Full Body 3x/sem", price=2000, trainer_id=user.id)
db.add(plan)
db.commit()
db.refresh(plan)

# Crear una rutina dentro del plan
routine = Routine(name="Rutina Full Body", plan_id=plan.id)
db.add(routine)
db.commit()
db.refresh(routine)

session_template = SessionTemplate(name="Día 1 - Push", routine_id=routine.id)
db.add(session_template)
db.commit()
db.refresh(session_template)

# Crear ejercicios abstractos
exercise1 = ExerciseTemplate(
    session_template_id=session_template.id,
    exercise_name="Press de banca",
    target_sets=3,
    target_reps=10,
    target_weight=50,
    primary_muscles=["pecho", "tríceps"],
    secondary_muscles=["hombros"]
)
exercise2 = ExerciseTemplate(
    session_template_id=session_template.id,
    exercise_name="Press militar",
    target_sets=3,
    target_reps=12,
    target_weight=30,
    primary_muscles=["hombros"],
    secondary_muscles=["tríceps"]
)

db.add_all([exercise1, exercise2])
db.commit()

# Compra del plan
purchase = Purchase(user_id=user.id, plan_id=plan.id)
db.add(purchase)
db.commit()
db.refresh(purchase)

# Crear sesión concreta a partir de SessionTemplate
user_session = Session(purchase_id=purchase.id, session_template_id=session_template.id)
db.add(user_session)
db.commit()
db.refresh(user_session)

# Registrar ejercicios concretos
performed1 = PerformedExercise(
    session_id=user_session.id,
    exercise_name=exercise1.exercise_name,
    set_number=1,
    performed_reps=10,
    performed_weight=50
)
performed2 = PerformedExercise(
    session_id=user_session.id,
    exercise_name=exercise1.exercise_name,
    set_number=2,
    performed_reps=9,
    performed_weight=50
)

db.add_all([performed1, performed2])
db.commit()

# Verificar ejercicios de la sesión abstracta
sess_temp = db.query(SessionTemplate).first()
for ex in sess_temp.exercises:
    print(ex.exercise_name, ex.target_sets, ex.target_reps)

# Verificar ejercicios realizados en la sesión concreta
sess = db.query(Session).first()
for ex in sess.performed_exercises:
    print(ex.exercise_name, ex.set_number, ex.performed_reps)