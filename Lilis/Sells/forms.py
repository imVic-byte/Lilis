from .models import Client, Location, Warehouse, WareClient,Transaction, SaleOrder, SaleOrderDetail
from django import forms
from Main.validators import *

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['bussiness_name', 'fantasy_name', 'rut', 'email', 'phone', 'credit_limit', 'debt' ,'max_debt']
        labels = {
            'bussiness_name': 'Razon social de la empresa',
            'fantasy_name': 'Nombre fantasia de la empresa',
            'rut': 'Rut de la empresa',
            'email': 'Correo electronico',
            'phone': 'Telefono',
            'credit_limit': 'Limite de credito',
            'debt': 'Deuda',
            'max_debt': 'Maximo de deuda'
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
        
class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'city', 'country']
        labels = {
            'name': 'Nombre de la localidad',
            'city': 'Ciudad',
            'country': 'Pais'
        }
        
    def clean_name(self):
        return validate_text_length(self.cleaned_data.get('name'), field_name="El nombre")

    def clean_city(self):
        return validate_text_length(self.cleaned_data.get('city'), field_name="La ciudad")

    def clean_country(self):
        return validate_text_length(self.cleaned_data.get('country'), field_name="El país")
        
    def save(self, commit=True):
        location = super(LocationForm, self).save(commit=False)
        if commit:
            location.save()
            return location
        return location
        
class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'address', 'total_area', 'location']
        labels = {
            'name': 'Nombre del almacén',
            'address': 'Direccion',
            'total_area': 'Area total',
            'location': 'Localidad'
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
        fields = ['warehouse', 'type', 'batch']
        labels = {
            'warehouse': 'Bodega',
            'type': 'Tipo',
            'batch': 'Lote'
        }
        
    def save(self, commit=True):
        transaction = super(TransactionForm, self).save(commit=False)
        if commit:
            transaction.save()
            return transaction
        return transaction
        
class SaleOrderForm(forms.ModelForm):
    class Meta:
        model = SaleOrder
        fields = ['client', 'confirmation_date', 'status', 'exchange', 'payment_terms', 'observation']
        labels = {
            'client': 'Cliente',
            'confirmation_date': 'Fecha de confirmacion',
            'status': 'Estado',
            'exchange': 'Tipo de cambio',
            'payment_terms': 'Plazo de pago',
        }

    def clean_confirmation_date(self):
        conf_date = self.cleaned_data.get('confirmation_date')
        if conf_date:
            return validate_past_or_today_date(conf_date, field_name="La fecha de confirmación")
        return conf_date

    def save(self, commit=True):
        sale_order = super(SaleOrderForm, self).save(commit=False)
        if commit:
            sale_order.save()
            return sale_order
        return sale_order
        
class SaleOrderDetailForm(forms.ModelForm):
    class Meta:
        model = SaleOrderDetail
        fields = ['product', 'quantity']
        labels = {
            'product': 'Producto',
            'quantity': 'Cantidad'
        }
        
    def save(self, commit=True):
        sale_order_detail = super(SaleOrderDetailForm, self).save(commit=False)
        if commit:
            sale_order_detail.save()
            return sale_order_detail
        return sale_order_detail
