from django.db import models

class Supplier(models.Model):
    bussiness_name = models.CharField(max_length=100)
    fantasy_name = models.CharField(max_length=100)
    rut = models.CharField(max_length=20, unique=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    trade_terms = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.bussiness_name} - {self.rut}'

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name  
    
class RawMaterial(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_perishable = models.BooleanField(default=False)
    expiration_date = models.DateField(null=True, blank=True)
    created_at = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="raw_materials")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="raw_materials")
    measurement_unit = models.CharField(max_length=100, choices = [('U','Unidades'), ('KG','Kilogramos'), ('L','Litros')])
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name    
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey("Category", on_delete=models.PROTECT, related_name="products")
    is_perishable = models.BooleanField(default=False)
    expiration_date = models.DateField(null=True, blank=True)
    created_at = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    measurement_unit = models.CharField(max_length=100, choices = [('U','Unidades'), ('KG','Kilogramos'), ('L','Litros')])
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.name} - {self.sku}'
    
    def get_product_price(self):
        last_price = self.price_histories.order_by('-date').first()
        return last_price.unit_price

class PriceHistories(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="price_histories")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=1.19)

    def __str__(self):
        return f'{self.product.name} - {self.unit_price} - {self.date}'

class Batch(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, null=True)
    batch_code = models.CharField(max_length=100, unique=True)
    min_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    current_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    max_quantity = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.batch_code}"
    
    def get_product_price(self):
        last_price = self.product.price_histories.order_by('-date').first()
        return last_price.unit_price
    
    def get_total_product_stock(self):
        stock = self.current_quantity * self.product.quantity
        return stock
    
    def get_total_raw_material_stock(self):
        stock = self.current_quantity * self.raw_material.quantity
        return stock