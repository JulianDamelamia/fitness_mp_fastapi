"""Tests para verificar la creación y relaciones de Rutinas y Sesiones en la base de datos."""

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base
from app.models.user import User
from app.models.fitness import Routine, Session


DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    """Crea una sesión temporal de base de datos para los tests."""
    engine = create_engine(DATABASE_URL, echo=False)
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_create_routine_with_sessions(db_session):
    user = User(username="julian", email="julian@example.com", hashed_password="1234")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    s1 = Session(session_name="Día 1 - Push")
    s2 = Session(session_name="Día 2 - Pull")
    s3 = Session(session_name="Día 3 - Legs")
    sesiones_list = [s1, s2, s3]
    db_session.add_all(sesiones_list)
    db_session.commit()

    rutina = Routine(name="Full Body 3x", creator_id=user.id, sessions=sesiones_list)
    db_session.add(rutina)
    db_session.commit()
    db_session.refresh(rutina)

    # existencia
    assert rutina.id is not None
    assert len(rutina.sessions) == 3
    assert rutina.sessions[0].session_name in ["Día 1 - Push", "Día 2 - Pull"]

    # relación inversa
    assert s1.routines[0].name == "Full Body 3x"

    # verificar relación con el creador
    assert rutina.creator.username == "julian"
    assert rutina.creator.email == "julian@example.com"

    # Consultas directas
    all_routines = db_session.query(Routine).all()
    assert len(all_routines) == 1

    all_sessions = db_session.query(Session).all()
    assert len(all_sessions) == 3

    # test join (routines -> sessions)
    result = (
        db_session.query(Routine)
        .filter(Routine.sessions.any(Session.session_name == "Día 1 - Push"))
        .first()
    )
    assert result.name == "Full Body 3x"
