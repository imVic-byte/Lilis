from .forms import RegistroForm, UserForm, ProfileForm
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

    def save_user(self, data):
        form = self.form_class(data)
        if form.is_valid():
            user = form.save()
            return True, user
        return False, form

    def update_user(self, id, data):
        try:
            usuario = self.model.objects.select_related('profile').get(id=id)
            form = self.form_class(data, instance=usuario.profile, user_instance=usuario)
            if form.is_valid():
                obj = form.save()
                return True, obj
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