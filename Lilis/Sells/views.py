from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .services import ClientService, WarehouseService, TransactionService
from Main.decorator import permission_or_redirect
from Main.utils import generate_excel_response
from django.http import JsonResponse
from Products.services import ProductService, RawMaterialService, SupplierService
from datetime import date

client_service = ClientService()
warehouse_service = WarehouseService()
transaction_service = TransactionService()
product_service = ProductService()
raw_material_service = RawMaterialService()
supplier_service = SupplierService()
LILIS_RUT = "2519135-8"
# ===================================
# VISTAS DE CLIENTES
# ===================================

@login_required
@permission_or_redirect('Sells.view_client','dashboard', 'No teni permiso')
def client_list_all(request):
    q = (request.GET.get("q") or "").strip()
    allowed_per_page = [5, 25, 50, 100]
    default_per_page = request.user.profile.per_page
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except ValueError:
        per_page = default_per_page
    if per_page not in allowed_per_page:
        per_page = default_per_page
    allowed_sort_fields = ['rut', 'fantasy_name', 'bussiness_name', 'email', 'phone']
    sort_by = request.GET.get('sort_by', 'fantasy_name')
    order = request.GET.get('order', 'asc')
    if sort_by not in allowed_sort_fields:
        sort_by = 'fantasy_name'
    if order not in ['asc', 'desc']:
        order = 'asc'
    order_by_field = f'-{sort_by}' if order == 'desc' else sort_by
    qs = client_service.list_actives()
    if q:
        qs = qs.filter(
            Q(fantasy_name__icontains=q) |
            Q(bussiness_name__icontains=q) |
            Q(rut__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q)
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
        return redirect('client_list_all')

@login_required
@permission_or_redirect('Sells.add_client','dashboard', 'No teni permiso')
def client_create(request):
    form = client_service.form_class()
    if request.method == 'POST':
        success, obj = client_service.save(request.POST)
        if success:
            return redirect('client_list_all')
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

# ===================================
# VISTAS DE WAREHOUSES (Indentación Corregida)
# ===================================
@login_required
@permission_or_redirect('Sells.view_warehouse','dashboard', 'No teni permiso')
def warehouse_list(request):
    q = (request.GET.get("q") or "").strip()
    allowed_per_page = [5, 25, 50, 100]
    default_per_page = 25
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except ValueError:
        per_page = default_per_page
    if per_page not in allowed_per_page:
        per_page = default_per_page
    allowed_sort_fields = ['name', 'address', 'location__name', 'total_area']
    sort_by = request.GET.get('sort_by', 'name')
    order = request.GET.get('order', 'asc')
    if sort_by not in allowed_sort_fields:
        sort_by = 'name'
    if order not in ['asc', 'desc']:
        order = 'asc'
        
    order_by_field = f'-{sort_by}' if order == 'desc' else sort_by
    qs = warehouse_service.model.objects.all()
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(address__icontains=q) |
            Q(location__name__icontains=q)
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
                    return render(request, 'warehouses/warehouse_create.html', {'form': warehouse, 'error': 'No se pudo asignar la bodega.'})
            else:
                return render(request, 'warehouses/warehouse_create.html', {'form': warehouse, 'error': 'No se pudo crear la bodega.'})
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

def get_warehouses(request):
    id = request.GET.get('id')
    type = request.GET.get('type')
    if type == 'salida':
        warehouses_list = []
        if id:
            client = client_service.get(id)
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
    elif type == 'ingreso':
        warehouses_list = []
        if id:
            suppliers = supplier_service.list_actives()
            for s in suppliers:
                warehouses = warehouse_service.filter_by_supplier(s)
                for w in warehouses:
                    warehouses_list.append({
                        'id': w.id,
                        'name': w.name,
                        'address': w.address,
                        'location': w.location,
                    })
            return JsonResponse({'warehouses': warehouses_list})    
    else:
        warehouses_list = []
        if id:
            clients = client_service.list_actives().filter(id=id)

def get_stock_by_product(request):
    product = request.GET.get('product_id')
    p, id = product.split('-')
    if p == 'product':
        stock = product_service.get_stock_by_product(id)
    else:
        stock = raw_material_service.get_stock_by_raw_material(id)
    return JsonResponse({'stock': stock})


def warehouse_to_dict(w):
    return {
        'id': w.id,
        'name': w.name,
        'address': w.address,
        'location': w.location,
    }


def raw_material_to_dict(rm):
    return {
        'id': rm.id,
        'name': rm.name,
        'sku': rm.sku,
        'measurement_unit': rm.measurement_unit,
    }


def supplier_base_dict(s):
    return {
        'id': s.id,
        'bussiness_name': s.bussiness_name,
        'rut': s.rut,
    }


def get_warehouses_for_client(client):
    warehouses = warehouse_service.filter_by_client(client)
    return [warehouse_to_dict(w) for w in warehouses]


def handle_ingreso():
    l = client_service.search_by_rut(LILIS_RUT)[0]
    data = {
        'warehouses': get_warehouses_for_client(l),
        'suppliers': [],
    }
    suppliers = supplier_service.list_actives()
    for s in suppliers:
        supplier_data = supplier_base_dict(s)
        rms = transaction_service.inventario.raw_class.objects.filter(supplier_id=s.id)
        supplier_data['raw_materials'] = [raw_material_to_dict(rm) for rm in rms]
        data['suppliers'].append(supplier_data)
    return JsonResponse({'data': data})

def handle_salida():
    data = []
    clients = client_service.list_actives().exclude(rut=LILIS_RUT)

    for c in clients:
        client_data = {
            'id': c.id,
            'bussiness_name': c.bussiness_name,
            'rut': c.rut,
            'warehouses': get_warehouses_for_client(c),
        }
        data.append(client_data)

    return JsonResponse({'data': data})


def handle_devolucion():
    data = {
        'clients': [],
        'products': [],
        'raw_materials': [],
        'warehouses': [],
    }
    clients = client_service.list_actives().exclude(rut=LILIS_RUT)
    for c in clients:
        data['clients'].append(supplier_base_dict(c))
    suppliers = supplier_service.list_actives().exclude(rut=LILIS_RUT)
    for s in suppliers:
        data['clients'].append(supplier_base_dict(s))
    products = transaction_service.inventario.product_class.objects.all().filter(is_active=True)
    for p in products:
        data['products'].append(raw_material_to_dict(p))
    raw_materials = transaction_service.inventario.raw_class.objects.all().filter(is_active=True)
    for rm in raw_materials:
        data['raw_materials'].append(raw_material_to_dict(rm))
    l = client_service.search_by_rut(LILIS_RUT)[0]
    warehouses = get_warehouses_for_client(l)
    for w in warehouses:
        data['warehouses'].append(w)
    return JsonResponse({'data': data})


def handle_transfer():
    c = client_service.search_by_rut(LILIS_RUT)[0]
    data = {
        'clients': [supplier_base_dict(c)],
        'products': [],
        'raw_materials': [],
        'warehouses': [],
    }
    products = product_service.list_actives()
    for p in products:
        data['products'].append(raw_material_to_dict(p))
    raw_materials = transaction_service.inventario.raw_class.objects.all().filter(is_active=True)
    for rm in raw_materials:
        data['raw_materials'].append(raw_material_to_dict(rm))
    l = client_service.search_by_rut(LILIS_RUT)[0]
    warehouses = get_warehouses_for_client(l)
    for w in warehouses:
        data['warehouses'].append(w)
    return JsonResponse({'data': data})

def get_raw_materials_by_supplier(request):
    id = request.GET.get('id')
    type = request.GET.get('type')
    if type == 'ingreso':
        p = []
        raw_materials = transaction_service.inventario.raw_class.objects.filter(supplier_id=id).filter(is_active=True)
        for rm in raw_materials:
            p.append({
                'id': rm.id,
                'name': rm.name,
                'sku': rm.sku,
                'measurement_unit': rm.measurement_unit,
            })
        return JsonResponse({'p': p})
    elif type == 'salida':
        p = []
        products = transaction_service.inventario.product_class.objects.all().filter(is_active=True)
        for pr in products:
            p.append({
                'id': pr.id,
                'sku': pr.sku,
                'name': pr.name,
                'measurement_unit': pr.measurement_unit,
            })
        return JsonResponse({'p': p})



def get_by_type(request):
    tipo = request.GET.get('type')
    match tipo:
        case 'ingreso':
            return handle_ingreso()
        case 'salida':
            return handle_salida()
        case 'devolucion':
            return handle_devolucion()
        case _:
            return handle_transfer()
    
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
    allowed_sort_fields = ['date', 'type', 'client']
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
            Q(type__icontains=q)|
            Q(client__rut__startswith=q)|
            Q(client__bussiness_name__icontains=q)
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
    products = transaction_service.inventario.product_class.objects.all().filter(is_active=True)
    raw_materials = transaction_service.inventario.raw_class.objects.all().filter(is_active=True)
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
            'date':request.POST.get('fecha'),
        }
        print(data)
        transaction_service.create_transaction(data)
        return redirect('transaction_list')
    return render(request,'transactions/transaction.html',{
        'products': products, 
        'raw_materials': raw_materials,
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

@login_required
@permission_or_redirect('Sells.change_transaction','dashboard', 'No teni permiso')
def transaction_update(request, id):
    original = transaction_service.model.objects.get(id=id)
    if request.method == 'POST':
        form = transaction_service.form_class(request.POST, base_transaction=original)
        if form.is_valid():
            form.save() 
            return redirect('transaction_list')
    else:
        form = transaction_service.form_class(base_transaction=original)
    return render(request, 'transactions/transaction_update.html', {'form': form})

def product_batch_list(request):
    q = (request.GET.get("q") or "").strip()
    default_per_page = 25
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except ValueError:
        per_page = default_per_page
    if per_page > 101 or per_page <= 0:
        per_page = default_per_page
    allowed_sort_fields = ['inventario__producto__name', 'inventario__producto__category__name', 'inventario__producto__sku']
    sort_by = request.GET.get('sort_by', 'inventario__producto__name')
    order = request.GET.get('order', 'asc')

    if sort_by not in allowed_sort_fields:
        sort_by = 'inventario__producto__name'
    if order not in ['asc', 'desc']:
        order = 'asc'
        
    order_by_field = f'-{sort_by}' if order == 'desc' else sort_by
    qs = transaction_service.inventario.lote.objects.all().filter(inventario__producto__is_active=True)

    if q:
        qs = qs.filter(
            Q(inventario__producto__name__icontains=q) |
            Q(inventario__producto__description__icontains=q)|
            Q(inventario__producto__sku__icontains=q)
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
    return render(request, 'batches/product_batch_list.html', context)

def product_batch_create(request):
    l = client_service.search_by_rut(LILIS_RUT)[0]
    warehouses = get_warehouses_for_client(l)
    products = product_service.list_actives()
    if request.method == 'POST':
        print(request.POST)
        success, obj = transaction_service.inventario.agregar_lote_producto(request.POST)

        if success:
            return redirect('product_batch_list')
        context = {
            'warehouses': warehouses,
            'products': products,
        }

        if isinstance(obj, str):
            context['error_message'] = obj
            context['form'] = transaction_service.inventario.lote_form_class(request.POST)  
        else:
            context['form'] = obj

        return render(request, 'batches/product_batch_create.html', context)

    return render(request, 'batches/product_batch_create.html', {
        'form': transaction_service.inventario.lote_form_class(),
        'warehouses': warehouses,
        'products': products,
    })
