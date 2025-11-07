from django import forms
from Products.models import Product, Category, Supplier, RawMaterial, PriceHistories, Batch
from Main.validators import *

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'description', 'category', 'is_perishable', 'measurement_unit', 'quantity', 'created_at', 'expiration_date',]
        labels = {
            'name': 'Nombre',
            'sku': 'Código SKU',
            'description': 'Descripción',
            'category': 'Categoría',
            'is_perishable': 'Es Perecible',
            'measurement_unit': 'Unidad de Medida',
            'quantity' : 'Cantidad',
            'created_at' : 'Fecha de creación',
            'expiration_date' : 'Fecha de vencimiento',
        }
        widgets = {
            'expiration_date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'required': False}
            ),
            'created_at': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'required': True}
            ),
        }
        
    def clean_name(self):
        return validate_text_length(self.cleaned_data.get('name'), field_name="El nombre")

    def clean_sku(self):
        return validate_alphanumeric(self.cleaned_data.get('sku'), field_name="El SKU", min_length=3)
    
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
        product = super().save(commit=False)
        if commit:
            product.save()
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

class ProductBatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['product', 'batch_code', 'min_quantity', 'current_quantity', 'max_quantity']
        labels = {
            'product': 'Producto',
            'batch_code': 'Codigo de lote',
            'min_quantity': 'Cantidad Minima (Generar Aviso)',
            'current_quantity': 'Cantidad actual',
            'max_quantity' : 'Cantidad Maxima',
        }

    def clean_batch_code(self):
        return validate_alphanumeric(self.cleaned_data.get('batch_code'), field_name="El código de lote")
    
    def clean_min_quantity(self):
        return validate_positive_number(self.cleaned_data.get('min_quantity'), field_name="La cantidad mínima")

    def clean_current_quantity(self):
        return validate_is_number(self.cleaned_data.get('current_quantity'), field_name="La cantidad actual", allow_zero=True)

    def clean_max_quantity(self):
        return validate_positive_number(self.cleaned_data.get('max_quantity'), field_name="La cantidad máxima")

    def save(self, commit=True):
        batch = super().save(commit=False)
        if commit:
            batch.save()
        return batch
    
class RawBatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['raw_material', 'batch_code', 'min_quantity', 'current_quantity', 'max_quantity']
        labels = {
            'raw_material': 'Materia Prima',
            'batch_code': 'Codigo de lote',
            'min_quantity': 'Cantidad minima (Generar Aviso)',
            'current_quantity': 'Cantidad actual',
            'max_quantity' : 'Cantidad Maxima'
        }

    def clean_batch_code(self):
        return validate_alphanumeric(self.cleaned_data.get('batch_code'), field_name="El código de lote")

    def clean_min_quantity(self):
        return validate_positive_number(self.cleaned_data.get('min_quantity'), field_name="La cantidad mínima")

    def clean_current_quantity(self):
        return validate_is_number(self.cleaned_data.get('current_quantity'), field_name="La cantidad actual", allow_zero=True)

    def clean_max_quantity(self):
        return validate_positive_number(self.cleaned_data.get('max_quantity'), field_name="La cantidad máxima")

    
    def save(self, commit=True):
        batch = super().save(commit=False)
        if commit:
            batch.save()
        return batch
    
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
        model = RawMaterial
        fields = ['name', 'description', 'is_perishable', 'supplier' , 'category' , 'measurement_unit', 'quantity', 'created_at', 'expiration_date']
        labels = {
            'name': 'Nombre',
            'description': 'Descripción',
            'is_perishable' : 'Es perecible',
            'supplier': 'Proveedor',
            'category': 'Categoria',
            'measurement_unit' : 'Unidad de medida',
            'quantity' : 'Cantidad',
            'created_at' : 'Fecha de creacion',
            'expiration_date' : 'Fecha de vencimiento'
        }
        widgets = {
            'expiration_date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'required': True}
            ),
            'created_at': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'required': True}
            ),
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
        raw_material = super().save(commit=False)
        if commit:
            raw_material.save()
        return raw_material

class PriceHistoriesForm(forms.ModelForm):
    class Meta:
        model = PriceHistories
        fields = ['product','unit_price', 'date', 'iva']
        labels = {
            'unit_price': 'Precio',
            'date': 'Fecha',
            'iva' : 'IVA'
        }

    def clean_unit_price(self):
        return validate_positive_number(self.cleaned_data.get('unit_price'), field_name="El precio unitario")

    def clean_date(self):
        return validate_past_or_today_date(self.cleaned_data.get('date'), field_name="La fecha")
    
    def clean_iva(self):
        return validate_positive_number(self.cleaned_data.get('iva'), field_name="El IVA")
    
    def save(self, commit=True):
        price_history = super().save(commit=False)
        if commit:
            price_history.save()
        return price_history

