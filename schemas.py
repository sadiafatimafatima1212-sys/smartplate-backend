from pydantic import BaseModel

class MenuItemCreate(BaseModel):
    name: str
    category: str
    unit: str = "kg"

class MenuItemOut(MenuItemCreate):
    id: int
    class Config:
        from_attributes = True

from datetime import date

class MealSessionCreate(BaseModel):
    date: date
    meal_type: str  # "breakfast", "lunch", or "dinner"

class MealSessionOut(MealSessionCreate):
    id: int
    class Config:
        from_attributes = True

class PrepRecordCreate(BaseModel):
    session_id: int
    item_id: int
    quantity_prepared: float

class PrepRecordOut(PrepRecordCreate):
    id: int
    class Config:
        from_attributes = True

class ConsumptionRecordCreate(BaseModel):
    session_id: int
    item_id: int
    quantity_consumed: float
    quantity_wasted: float

class ConsumptionRecordOut(ConsumptionRecordCreate):
    id: int
    class Config:
        from_attributes = True

class PredictionOut(BaseModel):
    session_id: int
    item_id: int
    predicted_quantity: float
    model_version: str
    class Config:
        from_attributes = True

class DashboardSummary(BaseModel):
    total_prepared_kg: float
    total_waste_kg: float
    cost_saved_inr: float
    waste_percentage: float

class WeeklyDemandPoint(BaseModel):
    date: date
    day_label: str
    actual_plates: float
    predicted_plates: float

class AlertOut(BaseModel):
    type: str
    title: str
    message: str
    date: date
    meal_type: str

class MenuPlannerItem(BaseModel):
    id: int
    name: str
    meal_type: str
    base_plate_count: int
    ai_variance_factor: int
    target_production: int

class MenuPlannerUpdate(BaseModel):
    base_plate_count: int