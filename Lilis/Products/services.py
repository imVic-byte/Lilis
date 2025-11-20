from Products.models import (
    Category, Supplier, RawMaterialClass, Producto,
)

from decimal import Decimal
from Products.forms import (
    CategoryForm, SupplierForm, RawMaterialForm, ProductForm
)

from Main.CRUD import CRUD

class CategoryService(CRUD):
    def __init__(self):
        self.model = Category
        self.form_class = CategoryForm
    
    def filter_by_category(self, category_id):
        category = self.model.objects.filter(id=category_id).first()
        if category:
            return category.products.all()
        return self.model.objects.none()
    

class ProductService(CRUD):
    def __init__(self):
        self.model = Producto
        self.form_class = ProductForm
    
    def search_by_sku(self, sku):
        return self.model.objects.filter(sku=sku).first()
    
    def search_by_description(self, description):
        return self.model.objects.filter(description__icontains=description)
    
    def list_actives(self):
        return self.model.objects.filter(is_active=True)
    
    def get_stock_by_product(self, product_id):
        product = self.get(id=product_id)
        quantity = product.quantity
        return quantity
    
class SupplierService(CRUD):
    def __init__(self):
        self.model = Supplier
        self.form_class = SupplierForm
    
    def search_by_rut(self, rut):
        return self.model.objects.filter(rut=rut).first()
    
    def search_by_trade_terms(self, trade_terms):
        return self.model.objects.filter(trade_terms__icontains=trade_terms)
    
    def count_actives(self):
        return self.model.objects.filter(is_active=True).count()
    
    def count_inactives(self):
        return self.model.objects.filter(is_active=False).count()
    
    def make_inactive(self, id):
        try:
            supplier = self.model.objects.filter(id=id).first()
            if supplier:
                supplier.is_active = False
                supplier.save()
                return True, supplier
            return False, None
        except self.model.DoesNotExist:
            return False, None

    def make_active(self, id):
        try:
            supplier = self.model.objects.filter(id=id).first()
            if supplier:
                supplier.is_active = True
                supplier.save()
                return True, supplier
            return False, None
        except self.model.DoesNotExist:
            return False, None

    def list_actives(self):
        return self.model.objects.filter(is_active=True)

class RawMaterialService(CRUD):
    def __init__(self):
        self.model = RawMaterialClass
        self.form_class = RawMaterialForm

    def search_by_description(self, description):
        return self.model.objects.filter(description__icontains=description)
    
    def deactivate(self, id):
        try:
            raw_material = self.model.objects.filter(id=id).first()
            if raw_material:
                raw_material.is_active = False
                raw_material.save()
                return True, raw_material
            return False, None
        except self.model.DoesNotExist:
            return False, None
    
    def list_actives(self):
        return self.model.objects.filter(is_active=True)

    def save_raw_material_class(self, data, supplier):
        form = self.form_class(data)
        if form.is_valid():
            raw_material_class = form.save(commit=False)
            raw_material_class.supplier = supplier
            raw_material_class.save()
            return True, raw_material_class
        return False, form