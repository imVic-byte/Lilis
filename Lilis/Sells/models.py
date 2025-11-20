from django.db import models
from Products.models import Producto, RawMaterialClass
from Accounts.models import Profile

class Client(models.Model):
    bussiness_name = models.CharField(max_length=100)
    fantasy_name = models.CharField(max_length=100)
    rut = models.CharField(max_length=20, unique=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.IntegerField(null=True, blank=True)
    credit_limit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    debt = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_debt = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_suspended = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.bussiness_name} - {self.rut}'
    
class Location (models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="Chile")

    def __str__(self):
        return self.name

class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    total_area = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    location = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.name} - {self.location}'
    
class WareClient(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="wareclients")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="wareclients")
    status = models.CharField(max_length=20, choices=[('A', 'Activo'), ('I', 'Inactivo')], default='A')
    association_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.client.bussiness_name} - {self.warehouse.name} - status: {self.status}'
    
#VOY A PROBAR ALGUNAS COSAS
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
    batch = models.ForeignKey(Lote, on_delete=models.PROTECT, related_name="transactiondetails")
    serie = models.ForeignKey(Serie, on_delete=models.PROTECT, related_name="transactiondetails")