import pytest
from fastapi.testclient import TestClient
from app.models import User, Plan, Purchase


def test_ver_catalogo_planes_como_usuario_autenticado(authenticated_client, db_session):
    """
    Prueba que un usuario autenticado puede ver el catálogo de planes.
    """
    # Crear un plan en la DB para que no esté vacía
    user = db_session.query(User).filter_by(username="testuser").first()
    db_plan = Plan(title="Plan de Test", description="Descripción de prueba", price=1500, trainer_id=user.id)
    db_session.add(db_plan)
    db_session.commit()

    # Visitar la página del catálogo
    response = authenticated_client.get("/plans/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Plan de Test" in response.text
    assert "Descripción de prueba" in response.text


def test_comprar_plan_y_ver_en_mis_planes(authenticated_client, db_session):
    """
    Prueba el flujo completo:
    Un usuario compra un plan.
    Es redirigido a "Mis Planes".
    "Mis Planes" ahora muestra el plan comprado.
    """

    user = db_session.query(User).filter_by(username="testuser").first()
    plan_to_buy = Plan(title="Plan Comprable", price=2000, trainer_id=user.id)
    db_session.add(plan_to_buy)
    db_session.commit()
    db_session.refresh(plan_to_buy) # Para obtener el ID

    # Simular el clic en "Comprar"
    response_purchase = authenticated_client.post(
        "/plans/purchase",
        data={"plan_id": plan_to_buy.id},
        follow_redirects=False # Capturamos la redirección
    )

    # Verificación de la compra
    assert response_purchase.status_code == 303
    assert response_purchase.headers["location"] == "/plans/my-plans/"

    # Verificación en la base de datos
    purchase = db_session.query(Purchase).filter_by(user_id=user.id, plan_id=plan_to_buy.id).first()
    assert purchase is not None

    # Seguir la redirección y ver la página de "Mis Planes"
    response_my_plans = authenticated_client.get("/plans/my-plans/")
    
    # Verificación final
    assert response_my_plans.status_code == 200
    assert "Mis Planes Comprados" in response_my_plans.text
    assert "Plan Comprable" in response_my_plans.text


def test_comprar_plan_sin_autenticacion(client, db_session):
    """
    Prueba que un usuario NO logueado (un visitante) es rechazado
    si intenta comprar un plan.
    """
    # Crear un plan (no necesitamos un usuario)
    trainer = User(username="trainer", email="trainer@test.com", hashed_password="...")
    db_session.add(trainer)
    db_session.commit()
    db_session.refresh(trainer)

    plan_a_comprar = Plan(title="Plan Secreto", price=100, trainer_id=trainer.id)
    db_session.add(plan_a_comprar)
    db_session.commit()
    db_session.refresh(plan_a_comprar)

    # Intentar comprar usando el 'client' (que no está logueado)
    response_purchase = client.post(
        "/plans/purchase",
        data={"plan_id": plan_a_comprar.id},
        follow_redirects=False 
    )

    # 3. Verificación:
    #    La dependencia 'get_current_user' debe fallar con 401 Unauthorized
    assert response_purchase.status_code == 401


def test_comprar_plan_que_no_existe(authenticated_client, db_session):
    """
    Prueba que la app maneja correctamente si un usuario logueado
    intenta comprar un plan_id que no existe.
    """
    id_inexistente = 999

    # Intentar comprar el plan con ID 999
    response_purchase = authenticated_client.post(
        "/plans/purchase",
        data={"plan_id": id_inexistente},
        follow_redirects=False
    )

    # Verificación:
    assert response_purchase.status_code == 404
    assert "Plan no encontrado" in response_purchase.text

def test_comprar_sin_enviar_plan_id(authenticated_client):
    """
    Prueba que la app devuelve un error si el formulario se envía
    sin el campo 'plan_id'.
    """
    # Enviar el formulario vacío
    response_purchase = authenticated_client.post(
        "/plans/purchase",
        data={}, # ¡No enviamos el 'plan_id'!
        follow_redirects=False
    )

    # Verificación:
    assert response_purchase.status_code == 422