from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.business import Plan, Purchase
from app.schemas.business import Plan as PlanSchema, Purchase as PurchaseSchema, PurchaseCreate

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# GET /planes -> Listar planes disponibles
@router.get("/", response_class=HTMLResponse)
def get_available_plans(
    request: Request,
    db: Session = Depends(get_db), skip: int = 0, limit: int = 100):
    plans = db.query(Plan).all()
    #plans = db.query(Plan).offset(skip).limit(limit).all()
    #return plans
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
    # Usar la relación 'purchased_plans' definida en modelo User
    # O hacer una consulta explícita
    plans = current_user.purchased_plans
    
    # Alternativa usando la relación (si está cargada o configurada para lazy load):
    # plans = current_user.purchased_plans # Usar esta linea si se puede
    
    return templates.TemplateResponse("my-plans.html", {
        "request": request,
        "plans": plans
    })

