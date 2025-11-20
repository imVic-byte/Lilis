from .models import Client, Location, Warehouse, WareClient,Transaction
from django import forms
from Main.validators import *

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['bussiness_name', 'fantasy_name', 'rut', 'email', 'phone', 'credit_limit', 'debt' ,'max_debt' ,'is_suspended']
        labels = {
            'bussiness_name': 'Razon social de la empresa',
            'fantasy_name': 'Nombre fantasia de la empresa',
            'rut': 'Rut de la empresa',
            'email': 'Correo electronico',
            'phone': 'Telefono',
            'credit_limit': 'Limite de credito',
            'debt': 'Deuda',
            'max_debt': 'Maximo de deuda',
            'is_suspended': 'Esta suspendido'
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
             'batch_code', 'serie_code', 'expiration_date'
        ]
        labels = {
            'warehouse': 'Almacén',
            'client': 'Cliente',
            'user': 'Usuario',
            'notes': 'Observaciones',
            'quantity': 'Cantidad',
            'batch_code': 'Lote',
            'serie_code': 'Serie',
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
