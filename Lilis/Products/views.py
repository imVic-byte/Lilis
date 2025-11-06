from django.shortcuts import render, redirect
from .services import CategoryService, ProductService, SupplierService, RawMaterialService, BatchService, PriceHistoriesService
from django.contrib.auth.decorators import login_required
from Main.decorator import permission_or_redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse
from Main.utils import generate_excel_response

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
    
    # 2. Obtener 'por página' (rango 1-10)
    default_per_page = 10
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except ValueError:
        per_page = default_per_page
    
    if per_page > 10 or per_page <= 0:
        per_page = default_per_page

    # 3. Obtener queryset base
    qs = category_service.list().order_by('name')

    # 4. Aplicar filtro de búsqueda
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q)
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
        "page_obj": page_obj,      # ¡Cambiamos 'categories' por 'page_obj'!
        "q": q,
        "per_page": per_page,
        "querystring": querystring,
        "total": qs.count(),
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
    
    # 2. Obtener 'por página' (rango 1-10)
    default_per_page = 10
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except ValueError:
        per_page = default_per_page
    
    if per_page > 10 or per_page <= 0:
        per_page = default_per_page

    # 3. Obtener queryset base
    # ¡Optimizamos con select_related para traer la categoría!
    qs = product_service.list().filter(is_active=True).select_related("category").order_by('name')

    # 4. Aplicar filtro de búsqueda
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(category__name__icontains=q) # Búsqueda en la FK
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
        "page_obj": page_obj,      # ¡Cambiamos 'products' por 'page_obj'!
        "q": q,
        "per_page": per_page,
        "querystring": querystring,
        "total": qs.count(),
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
            try:
                product = product_service.get(id)
                product.is_active = False
                product.save()
            except:
                pass

            return redirect('products_list')
        return redirect('products_list')

@login_required
@permission_or_redirect('Products.delete_products','dashboard', 'No teni permiso')
def export_products_excel(request):
    q = (request.GET.get("q") or "").strip()
    qs = product_service.list().filter(is_active=True).select_related("category").order_by('name')

    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(category__name__icontains=q)
        )
    
    qs_limit = request.GET.get("limit")
    if qs_limit:
        try:
            limit = int(qs_limit)
            if limit > 0:
                qs = qs[:limit] 
        except ValueError:
            pass 

    # --- 2. PREPARAR LOS DATOS PARA EL EXCEL ---
    headers = ["Nombre", "Categoría", "Stock", "Perecible", "Vencimiento"]
    data_rows = []
    
    for p in qs:
        is_perishable_str = "Sí" if p.is_perishable else "No"
        expiration_date_str = p.expiration_date.strftime("%d-%m-%Y") if p.expiration_date else "N/A"
        
        data_rows.append([
            p.name,
            p.category.name,
            p.quantity,
            is_perishable_str,
            expiration_date_str
        ])

    # --- 3. LLAMAR A LA FUNCIÓN UTILITARIA ---
    return generate_excel_response(headers, data_rows, "Lilis_Productos")


#SUPPLIERRRR
@login_required
@permission_or_redirect('Products.view_supplier','dashboard', 'No teni permiso')
def supplier_list(request):
    
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
    qs = supplier_service.list().order_by('fantasy_name')

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

    # 6. Preparar querystring
    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()

    # 7. Preparar contexto
    context = {
        "page_obj": page_obj,      # ¡Cambiamos 'suppliers' por 'page_obj'!
        "q": q,
        "per_page": per_page,
        "querystring": querystring,
        "total": qs.count(),
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
    
    # 2. Obtener 'por página' (rango 1-10)
    default_per_page = 10
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except ValueError:
        per_page = default_per_page
    
    if per_page > 10 or per_page <= 0:
        per_page = default_per_page

    # 3. Obtener queryset base (mantenemos list_actives())
    # ¡Optimizamos con select_related para traer proveedor y categoría!
    qs = raw_material_service.list_actives().select_related(
        "supplier", 
        "category"
    ).order_by('name')

    # 4. Aplicar filtro de búsqueda
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(supplier__fantasy_name__icontains=q) |
            Q(category__name__icontains=q)
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
        "page_obj": page_obj,      # ¡Cambiamos 'raw_materials' por 'page_obj'!
        "q": q,
        "per_page": per_page,
        "querystring": querystring,
        "total": qs.count(),
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
    
    # 2. Obtener 'por página' (rango 1-10)
    default_per_page = 10
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except ValueError:
        per_page = default_per_page
    
    if per_page > 10 or per_page <= 0:
        per_page = default_per_page

    # 3. Obtener queryset base
    # ¡Optimizamos con select_related para traer el producto!
    qs = batch_service.list_products().select_related("product").order_by('batch_code')

    # 4. Aplicar filtro de búsqueda
    if q:
        qs = qs.filter(
            Q(product__name__icontains=q) | # Buscar por nombre de producto
            Q(batch_code__icontains=q)      # Buscar por código de lote
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
        "page_obj": page_obj,      # ¡Cambiamos 'batches' por 'page_obj'!
        "q": q,
        "per_page": per_page,
        "querystring": querystring,
        "total": qs.count(),
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
    
    # 2. Obtener 'por página' (rango 1-10)
    default_per_page = 10
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except ValueError:
        per_page = default_per_page
    
    if per_page > 10 or per_page <= 0:
        per_page = default_per_page

    # 3. Obtener queryset base
    # ¡Optimizamos con select_related para traer materia prima y proveedor!
    qs = batch_service.list_raw_materials().select_related(
        "raw_material", 
        "raw_material__supplier"
    ).order_by('batch_code')

    # 4. Aplicar filtro de búsqueda
    if q:
        qs = qs.filter(
            Q(raw_material__name__icontains=q) | # "nombre"
            Q(batch_code__icontains=q) |         # "codigo"
            Q(raw_material__supplier__name__icontains=q) # "proveedor"
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
        "page_obj": page_obj,      # ¡Cambiamos 'batches' por 'page_obj'!
        "q": q,
        "per_page": per_page,
        "querystring": querystring,
        "total": qs.count(),
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

