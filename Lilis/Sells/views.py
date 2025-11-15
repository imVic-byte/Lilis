from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .services import ClientService, WarehouseService, SaleOrderService, TransactionService
from Main.decorator import permission_or_redirect
from Main.utils import generate_excel_response
from django.http import JsonResponse
from Products.services import BatchService
from Products.services import ProductService, RawMaterialService
from datetime import date

client_service = ClientService()
warehouse_service = WarehouseService()
sale_order_service = SaleOrderService()
transaction_service = TransactionService()
batch_service = BatchService()
product_service = ProductService()
raw_material_service = RawMaterialService()

# ===================================
# VISTAS DE CLIENTES
# ===================================

@login_required
@permission_or_redirect('Sells.view_client','dashboard', 'No teni permiso')
def client_list_all(request):
    
    # 1. Obtener filtros de la URL
    q = (request.GET.get("q") or "").strip()
    
    # ===================================
    #   ¡CAMBIO! Nuevas opciones de paginación
    # ===================================
    allowed_per_page = [5, 25, 50, 100]
    default_per_page = request.user.profile.per_page
    
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
    

     
    qs = client_service.list_actives()

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
    request.user.profile.per_page = per_page
    return render(request, 'clients/client_list.html', context)

# --- Vistas antiguas de Cliente (Las comentamos para guardarlas) ---
@login_required
@permission_or_redirect('Sells.view_client','dashboard', 'No teni permiso')
def client_list_actives(request):
    clients = client_service.list_actives()
    # Esta vista antigua usa la variable 'clients', por eso no funciona con el nuevo HTML
    return render(request, 'clients/client_list.html', {'clients': clients}) 

@login_required
@permission_or_redirect('Sells.view_client','dashboard', 'No teni permiso')
def client_list_inactives(request):
    clients = client_service.list_inactives()
    
    return render(request, 'clients/client_list.html', {'clients': clients})

# --- Resto de vistas de Cliente (con redirects actualizados) ---
@login_required()
@permission_or_redirect('Sells.view_client','dashboard', 'No teni permiso')
def client_search(request):
    q = request.GET.get('q', '')
    clients = client_service.model.objects.filter(is_suspended=False).filter(
        Q(fantasy_name__icontains=q) |
        Q(bussiness_name__icontains=q) |
        Q(rut__icontains=q)
    ).values('id', 'fantasy_name', 'bussiness_name', 'rut', 'email', 'phone', 'is_suspended', 'credit_limit', 'debt', 'max_debt')
    return JsonResponse(list(clients), safe=False)

@login_required
@permission_or_redirect('Sells.view_client','dashboard', 'No teni permiso')
def client_view(request, id):
    if request.method == 'GET':
        client = client_service.get(id)
        warehouses = client.wareclients.all()
        return render(request, 'clients/client_view.html', {'b': client, 'warehouses': warehouses})
    else:
        return redirect('client_list_all') # ¡Redirect actualizado!

@login_required
@permission_or_redirect('Sells.add_client','dashboard', 'No teni permiso')
def client_create(request):
    form = client_service.form_class()
    if request.method == 'POST':
        success, obj = client_service.save(request.POST)
        if success:
            return redirect('client_list_all') # ¡Redirect actualizado!
        else:
            return render(request, 'clients/client_create.html', {'form': obj})
    return render(request, 'clients/client_create.html', {'form': form})

@login_required
@permission_or_redirect('Sells.change_client','dashboard', 'No teni permiso')
def client_update(request, id):
    if request.method == 'POST':
        success, obj = client_service.update(id, request.POST)
        if success:
            return redirect('client_list_all') # ¡Redirect actualizado!
        else:
            return render(request, 'clients/client_update.html', {'form': obj})
    else:
        client = client_service.get(id)
        form = client_service.form_class(instance=client)
    return render(request, 'clients/client_update.html', {'form': form})
    
@login_required
@permission_or_redirect('Sells.delete_client','dashboard', 'No teni permiso')
def client_delete(request, id):
    if request.method == 'GET':
        success = client_service.to_suspend(id)
        if success:
            return redirect('client_list_all')
    return redirect('client_list_all')

@login_required
@permission_or_redirect('Sells.view_client','dashboard', 'No teni permiso')
def export_clients_excel(request):
    q = (request.GET.get("q") or "").strip()
    limit = request.GET.get("limit")
    qs = client_service.list().order_by('fantasy_name')
    if q:
        qs = qs.filter(
            Q(fantasy_name__icontains=q) |
            Q(bussiness_name__icontains=q) |
            Q(rut__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q)
        )
    if limit:
        try:
            limit = int(limit)
            qs = qs[:limit]
        except ValueError:
            pass
    headers = ["Nombre Fantasía", "Razón Social", "RUT", "Email", "Teléfono", "Estado", "Limite de Credito", "Deuda", "Deuda Máxima"]
    data_rows = []
    for client in qs:
        data_rows.append([
            client.fantasy_name,
            client.bussiness_name,
            client.rut,
            client.email,
            client.phone,
            "Inactivo" if client.is_suspended else "Activo",
            client.credit_limit,
            client.debt,
            client.max_debt
        ])
    return generate_excel_response(headers, data_rows, "Lilis_Clientes")

@login_required
@permission_or_redirect('Sells.view_location','dashboard', 'No teni permiso')
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
    return render(request, 'locations/location_list.html', context)

@login_required
@permission_or_redirect('Sells.view_location','dashboard', 'No teni permiso')
def location_view(request, id):
    if request.method == 'GET':
        location = warehouse_service.location_model.objects.get(id=id)
        return render(request, 'locations/location_view.html', {'location': location})
    else:
        return redirect('location_list')

@login_required
@permission_or_redirect('Sells.add_location','dashboard', 'No teni permiso')
def location_create(request):
    form = warehouse_service.location_form_class()
    if request.method == 'POST':
        success, obj = warehouse_service.create_location(request.POST)
        if success:
            return redirect('location_list')
        else:
            return render(request, 'locations/location_create.html', {'form': obj})
    return render(request, 'locations/location_create.html', {'form': form})

@login_required
@permission_or_redirect('Sells.change_location','dashboard', 'No teni permiso')
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
    return render(request, 'locations/location_update.html', {'form': form})

@login_required
@permission_or_redirect('Sells.delete_location','dashboard', 'No teni permiso')
def location_delete(request, id):
    if request.method == 'GET':
        success = warehouse_service.delete_location(id)
        if success:
            return redirect('location_list')
    return redirect('location_list')

@login_required
@permission_or_redirect('Sells.view_location','dashboard', 'No teni permiso')
def export_locations_excel(request):
    q= (request.GET.get("q") or "").strip()
    qs = warehouse_service.location_model.objects.all().order_by('name')
    limit = request.GET.get("limit")
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(city__icontains=q) |
            Q(country__icontains=q)
        )
    if limit:
        try:
            limit = int(limit)
            qs = qs[:limit]
        except ValueError:
            pass
    headers = ["Nombre", "Ciudad", "País"]
    data_rows = []
    for location in qs:
        data_rows.append([
            location.name,
            location.city,
            location.country,
        ])
    return generate_excel_response(headers, data_rows, "Lilis_Ubicaciones")

# ===================================
# VISTAS DE WAREHOUSES (Indentación Corregida)
# ===================================
@login_required
@permission_or_redirect('Sells.view_warehouse','dashboard', 'No teni permiso')
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
    qs = warehouse_service.model.objects.all()

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
    return render(request, 'warehouses/warehouse_list.html', context)

@login_required
@permission_or_redirect('Sells.view_warehouse','dashboard', 'No teni permiso')
def warehouse_view(request, id):
    if request.method == 'GET':
        warehouse = warehouse_service.model.objects.get(id=id)
        return render(request, 'warehouses/warehouse_view.html', {'w': warehouse})
    else:
        return redirect('warehouse_list')

@login_required
@permission_or_redirect('Sells.add_warehouse','dashboard', 'No teni permiso')
def warehouse_create(request):
    form = warehouse_service.form_class()
    if request.method == 'POST':
        if request.GET.get('client'):
            client = client_service.get(request.GET.get('client'))
            success, warehouse = warehouse_service.save(request.POST)
            if success:
                success2, obj2 = warehouse_service.warehouse_assign(client, warehouse.id)
                if success2:
                    next = request.GET.get('next')
                    return redirect(next)
                else:
                    return render(request, 'warehouses/warehouse_create.html', {'form': obj, 'error': 'No se pudo asignar la bodega.'})
            else:
                return render(request, 'warehouses/warehouse_create.html', {'form': obj, 'error': 'No se pudo crear la bodega.'})
        else:
            success, obj = warehouse_service.save(request.POST)
            if success:
                return redirect('warehouse_list')
    else:
        return render(request, 'warehouses/warehouse_create.html', {'form': form})
    return render(request, 'warehouses/warehouse_create.html', {'form': form})

@login_required
@permission_or_redirect('Sells.change_warehouse','dashboard', 'No teni permiso')
def warehouse_update(request, id):
    if request.method == 'POST':
        if request.GET.get('client'):
            success, obj = warehouse_service.update(id, request.POST)
            if success:
                next = request.GET.get('next')
                return redirect(next)
            else:
                return render(request, 'warehouses/warehouse_update.html', {'form': obj})
        else:
            success, obj = warehouse_service.update(id, request.POST)
            if success:
                return redirect('warehouse_list')
            else:
                return render(request, 'warehouses/warehouse_update.html', {'form': obj})
    else:
        warehouse = warehouse_service.model.objects.get(id=id)
        form = warehouse_service.form_class(instance=warehouse)
    return render(request, 'warehouses/warehouse_update.html', {'form': form})

@login_required
@permission_or_redirect('Sells.delete_warehouse','dashboard', 'No teni permiso')
def warehouse_delete(request, id):
    if request.method == 'GET':
        success = warehouse_service.delete(id)
        if success:
            if request.GET.get('client'):
                next = request.GET.get('next')
                return redirect(next)
            return redirect('warehouse_list')
    return redirect('warehouse_list')

@login_required
@permission_or_redirect('Sells.view_warehouse','dashboard', 'No teni permiso')
def export_warehouse_excel(request):
    q = (request.GET.get("q") or "").strip()
    qs = warehouse_service.model.objects.select_related("location").all().order_by('name')
    limit = request.GET.get("limit")
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(address__icontains=q) |
            Q(location__name__icontains=q) # Búsqueda en la FK
        )
    if limit:
        try:
            limit = int(limit)
            qs = qs[:limit]
        except ValueError:
            pass
    headers = ["Nombre", "Dirección", "Ubicación", "Área Total"]
    data_rows = []
    for warehouse in qs:
        data_rows.append([
            warehouse.name,
            warehouse.address,
            warehouse.location.name if warehouse.location else "N/A",
            warehouse.total_area,
        ])
    return generate_excel_response(headers, data_rows, "Lilis_Bodegas")

def get_warehouses_by_client(request):
    client_id = request.GET.get('client_id')
    warehouses_list = []

    if client_id:
        client = client_service.get(client_id)
        if client:
            warehouses = warehouse_service.filter_by_client(client)
            for w in warehouses:
                warehouses_list.append({
                    'id': w.id,
                    'name': w.name,
                    'address': w.address,
                    'location': w.location,
                })

    return JsonResponse({'warehouses': warehouses_list})

def get_stock_by_product(request):
    product_id = request.GET.get('product_id')
    stock = product_service.get_stock_by_product(product_id)
    return JsonResponse({'stock': stock})

def get_products(request):
    products = product_service.list_actives()
    return JsonResponse({'products': products})

def get_raw_materials(request):
    raw_materials = raw_material_service.list_actives()
    return JsonResponse({'raw_materials': raw_materials})

def validate_code(request):
    code = request.GET.get('code')
    return JsonResponse({'valid': transaction_service.validate_code(code)})

def transaction(request):
    q = (request.GET.get("q") or "").strip()
    allowed_per_page = [5, 25, 50, 100]
    default_per_page = 25
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except ValueError:
        per_page = default_per_page
    if per_page not in allowed_per_page:
        per_page = default_per_page
    allowed_sort_fields = ['date', 'type', 'sku', 'client']
    sort_by = request.GET.get('sort_by', 'date')
    order = request.GET.get('order', 'desc')
    if sort_by not in allowed_sort_fields:
        sort_by = 'date'
    if order not in ['asc', 'desc']:
        order = 'asc'
        
    order_by_field = f'-{sort_by}' if order == 'desc' else sort_by
    qs = transaction_service.list()
    if q:
        qs = qs.filter(
            Q(product__sku__istartswith=q)|
            Q(type__icontains=q)|
            Q(client__rut__startswith=q)
        )
    qs = qs.order_by(order_by_field)
    paginator = Paginator(qs, per_page)
    page_number = request.GET.get("page")
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
    products = product_service.list_actives()
    lotes = batch_service.list_product()
    clients = client_service.list_actives()
    transactions = transaction_service.list()
    today = []
    for t in transactions:
        t.date = t.date.date()
        if t.date == date.today():
            today.append(t)
    transactions_today = len(today)
    if request.method == 'POST':
        data = {
            'warehouse':request.POST.get('warehouse'),
            'client':request.POST.get('client'),
            'user':request.user.profile,
            'notes':request.POST.get('observaciones'),
            'type':request.POST.get('tipo'),
            'quantity':request.POST.get('cantidad'),
            'product':request.POST.get('producto'),
            'batch_code':request.POST.get('lote'),
            'serie_code':request.POST.get('serie'),
            'expiration_date':request.POST.get('vencimiento'),
        }
        print(data)
        transaction_service.create_transaction(data)
        return redirect('transaction_list')
    return render(request,'transactions/transaction.html',{
        'lotes': lotes, 
        'products': products, 
        'clients': clients, 
        'transactions': transactions, 
        'transactions_today': transactions_today,
        "page_obj": page_obj,  
        "q": q,
        "per_page": per_page,
        "total": qs.count(),
        "querystring": querystring_pagination, 
        "querystring_sorting": querystring_sorting,
        "current_sort_by": sort_by,
        "current_order": order,
        "order_next": "desc" if order == "asc" else "asc",
        })

def export_transaction_excel(request):
    q = (request.GET.get("q") or "").strip()
    qs = transaction_service.list().order_by('date')
    limit = request.GET.get("limit")
    if q:
        qs = qs.filter(
            Q(product__sku__istartswith=q)|
            Q(type__icontains=q)|
            Q(client__rut__startswith=q)
        )
    if limit:
        try:
            limit = int(limit)
            qs = qs[:limit]
        except ValueError:
            pass
    data_rows = []
    for transaction in qs:
        data_rows.append([
            transaction.type,
            transaction.product.sku,
            transaction.client.rut,
            transaction.warehouse.name,
            transaction.date.strftime("%Y-%m-%d"),
            transaction.expiration_date.strftime("%Y-%m-%d") if transaction.expiration_date else "",
            transaction.batch_code,
            transaction.serie_code,
            transaction.notes,
        ])
    headers = ["Tipo", "SKU", "Cliente", "Bodega", "Fecha", "Vencimiento", "Lote", "Serie", "Observaciones"]
    return generate_excel_response(headers, data_rows, "Lilis_Transacciones")