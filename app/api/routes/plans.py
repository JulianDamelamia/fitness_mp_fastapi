from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.api.dependencies import get_db, get_current_user, get_current_trainer
from app.models.user import User
from app.models.business import Plan, Purchase, PlanCreate
from app.schemas.business import Plan as PlanSchema, Purchase as PurchaseSchema, PurchaseCreate, PlanResponse

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


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


# GET /planes/{id} -> Obtener detalle de un plan
@router.get("/{id}", response_model=PlanSchema)
def get_plan_details(id: int, db: Session = Depends(get_db)):
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


#TODO: mergear con el metodo de crear plan hecho en la HU1
@router.post("/planes", response_model=PlanResponse)
def create_plan(
    plan_in: PlanCreate, 
    db: Session = Depends(get_db),
    # Solo un trainer puede crear un plan para vender
    current_trainer: User = Depends(get_current_trainer) 
):
    # Creamos el plan
    db_plan = Plan(
        name=plan_in.name,
        price=plan_in.price,
        creator_id=current_trainer.id
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


# GET /entrenador/planes
@router.get("/planes/me", response_model=List[PlanResponse])
def get_my_published_plans(
    db: Session = Depends(get_db),
    current_trainer: User = Depends(get_current_trainer)
):
    return current_trainer.created_plans