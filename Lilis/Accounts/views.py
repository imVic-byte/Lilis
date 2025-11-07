from django.contrib.auth import login
from django.shortcuts import render, redirect
from .services import UserService
from django.contrib.auth.decorators import login_required
from Main.decorator import permission_or_redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

user_service = UserService()

@login_required
@permission_or_redirect('Accounts.view_user','dashboard', 'No teni permiso')
def user_list(request):
    users = user_service.list()
    return render(request, "user_list.html", {"users": users})

def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if user_service.send_email(email):
            return redirect('token_verify')
        else:
            return render(request, 'password_reset.html', {'error': 'No se encontró una cuenta con ese correo electrónico.'})
    return render(request, 'password_reset.html')

def password_change(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        user = request.user
        if not user.check_password(current_password):
            return render(request, 'password_change.html', {'error': 'La contraseña actual es incorrecta.'})
        if new_password != confirm_password:
            return render(request, 'password_change.html', {'error': 'Las nuevas contraseñas no coinciden.'})
        if not user_service.validar_password(new_password):
            return render(request, 'password_change.html', {'error': 'La nueva contraseña no cumple con los requisitos de seguridad.'})            
        user.set_password(new_password)
        user.save()
        return redirect('dashboard')
    return render(request, 'password_change.html')


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
@permission_or_redirect('Accounts.delete_user','dashboard', 'No teni permiso')
def user_delete(request, id):
    if request.method == "GET":
        success = user_service.delete_user(id)
        if success:
            return redirect('user_list')
    return redirect("user_list")

@login_required
@permission_or_redirect('Accounts.view_user','dashboard', 'No teni permiso')
def user_view(request, id):
    user = user_service.model.objects.select_related('profile').get(id=id)
    return render(request, "user_view.html", {"user": user})

@login_required
@permission_or_redirect('Accounts.view_user','dashboard', 'No teni permiso')
def user_list(request):
    
    q = (request.GET.get("q") or "").strip()

    # ===================================
    #   ¡CAMBIO! Lógica para 'por página' (1-10)
    # ===================================
    default_per_page = 10  # Mantenemos 10 como el default
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except ValueError:
        per_page = default_per_page
    
    # ¡CAMBIO! Nueva validación para el rango 1-10
    if per_page > 10 or per_page <= 0:
        per_page = default_per_page
    # ===================================

    # 2. Queryset (sin cambios)
    qs = user_service.list().select_related("profile", "profile__role").order_by("username")

    # 3. Filtro (sin cambios)
    if q:
        qs = qs.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(username__icontains=q) |
            Q(profile__run__icontains=q) | 
            Q(profile__role__group__name__icontains=q)
        )

    # 4. Paginador (sin cambios, usa la variable per_page)
    paginator = Paginator(qs, per_page) 
    page_number = request.GET.get("page")

    # 5. Obtener página (sin cambios)
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # 6. Querystring (sin cambios)
    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()

    # 7. Contexto (¡importante!)
    context = {
        "page_obj": page_obj,  
        "q": q,
        "querystring": querystring,
        "total": qs.count(),
        "per_page": per_page, # ¡Pasamos el 'per_page' para el select!
    }
    return render(request, "user_list.html", context)

def token_verify(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        success, user = user_service.verify_token(token)
        if success:
            request.session['password_reset_user_id'] = user.id
            return redirect('password_recover')
        else:
            return render(request, 'token_verify.html', {'error': 'Token inválido o ya usado.'})
    return render(request, 'token_verify.html')

def password_recover(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        user_id = request.session.get('password_reset_user_id')
        if new_password != confirm_password:
            return render(request, 'password_recover.html', {'error': 'Las contraseñas no coinciden.'})
        if not user_service.validar_password(new_password):
            return render(request, 'password_recover.html', {'error': 'La nueva contraseña no cumple con los requisitos de seguridad.'})    
        if not user_id:
            return render(request, 'password_recover.html', {'error': 'Sesión expirada. Por favor, inicia el proceso nuevamente.'})    
        if user_id:
            success = user_service.password_change(user_id, new_password)
            if success:
                request.session.pop('password_reset_user_id', None)
                return redirect('login')
            else:
                return render(request, 'password_recover.html', {'error': 'Ha ocurrido un error. Inténtalo de nuevo.'})
        else:
            return render(request, 'password_recover.html', {'error': 'Sesión expirada. Por favor, inicia el proceso nuevamente.'})
    return render(request, 'password_recover.html')

def role_changer(request):
    user_id = request.GET.get("user_id")
    field_name = request.GET.get("field_name")
    previous_data = request.GET.get("previous_data")
    if request.method == "POST":
        role = user_service.roles.objects.get(id=request.POST.get("role"))
        success = user_service.edit_field(user_id, field_name, role)
        if success:
            return redirect('user_view', id=user_id)
        else:
            render(request, "role_changer.html", {'form':form, "error": "No se pudo cambiar el rol."})
    else:
        form = user_service.role_form_class(initial={'role': previous_data})
    return render(request, "role_changer.html", {"form": form, "field_name": field_name, "previous_data": previous_data})

@login_required
@permission_or_redirect('Accounts.change_user','dashboard', 'No teni permiso')
def edit_field(request):
    user_id = request.GET.get("user_id")
    field_name = request.GET.get("field_name")
    previous_data = request.GET.get("previous_data")
    if request.method == "POST":
        form = user_service.update_field_form_class(request.POST)
        if form.is_valid():
            success = user_service.edit_field(user_id, form.cleaned_data["field_name"], form.cleaned_data["new_data"])
            if success:
                return redirect('user_view', id=user_id)
    else:
        form = user_service.update_field_form_class(
            initial={'field_name': field_name, 'new_data': previous_data}
        )
    return render(
        request, 
        "edit_field.html", 
        {"field_name": field_name, "previous_data": previous_data, 'form': form}
    )

def user_picture(request, id):
    if request.method == "POST":
        photo = request.FILES.get("photo")
        if photo:
            print(request.FILES)
            user_service.change_user_picture(id, photo)
            return redirect('user_view', id=id)
        else:
            return render(request, "user_picture.html", {"error": "No se pudo cargar la foto."})
    else:
        photo = user_service.obtain_user_picture(id)
    return render(request, "user_picture.html", {"photo": photo, "id": id})