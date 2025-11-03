from django import forms
from django.contrib.auth.models import User
from .models import Profile, Role
from Main.validators import validate_rut_format, validate_phone_format, validate_password

class RegistroForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user_instance = kwargs.pop("user_instance", None)
        super().__init__(*args, **kwargs)

        if self.user_instance:
            self.fields["username"].initial = self.user_instance.username
            self.fields["first_name"].initial = self.user_instance.first_name
            self.fields["last_name"].initial = self.user_instance.last_name
            self.fields["email"].initial = self.user_instance.email
            self.fields["password1"].required = False
            self.fields["password2"].required = False

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

    def clean_password(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        # Caso update: ninguno de los campos ingresado → no se cambia contraseña
        if self.user_instance and not password1 and not password2:
            return None

        # Si solo uno de los dos campos está lleno → error
        if bool(password1) != bool(password2):
            raise forms.ValidationError("Ambos campos de contraseña deben completarse para cambiarla.")

        # Si ambos campos están llenos pero no coinciden → error
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        # Si hay contraseña válida, aplicamos tu validador
        if password1:
            return validate_password(password1)

        # Por defecto, devolver None
        return None

    def clean_rut(self):
        rut = self.cleaned_data.get("run")
        if validate_rut_format(rut):
            return rut
        else:
            raise forms.ValidationError("El formato del RUT es incorrecto.")


    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        return validate_phone_format(phone)
    
    
    def save(self, commit=True):
        if self.user_instance:
            user = self.user_instance
            user.username = self.cleaned_data["username"]
            user.first_name = self.cleaned_data["first_name"]
            user.last_name = self.cleaned_data["last_name"]
            user.email = self.cleaned_data["email"]
            
            password = self.cleaned_data.get("password1")
            if password:
                user.set_password(password)

            profile = user.profile
            profile.run = self.cleaned_data.get("run")
            profile.phone = self.cleaned_data.get("phone")
            profile.role = self.cleaned_data.get("role")

            if commit:
                user.save()
                profile.save()

            return user

        else:
            user = User.objects.create_user(
                username=self.cleaned_data["username"],
                email=self.cleaned_data["email"],
                password=self.cleaned_data["password1"],
                first_name=self.cleaned_data["first_name"],
                last_name=self.cleaned_data["last_name"],
            )

            profile = Profile(
                user=user,
                run=self.cleaned_data.get("run"),
                phone=self.cleaned_data.get("phone"),
                role=self.cleaned_data.get("role"),
            )

            if commit:
                user.save()
                profile.save()
                selected_role = self.cleaned_data.get("role")
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

class UpdateForm(forms.Form):
    run = forms.CharField(
        max_length=12,
        label="RUT",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12345678-9'})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        label="Teléfono",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 987654321'})
    )

    username = forms.CharField(
        max_length=150,
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: juanperez'})
    )

    first_name = forms.CharField(
        max_length=30,
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan'})
    )

    last_name = forms.CharField(
        max_length=150,
        label="Apellido",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Pérez'})
    )

    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@correo.cl'})
    )
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exclude(username=self.cleaned_data.get("username")).exists():
            raise forms.ValidationError("El correo electrónico ya está en uso por otro usuario.")
        return email
    
    def clean_run(self):
        rut = self.cleaned_data.get("run")
        if validate_rut_format(rut):
            return rut
        else:
            raise forms.ValidationError("El formato del RUT es incorrecto.")
        
    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        return validate_phone_format(phone)
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if not first_name:
            raise forms.ValidationError("El nombre no puede estar vacío.")
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")
        if not last_name:
            raise forms.ValidationError("El apellido no puede estar vacío.")
        return last_name
    
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exclude(email=self.cleaned_data.get("email")).exists():
            raise forms.ValidationError("El nombre de usuario ya está en uso por otro usuario.")
        return username
    