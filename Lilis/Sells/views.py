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
    
    # 2. Obtener 'por página' (rango 1-10)
    default_per_page = 10
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except ValueError:
        per_page = default_per_page
    
    if per_page > 10 or per_page <= 0:
        per_page = default_per_page

    # 3. Obtener queryset base (solo "todos")
    qs = client_service.list().order_by('fantasy_name')

    # 4. Aplicar filtro de búsqueda
    if q:
        qs = qs.filter(
            Q(fantasy_name__icontains=q) |
            Q(bussiness_name__icontains=q) |
            Q(rut__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q)
        )

    # 5. Aplicar paginación
    paginator = Paginator(qs, per_page)
    page_number = request.GET.get("page")

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # 6. Preparar querystring para los enlaces de paginación
    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()

    # 7. Preparar contexto para el template
    context = {
        "page_obj": page_obj,      # ¡Aquí está la variable correcta!
        "q": q,
        "per_page": per_page,
        "querystring": querystring,
        "total": qs.count(),
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
    # Esta vista antigua usa la variable 'clients', por eso no funciona con el nuevo HTML
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
    
    # 2. Obtener 'por página' (rango 1-10)
    default_per_page = 10
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except ValueError:
        per_page = default_per_page
    
    if per_page > 10 or per_page <= 0:
        per_page = default_per_page

    # 3. Obtener queryset base
    qs = warehouse_service.location_model.objects.all().order_by('name')

    # 4. Aplicar filtro de búsqueda
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(city__icontains=q) |
            Q(country__icontains=q)
        )

    # 5. Aplicar paginación
    paginator = Paginator(qs, per_page)
    page_number = request.GET.get("page")

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # 6. Preparar querystring
    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()

    # 7. Preparar contexto
    context = {
        "page_obj": page_obj,      # ¡Cambiamos 'locations' por 'page_obj'!
        "q": q,
        "per_page": per_page,
        "querystring": querystring,
        "total": qs.count(),
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
    
    # 2. Obtener 'por página' (rango 1-10)
    default_per_page = 10
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except ValueError:
        per_page = default_per_page
    
    if per_page > 10 or per_page <= 0:
        per_page = default_per_page

    # 3. Obtener queryset base
    # ¡Optimizamos con select_related para traer la ubicación!
    qs = warehouse_service.model.objects.select_related("location").all().order_by('name')

    # 4. Aplicar filtro de búsqueda
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(address__icontains=q) |
            Q(location__name__icontains=q) # Búsqueda en la FK
        )

    # 5. Aplicar paginación
    paginator = Paginator(qs, per_page)
    page_number = request.GET.get("page")

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # 6. Preparar querystring
    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()

    # 7. Preparar contexto
    context = {
        "page_obj": page_obj,      # ¡Cambiamos 'warehouses' por 'page_obj'!
        "q": q,
        "per_page": per_page,
        "querystring": querystring,
        "total": qs.count(),
    }
    return render(request, 'warehouse_list.html', context)

@login_required
@permission_or_redirect('.view_warehouse','dashboard', 'No teni permiso')
def warehouse_view(request, id):
    if request.method == 'GET':
        warehouse = warehouse_service.model.objects.get(id=id)
        return render(request, 'warehouse_view.html', {'w': warehouse})
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