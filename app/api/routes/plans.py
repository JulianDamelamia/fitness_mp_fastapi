from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.api.dependencies import get_db, get_current_user, get_current_trainer
from app.models.user import User
from app.models.business import Plan, Purchase
from app.schemas.business import Plan as PlanSchema, Purchase as PurchaseSchema, PlanCreate
from app.models.fitness import Routine

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


#--- ENDPOINTS PARA CLIENTES ---

# GET /planes -> Listar planes disponibles
@router.get("/", response_class=HTMLResponse)
def get_available_plans(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # subquery con los IDs de los planes que el usuario ya compró
    purchased_plan_ids_subquery = db.query(Purchase.plan_id).filter(
        Purchase.user_id == current_user.id
    ).subquery()

    # planes que no estén en la lista de comprados
    plans = db.query(Plan).filter(
        Plan.id.notin_(purchased_plan_ids_subquery)
    ).all()
    
    return templates.TemplateResponse("plans.html", {
        "request": request, 
        "plans": plans
    })


@router.get("/{id}", response_model=PlanSchema)
def get_plan_details(
    id: int, 
    db: Session = Depends(get_db)
):
    plan = db.query(Plan).filter(Plan.id == id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    return plan


# POST /compra -> Registrar una compra
@router.post("/purchase", response_model=PurchaseSchema)
def purchase_plan(
    plan_id: int = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Usuario autenticado
):
    # Verificar que el plan existe
    plan_to_buy = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan_to_buy:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
        
    # Crear la nueva compra
    db_purchase = Purchase(
        user_id=current_user.id,
        plan_id=plan_id
        # La 'purchase_date' se establece automáticamente
    )
    
    db.add(db_purchase)
    db.commit()
    
    return RedirectResponse(url="/plans/my-plans/", status_code=303)

# GET /mis_planes -> Listar los planes comprados por el usuario
@router.get("/my-plans/", response_class=HTMLResponse)
def get_my_purchased_plans(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Usuario autenticado
):
    plans = current_user.purchased_plans

    return templates.TemplateResponse("my-plans.html", {
        "request": request,
        "plans": plans
    })

# --- ENDPOINTS PARA ENTRENADORES ---

#TODO: mergear con el metodo de crear plan hecho en la HU1
@router.post("/", response_model=PlanSchema)
def create_plan(
    title: str = Form(...),
    description: str = Form(""), # Descripción opcional
    price: int = Form(...),
    routine_ids: List[int] = Form([]),
    db: Session = Depends(get_db),
    current_trainer: User = Depends(get_current_trainer)
):
    # Creamos el plan
    db_plan = Plan(
        title=title,
        description=description,
        price=price,
        trainer_id=current_trainer.id
    )

    if routine_ids:
        selected_routines = db.query(Routine).filter(
            Routine.id.in_(routine_ids),
            Routine.creator_id == current_trainer.id # Seguridad: solo puede agregar sus propias rutinas
        ).all()
        db_plan.routines.extend(selected_routines)

    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)

    return RedirectResponse(url="/plans/my-creations/", status_code=303)


@router.get("/my-creations/", response_class=HTMLResponse)
def get_my_created_plans(
    request: Request,
    db: Session = Depends(get_db),
    current_trainer: User = Depends(get_current_trainer)
):
    """
    Muestra los planes creados por el entrenador logueado.
    """
    plans = db.query(Plan).filter(Plan.trainer_id == current_trainer.id).all()    
    
    my_routines = db.query(Routine).filter(Routine.creator_id == current_trainer.id).all()

    return templates.TemplateResponse("my-creations.html", {
        "request": request,
        "plans": plans,
        "username": current_trainer.username,
        "routines": my_routines
    })


@router.put("/{plan_id}", response_model=PlanSchema)
def update_my_plan(
    plan_id: int,
    title: str = Form(...),
    description: str = Form(""),
    price: int = Form(...),
    db: Session = Depends(get_db),
    current_trainer: User = Depends(get_current_trainer)
):
    """
    Edita un plan que le pertenece.
    """
    db_plan = db.query(Plan).filter(Plan.id == plan_id).first()

    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    # Verificación de propiedad
    if db_plan.trainer_id != current_trainer.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para editar este plan")

    # Actualizar los datos
    db_plan.title = title
    db_plan.description = description
    db_plan.price = price
    
    db.commit()
    return RedirectResponse(url="/plans/my-creations/", status_code=303)

@router.delete("/{plan_id}", response_model=dict)
def delete_my_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_trainer: User = Depends(get_current_trainer)
):
    """
    Desactiva (elimina) un plan que le pertenece.
    """
    db_plan = db.query(Plan).filter(Plan.id == plan_id).first()

    if not db_plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    # Verificación de propiedad
    if db_plan.trainer_id != current_trainer.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este plan")

    db.delete(db_plan)
    db.commit()
    
    return {"message": "Plan eliminado exitosamente"}