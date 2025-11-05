from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required

# ¡Importante! Asegúrate de que estas importaciones están
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from .services import ClientService, WarehouseService, SaleOrderService, TransactionService
from Main.decorator import permission_or_redirect

client_service = ClientService()
warehouse_service = WarehouseService()
sale_order_service = SaleOrderService()
transaction_service = TransactionService()

# ===================================
# VISTAS DE CLIENTES
# ===================================

@login_required
@permission_or_redirect('.view_client','dashboard', 'No teni permiso')
def client_list_all(request):
    
    # 1. Obtener filtros de la URL
    q = (request.GET.get("q") or "").strip()
    
    # ===================================
    #   ¡CAMBIO! Nuevas opciones de paginación
    # ===================================
    allowed_per_page = [5, 25, 50, 100]
    default_per_page = 25  # Nuevo default
    
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except ValueError:
        per_page = default_per_page
    
    # Validar que el valor esté en la lista permitida
    if per_page not in allowed_per_page:
        per_page = default_per_page
    # ===================================
    
    # ===================================
    #   ¡NUEVO! Lógica de Ordenamiento
    # ===================================
    # 3. Obtener parámetros de ordenamiento
    allowed_sort_fields = ['rut', 'fantasy_name', 'bussiness_name', 'email', 'phone']
    sort_by = request.GET.get('sort_by', 'fantasy_name') # Default: fantasy_name
    order = request.GET.get('order', 'asc')              # Default: asc

    # Validar que los campos y el orden sean correctos
    if sort_by not in allowed_sort_fields:
        sort_by = 'fantasy_name'
    if order not in ['asc', 'desc']:
        order = 'asc'
        
    order_by_field = f'-{sort_by}' if order == 'desc' else sort_by
    

     
    qs = client_service.list()

    #filtro de búsqueda
    if q:
        qs = qs.filter(
            Q(fantasy_name__icontains=q) |
            Q(bussiness_name__icontains=q) |
            Q(rut__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q)
        )
        
    #ordenamiento
    qs = qs.order_by(order_by_field)

    #Paginación
    paginator = Paginator(qs, per_page)
    page_number = request.GET.get("page")

    # 8. Obtener página
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)


    params_pagination = request.GET.copy()
    params_pagination.pop("page", None)
    querystring_pagination = params_pagination.urlencode()

   
    params_sorting = request.GET.copy()
    params_sorting.pop("page", None)
    params_sorting.pop("sort_by", None)
    params_sorting.pop("order", None)
    querystring_sorting = params_sorting.urlencode()
   

    
    context = {
        "page_obj": page_obj,  
        "q": q,
        "per_page": per_page,
        "total": qs.count(),
        
        
        "querystring": querystring_pagination, 
        
        
        "querystring_sorting": querystring_sorting,
        "current_sort_by": sort_by,
        "current_order": order,
        "order_next": "desc" if order == "asc" else "asc", 
    }
    return render(request, 'client_list.html', context)

# --- Vistas antiguas de Cliente (Las comentamos para guardarlas) ---
@login_required
@permission_or_redirect('.view_client','dashboard', 'No teni permiso')
def client_list_actives(request):
    clients = client_service.list_actives()
    # Esta vista antigua usa la variable 'clients', por eso no funciona con el nuevo HTML
    return render(request, 'client_list.html', {'clients': clients}) 

@login_required
@permission_or_redirect('.view_client','dashboard', 'No teni permiso')
def client_list_inactives(request):
    clients = client_service.list_inactives()
    
    return render(request, 'client_list.html', {'clients': clients})

# --- Resto de vistas de Cliente (con redirects actualizados) ---
@login_required
@permission_or_redirect('.view_client','dashboard', 'No teni permiso')
def client_view(request, id):
    if request.method == 'GET':
        client = client_service.get(id)
        return render(request, 'client_view.html', {'b': client})
    else:
        return redirect('client_list_all') # ¡Redirect actualizado!

@login_required
@permission_or_redirect('.add_client','dashboard', 'No teni permiso')
def client_create(request):
    form = client_service.form_class()
    if request.method == 'POST':
        success, obj = client_service.save(request.POST)
        if success:
            return redirect('client_list_all') # ¡Redirect actualizado!
        else:
            return render(request, 'client_create.html', {'form': obj})
    return render(request, 'client_create.html', {'form': form})

@login_required
@permission_or_redirect('.change_client','dashboard', 'No teni permiso')
def client_update(request, id):
    if request.method == 'POST':
        success, obj = client_service.update(id, request.POST)
        if success:
            return redirect('client_list_all') # ¡Redirect actualizado!
        else:
            return render(request, 'client_update.html', {'form': obj})
    else:
        client = client_service.get(id)
        form = client_service.form_class(instance=client)
    return render(request, 'client_update.html', {'form': form})
    
@login_required
@permission_or_redirect('.delete_client','dashboard', 'No teni permiso')
def client_delete(request, id):
    if request.method == 'GET':
        success = client_service.delete(id)
        if success:
            return redirect('client_list_all') # ¡Redirect actualizado!
    return redirect('client_list_all') # ¡Redirect actualizado!

# ===================================
# VISTAS DE LOCATIONS (Indentación Corregida)
# ===================================
@login_required
@permission_or_redirect('.view_location','dashboard', 'No teni permiso')
def location_list(request):
    
    # 1. Obtener filtros de la URL
    q = (request.GET.get("q") or "").strip()
    
    # ===================================
    #   ¡CAMBIO! Nuevas opciones de paginación
    # ===================================
    allowed_per_page = [5, 25, 50, 100]
    default_per_page = 25  # Nuevo default
    
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except ValueError:
        per_page = default_per_page
    
    # Validar que el valor esté en la lista permitida
    if per_page not in allowed_per_page:
        per_page = default_per_page
    # ===================================

    # ===================================
    #   ¡NUEVO! Lógica de Ordenamiento
    # ===================================
    # 3. Obtener parámetros de ordenamiento
    allowed_sort_fields = ['name', 'city', 'country']
    sort_by = request.GET.get('sort_by', 'name') # Default: name
    order = request.GET.get('order', 'asc')      # Default: asc

    # Validar que los campos y el orden sean correctos
    if sort_by not in allowed_sort_fields:
        sort_by = 'name'
    if order not in ['asc', 'desc']:
        order = 'asc'
        
    order_by_field = f'-{sort_by}' if order == 'desc' else sort_by
    # ===================================

    # 4. Queryset base (¡quitamos el .order_by() de aquí!)
    qs = warehouse_service.location_model.objects.all()

    # 5. Aplicar filtro de búsqueda
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(city__icontains=q) |
            Q(country__icontains=q)
        )
        
    # 6. Aplicar ordenamiento (¡justo antes de paginar!)
    qs = qs.order_by(order_by_field)

    # 7. Paginación
    paginator = Paginator(qs, per_page)
    page_number = request.GET.get("page")

    # 8. Obtener página
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # ===================================
    #   ¡NUEVO! Querystrings actualizados
    # ===================================
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
    # ===================================

    # 11. Contexto
    context = {
        "page_obj": page_obj,  
        "q": q,
        "per_page": per_page,
        "total": qs.count(),
        "querystring": querystring_pagination, 
        "querystring_sorting": querystring_sorting,
        "current_sort_by": sort_by,
        "current_order": order,
        "order_next": "desc" if order == "asc" else "asc",
    }
    return render(request, 'location_list.html', context)

@login_required
@permission_or_redirect('.view_location','dashboard', 'No teni permiso')
def location_view(request, id):
    if request.method == 'GET':
        location = warehouse_service.location_model.objects.get(id=id)
        return render(request, 'location_view.html', {'location': location})
    else:
        return redirect('location_list')

@login_required
@permission_or_redirect('.add_location','dashboard', 'No teni permiso')
def location_create(request):
    form = warehouse_service.location_form_class()
    if request.method == 'POST':
        success, obj = warehouse_service.create_location(request.POST)
        if success:
            return redirect('location_list')
        else:
            return render(request, 'location_create.html', {'form': obj})
    return render(request, 'location_create.html', {'form': form})

@login_required
@permission_or_redirect('.change_location','dashboard', 'No teni permiso')
def location_update(request, id):
    if request.method == 'POST':
        success, obj = warehouse_service.update_location(id, request.POST)
        if success:
            return redirect('location_list')
        else:
            return render(request, 'location_update.html', {'form': obj})
    else:
        location = warehouse_service.location_model.objects.get(id=id)
        form = warehouse_service.location_form_class(instance=location)
    return render(request, 'location_update.html', {'form': form})

@login_required
@permission_or_redirect('.delete_location','dashboard', 'No teni permiso')
def location_delete(request, id):
    if request.method == 'GET':
        success = warehouse_service.delete_location(id)
        if success:
            return redirect('location_list')
    return redirect('location_list')

# ===================================
# VISTAS DE WAREHOUSES (Indentación Corregida)
# ===================================
@login_required
@permission_or_redirect('.view_warehouse','dashboard', 'No teni permiso')
def warehouse_list(request):
    
    # 1. Obtener filtros de la URL
    q = (request.GET.get("q") or "").strip()
    
    # ===================================
    #   ¡CAMBIO! Nuevas opciones de paginación
    # ===================================
    allowed_per_page = [5, 25, 50, 100]
    default_per_page = 25  # Nuevo default
    
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except ValueError:
        per_page = default_per_page
    
    # Validar que el valor esté en la lista permitida
    if per_page not in allowed_per_page:
        per_page = default_per_page
    # ===================================

    # ===================================
    #   ¡NUEVO! Lógica de Ordenamiento
    # ===================================
    # 3. Obtener parámetros de ordenamiento
    allowed_sort_fields = ['name', 'address', 'location__name', 'total_area']
    sort_by = request.GET.get('sort_by', 'name') # Default: 'name' (como pediste)
    order = request.GET.get('order', 'asc')      # Default: asc

    # Validar que los campos y el orden sean correctos
    if sort_by not in allowed_sort_fields:
        sort_by = 'name'
    if order not in ['asc', 'desc']:
        order = 'asc'
        
    order_by_field = f'-{sort_by}' if order == 'desc' else sort_by
    # ===================================

    # 4. Queryset base (¡quitamos el .order_by() de aquí!)
    qs = warehouse_service.model.objects.select_related("location").all()

    # 5. Aplicar filtro de búsqueda
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(address__icontains=q) |
            Q(location__name__icontains=q) # Búsqueda en la FK
        )
        
    # 6. Aplicar ordenamiento (¡justo antes de paginar!)
    qs = qs.order_by(order_by_field)

    # 7. Paginación
    paginator = Paginator(qs, per_page)
    page_number = request.GET.get("page")

    # 8. Obtener página
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # ===================================
    #   ¡NUEVO! Querystrings actualizados
    # ===================================
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
    # ===================================

    # 11. Contexto
    context = {
        "page_obj": page_obj,  
        "q": q,
        "per_page": per_page,
        "total": qs.count(),
        
        "querystring": querystring_pagination, 
        
        "querystring_sorting": querystring_sorting,
        "current_sort_by": sort_by,
        "current_order": order,
        "order_next": "desc" if order == "asc" else "asc",
    }
    return render(request, 'warehouse_list.html', context)

@login_required
@permission_or_redirect('.view_warehouse','dashboard', 'No teni permiso')
def warehouse_view(request, id):
    if request.method == 'GET':
        warehouse = warehouse_service.model.objects.get(id=id)
        return render(request, 'warehouse_view.html', {'warehouse': warehouse})
    else:
        return redirect('warehouse_list')

@login_required
@permission_or_redirect('.add_warehouse','dashboard', 'No teni permiso')
def warehouse_create(request):
    form = warehouse_service.form_class()
    if request.method == 'POST':
        success, obj = warehouse_service.save(request.POST)
        if success:
            return redirect('warehouse_list')
        else:
            return render(request, 'warehouse_create.html', {'form': obj})
    return render(request, 'warehouse_create.html', {'form': form})

@login_required
@permission_or_redirect('.change_warehouse','dashboard', 'No teni permiso')
def warehouse_update(request, id):
    if request.method == 'POST':
        success, obj = warehouse_service.update(id, request.POST)
        if success:
            return redirect('warehouse_list')
        else:
            return render(request, 'warehouse_update.html', {'form': obj})
    else:
        warehouse = warehouse_service.model.objects.get(id=id)
        form = warehouse_service.form_class(instance=warehouse)
    return render(request, 'warehouse_update.html', {'form': form})

@login_required
@permission_or_redirect('.delete_warehouse','dashboard', 'No teni permiso')
def warehouse_delete(request, id):
    if request.method == 'GET':
        success = warehouse_service.delete(id)
        if success:
            return redirect('warehouse_list')
    return redirect('warehouse_list')