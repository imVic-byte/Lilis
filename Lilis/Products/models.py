from django.db import models
from Sells.models import Client, Warehouse
from Accounts.models import Profile

class Supplier(models.Model):
    bussiness_name = models.CharField(max_length=100)
    fantasy_name = models.CharField(max_length=100, blank=True, null=True)
    rut = models.CharField(max_length=20, unique=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=200, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default='Chile')
    web_site = models.URLField(blank=True, null=True)
    payment_terms_days = models.IntegerField(default=30)
    currency = models.CharField(max_length=10, choices=[('CLP', 'Peso Chileno'), ('USD', 'Dólar'), ('EUR', 'Euro')], default='CLP')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    trade_terms = models.TextField(blank=True, null=True)
    is_preferred = models.BooleanField(default=False)
    lead_time_days = models.IntegerField(default=7)
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
    sku = models.CharField(max_length=50, unique=True)
    ean_upc = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=50, blank=True, null=True)  
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey("Category", on_delete=models.PROTECT, related_name="raw_materials")
    brand = models.CharField(max_length=50, blank=True, null=True)
    model_code = models.CharField(max_length=50, blank=True, null=True)
    uom_purchase = models.CharField(max_length=100, choices = [('U','Unidades'), ('KG','Kilogramos'), ('L','Litros')], default='U')
    uom_sale = models.CharField(max_length=100, choices = [('U','Unidades'), ('KG','Kilogramos'), ('L','Litros')], default='U')
    conversion_factor = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    standard_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    iva = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    min_stock = models.IntegerField(default=0)
    max_stock = models.IntegerField(default=0)
    reordering_level = models.IntegerField(default=0)
    serie_control = models.BooleanField(default=False)
    batch_control = models.BooleanField(default=False)
    alerta_bajo_stock = models.BooleanField(default=False)
    alerta_por_vencer = models.BooleanField(default=False)
    url_image = models.URLField(blank=True, null=True)
    technical_sheet = models.FileField(upload_to='technical_sheets', blank=True, null=True)
    measurement_unit = models.CharField(max_length=100, choices = [('U','Unidades'), ('KG','Kilogramos'), ('L','Litros')], default='U')
    is_perishable = models.BooleanField(default=False)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="raw_materials")

    def __str__(self):
        return self.name + " - " + self.sku

class Producto(models.Model):
    sku = models.CharField(max_length=50, unique=True)
    ean_upc = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=50, blank=True, null=True)  
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey("Category", on_delete=models.PROTECT, related_name="products")
    brand = models.CharField(max_length=50, blank=True, null=True)
    model_code = models.CharField(max_length=50, blank=True, null=True)
    uom_purchase = models.CharField(max_length=100, choices = [('U','Unidades'), ('KG','Kilogramos'), ('L','Litros')], default='U')
    uom_sale = models.CharField(max_length=100, choices = [('U','Unidades'), ('KG','Kilogramos'), ('L','Litros')], default='U')
    conversion_factor = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    standard_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    iva = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    min_stock = models.IntegerField(default=0)
    max_stock = models.IntegerField(default=0)
    reordering_level = models.IntegerField(default=0)
    serie_control = models.BooleanField(default=False)
    batch_control = models.BooleanField(default=False)
    alerta_bajo_stock = models.BooleanField(default=False)
    alerta_por_vencer = models.BooleanField(default=False)
    url_image = models.URLField(blank=True, null=True)
    technical_sheet = models.FileField(upload_to='technical_sheets', blank=True, null=True)
    measurement_unit = models.CharField(max_length=100, choices = [('U','Unidades'), ('KG','Kilogramos'), ('L','Litros')], default='U')
    is_perishable = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} - {self.sku}'

class Transaction(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="transactions", null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="transactions",null=True, blank=True)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="transactions",null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=20, choices=[('I', 'Ingreso'), ('S', 'Salida'), ('D', 'Devolucion'), ('T', 'Transferencia'), ('A', 'Ajuste')], default='I')
    quantity = models.IntegerField(default=1)
    batch_code = models.CharField(max_length=100, unique=True, blank=True, null=True)
    serie_code = models.CharField(max_length=100, unique=True, null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.type}: Lote: {self.batch_code} - Bodega: {self.warehouse.name} - {self.date}'

class Inventario(models.Model):
    materia_prima = models.ForeignKey(RawMaterialClass, on_delete=models.PROTECT, related_name="inventario", blank=True, null=True )
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="inventario", blank=True, null=True )
    bodega = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="inventario")
    stock_total = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)

    def __str__(self):
        if self.producto:
            return f'{self.producto.name} - {self.producto.sku}'
        return f'{self.materia_prima.name} - {self.materia_prima.sku}'


class Lote(models.Model):
    codigo = models.CharField(max_length=100, unique=True)
    inventario = models.ForeignKey(Inventario, on_delete=models.PROTECT, related_name="lotes")
    cantidad_actual = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_expiracion = models.DateField(null=True, blank=True)
    origen = models.CharField(max_length=20, choices=[('I', 'Ingreso'), ('S', 'Salida'), ('D', 'Devolucion'), ('T', 'Transferencia'), ('A', 'Ajuste')], default='I')

class Serie(models.Model):
    codigo = models.CharField(max_length=100, unique=True)
    inventario = models.ForeignKey(Inventario, on_delete=models.PROTECT, related_name="series")
    estado = models.CharField(max_length=20, choices=[('A', 'Activo'), ('I', 'Inactivo')], default='A')
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_expiracion = models.DateField(null=True, blank=True)

class TransactionDetail(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.PROTECT, related_name="details")
    code = models.CharField(max_length=100, unique=True)
    batch = models.ForeignKey(Lote, on_delete=models.PROTECT, related_name="transactiondetails", null=True, blank=True)
    serie = models.ForeignKey(Serie, on_delete=models.PROTECT, related_name="transactiondetails", null=True, blank=True)