from django.db import models
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
    