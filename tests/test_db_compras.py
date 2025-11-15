"""Tests para las operaciones de compra en la base de datos de la aplicación de fitness."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from app.models import User, Plan, Purchase

from app.db.session import Base


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()


def test_user_can_purchase_plan(session):
    user = User(username="alice")
    plan = Plan(title="Plan Full Body", price=1000, creator=user)
    session.add_all([user, plan])
    session.commit()

    purchase = Purchase(user_id=user.id, plan_id=plan.id)
    session.add(purchase)
    session.commit()

    assert purchase.id is not None
    assert purchase.user_id == user.id
    assert purchase.plan_id == plan.id

    session.refresh(user)
    session.refresh(plan)

    assert plan in user.purchased_plans
    assert user in plan.buyers
    assert len(user.purchases) == 1
    assert user.purchases[0].plan == plan


def test_user_can_have_multiple_purchases(session):
    user = User(username="carol")
    plan1 = Plan(title="Plan Principiante", price=800, creator=user)
    plan2 = Plan(title="Plan Avanzado", price=1500, creator=user)
    session.add_all([user, plan1, plan2])
    session.commit()

    purchase1 = Purchase(user_id=user.id, plan_id=plan1.id)
    purchase2 = Purchase(user_id=user.id, plan_id=plan2.id)
    session.add_all([purchase1, purchase2])
    session.commit()

    session.refresh(user)
    assert len(user.purchased_plans) == 2
    assert plan1 in user.purchased_plans and plan2 in user.purchased_plans
