from django.db import models
from Sells.models import Client, Warehouse
from Accounts.models import Profile

class Supplier(models.Model):
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

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(blank=True, null=True, verbose_name='Descripción')

    def __str__(self):
        return self.name  
    
    def count_products(self):
        return self.products.filter(is_active=True).count()
    
    def count_raw_materials(self):
        return self.raw_materials.filter(is_active=True).count()
    
    @classmethod
    def get_create_fields(cls):
        return ['name', 'description']

class RawMaterialClass(models.Model):
    sku = models.CharField(max_length=50, unique=True, verbose_name='SKU')
    ean_upc = models.CharField(max_length=50, blank=True, null=True, verbose_name='EAN/UPC')
    name = models.CharField(max_length=100, verbose_name='Nombre')
    model = models.CharField(max_length=50, blank=True, null=True, verbose_name='Modelo')  
    description = models.TextField(blank=True, null=True, verbose_name='Descripción')
    category = models.ForeignKey("Category", on_delete=models.PROTECT, related_name="raw_materials", verbose_name='Categoría')
    brand = models.CharField(max_length=50, blank=True, null=True, verbose_name='Marca')
    model_code = models.CharField(max_length=50, blank=True, null=True, verbose_name='Código de modelo')
    uom_purchase = models.CharField(max_length=100, choices=[('U','Unidades'), ('KG','Kilogramos'), ('L','Litros')], default='U', verbose_name='Unidad de medida (compra)')
    uom_sale = models.CharField(max_length=100, choices=[('U','Unidades'), ('KG','Kilogramos'), ('L','Litros')], default='U', verbose_name='Unidad de medida (venta)')
    conversion_factor = models.DecimalField(max_digits=10, decimal_places=2, default=1.00, verbose_name='Factor de conversión')
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Costo')
    standard_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Costo estándar')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Precio')
    iva = models.IntegerField(default=0, verbose_name='IVA')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    min_stock = models.IntegerField(default=0, verbose_name='Stock mínimo')
    max_stock = models.IntegerField(default=0, verbose_name='Stock máximo')
    reordering_level = models.IntegerField(default=0, verbose_name='Nivel de reorden')
    serie_control = models.BooleanField(default=False, verbose_name='Control de serie')
    batch_control = models.BooleanField(default=False, verbose_name='Control de lote')
    alerta_bajo_stock = models.BooleanField(default=False, verbose_name='Alerta: bajo stock')
    alerta_por_vencer = models.BooleanField(default=False, verbose_name='Alerta: por vencer')
    url_image = models.URLField(blank=True, null=True, verbose_name='URL imagen')
    technical_sheet = models.FileField(upload_to='technical_sheets', blank=True, null=True, verbose_name='Ficha técnica')
    measurement_unit = models.CharField(max_length=100, choices=[('U','Unidades'), ('KG','Kilogramos'), ('L','Litros')], default='U', verbose_name='Unidad de medida')
    is_perishable = models.BooleanField(default=False, verbose_name='Perecedero')
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name="raw_materials", verbose_name='Proveedor')

    def __str__(self):
        return self.name + " - " + self.sku

    @classmethod
    def get_create_fields(cls):
        return [
            'sku',
            'ean_upc',
            'name',
            'model',
            'description',
            'category',
            'brand',
            'model_code',
            'uom_purchase',
            'uom_sale',
            'conversion_factor',
            'cost',
            'standard_cost',
            'price',
            'iva',
            'is_active',
            'min_stock',
            'max_stock',
            'reordering_level',
            'serie_control',
            'batch_control',
            'alerta_bajo_stock',
            'alerta_por_vencer',
            'url_image',
            'technical_sheet',
            'measurement_unit',
            'is_perishable',
            'supplier',
        ]

class Producto(models.Model):
    sku = models.CharField(max_length=50, unique=True, verbose_name='SKU')
    ean_upc = models.CharField(max_length=50, blank=True, null=True, verbose_name='EAN/UPC')
    name = models.CharField(max_length=100, verbose_name='Nombre')
    model = models.CharField(max_length=50, blank=True, null=True, verbose_name='Modelo')  
    description = models.TextField(blank=True, null=True, verbose_name='Descripción')
    category = models.ForeignKey("Category", on_delete=models.PROTECT, related_name="products", verbose_name='Categoría')
    brand = models.CharField(max_length=50, blank=True, null=True, verbose_name='Marca')
    model_code = models.CharField(max_length=50, blank=True, null=True, verbose_name='Código de modelo')
    uom_purchase = models.CharField(max_length=100, choices = [('U','Unidades'), ('KG','Kilogramos'), ('L','Litros')], default='U', verbose_name='Unidad de medida (compra)')
    uom_sale = models.CharField(max_length=100, choices = [('U','Unidades'), ('KG','Kilogramos'), ('L','Litros')], default='U', verbose_name='Unidad de medida (venta)')
    conversion_factor = models.DecimalField(max_digits=10, decimal_places=2, default=1.00, verbose_name='Factor de conversión')
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Costo')
    standard_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Costo estándar')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Precio')
    iva = models.IntegerField(default=0, verbose_name='IVA')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    min_stock = models.IntegerField(default=0, verbose_name='Stock mínimo')
    max_stock = models.IntegerField(default=0, verbose_name='Stock máximo')
    reordering_level = models.IntegerField(default=0, verbose_name='Nivel de reorden')
    serie_control = models.BooleanField(default=False, verbose_name='Control de serie')
    batch_control = models.BooleanField(default=False, verbose_name='Control de lote')
    alerta_bajo_stock = models.BooleanField(default=False, verbose_name='Alerta: bajo stock')
    alerta_por_vencer = models.BooleanField(default=False, verbose_name='Alerta: por vencer')
    url_image = models.URLField(blank=True, null=True, verbose_name='URL imagen')
    technical_sheet = models.FileField(upload_to='technical_sheets', blank=True, null=True, verbose_name='Ficha técnica')
    measurement_unit = models.CharField(max_length=100, choices = [('U','Unidades'), ('KG','Kilogramos'), ('L','Litros')], default='U', verbose_name='Unidad de medida')
    is_perishable = models.BooleanField(default=False, verbose_name='Perecedero')

    def __str__(self):
        return f'{self.name} - {self.sku}'

    @classmethod
    def get_create_fields(cls):
        return [
            'sku',
            'ean_upc',
            'name',
            'model',
            'description',
            'category',
            'brand',
            'model_code',
            'uom_purchase',
            'uom_sale',
            'conversion_factor',
            'cost',
            'standard_cost',
            'price',
            'iva',
            'is_active',
            'min_stock',
            'max_stock',
            'reordering_level',
            'serie_control',
            'batch_control',
            'alerta_bajo_stock',
            'alerta_por_vencer',
            'url_image',
            'technical_sheet',
            'measurement_unit',
            'is_perishable',
        ]

class Transaction(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name="transactions", null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="transactions",null=True, blank=True)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="transactions",null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=20, choices=[('I', 'Ingreso'), ('S', 'Salida'), ('D', 'Devolucion'), ('T', 'Transferencia'), ('A', 'Ajuste')], default='I')
    quantity = models.IntegerField(default=1)
    batch_code = models.CharField(max_length=100, blank=True, null=True)
    serie_code = models.CharField(max_length=100, null=True, blank=True)
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
    codigo = models.CharField(max_length=100)
    inventario = models.ForeignKey(Inventario, on_delete=models.PROTECT, related_name="lotes")
    cantidad_actual = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_expiracion = models.DateField(null=True, blank=True)
    origen = models.CharField(max_length=20, choices=[('I', 'Ingreso'), ('S', 'Salida'), ('D', 'Devolucion'), ('T', 'Transferencia'), ('A', 'Ajuste')], default='I')

class Serie(models.Model):
    codigo = models.CharField(max_length=100)
    inventario = models.ForeignKey(Inventario, on_delete=models.PROTECT, related_name="series")
    estado = models.CharField(max_length=20, choices=[('A', 'Activo'), ('I', 'Inactivo')], default='A')
    fecha_creacion = models.DateField(auto_now_add=True)
    fecha_expiracion = models.DateField(null=True, blank=True)

class TransactionDetail(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.PROTECT, related_name="details")
    code = models.CharField(max_length=100)
    batch = models.ForeignKey(Lote, on_delete=models.PROTECT, related_name="transactiondetails", null=True, blank=True)
    serie = models.ForeignKey(Serie, on_delete=models.PROTECT, related_name="transactiondetails", null=True, blank=True)