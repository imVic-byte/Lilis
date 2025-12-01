from Accounts.models import Lilis
from django import forms
import Main.validators

class LilisForm(forms.ModelForm):
    class Meta:
        model = Lilis
        fields = ['bussiness_name', 'fantasy_name', 'rut', 'email', 'phone', 'address','web_site']
        labels = {
            'bussiness_name': 'Razón Social',
            'fantasy_name': 'Nombre Fantasía',
            'rut': 'RUT',
            'email': 'Correo Electrónico',
            'phone': 'Teléfono',
            'address': 'Dirección',
            'web_site': 'Página Web',
        }
    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if not Main.validators.validate_rut_format(rut):
            raise forms.ValidationError("RUT inválido.")
        return rut
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not Main.validators.validate_phone_format(phone):
            raise forms.ValidationError("Número de teléfono inválido.")
        return phone
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not Main.validators.validate_email(email):
            raise forms.ValidationError("Correo electrónico inválido.")
        return email
    
    def clean_bussiness_name(self):
        bussiness_name = self.cleaned_data.get('bussiness_name')
        if not bussiness_name:
            raise forms.ValidationError("El nombre del negocio es obligatorio.")
        return bussiness_name
    
    def clean_fantasy_name(self):
        fantasy_name = self.cleaned_data.get('fantasy_name')
        return fantasy_name
    
    def save(self, commit=True):
        lilis = super().save(commit=False)
        if commit:
            lilis.save()
        return lilis