from sqlalchemy import Column, Integer, String, Date, ForeignKey, Numeric, DateTime, Enum
from sqlalchemy.sql import func
from database import Base
import enum

class MealType(str, enum.Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"

class MenuItem(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String)
    unit = Column(String, default="kg")
    base_plate_count = Column(Integer, default=50)
    

class MealSession(Base):
    __tablename__ = "meal_sessions"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    meal_type = Column(Enum(MealType), nullable=False)

class PrepRecord(Base):
    __tablename__ = "prep_records"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("meal_sessions.id"))
    item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity_prepared = Column(Numeric, nullable=False)

class ConsumptionRecord(Base):
    __tablename__ = "consumption_records"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("meal_sessions.id"))
    item_id = Column(Integer, ForeignKey("menu_items.id"))
    quantity_consumed = Column(Numeric, nullable=False)
    quantity_wasted = Column(Numeric, nullable=False)

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("meal_sessions.id"))
    item_id = Column(Integer, ForeignKey("menu_items.id"))
    predicted_quantity = Column(Numeric, nullable=False)
    model_version = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())