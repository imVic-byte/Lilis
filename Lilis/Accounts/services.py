from .forms import RegistroForm, UserForm, ProfileForm, UpdateFieldForm
from django.contrib.auth.models import User
from .models import Profile
from Main.CRUD import CRUD

class UserService(CRUD ):
    def __init__(self):
        self.model = User
        self.profile_model = Profile
        self.form_class = RegistroForm
        self.user_form_class = UserForm
        self.profile_form_class = ProfileForm
        self.update_field_form_class = UpdateFieldForm
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