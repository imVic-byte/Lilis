from django.shortcuts import render, redirect
from .services import CategoryService, ProductService, SupplierService, RawMaterialService, BatchService, PriceHistoriesService
from django.contrib.auth.decorators import login_required, permission_required
from Main.decorator import permission_or_redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

category_service = CategoryService()
product_service = ProductService()
supplier_service = SupplierService()
raw_material_service = RawMaterialService()
batch_service = BatchService()
price_histories_service = PriceHistoriesService()

@login_required
@permission_or_redirect('Products.view_category','dashboard', 'No teni permiso')
def category_list(request):
    
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
    allowed_sort_fields = ['name', 'description']
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
    qs = category_service.list()

    # 5. Aplicar filtro de búsqueda
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q)
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
    return render(request, 'main/category_list.html', context)

@login_required
@permission_or_redirect('Products.add_category','dashboard', 'No teni permiso')
def category_create(request):
    form = category_service.form_class()
    if request.method == 'POST':
        success, obj = category_service.save(request.POST)
        if success:
            return redirect('category_list')
        else:
            return render(request, 'main/category_create.html', {'form': obj})
    return render(request, 'main/category_create.html', {'form': form})


@login_required
@permission_or_redirect('Products.change_category','dashboard', 'No teni permiso')
def category_update(request, id):
    if request.method == 'POST':
        success, obj = category_service.update(id, request.POST)
        if success:
            return redirect('category_list')
        else:
            return render(request, 'main/category_update.html', {'form': obj})
    else:
        category = category_service.get(id)
        form = category_service.form_class(instance=category)
    return render(request, 'main/category_update.html', {'form': form})

@login_required
@permission_or_redirect('Products.delete_category','dashboard', 'No teni permiso')
def category_delete(request, id):
    if request.method == 'GET':
        success = category_service.delete(id)
        if success:
            return redirect('category_list')
    return redirect('category_list') 

#PRODUCTOSSSSSSSSSs
@login_required
@permission_or_redirect('Products.view_products','dashboard', 'No teni permiso')
def products_list(request):
    
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
    allowed_sort_fields = ['name', 'category__name', 'quantity', 'expiration_date']
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
    # ¡Optimizamos con select_related para traer la categoría!
    qs = product_service.list().select_related("category")

    # 5. Aplicar filtro de búsqueda
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(category__name__icontains=q) # Búsqueda en la FK
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
    return render(request, 'main/products_list.html', context)

@login_required
@permission_or_redirect('Products.view_products','dashboard', 'No teni permiso')
def product_view(request, id):
    product = product_service.get(id)
    return render(request, 'main/product.html', {'p': product})

@login_required
@permission_or_redirect('Products.add_products','dashboard', 'No teni permiso')
def product_create(request):
    form = product_service.form_class()
    if request.method == 'POST':
        success, obj = product_service.save(request.POST)
        if success:
            return redirect('products_list')
        else:
            return render(request, 'main/product_create.html', {'form': obj})
    return render(request, 'main/product_create.html', {'form': form})


@login_required
@permission_or_redirect('Products.change_products','dashboard', 'No teni permiso')
def product_update(request, id):
    if request.method == 'POST':
        success, obj = product_service.update(id, request.POST)
        if success:
            return redirect('products_list')
        else:
            return render(request, 'main/product_update.html', {'form': obj})
    else:
        product = product_service.get(id)
        form = product_service.form_class(instance=product)
    return render(request, 'main/product_update.html', {'form': form})

@login_required
@permission_or_redirect('Products.delete_products','dashboard', 'No teni permiso')
def product_delete(request, id):
        if request.method == 'GET':
            success = product_service.delete(id)
            if success:
                return redirect('products_list')
        return redirect('products_list') 


#SUPPLIERRRR
@login_required
@permission_or_redirect('Products.view_supplier','dashboard', 'No teni permiso')
@login_required
@permission_or_redirect('Products.view_supplier','dashboard', 'No teni permiso')
def supplier_list(request):
    
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
    allowed_sort_fields = ['fantasy_name', 'bussiness_name', 'rut', 'email', 'phone']
    sort_by = request.GET.get('sort_by', 'fantasy_name') # Default: 'fantasy_name'
    order = request.GET.get('order', 'asc')           # Default: asc

    # Validar que los campos y el orden sean correctos
    if sort_by not in allowed_sort_fields:
        sort_by = 'fantasy_name'
    if order not in ['asc', 'desc']:
        order = 'asc'
        
    order_by_field = f'-{sort_by}' if order == 'desc' else sort_by
    # ===================================

    # 4. Queryset base (¡quitamos el .order_by() de aquí!)
    qs = supplier_service.list()

    # 5. Aplicar filtro de búsqueda
    if q:
        qs = qs.filter(
            Q(fantasy_name__icontains=q) |
            Q(bussiness_name__icontains=q) |
            Q(rut__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q)
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
    return render(request, 'main/supplier_list.html', context)
@login_required
@permission_or_redirect('Products.view_supplier','dashboard', 'No teni permiso')
def supplier_view(request, id):
    supplier = supplier_service.get(id)
    return render(request, 'main/supplier.html', {'s': supplier})

@login_required
@permission_or_redirect('Products.add_supplier','dashboard', 'No teni permiso')
def supplier_create(request):
    form = supplier_service.form_class()
    if request.method == 'POST':
        success, obj = supplier_service.save(request.POST)
        if success:
            return redirect('supplier_list')
        else:
            return render(request, 'main/supplier_create.html', {'form': obj})
    return render(request, 'main/supplier_create.html', {'form': form})

@login_required
@permission_or_redirect('Products.change_supplier','dashboard', 'No teni permiso')
def supplier_update(request, id):
    if request.method == 'POST':
        success, obj = supplier_service.update(id, request.POST)
        if success:
            return redirect('supplier_list')
    else:
        supplier = supplier_service.get(id)
        form = supplier_service.form_class(instance=supplier)
    return render(request, 'main/supplier_update.html', {'form': form})

@login_required
@permission_or_redirect('Products.delete_supplier','dashboard', 'No teni permiso')
def supplier_delete(request, id):
    if request.method == 'GET':
        success = supplier_service.delete(id)
        if success:
            return redirect('supplier_list')
    return redirect('supplier_list') 

#RAWMATERIAAAAAAAAAL
@login_required
@permission_or_redirect('Products.view_rawmaterial','dashboard', 'No teni permiso')
def raw_material_list(request):
    
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
    allowed_sort_fields = ['name', 'supplier__fantasy_name', 'category__name']
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
    qs = raw_material_service.list_actives().select_related(
        "supplier", 
        "category"
    )

    # 5. Aplicar filtro de búsqueda
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(supplier__fantasy_name__icontains=q) |
            Q(category__name__icontains=q)
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
    return render(request, 'main/raw_material_list.html', context)


@login_required
@permission_or_redirect('Products.view_rawmaterial','dashboard', 'No teni permiso')
def raw_material_view(request, id):
    raw_material = raw_material_service.get(id)
    return render(request, 'main/raw_material.html', {'rm': raw_material})

@login_required
@permission_or_redirect('Products.add_rawmaterial','dashboard', 'No teni permiso')
def raw_material_create(request):
    form = raw_material_service.form_class()
    if request.method == 'POST':
        success, obj = raw_material_service.save(request.POST)
        if success:
            return redirect('raw_material_list')
        else:
            return render(request, 'main/raw_material_create.html', {'form': obj})
    return render(request, 'main/raw_material_create.html', {'form': form})

@login_required
@permission_or_redirect('Products.change_rawmaterial','dashboard', 'No teni permiso')
def raw_material_update(request, id):
    if request.method == 'POST':
        success, obj = raw_material_service.update(id, request.POST)
        if success:
            return redirect('raw_material_list')
    else:
        raw_material = raw_material_service.get(id)
        form = raw_material_service.form_class(instance=raw_material)
    return render(request, 'main/raw_material_update.html', {'form': form})

@login_required
@permission_or_redirect('Products.delete_rawmaterial','dashboard', 'No teni permiso')
def raw_material_delete(request, id):
    if request.method == 'GET':
        success = raw_material_service.delete(id)
        if success:
            return redirect('raw_material_list')
    return redirect('raw_material_list') 


#BATCHESSS
@login_required
@permission_or_redirect('Products.view_batch','dashboard', 'No teni permiso')
def product_batch_list(request):
    
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
    allowed_sort_fields = ['product__name', 'batch_code']
    sort_by = request.GET.get('sort_by', 'batch_code') # Default: batch_code
    order = request.GET.get('order', 'asc')          # Default: asc

    # Validar que los campos y el orden sean correctos
    if sort_by not in allowed_sort_fields:
        sort_by = 'batch_code'
    if order not in ['asc', 'desc']:
        order = 'asc'
        
    order_by_field = f'-{sort_by}' if order == 'desc' else sort_by
    # ===================================

    # 4. Queryset base (¡quitamos el .order_by() de aquí!)
    # ¡Optimizamos con select_related para traer el producto!
    qs = batch_service.list_products().select_related("product")

    # 5. Aplicar filtro de búsqueda
    if q:
        qs = qs.filter(
            Q(product__name__icontains=q) | # Buscar por nombre de producto
            Q(batch_code__icontains=q)      # Buscar por código de lote
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
    return render(request, 'main/product_batch_list.html', context)

@login_required
@permission_or_redirect('Products.view_batch','dashboard', 'No teni permiso')
def product_batch_view(request, id):
    batch = batch_service.get(id)
    return render(request, 'main/product_batch.html', {'b': batch})

@login_required
@permission_or_redirect('Products.add_batch','dashboard', 'No teni permiso')
def product_batch_create(request):
    form = batch_service.product_form_class()
    if request.method == 'POST':
        success, obj = batch_service.save_product_batch(request.POST)
        if success:
            return redirect('product_batch_list')
        else:
            return render(request, 'main/product_batch_create.html', {'form': obj})
    return render(request, 'main/product_batch_create.html', {'form': form})

@login_required
@permission_or_redirect('Products.change_batch','dashboard', 'No teni permiso')
def product_batch_update(request, id):
    if request.method == 'POST':
        success, obj = batch_service.update_product_batch(id, request.POST)
        if success:
            return redirect('product_batch_list')
    else:
        batch = batch_service.get(id)
        form = batch_service.product_form_class(instance=batch)
    return render(request, 'main/product_batch_update.html', {'form': form})

@login_required
@permission_or_redirect('Products.delete_batch','dashboard', 'No teni permiso')
def product_batch_delete(request, id):
    if request.method == 'GET':
        success = batch_service.delete_product_batch(id)
        if success:
            return redirect('product_batch_list')
    return redirect('product_batch_list') 

@login_required
@permission_or_redirect('Products.view_batch','dashboard', 'No teni permiso')
def raw_batch_list(request):
    
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
    allowed_sort_fields = ['raw_material__name', 'raw_material__supplier__name', 'batch_code']
    sort_by = request.GET.get('sort_by', 'batch_code') # Default: batch_code
    order = request.GET.get('order', 'asc')          # Default: asc

    # Validar que los campos y el orden sean correctos
    if sort_by not in allowed_sort_fields:
        sort_by = 'batch_code'
    if order not in ['asc', 'desc']:
        order = 'asc'
        
    order_by_field = f'-{sort_by}' if order == 'desc' else sort_by
    # ===================================

    # 4. Queryset base (¡quitamos el .order_by() de aquí!)
    qs = batch_service.list_raw_materials().select_related(
        "raw_material", 
        "raw_material__supplier"
    )

    # 5. Aplicar filtro de búsqueda
    if q:
        qs = qs.filter(
            Q(raw_material__name__icontains=q) | # "nombre"
            Q(batch_code__icontains=q) |         # "codigo"
            Q(raw_material__supplier__name__icontains=q) # "proveedor"
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
    return render(request, 'main/raw_batch_list.html', context)

@login_required
@permission_or_redirect('Products.view_batch','dashboard', 'No teni permiso')
def raw_batch_view(request, id):
    batch = batch_service.get(id)
    return render(request, 'main/raw_batch.html', {'b': batch})

@login_required
@permission_or_redirect('Products.add_batch','dashboard', 'No teni permiso')
def raw_batch_create(request):
    form = batch_service.raw_form_class()
    if request.method == 'POST':
        success, obj = batch_service.save_raw_batch(request.POST)
        if success:
            return redirect('raw_batch_list')
        else:
            return render(request, 'main/raw_batch_create.html', {'form': obj})
    return render(request, 'main/raw_batch_create.html', {'form': form})

@login_required
@permission_or_redirect('Products.change_batch','dashboard', 'No teni permiso')
def raw_batch_update(request, id):
    if request.method == 'POST':
        success, obj = batch_service.update_raw_batch(id, request.POST)
        if success:
            return redirect('raw_batch_list')
    else:
        batch = batch_service.get(id)
        form = batch_service.raw_form_class(instance=batch)
    return render(request, 'main/raw_batch_update.html', {'form': form})

@login_required
@permission_or_redirect('Products.delete_batch','dashboard', 'No teni permiso')
def raw_batch_delete(request, id):
    if request.method == 'GET':
        success = batch_service.delete_raw_batch(id)
        if success:
            return redirect('raw_batch_list')
    return redirect('raw_batch_list') 

#PRICEHISTORIESSSSSSS
@login_required
@permission_or_redirect('Products.change_pricehistories','dashboard', 'No teni permiso')
def price_histories_save(request, id):
    form = price_histories_service.form_class()
    if request.method == 'POST':
        product = product_service.get(id)
        data = {
            'product': product,
            'unit_price' : request.POST.get('unit_price'),
            'date' : request.POST.get('date'),
            'iva': request.POST.get('iva')
        }
        success, obj = price_histories_service.save(data)
        if success:
            return redirect('product_view', id)
        else:
            return render(request, 'main/product.html', {'p': product, 'form': obj})
    return render(request, 'main/product.html', {'p': product, 'form': form})







        