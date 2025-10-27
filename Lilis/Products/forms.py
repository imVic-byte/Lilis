from django import forms
import datetime
from Products.models import Product, Category, Supplier, RawMaterial, PriceHistories, Batch
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
                attrs={'type': 'date', 'required': True}
            ),
            'created_at': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'required': True}
            ),
        }
        
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError('Se requiere un nombre.')
        if len(name) < 2:
            raise forms.ValidationError('El nombre debe tener mas de 2 letras.')
        return name

    def clean_sku(self):
        sku = self.cleaned_data.get('sku')
        if not sku:
            raise forms.ValidationError('Se requiere un SKU.')
        if len(sku) < 3:
            raise forms.ValidationError('El SKU debe tener mas de 3 caracteres.')
        return sku

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
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError('Se requiere un nombre.')
        if len(name) < 2:
            raise forms.ValidationError('El nombre debe tener mas de 2 letras.')
        return name
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description) < 5:
            raise forms.ValidationError('La descripcion debe tener mas de 5 letras.')
        return description

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
            'max_quantity' : 'Cantidad Maxima'
        }
    def clean_batch_code(self):
        batch_code = self.cleaned_data.get('batch_code')
        if not batch_code:
            raise forms.ValidationError('Se requiere un codigo de lote.')
        if len(batch_code) < 3:
            raise forms.ValidationError('El codigo de lote debe tener mas de 3 caracteres.')
        return batch_code

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
        batch_code = self.cleaned_data.get('batch_code')
        if not batch_code:
            raise forms.ValidationError('Se requiere un codigo de lote.')
        if len(batch_code) < 3:
            raise forms.ValidationError('El codigo de lote debe tener mas de 3 caracteres.')
        return batch_code

    
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
        bussiness_name = self.cleaned_data.get('bussiness_name')
        if not bussiness_name:
            raise forms.ValidationError('Se requiere un nombre de empresa.')
        if len(bussiness_name) < 2:
            raise forms.ValidationError('El nombre de la empresa debe tener mas de 2 letras.')
        return bussiness_name

    def clean_fantasy_name(self):
        fantasy_name = self.cleaned_data.get('fantasy_name')
        if not fantasy_name:
            raise forms.ValidationError('Se requiere un nombre de fantasia.')
        if len(fantasy_name) < 2:
            raise forms.ValidationError('El nombre de fantasia debe tener mas de 2 letras.')
        return fantasy_name
    
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if not rut:
            raise forms.ValidationError('Se requiere un RUT.')
        if len(rut) < 8:
            raise forms.ValidationError('El RUT debe tener mas de 8 caracteres.')
        return rut

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not forms.EmailField().clean(email):
            raise forms.ValidationError('Ingrese un correo electronico valido.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and len(phone) < 8:
            raise forms.ValidationError('El telefono debe tener mas de 8 caracteres.')
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
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError('Se requiere un nombre.')
        if len(name) < 2:
            raise forms.ValidationError('El nombre debe tener mas de 2 letras.')
        return name

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description and len(description) < 5:
            raise forms.ValidationError('La descripcion debe tener mas de 5 letras.')
        return description
    
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
        price = self.cleaned_data.get('unit_price')
        if price is None or price < 0:
            raise forms.ValidationError('El precio debe ser un numero positivo.')
        return price

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if not date:
            raise forms.ValidationError('Se requiere una fecha.')
        return date
    
    def clean_iva(self):
        iva = self.cleaned_data.get('iva')
        if iva is None or iva < 0:
            raise forms.ValidationError('El IVA debe ser un numero positivo.')
        return iva
    
    def save(self, commit=True):
        price_history = super().save(commit=False)
        if commit:
            price_history.save()
        return price_history

