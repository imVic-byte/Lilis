from .models import Client, Location, Warehouse, WareClient,Transaction, SaleOrder, SaleOrderDetail
from django import forms
import datetime

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
