from .forms import RegistroForm, UserForm, ProfileForm
from django.contrib.auth.models import User
from .models import Profile
from Main.CRUD import CRUD

class UserService(CRUD ):
    def __init__(self):
        self.model = User
        self.form_class = RegistroForm

    def save_user(self, data):
        user_form = UserForm(data)
        profile_form = ProfileForm(data)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return True, user
        return False, (user_form, profile_form)

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


