from .models import Client, Warehouse, WareClient
from Products.models import Producto, Transaction, Lote, Inventario
from django import forms
from Main.validators import *


class LoteProductoForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = [ 'cantidad_actual', 'fecha_expiracion', 'origen']
        labels = {
            'cantidad_actual': 'Cantidad actual',
            'fecha_expiracion': 'Fecha de vencimiento',
            'origen': 'Origen',
        }
        widgets = {
            'fecha_expiracion': forms.DateInput(attrs={'class': 'form-control','type': 'date'}),
        }

    def clean_fecha_expiracion(self):
        return self.cleaned_data.get('fecha_expiracion')

    def clean_origen(self):
        return self.cleaned_data.get('origen')

    def save(self, commit=True):
        lote = super().save(commit=False)
        if commit:
            lote.save()
            return lote
        return lote

class ClientForm(forms.ModelForm):
    class Meta: 
        model = Client
        fields = [
            'bussiness_name', 'fantasy_name', 'rut', 
            'email', 'phone', 'address', 'city', 'country', 'web_site',
            'payment_terms_days', 'currency', 'discount_percentage', 'trade_terms',
            'is_preferred', 'lead_time_days'
        ]
        labels = {
            'bussiness_name': 'Razón social (requerido)',
            'fantasy_name': 'Nombre de fantasía',
            'rut': 'RUT (requerido)',
            'email': 'Correo electrónico (requerido)',
            'phone': 'Teléfono',
            'address': 'Dirección',
            'city': 'Ciudad',
            'country': 'País (requerido)',
            'web_site': 'Sitio web',
            'payment_terms_days': 'Plazo de pago (días) (requerido)',
            'currency': 'Moneda (requerido)',
            'discount_percentage': 'Descuento (%)',
            'trade_terms': 'Términos comerciales',
            'is_preferred': 'Proveedor preferente',
            'lead_time_days': 'Tiempo de entrega (días)'
        }
    
    def clean_bussiness_name(self):
        return validate_text_length(self.cleaned_data.get('bussiness_name'), field_name="La razón social")

    def clean_fantasy_name(self):
        return validate_text_length(self.cleaned_data.get('fantasy_name'), field_name="El nombre de fantasía")

    def clean_rut(self):
        return validate_rut_format(self.cleaned_data.get('rut'))
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            return validate_email(email)
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            return validate_phone_format(phone)
        return phone

    def clean_credit_limit(self):
        return validate_positive_number(self.cleaned_data.get('credit_limit'), field_name="El límite de crédito", allow_zero=True)

    def clean_debt(self):
        return validate_positive_number(self.cleaned_data.get('debt'), field_name="La deuda", allow_zero=True)

    def clean_max_debt(self):
        return validate_positive_number(self.cleaned_data.get('max_debt'), field_name="La deuda máxima", allow_zero=True)
        
    def save(self, commit=True):
        client = super(ClientForm, self).save(commit=False)
        if commit:
            client.save()
            return client
        return client

        
PAISES = [
    ("CL", "Chile"),
    ("AR", "Argentina"),
    ("PE", "Perú"),
    ("CO", "Colombia"),
    ("MX", "México"),
    ("ES", "España"),
    ("US", "Estados Unidos"),
]

class WarehouseForm(forms.ModelForm):
    location = forms.ChoiceField(
        choices=PAISES,
        label="Localidad",
    )

    class Meta:
        model = Warehouse
        fields = ['name', 'address', 'location', 'total_area']
        labels = {
            'name': 'Nombre del almacén',
            'address': 'Direccion',
            'location': 'Localidad',
            'total_area': 'Area total'
        }
        
    def clean_name(self):
        return validate_text_length(self.cleaned_data.get('name'), field_name="El nombre")

    def clean_address(self):
        return validate_text_length(self.cleaned_data.get('address'), min_length=5, field_name="La dirección")

    def clean_total_area(self):
        return validate_positive_number(self.cleaned_data.get('total_area'), field_name="El área total")
        
    def save(self, commit=True):
        warehouse = super(WarehouseForm, self).save(commit=False)   
        if commit:
            warehouse.save()
            return warehouse
        return warehouse
        


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = [
            'warehouse', 'client', 'user', 'notes', 'quantity',
             'code', 'expiration_date'
        ]
        labels = {
            'warehouse': 'Almacén',
            'client': 'Cliente',
            'user': 'Usuario',
            'notes': 'Observaciones',
            'quantity': 'Cantidad',
            'code': 'Código',
            'expiration_date': 'Vencimiento'
        }
        widgets = {
            'user': forms.HiddenInput(),
            'type': forms.TextInput(attrs={'class': 'd-none'}),
        }

    def __init__(self, *args, **kwargs):
        base_transaction = kwargs.pop('base_transaction', None)
        super().__init__(*args, **kwargs)
        if base_transaction:
            for field in self.fields:
                self.fields[field].initial = getattr(base_transaction, field)

    def save(self, commit=True):
        transaction = Transaction()
        transaction.type = 'A'
        for field in self.cleaned_data:
            setattr(transaction, field, self.cleaned_data[field])
        if commit:
            transaction.save()
        return transaction
