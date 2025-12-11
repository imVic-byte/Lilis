from django import forms
from django.contrib.auth.models import User, Group
from .models import Profile, Role
from Main.validators import *
import random

class RegistrarUsuarioForm(forms.Form):
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
    run = forms.CharField(
        label="RUT",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 12345678-9'
        })
    )
    phone = forms.CharField(
        label="Teléfono",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 987654321'
        })
    )
    role = forms.ModelChoiceField(
        label="Rol",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Vendedor'
        }),
        queryset=Group.objects.all()
    )

    def clean_run(self):
        run = self.cleaned_data.get("run")
        if Profile.objects.filter(run=run).exists():
            raise forms.ValidationError("El RUT ya está en uso.")
        if validate_rut_format(run):
            return run
        raise forms.ValidationError("El RUT no es válido.")

    def clean_phone(self):
        return validate_phone_format(self.cleaned_data.get("phone"))

    def clean_email(self):
        email = self.cleaned_data.get("email")
        validate_email(email)
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("El correo electrónico ya está en uso.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("El nombre de usuario ya está en uso.")
        return username
    
    def save(self):
        contraseña = str(random.randint(100000, 999999))
        user_data = {
            "username": self.cleaned_data.get("username"),
            "first_name": self.cleaned_data.get("first_name"),
            "last_name": self.cleaned_data.get("last_name"),
            "email": self.cleaned_data.get("email"),
            "password": contraseña
        }
        user = User.objects.create_user(**user_data)
        user.groups.add(self.cleaned_data.get("role"))
        user.save()
        profile_data = {
            "user": user,
            "run": self.cleaned_data.get("run"),
            "phone": self.cleaned_data.get("phone"),
            "role": None,
            "is_new": True,
        }
        profile = Profile.objects.create(**profile_data)
        profile.save()
        return user, contraseña

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

    def clean_run(self):
        run = self.cleaned_data.get("run")
        if (self.user_instance and self.user_instance.profile.run != run) or not self.user_instance:
            if Profile.objects.filter(run=run).exists():
                raise forms.ValidationError("El RUT ya está en uso.")
        return run    

    def clean_phone(self):
        return validate_phone_format(self.cleaned_data.get("phone"))
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        validate_email(email)
        if (self.user_instance and self.user_instance.email != email) or not self.user_instance:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("El correo electrónico ya está en uso.")
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get("username")
        if (self.user_instance and self.user_instance.username != username) or not self.user_instance:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("El nombre de usuario ya está en uso.")
        return username

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


class ProfileForm(forms.Form):
    photo = forms.ImageField(required=True)

class UpdateFieldForm(forms.Form):
    field_name = forms.CharField(widget=forms.HiddenInput())
    new_data = forms.CharField(
        label="",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        field = cleaned_data.get("field_name")
        value = cleaned_data.get("new_data")

        if not field:
            raise forms.ValidationError("No se especificó el campo a modificar.")
        if value is None or value == "":
            raise forms.ValidationError("El nuevo valor no puede estar vacío.")

        try:
            if field == 'email':
                cleaned_data["new_data"] = validate_email(value)
                if User.objects.filter(email=value).exists():
                    raise forms.ValidationError("El correo electrónico ya está en uso.")
            elif field == 'run':
                cleaned_data["new_data"] = validate_rut_format(value)
                if Profile.objects.filter(run=value).exists():
                    raise forms.ValidationError("El RUT ya está en uso.")
            elif field == 'phone':
                cleaned_data["new_data"] = validate_phone_format(value)
            elif field == 'first_name':
                cleaned_data["new_data"] = validate_text_length(value, field_name="El nombre")
            elif field == 'last_name':
                cleaned_data["new_data"] = validate_text_length(value, field_name="El apellido")
            elif field == 'username':
                cleaned_data["new_data"] = validate_text_length(value, field_name="El nombre de usuario")
                if User.objects.filter(username=value).exists():
                    raise forms.ValidationError("El nombre de usuario ya está en uso.")

            else:
                raise forms.ValidationError(f"Este cambio no es válido.")
        except forms.ValidationError as e:
            self.add_error('new_data', e)

        return cleaned_data

    def clean_email(self, email):
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("El correo electrónico ya está en uso.")
        if validate_email(email):
            return email
        raise forms.ValidationError("El correo electrónico no es válido.")

    def clean_run(self, rut):
        if validate_rut_format(rut):
            return rut
        raise forms.ValidationError("El formato del RUT es incorrecto.")

    def clean_phone(self, phone):
        return validate_phone_format(phone)

    def clean_first_name(self, first_name):
        if not first_name.strip():
            raise forms.ValidationError("El nombre no puede estar vacío.")
        return first_name

    def clean_last_name(self, last_name):
        if not last_name.strip():
            raise forms.ValidationError("El apellido no puede estar vacío.")
        return last_name

    def clean_username(self, username):
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("El nombre de usuario ya está en uso por otro usuario.")
        return username

class RoleForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['groups']
        labels = {
            'groups': '',
        }
        widgets = {
            'groups': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Seleccione Rol'
            }),
        }
    
    def clean_role(self):
        role = self.cleaned_data.get("groups")
        if not role:
            raise forms.ValidationError("Debe seleccionar un rol válido.")
        return role

