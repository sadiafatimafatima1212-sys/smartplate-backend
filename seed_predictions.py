import random
from database import SessionLocal
import models

db = SessionLocal()

prep_records = db.query(models.PrepRecord).all()

count = 0
for rec in prep_records:
    existing = db.query(models.Prediction).filter(
        models.Prediction.session_id == rec.session_id,
        models.Prediction.item_id == rec.item_id
    ).first()
    if existing:
        continue

    variance = random.uniform(-0.15, 0.10)
    predicted_qty = round(float(rec.quantity_prepared) * (1 + variance), 2)

    prediction = models.Prediction(
        session_id=rec.session_id,
        item_id=rec.item_id,
        predicted_quantity=predicted_qty,
        model_version="placeholder-v0"
    )
    db.add(prediction)
    count += 1

db.commit()
print(f"✅ Generated {count} placeholder predictions!")
db.close()