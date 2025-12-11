from django.db import models

class Client(models.Model):
    bussiness_name = models.CharField(max_length=100, verbose_name='Nombre')
    fantasy_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Nombre fantasía')
    rut = models.CharField(max_length=20, unique=True, verbose_name='RUT')
    email = models.EmailField(null=True, blank=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Teléfono')
    address = models.CharField(max_length=200, blank=True, null=True, verbose_name='Dirección')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='Ciudad')
    country = models.CharField(max_length=100, default='Chile', verbose_name='País')
    web_site = models.URLField(blank=True, null=True, verbose_name='Página web')
    payment_terms_days = models.IntegerField(default=30, verbose_name='Días de pago')
    currency = models.CharField(max_length=10, choices=[('CLP', 'Peso Chileno'), ('USD', 'Dólar'), ('EUR', 'Euro')], default='CLP', verbose_name='Moneda')
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name='Descuento')    
    trade_terms = models.TextField(blank=True, null=True, verbose_name='Términos de comercio')
    is_preferred = models.BooleanField(default=False, verbose_name='Preferido')
    lead_time_days = models.IntegerField(default=7, verbose_name='Días de atención')
    is_active = models.BooleanField(default=True, verbose_name='Activo')

    def __str__(self):
        return f'{self.bussiness_name} - {self.rut}'
    
    @classmethod
    def get_create_fields(cls):
        return [
            'bussiness_name',
            'fantasy_name',
            'rut',
            'email',
            'phone',
            'address',
            'city',
            'country',
            'web_site',
            'payment_terms_days',
            'currency',
            'discount_percentage',
            'trade_terms',
            'is_preferred',
            'lead_time_days',
            'is_active',
        ]

class Warehouse(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nombre')
    address = models.CharField(max_length=200, verbose_name='Dirección')
    total_area = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Área total')
    location = models.CharField(max_length=200, verbose_name='Ubicación')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    lilis = models.BooleanField(default=False, verbose_name='Lilis')
    
    def __str__(self):
        return f'{self.name} - {self.location}'
    
    @classmethod
    def get_create_fields(cls):
        return [
            'name',
            'address',
            'total_area',
            'location',
        ]
    
class WareClient(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="wareclients")
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="wareclients")
    association_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name='Activo')

    def __str__(self):
        return f'{self.client.bussiness_name} - {self.warehouse.name} - status: {self.is_active}'
    