from Products.models import (
    Product, Category, RawMaterial, Batch, Supplier, PriceHistories,
)


from Products.forms import (
    RawMaterialForm,  PriceHistoriesForm, ProductBatchForm,RawBatchForm, ProductForm, 
    CategoryForm, SupplierForm,
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
        self.model = Product
        self.form_class = ProductForm
    
    def search_by_sku(self, sku):
        return self.model.objects.filter(sku=sku).first()
    
    def search_by_description(self, description):
        return self.model.objects.filter(description__icontains=description)
    
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
        self.model = RawMaterial
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

class BatchService(CRUD):
    def __init__(self):
        self.model = Batch
        self.product_form_class = ProductBatchForm
        self.raw_form_class = RawBatchForm

    def save_price(self, data):
        form = self.price_form(data)
        if form.is_valid():
            price = form.save()
            return True, price
        return False, form
    
    def delete_price(self, id):
        try:
            prices = self.price_model.objects.filter(batch__id=id)
            for p in prices:
                p.delete()
            return True, prices
        except self.price_model.DoesNotExist:
            return False, None
    
    def save_product_batch(self,data):
        form = self.product_form_class(data)
        if form.is_valid():
            product = form.save()
            return True, product
        return False, form
    
    def save_raw_batch(self,data):
        form = self.raw_form_class(data)
        if form.is_valid():
            raw = form.save()
            return True, raw
        return False, form
    
    def update_product_batch(self,id,data):
        batch = self.get(id)
        form = self.product_form_class(data, instance=batch)
        if form.is_valid():
            obj = form.save()
            return True, obj
        return False, obj
    
    def update_raw_batch(self,id,data):
        batch = self.get(id)
        form = self.raw_form_class(data, instance=batch)
        if form.is_valid():
            form.save()
            return True, form
        return False, form
    
    def delete_product_batch(self, id):
        batch = self.get(id)
        try:
            batch.delete()
            return True, batch
        except self.model.DoesNotExist:
            return False, None
    
    def delete_raw_batch(self, id):
        batch = self.get(id)
        try:
            batch.delete()
            return True, batch
        except self.model.DoesNotExist:
            return False, None

    def search_by_product(self, product_id):
        return self.model.objects.filter(product__id=product_id)
    
    def search_by_raw_material(self, raw_material_id):
        return self.model.objects.filter(raw_material__id=raw_material_id)
    
    def list_product(self):
        return self.model.objects.filter(product__isnull=False)
    
    def list_raw_materials(self):
        return self.model.objects.filter(raw_material__isnull=False)
    
class PriceHistoriesService(CRUD):
    
    def __init__(self):
        self.model = PriceHistories
        self.form_class = PriceHistoriesForm
    