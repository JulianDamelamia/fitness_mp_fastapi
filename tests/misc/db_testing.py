from app.models.fitness import Session, Exercise
from app.api.dependencies import get_db

db = next(get_db())

s = Session(name="Test session")
db.add(s)
db.commit()
db.refresh(s)

e = Exercise(name="Press banca", session_id=s.id)
db.add(e)
db.commit()

print('comprobacion')
print(s.exercises[0].name)  # debería mostrar 'Press banca'

