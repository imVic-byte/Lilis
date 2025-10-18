import requests
from Products.models import Supplier, RawMaterial

API_URL = "http://3.226.223.190"

class API:
    def get_data():
        response = requests.get(f"{API_URL}/api/suppliers")
        suppliers_list = []
        if response.status_code == 200:
            data = response.json()
            for item in data:
                supplier = Supplier(
                    id=item.get("id"),
                    bussiness_name=item.get("bussiness_name"),
                    rut=item.get("rut"),
                    email=item.get("email"),
                    phone=item.get("phone"),
                    trade_terms=item.get("trade_terms")
                )
                raw_materials = []
                for rm in item.get("rawMaterials", []):
                        raw = RawMaterial(
                            id=rm.get("id"),
                            name=rm.get("name"),
                            description=rm.get("description"),
                            stock_quantity=rm.get("stock_quantity"),
                            expiration_date=rm.get("expiration_date"),
                            is_active=rm.get("is_active")
                        )
                        raw.current_price = rm.get("price", None)
                        raw_materials.append(raw)
                supplier.temp_raw_materials = raw_materials
                suppliers_list.append(supplier)
        else:
            print("FALLOOOOOOOOOOOOOOOO")
        return suppliers_list