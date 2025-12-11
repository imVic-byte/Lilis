from django import forms
from Products.models import Producto, Category, Supplier, RawMaterialClass
from Main.validators import *


class ProductForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'sku', 'ean_upc', 'name', 'model', 'description', 'category', 'brand', 'model_code',
            'uom_purchase', 'uom_sale', 'conversion_factor', 
            'cost', 'standard_cost', 'price', 'iva',
            'min_stock', 'max_stock', 'reordering_level',
            'serie_control', 'batch_control', 
            'alerta_bajo_stock', 'alerta_por_vencer',
            'url_image', 'technical_sheet', 'measurement_unit', 'is_perishable'
        ]
        labels = {
            'sku': 'SKU (requerido)',
            'ean_upc': 'EAN/UPC',
            'name': 'Nombre (requerido)',
            'model': 'Modelo',
            'description': 'Descripción',
            'category': 'Categoría (requerido)',
            'brand': 'Marca',
            'model_code': 'Código de modelo',
            'uom_purchase': 'Unidad de medida compra (requerido)',
            'uom_sale': 'Unidad de medida venta (requerido)',
            'conversion_factor': 'Factor de conversión (requerido)',
            'cost': 'Costo promedio (lectura)',
            'standard_cost': 'Costo estándar',
            'price': 'Precio de venta',
            'iva': 'IVA (%) (requerido)',
            'min_stock': 'Stock mínimo (requerido)',
            'max_stock': 'Stock máximo',
            'reordering_level': 'Punto de reorden (opcional, si no, usar mínimo)',
            'serie_control': 'Control por serie (opcional, se requiere un tipo de control)',
            'batch_control': 'Control por lote (opcional, se requiere un tipo de control)',
            'alerta_bajo_stock': 'Alerta bajo stock (opcional)',
            'alerta_por_vencer': 'Alerta por vencer (opcional)',
            'url_image': 'URL de imagen (opcional)',
            'technical_sheet': 'Ficha técnica (opcional)',
            'measurement_unit': 'Unidad de medida (requerido)',
            'is_perishable': 'Es perecible (requerido)'
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'uom_purchase': forms.Select(choices=[('U','Unidades'), ('KG','Kilogramos'), ('L','Litros')]),
            'uom_sale': forms.Select(choices=[('U','Unidades'), ('KG','Kilogramos'), ('L','Litros')]),
            'measurement_unit': forms.Select(choices=[('U','Unidades'), ('KG','Kilogramos'), ('L','Litros')]),
            'is_perishable': forms.CheckboxInput(),
        }
    
    def clean_conversion_factor(self):
        factor = self.cleaned_data.get('conversion_factor')
        if factor and factor <= 0:
            raise forms.ValidationError('El factor de conversión debe ser mayor a 0')
        return factor
    
    def clean_cost(self):
        cost = self.cleaned_data.get('cost')
        if cost and cost <= 0:
            raise forms.ValidationError('El costo debe ser mayor a 0')
        return cost

    def clean_standard_cost(self):
        cost = self.cleaned_data.get('standard_cost')
        if cost and cost <= 0:
            raise forms.ValidationError('El costo estándar debe ser mayor a 0')
        return cost

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise forms.ValidationError('El precio debe ser mayor a 0')
        return price

    def clean_min_stock(self):
        stock = self.cleaned_data.get('min_stock')
        if stock and stock <= 0:
            raise forms.ValidationError('El stock mínimo debe ser mayor a 0')
        return stock

    def clean_max_stock(self):
        stock = self.cleaned_data.get('max_stock')
        if stock and stock <= 0:
            raise forms.ValidationError('El stock máximo debe ser mayor a 0')
        return stock

    def clean_reordering_level(self):
        level = self.cleaned_data.get('reordering_level')
        if level and level <= 0:
            raise forms.ValidationError('El nivel de reorden debe ser mayor a 0')
        return level

    def clean_batch_control(self):
        if self.cleaned_data.get('batch_control') and self.cleaned_data.get('serie_control'):
            raise forms.ValidationError('No puede haber control por lote y por serie al mismo tiempo')
        return self.cleaned_data.get('batch_control')

    def clean_controles(self):
        if self.cleaned_data.get('batch_control') or self.cleaned_data.get('serie_control'):
            return True
        raise forms.ValidationError('Debe haber al menos un control')

    def clean_name(self):
        return validate_text_length(self.cleaned_data.get('name'), field_name="El nombre")

    def clean_sku(self):
        return validate_text_length(self.cleaned_data.get('sku'), field_name="El SKU")

    def clean_description(self):
        return validate_text_length(self.cleaned_data.get('description'), min_length=5, field_name="La descripción", allow_empty=True)

    def clean_category(self):
        return self.cleaned_data.get('category')

    def clean_iva(self):
        iva = self.cleaned_data.get('iva')
        if iva and (iva < 0 or iva > 100):
            raise forms.ValidationError('El IVA debe estar entre 0 y 100')
        return iva

    def clean_is_active(self):
        return self.cleaned_data.get('is_active')

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
        widgets = {
            'trade_terms': forms.Textarea(attrs={'rows': 3}),
            'currency': forms.Select(choices=[('CLP', 'Peso Chileno'), ('USD', 'Dólar'), ('EUR', 'Euro')]),
        }
        
    def clean_bussiness_name(self):
        return validate_text_length(self.cleaned_data.get('bussiness_name'), field_name="El nombre de empresa")

    def clean_fantasy_name(self):
        fantasy_name = self.cleaned_data.get('fantasy_name')
        if fantasy_name:
            return validate_text_length(fantasy_name, field_name="El nombre de fantasía", allow_empty=True)
        return fantasy_name
    
    def clean_fantasy_name(self):
        fantasy_name = self.cleaned_data.get('fantasy_name')
        if not fantasy_name:
            raise forms.ValidationError('El nombre de fantasía es requerido')
        return fantasy_name

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

    def clean_discount_percentage(self):
        discount = self.cleaned_data.get('discount_percentage')
        if discount and (discount < 0 or discount > 100):
            raise forms.ValidationError('El descuento debe estar entre 0 y 100')
        return discount

    def clean_payment_terms_days(self):
        days = self.cleaned_data.get('payment_terms_days')
        if days and days < 0:
            raise forms.ValidationError('Los días de plazo de pago no pueden ser negativos')
        return days

    def clean_lead_time_days(self):
        days = self.cleaned_data.get('lead_time_days')
        if days and days < 0:
            raise forms.ValidationError('El tiempo de entrega no puede ser negativo')
        return days

    def save(self, commit=True):
        supplier = super().save(commit=False)
        if commit:
            supplier.save()
        return supplier
    
class RawMaterialForm(forms.ModelForm):
    class Meta:
        model = RawMaterialClass
        fields = [
            'sku', 'ean_upc', 'name', 'model', 'description', 'category', 'brand', 'model_code',
            'uom_purchase', 'uom_sale', 'conversion_factor', 
            'cost', 'standard_cost', 'price', 'iva',
            'min_stock', 'max_stock', 'reordering_level',
            'serie_control', 'batch_control', 
            'alerta_bajo_stock', 'alerta_por_vencer',
            'url_image', 'technical_sheet', 'measurement_unit', 'is_perishable', 'supplier'
        ]
        labels = {
            'sku': 'SKU (requerido)',
            'ean_upc': 'EAN/UPC',
            'name': 'Nombre (requerido)',
            'model': 'Modelo',
            'description': 'Descripción',
            'category': 'Categoría (requerido)',
            'brand': 'Marca',
            'model_code': 'Código de modelo',
            'uom_purchase': 'Unidad de medida compra (requerido)',
            'uom_sale': 'Unidad de medida venta (requerido)',
            'conversion_factor': 'Factor de conversión (requerido)',
            'cost': 'Costo promedio (lectura)',
            'standard_cost': 'Costo estándar',
            'price': 'Precio de venta',
            'iva': 'IVA (%) (requerido)',
            'min_stock': 'Stock mínimo (requerido)',
            'max_stock': 'Stock máximo',
            'reordering_level': 'Punto de reorden (opcional, si no, usar mínimo)',
            'serie_control': 'Control por serie (opcional, se requiere un tipo de control)',
            'batch_control': 'Control por lote (opcional, se requiere un tipo de control)',
            'alerta_bajo_stock': 'Alerta bajo stock (opcional)',
            'alerta_por_vencer': 'Alerta por vencer (opcional)',
            'url_image': 'URL de imagen (opcional)',
            'technical_sheet': 'Ficha técnica (opcional)',
            'measurement_unit': 'Unidad de medida (requerido)',
            'is_perishable': 'Es perecible (requerido)',
            'supplier': 'Proveedor (requerido)'
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'uom_purchase': forms.Select(choices=[('U','Unidades'), ('KG','Kilogramos'), ('L','Litros')]),
            'uom_sale': forms.Select(choices=[('U','Unidades'), ('KG','Kilogramos'), ('L','Litros')]),
            'measurement_unit': forms.Select(choices=[('U','Unidades'), ('KG','Kilogramos'), ('L','Litros')]),
            'is_perishable': forms.CheckboxInput(),
            'supplier': forms.Select()
        }

    def __init__(self, *args, supplier=None, **kwargs):
        super().__init__(*args, **kwargs)
        if supplier:
            self.fields['supplier'].initial = supplier
            self.fields['supplier'].widget.attrs['readonly'] = True

    def clean_conversion_factor(self):
        factor = self.cleaned_data.get('conversion_factor')
        if factor and factor <= 0:
            raise forms.ValidationError('El factor de conversión debe ser mayor a 0')
        return factor
    
    def clean_cost(self):
        cost = self.cleaned_data.get('cost')
        if cost and cost <= 0:
            raise forms.ValidationError('El costo debe ser mayor a 0')
        return cost

    def clean_standard_cost(self):
        cost = self.cleaned_data.get('standard_cost')
        if cost and cost <= 0:
            raise forms.ValidationError('El costo estándar debe ser mayor a 0')
        return cost

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise forms.ValidationError('El precio debe ser mayor a 0')
        return price

    def clean_min_stock(self):
        stock = self.cleaned_data.get('min_stock')
        if stock and stock <= 0:
            raise forms.ValidationError('El stock mínimo debe ser mayor a 0')
        return stock

    def clean_max_stock(self):
        stock = self.cleaned_data.get('max_stock')
        if stock and stock <= 0:
            raise forms.ValidationError('El stock máximo debe ser mayor a 0')
        return stock

    def clean_reordering_level(self):
        level = self.cleaned_data.get('reordering_level')
        if level and level <= 0:
            raise forms.ValidationError('El nivel de reorden debe ser mayor a 0')
        return level

    def clean_batch_control(self):
        if self.cleaned_data.get('batch_control') and self.cleaned_data.get('serie_control'):
            raise forms.ValidationError('No puede haber control por lote y por serie al mismo tiempo')
        return self.cleaned_data.get('batch_control')

    def clean_controles(self):
        if self.cleaned_data.get('batch_control') or self.cleaned_data.get('serie_control'):
            return True
        raise forms.ValidationError('Debe haber al menos un control')

    def clean_name(self):
        return validate_text_length(self.cleaned_data.get('name'), field_name="El nombre")

    def clean_sku(self):
        return validate_text_length(self.cleaned_data.get('sku'), field_name="El SKU")

    def clean_description(self):
        return validate_text_length(self.cleaned_data.get('description'), min_length=5, field_name="La descripción", allow_empty=True)

    def clean_category(self):
        return self.cleaned_data.get('category')

    def clean_iva(self):
        iva = self.cleaned_data.get('iva')
        if iva and (iva < 0 or iva > 100):
            raise forms.ValidationError('El IVA debe estar entre 0 y 100')
        return iva

    def clean_is_active(self):
        return self.cleaned_data.get('is_active')

    def save(self, commit=True):
        product = super().save(commit=False)
        if commit:
            product.save()
            return product
        return product
