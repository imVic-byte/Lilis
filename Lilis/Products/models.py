from django.db import models

class Supplier(models.Model):
    bussiness_name = models.CharField(max_length=100)
    fantasy_name = models.CharField(max_length=100)
    rut = models.CharField(max_length=20, unique=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    trade_terms = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.bussiness_name} - {self.rut}'

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name  
    
    def count_products(self):
        return self.products.filter(is_active=True).count()
    
    def count_raw_materials(self):
        return self.raw_materials.filter(is_active=True).count()
    
class RawMaterialClass(models.Model):
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_perishable = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="raw_materials")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="raw_materials")
    measurement_unit = models.CharField(max_length=100, choices = [('U','Unidades'), ('KG','Kilogramos'), ('L','Litros')])

    def __str__(self):
        return self.name

class Producto(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey("Category", on_delete=models.PROTECT, related_name="products")
    is_perishable = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    measurement_unit = models.CharField(max_length=100, choices = [('U','Unidades'), ('KG','Kilogramos'), ('L','Litros')])

    def __str__(self):
        return f'{self.name} - {self.sku}'
