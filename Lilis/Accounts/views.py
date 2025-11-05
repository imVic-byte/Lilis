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
@permission_or_redirect('Accounts.change_user','dashboard', 'No teni permiso')
def edit_field(request):
    user_id = request.GET.get("user_id")
    field_name = request.GET.get("field_name")
    previous_data = request.GET.get("previous_data")
    if request.method == "POST":
        print("POST data:", request.POST)
        form = user_service.update_field_form_class(request.POST)
        if form.is_valid():
            success = user_service.edit_field(user_id, form.cleaned_data["field_name"], form.cleaned_data["new_data"])
            if success:
                return redirect('user_list')
    else:
        form = user_service.update_field_form_class(
            initial={'field_name': field_name, 'new_data': previous_data}
        )
    return render(
        request, 
        "edit_field.html", 
        {"field_name": field_name, "previous_data": previous_data, 'form': form}
    )

@login_required
@permission_or_redirect('Accounts.view_user','dashboard', 'No teni permiso')
def user_list(request):
    
    q = (request.GET.get("q") or "").strip()

    
    allowed_per_page = [5, 25, 50, 100]
    default_per_page = 25  
    
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except ValueError:
        per_page = default_per_page
    
    # Validar que el valor esté en la lista permitida
    if per_page not in allowed_per_page:
        per_page = default_per_page
    # ===================================

    # 3. Lógica de Ordenamiento
    allowed_sort_fields = ['username', 'first_name', 'profile__run', 'profile__role__group__name']
    sort_by = request.GET.get('sort_by', 'username') 
    order = request.GET.get('order', 'asc')

    if sort_by not in allowed_sort_fields:
        sort_by = 'username'
    if order not in ['asc', 'desc']:
        order = 'asc'
        
    order_by_field = f'-{sort_by}' if order == 'desc' else sort_by

    # 4. Queryset
    qs = user_service.list().select_related("profile", "profile__role")

    # 5. Filtro de búsqueda
    if q:
        qs = qs.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(username__icontains=q) |
            Q(profile__run__icontains=q) | 
            Q(profile__role__group__name__icontains=q)
        )
        
    # 6. Ordenamiento
    qs = qs.order_by(order_by_field)

    # 7. Paginación
    paginator = Paginator(qs, per_page) 
    page_number = request.GET.get("page")

    # 8. Obtener página (¡Con la corrección de 'page_number'!)
    try:
        page_obj = paginator.get_page(page_number) 
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # 9. Querystring para Paginación
    params_pagination = request.GET.copy()
    params_pagination.pop("page", None)
    querystring_pagination = params_pagination.urlencode()

    # 10. Querystring para Ordenamiento
    params_sorting = request.GET.copy()
    params_sorting.pop("page", None)
    params_sorting.pop("sort_by", None)
    params_sorting.pop("order", None)
    querystring_sorting = params_sorting.urlencode()

    # 11. Contexto
    context = {
        "page_obj": page_obj,  
        "q": q,
        "per_page": per_page, # ¡Pasamos el 'per_page' para el select!
        "total": qs.count(),
        "querystring": querystring_pagination, 
        "querystring_sorting": querystring_sorting,
        "current_sort_by": sort_by,
        "current_order": order,
        "order_next": "desc" if order == "asc" else "asc",
    }
    return render(request, "user_list.html", context)


    
