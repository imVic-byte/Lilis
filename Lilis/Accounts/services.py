from .forms import RegistroForm, UserForm, ProfileForm, UpdateFieldForm, RoleForm
from django.contrib.auth.models import User
from .models import Profile, password_reset_token,Role
from Main.CRUD import CRUD
import re
from django.core.mail import send_mail
from django.conf import settings
import random

class UserService(CRUD ):
    def __init__(self):
        self.model = User
        self.tokens = password_reset_token
        self.profile_model = Profile
        self.form_class = RegistroForm
        self.user_form_class = UserForm
        self.profile_form_class = ProfileForm
        self.update_field_form_class = UpdateFieldForm
        self.role_form_class = RoleForm
        self.roles = Role

    def save_user(self, data):
        form = self.form_class(data)
        if form.is_valid():
            user = form.save()
            return True, user
        return False, form

    def update_user(self, id, data):
        try:
            usuario = self.model.objects.select_related('profile').get(id=id)
            profile = usuario.profile
            form = self.update_form_class(data, instance=profile, user_instance=usuario)
            if form.is_valid():
                usuario.username = form.cleaned_data["username"]
                usuario.email = form.cleaned_data["email"]
                usuario.first_name = form.cleaned_data["first_name"]
                usuario.last_name = form.cleaned_data["last_name"]
                password = form.cleaned_data["password1"]
                if password:
                    usuario.set_password(password)
                usuario.save()
                profile.run = form.cleaned_data["run"]
                profile.phone = form.cleaned_data["phone"]
                profile.role = form.cleaned_data["role"]
                profile.save()
                selected_role = form.cleaned_data.get("role")
                if selected_role:
                    usuario.groups.clear()
                    usuario.groups.add(selected_role.group)
                return True, usuario
            return False, form
        except self.model.DoesNotExist:
            return False, None

    def delete_user(self, id):
        try:
            user = self.model.objects.get(id=id)
            user.profile.delete()
            user.delete()
            return True
        except self.model.DoesNotExist:
            return False

    def get_profile(self, id):
        try:
            return self.profile_model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None
    
    def cargar_formulario(self, usuario):
        usuario = self.model.objects.select_related('profile').get(id=usuario.id)
        profile = usuario.profile
        form = self.update_form_class(
            initial={
                "username": usuario.username,
                "first_name": usuario.first_name,
                "last_name": usuario.last_name,
                "email": usuario.email,
                "run": profile.run,
                "phone": profile.phone,
                "role": profile.role,
            },
        )
        return form
    
    def edit_field(self, user_id, field_name, data):
        try:
            usuario = self.model.objects.select_related('profile').get(id=user_id)
            profile = usuario.profile
            if field_name == 'run' or field_name == 'phone' or field_name == 'role':
                setattr(profile, field_name, data)
                print(field_name,data)
                profile.save()
                return True
            else:
                setattr(usuario, field_name, data)
                print(field_name,data)
                usuario.save()
                return True
        except self.model.DoesNotExist: 
            return False, None
        
    def validar_password(self, password):
        if len(password) < 8:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"[0-9]", password):
            return False
        if not re.search(r"[^A-Za-z0-9]", password):
            return False
        return True
    
    def send_email(self, email):
        try:
            user = self.model.objects.get(email=email)
            if not user:
                return False
            token = ''.join(random.choices('1234567890', k=6))
            self.tokens.objects.create(user=user, token=token)
            asunto = 'Restablecimiento de contraseña'
            mensaje = f'Hola {user.username},\n\nPara restablecer tu contraseña, copia el siguiente codigo en la pagina de restablecimiento:\n\n{token}\n\nSi no solicitaste este cambio, puedes ignorar este correo.'
            send_mail(
                asunto,
                mensaje,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return True
        except self.model.DoesNotExist:
            return False
    
    def verify_token(self, token):
        try:
            token_entry = self.tokens.objects.get(token=token, is_used=False)
            return True, token_entry.user
        except self.tokens.DoesNotExist:
            return False, None
        
    def password_change(self, user_id, new_password):
        try:
            user = self.get(user_id)
            user.set_password(new_password)
            user.save()
            self.tokens.objects.filter(user=user, is_used=False).update(is_used=True)
            return True
        except:
            return False