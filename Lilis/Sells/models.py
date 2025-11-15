from django.db import models
from Products.models import Product, Batch
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
    

class Transaction(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="transactions", null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="transactions",null=True, blank=True)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="transactions",null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=20, choices=[('I', 'Ingreso'), ('S', 'Salida')], default='I')
    quantity = models.IntegerField(default=1)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="transactions", null=True, blank=True)
    batch_code = models.CharField(max_length=100, unique=True, blank=True, null=True)
    serie_code = models.CharField(max_length=100, unique=True, null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.type}: Lote: {self.batch_code} - Bodega: {self.warehouse.name} - {self.date}'

class SaleOrder(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="purchase_orders")
    user = models.ForeignKey(Profile, on_delete=models.PROTECT, related_name="purchase_orders")
    created_at = models.DateField(auto_now_add=True)
    confirmation_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('P', 'Pendiente'), ('C', 'Confirmada'), ('A', 'Anulada')], default='P')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    exchange = models.CharField(max_length=20)
    payment_terms = models.CharField(max_length=20)
    observation = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f'{self.status} - pedido: {self.id} - {self.supplier} - total: {self.total_price}'

    def total(self):
        total = sum(detail.subtotal() for detail in self.details.all())
        self.total_price = total
        self.save(update_fields=["total_price"])
        return total

class SaleOrderDetail(models.Model):
    sale_order = models.ForeignKey(SaleOrder, on_delete=models.PROTECT, related_name="details")
    product = models.ForeignKey(Product , on_delete=models.PROTECT, related_name="order_details", null=True)
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def subtotal(self):
        subtotal = self.product.get_product_price * self.quantity
        self.subtotal = subtotal
        self.save(update_fields=["subtotal"])
        return subtotal
    
    def __str__(self):
        return f'{self.sale_order.id} - {self.batch.product.name} x {self.quantity} = {self.subtotal()}'


