from django.contrib.auth import login
from django.shortcuts import render, redirect
from .services import UserService
from django.contrib.auth.decorators import login_required, permission_required
from Main.decorator import permission_or_redirect

user_service = UserService()

@login_required
@permission_or_redirect('Accounts.view_user','dashboard', 'No teni permiso')
def user_list(request):
    users = user_service.list()
    return render(request, "user_list.html", {"users": users})

def password_reset(request):
    return render(request, 'password_reset.html')

@login_required
@permission_or_redirect('Accounts.add_user','dashboard', 'No teni permiso')
def registro(request):
    if request.method == 'POST':
        form = user_service.form_class(request.POST)
        if form.is_valid():
            success, usuario = user_service.save_user(request.POST)
            if success:
                login(request, usuario)
                return redirect('dashboard')
        else:
            return render(request, 'registro.html', {'form': form})
    else:
        form = user_service.form_class()
    return render(request, 'registro.html', {'form': form})

@login_required
@permission_or_redirect('Accounts.change_user','dashboard', 'No teni permiso')
def user_update(request, id):
    user = user_service.model.objects.select_related('profile').get(id=id)
    if request.method == "POST":
        success, obj = user_service.update_user(id, request.POST)
        if success:
            return redirect("user_list")
        else:
            form = obj
    else:
        form = user_service.cargar_formulario(user)
    return render(request, "user_update.html", {"form": form})


@login_required
@permission_or_redirect('Accounts.delete_user','dashboard', 'No teni permiso')
def user_delete(request, id):
    if request.method == "GET":
        success = user_service.delete_user(id)
        if success:
            return redirect('user_list')
    return redirect("user_list")