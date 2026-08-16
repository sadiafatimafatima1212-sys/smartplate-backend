from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select
import models
import schemas
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "SmartPlate AI backend is running!"}

@app.post("/menu", response_model=schemas.MenuItemOut)
def create_menu_item(item: schemas.MenuItemCreate, db: Session = Depends(get_db)):
    new_item = models.MenuItem(name=item.name, category=item.category, unit=item.unit)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.get("/menu", response_model=list[schemas.MenuItemOut])
def list_menu_items(db: Session = Depends(get_db)):
    return db.execute(select(models.MenuItem)).scalars().all()
@app.post("/sessions", response_model=schemas.MealSessionOut)
def create_session(session: schemas.MealSessionCreate, db: Session = Depends(get_db)):
    new_session = models.MealSession(date=session.date, meal_type=session.meal_type)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@app.get("/sessions", response_model=list[schemas.MealSessionOut])
def list_sessions(db: Session = Depends(get_db)):
    return db.execute(select(models.MealSession)).scalars().all()
@app.post("/prep", response_model=schemas.PrepRecordOut)
def create_prep_record(record: schemas.PrepRecordCreate, db: Session = Depends(get_db)):
    new_record = models.PrepRecord(
        session_id=record.session_id,
        item_id=record.item_id,
        quantity_prepared=record.quantity_prepared
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

@app.get("/prep", response_model=list[schemas.PrepRecordOut])
def list_prep_records(db: Session = Depends(get_db)):
    return db.execute(select(models.PrepRecord)).scalars().all()

@app.post("/consumption", response_model=schemas.ConsumptionRecordOut)
def create_consumption_record(record: schemas.ConsumptionRecordCreate, db: Session = Depends(get_db)):
    new_record = models.ConsumptionRecord(
        session_id=record.session_id,
        item_id=record.item_id,
        quantity_consumed=record.quantity_consumed,
        quantity_wasted=record.quantity_wasted
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record

@app.get("/consumption", response_model=list[schemas.ConsumptionRecordOut])
def list_consumption_records(db: Session = Depends(get_db)):
    return db.execute(select(models.ConsumptionRecord)).scalars().all()

@app.post("/predictions/{session_id}/{item_id}", response_model=schemas.PredictionOut)
def generate_prediction(session_id: int, item_id: int, db: Session = Depends(get_db)):
    # PLACEHOLDER: Person 1 will replace this with their real model's output
    predicted_qty = 18.5

    new_prediction = models.Prediction(
        session_id=session_id,
        item_id=item_id,
        predicted_quantity=predicted_qty,
        model_version="placeholder-v0"
    )
    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)
    return new_prediction

@app.get("/predictions", response_model=list[schemas.PredictionOut])
def list_predictions(db: Session = Depends(get_db)):
    return db.execute(select(models.Prediction)).scalars().all()

from sqlalchemy import func

@app.get("/analytics/summary", response_model=schemas.DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_prepared = db.execute(
        select(func.coalesce(func.sum(models.PrepRecord.quantity_prepared), 0))
    ).scalar()

    total_waste = db.execute(
        select(func.coalesce(func.sum(models.ConsumptionRecord.quantity_wasted), 0))
    ).scalar()

    # Placeholder rate — swap for a real per-kg cost once you have one
    cost_per_kg = 80
    cost_saved = float(total_waste) * cost_per_kg

    waste_pct = (float(total_waste) / float(total_prepared) * 100) if total_prepared else 0

    return schemas.DashboardSummary(
        total_prepared_kg=float(total_prepared),
        total_waste_kg=float(total_waste),
        cost_saved_inr=round(cost_saved, 2),
        waste_percentage=round(waste_pct, 2)
    )

@app.get("/analytics/weekly-demand", response_model=list[schemas.WeeklyDemandPoint])
def weekly_demand(db: Session = Depends(get_db)):
    actual_rows = db.execute(
        select(
            models.MealSession.date,
            func.sum(models.PrepRecord.quantity_prepared).label("actual")
        )
        .join(models.PrepRecord, models.PrepRecord.session_id == models.MealSession.id)
        .group_by(models.MealSession.date)
    ).all()

    predicted_rows = db.execute(
        select(
            models.MealSession.date,
            func.sum(models.Prediction.predicted_quantity).label("predicted")
        )
        .join(models.Prediction, models.Prediction.session_id == models.MealSession.id)
        .group_by(models.MealSession.date)
    ).all()

    actual_map = {row.date: float(row.actual) for row in actual_rows}
    predicted_map = {row.date: float(row.predicted) for row in predicted_rows}

    all_dates = sorted(set(actual_map.keys()) | set(predicted_map.keys()))

    result = []
    for d in all_dates:
        result.append(schemas.WeeklyDemandPoint(
            date=d,
            day_label=d.strftime("%a"),
            actual_plates=actual_map.get(d, 0),
            predicted_plates=predicted_map.get(d, 0)
        ))
    return result

@app.get("/alerts", response_model=list[schemas.AlertOut])
def get_alerts(db: Session = Depends(get_db)):
    rows = db.execute(
        select(
            models.MenuItem.name,
            models.MealSession.date,
            models.MealSession.meal_type,
            models.PrepRecord.quantity_prepared,
            models.ConsumptionRecord.quantity_wasted
        )
        .select_from(models.ConsumptionRecord)
        .join(models.PrepRecord, (models.PrepRecord.session_id == models.ConsumptionRecord.session_id) &
                                  (models.PrepRecord.item_id == models.ConsumptionRecord.item_id))
        .join(models.MenuItem, models.MenuItem.id == models.ConsumptionRecord.item_id)
        .join(models.MealSession, models.MealSession.id == models.ConsumptionRecord.session_id)
    ).all()

    alerts = []
    for row in rows:
        prepared = float(row.quantity_prepared)
        wasted = float(row.quantity_wasted)
        if prepared == 0:
            continue
        waste_pct = round((wasted / prepared) * 100, 1)

        if waste_pct >= 20:
            alerts.append(schemas.AlertOut(
                type="critical",
                title="High Waste Alert",
                message=f"{waste_pct}% of {row.name} wasted during {row.meal_type}.",
                date=row.date,
                meal_type=row.meal_type
            ))
        elif waste_pct >= 10:
            alerts.append(schemas.AlertOut(
                type="info",
                title="Moderate Waste Notice",
                message=f"{waste_pct}% of {row.name} wasted during {row.meal_type}.",
                date=row.date,
                meal_type=row.meal_type
            ))

    alerts.sort(key=lambda a: a.date, reverse=True)
    return alerts[:15]

@app.get("/menu-planner", response_model=list[schemas.MenuPlannerItem])
def get_menu_planner(db: Session = Depends(get_db)):
    items = db.execute(select(models.MenuItem)).scalars().all()
    result = []
    for item in items:
        consumption_rows = db.execute(
            select(models.ConsumptionRecord).where(models.ConsumptionRecord.item_id == item.id)
        ).scalars().all()

        total_wasted = sum(float(r.quantity_wasted) for r in consumption_rows)
        total_consumed = sum(float(r.quantity_consumed) for r in consumption_rows)
        total = total_wasted + total_consumed

        variance = -round(item.base_plate_count * (total_wasted / total) * 0.5) if total > 0 else 0

        result.append(schemas.MenuPlannerItem(
            id=item.id,
            name=item.name,
            meal_type=item.category,
            base_plate_count=item.base_plate_count,
            ai_variance_factor=variance,
            target_production=item.base_plate_count + variance
        ))
    return result

@app.put("/menu-planner/{item_id}", response_model=schemas.MenuPlannerItem)
def update_menu_planner(item_id: int, update: schemas.MenuPlannerUpdate, db: Session = Depends(get_db)):
    item = db.get(models.MenuItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.base_plate_count = update.base_plate_count
    db.commit()
    db.refresh(item)

    consumption_rows = db.execute(
        select(models.ConsumptionRecord).where(models.ConsumptionRecord.item_id == item.id)
    ).scalars().all()
    total_wasted = sum(float(r.quantity_wasted) for r in consumption_rows)
    total_consumed = sum(float(r.quantity_consumed) for r in consumption_rows)
    total = total_wasted + total_consumed
    variance = -round(item.base_plate_count * (total_wasted / total) * 0.5) if total > 0 else 0

    return schemas.MenuPlannerItem(
        id=item.id,
        name=item.name,
        meal_type=item.category,
        base_plate_count=item.base_plate_count,
        ai_variance_factor=variance,
        target_production=item.base_plate_count + variance
    )