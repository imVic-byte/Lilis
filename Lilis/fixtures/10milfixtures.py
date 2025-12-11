import json
import random
from datetime import datetime, timedelta

num_fixtures = 10000
categories = [1, 2, 3]
measurement_units = ["U", "KG"]
names = ["Chocolate", "Galleta", "Barra Energética", "Caramelo", "Bombón", "Brownie", "Trufa", "Cupcake", "Turrón"]
descriptions = [
    "Delicioso producto artesanal",
    "Producto de alta calidad",
    "Ideal para compartir",
    "Hecho con ingredientes naturales",
    "Sabor único y exquisito"
]

fixtures = []

for i in range(1, num_fixtures + 1):
    category = random.choice(categories)
    unit = random.choice(measurement_units)
    name = f"{random.choice(names)} {i}"
    description = random.choice(descriptions)
    is_perishable = random.choice([True, False])
    
    if is_perishable:
        expiration_date = (datetime.now() + timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d")
    else:
        expiration_date = (datetime.now() + timedelta(days=random.randint(365, 1000))).strftime("%Y-%m-%d")
    
    fixture = {
        "model": "Products.Product",
        "pk": i,
        "fields": {
            "name": name,
            "sku": f"PROD-{i:05d}",
            "description": description,
            "category": category,
            "is_perishable": is_perishable,
            "expiration_date": expiration_date,
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "is_active": True,
            "measurement_unit": unit,
            "quantity": round(random.uniform(100, 1000), 2)
        }
    }
    
    fixtures.append(fixture)

with open("products_fixtures.json", "w", encoding="utf-8") as f:
    json.dump(fixtures, f, indent=2, ensure_ascii=False)

print(f"Se generaron {num_fixtures} fixtures en 'products_fixtures.json'.")
