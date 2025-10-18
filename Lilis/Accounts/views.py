from django.contrib.auth import login
from django.shortcuts import render, redirect
from .forms import RegistroForm, UserForm, ProfileForm
from django.contrib.auth.models import User
from .models import Profile

class UserService:
    def get(self, id):
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            return None

    def list(self):
        return User.objects.all()

    def delete(self, id):
        try:
            instance = User.objects.get(id=id)
            instance.delete()
            return True
        except User.DoesNotExist:
            return False

    def save(self, data):
        user_form = UserForm(data)
        profile_form = ProfileForm(data)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            return True, user
        return False, (user_form, profile_form)

    def update(self, id, data):
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



def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            return redirect('dashboard')
        else:
            return render(request, 'registration/registro.html', {'form': form})
    else:
        form = RegistroForm()
    return render(request, 'registration/registro.html', {'form': form})
