from django import forms
from django.contrib.auth.models import User
from .models import Profile

class RegistroForm(forms.ModelForm):
    username = forms.CharField(
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: juanperez'
        })
    )

    first_name = forms.CharField(
        label="Nombre",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Juan'
        })
    )
    last_name = forms.CharField(
        label="Apellido",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Pérez'
        })
    )
    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ejemplo@correo.cl'
        })
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa una contraseña'
        })
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repite la contraseña'
        })
    )

    class Meta:
        model = Profile
        fields = ['run', 'phone', 'role']
        labels = {
            'run': 'RUT',
            'phone': 'Teléfono',
            'role': 'Rol',
        }
        widgets = {
            'run': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 12345678-9'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 987654321'
            }),
            'role': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Vendedor'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Las contraseñas no coinciden.")
        return cleaned_data

    def clean_rut(self):
        rut = self.cleaned_data.get("run")
        if len(rut) != 10:
            raise forms.ValidationError("El RUT debe tener 10 caracteres.")
        return rut

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if len(phone) !=9:
            raise forms.ValidationError("El teléfono debe tener 9 caracteres.")
        return phone
    
    def save(self, commit=True):
    # Crear el usuario
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password1"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
        )

        selected_role = self.cleaned_data.get("role")

        # Crear el perfil asociado al usuario
        profile = Profile(
            user=user,
            run=self.cleaned_data.get("run"),
            phone=self.cleaned_data.get("phone"),
            role=self.cleaned_data.get("role"),
        )

        if commit:
            user.save()
            profile.save()
            if selected_role:
                user.groups.add(selected_role.group)

        return user

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        labels = {
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["run", "phone", "role"]
        labels = {
            "run": "RUT",
            "phone": "Teléfono",
            "role": "Rol",
        }