from datetime import date, timedelta
import random
from database import SessionLocal
import models

db = SessionLocal()

items_data = [
    {"name": "Idli Sambhar", "category": "breakfast", "unit": "kg"},
    {"name": "Poha", "category": "breakfast", "unit": "kg"},
    {"name": "Dal Tadka", "category": "lunch", "unit": "kg"},
    {"name": "Mix Veg", "category": "lunch", "unit": "kg"},
    {"name": "Roti", "category": "lunch", "unit": "pieces"},
    {"name": "Paneer Butter Masala", "category": "dinner", "unit": "kg"},
    {"name": "Jeera Rice", "category": "dinner", "unit": "kg"},
]

item_ids = {}
for it in items_data:
    existing = db.query(models.MenuItem).filter(models.MenuItem.name == it["name"]).first()
    if existing:
        item_ids[it["name"]] = existing.id
        continue
    new_item = models.MenuItem(**it)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    item_ids[it["name"]] = new_item.id

today = date.today()
start = today - timedelta(days=6)

for i in range(7):
    day = start + timedelta(days=i)
    for meal in ["breakfast", "lunch", "dinner"]:
        session = models.MealSession(date=day, meal_type=meal)
        db.add(session)
        db.commit()
        db.refresh(session)

        relevant_items = [it["name"] for it in items_data if it["category"] == meal]
        for name in relevant_items:
            prepared = random.randint(30, 60)
            wasted = random.randint(2, 10)
            consumed = prepared - wasted

            db.add(models.PrepRecord(session_id=session.id, item_id=item_ids[name], quantity_prepared=prepared))
            db.add(models.ConsumptionRecord(session_id=session.id, item_id=item_ids[name], quantity_consumed=consumed, quantity_wasted=wasted))
        db.commit()

print("✅ Sample data seeded successfully!")
db.close()