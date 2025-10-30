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
            user_instance = User.objects.get(id=id)
            profile_instance = Profile.objects.get(user=user_instance)
            user_form = UserForm(data, instance=user_instance)
            profile_form = ProfileForm(data, instance=profile_instance)

            if user_form.is_valid() and profile_form.is_valid():
                user = user_form.save()
                profile = profile_form.save(commit=False)
                
                new_role = profile_form.cleaned_data.get('role')
                if new_role != profile_instance.role:
                    user.groups.clear()
                    if new_role:
                        user.groups.add(new_role.group)

                profile.save()
                return True, (user_form, profile_form)
            return False, (user_form, profile_form)
        except (User.DoesNotExist, Profile.DoesNotExist):
            return False, None

    def delete_user(self, id):
        try:
            user = self.model.objects.get(id=id)
            user.profile.delete()
            user.delete()
            return True
        except self.model.DoesNotExist:
            return False

