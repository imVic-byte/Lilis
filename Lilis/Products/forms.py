from django import forms
from Products.models import Producto, Category, Supplier, RawMaterialClass
from Main.validators import *


class ProductForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['name', 'sku', 'description', 'category', 'is_perishable', 'is_active', 'measurement_unit']
        labels = {
            'name': 'Nombre',
            'sku': 'SKU',
            'description': 'Descripción',
            'category': 'Categoría',
            'is_perishable': 'Es perecible',
            'is_active': 'Está activo',
            'measurement_unit': 'Unidad de medida',
        }
    def clean_name(self):
        return validate_text_length(self.cleaned_data.get('name'), field_name="El nombre")

    def clean_sku(self):
        return validate_text_length(self.cleaned_data.get('sku'), field_name="El SKU")

    def clean_description(self):
        return validate_text_length(self.cleaned_data.get('description'), min_length=5, field_name="La descripción", allow_empty=True)

    def clean_category(self):
        return self.cleaned_data.get('category')

    def clean_is_perishable(self):
        return self.cleaned_data.get('is_perishable')

    def clean_is_active(self):
        return self.cleaned_data.get('is_active')

    def clean_measurement_unit(self):
        return self.cleaned_data.get('measurement_unit')
    
    def save(self, commit=True):
        product = super().save(commit=False)
        if commit:
            product.save()
            return product
        return product

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        labels = {
            'name': 'Nombre',
            'description': 'Descripción'
        }
    def clean_name(self):
        return validate_text_length(self.cleaned_data.get('name'), field_name="El nombre")
    
    def clean_description(self):
        return validate_text_length(self.cleaned_data.get('description'), field_name="La descripcion")

    def save(self, commit=True):
        category = super().save(commit=False)
        if commit:
            category.save()
        return category


class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['bussiness_name', 'fantasy_name', 'rut', 'email', 'phone', 'trade_terms']
        labels = {
                'bussiness_name': 'Nombre de la empresa',
                'fantasy_name': 'Nombre de fantasia',
                'rut': 'RUT',
                'email': 'Correo electronico',
                'phone': 'Telefono',
                'trade_terms': 'Términos de comercio' 
                }
        
    def clean_bussiness_name(self):
        return validate_text_length(self.cleaned_data.get('bussiness_name'), field_name="El nombre de empresa")

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

    def save(self, commit=True):
        supplier = super().save(commit=False)
        if commit:
            supplier.save()
        return supplier
    
class RawMaterialForm(forms.ModelForm):
    class Meta:
        model = RawMaterialClass
        fields = [ 'name', 'sku', 'description', 'is_perishable', 'measurement_unit', 'category']
        labels = {
            'name': 'Nombre',
            'sku': 'SKU',
            'description': 'Descripción',
            'is_perishable' : '',
            'measurement_unit' : 'Unidad de medida',
            'category': 'Categoría',
        }
        widgets = {
            'measurement_unit': forms.Select(choices=[('U','Unidades'), ('KG','Kilogramos'), ('L','Litros')]),
        }

        def clean_name(self):
            return validate_text_length(self.cleaned_data.get('name'), field_name="El nombre")

        def clean_description(self):
            return validate_text_length(self.cleaned_data.get('description'), min_length=5, field_name="La descripción", allow_empty=True)

        def clean_quantity(self):
            return validate_is_number(self.cleaned_data.get('quantity'), field_name="La cantidad")

        def clean_expiration_date(self):
            is_perishable = self.cleaned_data.get('is_perishable')
            exp_date = self.cleaned_data.get('expiration_date')
            if is_perishable and not exp_date:
                raise forms.ValidationError('Productos perecibles deben tener fecha de vencimiento.')
            if exp_date:
                return validate_future_date(exp_date, field_name="La fecha de vencimiento", allow_today=True)
            return exp_date

        def clean_created_at(self):
            created_at = self.cleaned_data.get('created_at')
            if created_at:
                return validate_past_or_today_date(created_at, field_name="La fecha de creación")
            return created_at

        def save(self, commit=True):
            raw_material_class = super().save(commit=False)
            if commit:
                raw_material_class.save()
            return raw_material_class

