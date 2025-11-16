"""Tests for the Plan and Routine models and their relationship."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base
from app.models.user import User
from app.models.fitness import Routine
from app.models.business import Plan


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()


def test_plan_routine_relationship(session):
    user = User(username="julian", hashed_password="1234", email="julian@example.com")
    session.add(user)
    session.commit()

    r1 = Routine(name="Full Body A", creator=user)
    r2 = Routine(name="Full Body B", creator=user)
    plan = Plan(title="Plan Fuerza", price=3000, creator=user)
    plan.routines.extend([r1, r2])

    session.add_all([r1, r2, plan])
    session.commit()

    plan_from_db = session.query(Plan).filter_by(title="Plan Fuerza").first()
    assert plan_from_db is not None
    assert len(plan_from_db.routines) == 2
    assert {r.name for r in plan_from_db.routines} == {"Full Body A", "Full Body B"}

    routine_from_db = session.query(Routine).filter_by(name="Full Body A").first()
    assert routine_from_db is not None
    assert len(routine_from_db.plans) == 1
    assert routine_from_db.plans[0].title == "Plan Fuerza"

    assert routine_from_db.creator.username == "julian"
    assert plan_from_db.creator.username == "julian"
