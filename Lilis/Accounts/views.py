from django.contrib.auth import login
from django.shortcuts import render, redirect
from .services import UserService
from django.contrib.auth.decorators import login_required, permission_required
from Main.decorator import permission_or_redirect

user_service = UserService()

def registro(request):
    if request.method == 'POST':
        form = user_service.form_class(request.POST)
        if form.is_valid():
            success, usuario = user_service.save_user(request.POST)
            if success:
                login(request, usuario)
                return redirect('dashboard')
        else:
            return render(request, 'registration/registro.html', {'form': form})
    else:
        form = user_service.form_class()
    return render(request, 'registration/registro.html', {'form': form})

def password_reset(request):
    return render(request, 'registration/password_reset.html')

@login_required
@permission_or_redirect('Accounts.view_user','dashboard', 'No teni permiso')
def user_list(request):
    users = user_service.list()
    return render(request, "main/user_list.html", {"users": users})


@login_required
@permission_or_redirect('Accounts.change_user','dashboard', 'No teni permiso')
def user_update(request, id):
    user = user_service.get(id)
    if request.method == "POST":
        success, forms = user_service.update(id, request.POST)
        if success:
            return redirect("user_list")
        else:
            user_form, profile_form = forms
    else:
        user_form = user_service.form_class(instance=user)
        profile_form = user_service.model.profile(instance=user.profile)

    return render(
        request,
        "main/user_update.html",
        {"user_form": user_form, "profile_form": profile_form, "user": user},
    )


@login_required
@permission_or_redirect('Accounts.delete_user','dashboard', 'No teni permiso')
def user_delete(request, id):
    if request.method == "GET":
        success = user_service.delete(id)
        if success:
            return redirect('user_list')
    return redirect("user_list")