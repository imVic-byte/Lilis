from django.shortcuts import render, redirect
from .services import CategoryService, ProductService, SupplierService, RawMaterialService
from django.contrib.auth.decorators import login_required
from Main.decorator import permission_or_redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from Main.utils import generate_excel_response

category_service = CategoryService()
product_service = ProductService()
supplier_service = SupplierService()
raw_material_service = RawMaterialService()

@login_required
@permission_or_redirect('Products.view_product','dashboard', 'No teni permiso')
def product_search(request):
    q = request.GET.get('q', '')
    products = product_service.model.objects.filter( is_active=True ).filter(
        Q(name__icontains=q)
    ).values('id', 'name', 'description', 'category__name', 'quantity', 'is_perishable')    
    return JsonResponse(list(products), safe=False)

@login_required
@permission_or_redirect('Products.view_category','dashboard', 'No teni permiso')
def category_list(request):
    
    q = (request.GET.get("q") or "").strip()
    
    default_per_page = 25
    
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except ValueError:
        per_page = default_per_page
    
    if per_page > 101 or per_page <= 0:
        per_page = default_per_page
    allowed_sort_fields = ['name', 'description']
    sort_by = request.GET.get('sort_by', 'name')
    order = request.GET.get('order', 'asc')

    if sort_by not in allowed_sort_fields:
        sort_by = 'name'
    if order not in ['asc', 'desc']:
        order = 'asc'
        
    order_by_field = f'-{sort_by}' if order == 'desc' else sort_by
    qs = category_service.list()

    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q)
        )
    qs = qs.order_by(order_by_field)

    paginator = Paginator(qs, per_page)
    page_number = request.GET.get
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
    return render(request, 'products/category_list.html', context)

@login_required
@permission_or_redirect('Products.add_category','dashboard', 'No teni permiso')
def category_create(request):
    form = category_service.form_class()
    if request.method == 'POST':
        success, obj = category_service.save(request.POST)
        if success:
            return redirect('category_list')
        else:
            return render(request, 'products/category_create.html', {'form': obj})
    return render(request, 'products/category_create.html', {'form': form})


@login_required
@permission_or_redirect('Products.change_category','dashboard', 'No teni permiso')
def category_update(request, id):
    if request.method == 'POST':
        success, obj = category_service.update(id, request.POST)
        if success:
            return redirect('category_list')
        else:
            return render(request, 'products/category_update.html', {'form': obj})
    else:
        category = category_service.get(id)
        form = category_service.form_class(instance=category)
    return render(request, 'products/category_update.html', {'form': form})

@login_required
@permission_or_redirect('Products.delete_category','dashboard', 'No teni permiso')
def category_delete(request, id):
    if request.method == 'GET':
        success = category_service.delete(id)
        if success:
            return redirect('category_list')
    return redirect('category_list') 

@login_required
@permission_or_redirect('Products.view_product','dashboard', 'No teni permiso')
def export_categories_excel(request):
    q = (request.GET.get("q") or "").strip()
    qs = category_service.list().order_by('name')

    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q)
        )

    qs_limit = request.GET.get("limit")
    if qs_limit:
        try:
            limit = int(qs_limit)
            if limit > 0:
                qs = qs[:limit] 
        except ValueError:
            pass

    headers = ["Nombre", "Descripción"]
    data_rows = []

    for c in qs:
        data_rows.append([
            c.name,
            c.description
        ])

    return generate_excel_response(headers, data_rows, "Lilis_Categorias")


@login_required
@permission_or_redirect('Products.view_product','dashboard', 'No teni permiso')
def products_list(request):
    q = (request.GET.get("q") or "").strip()
    default_per_page = 25
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except ValueError:
        per_page = default_per_page
    
    if per_page > 101 or per_page <= 0:
        per_page = default_per_page

    allowed_sort_fields = ['name', 'category__name', 'sku']
    sort_by = request.GET.get('sort_by', 'name')
    order = request.GET.get('order', 'asc')

    if sort_by not in allowed_sort_fields:
        sort_by = 'name'
    if order not in ['asc', 'desc']:
        order = 'asc'
        
    order_by_field = f'-{sort_by}' if order == 'desc' else sort_by

    qs = product_service.list().filter(is_active=True).select_related("category").order_by('name')

    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q)|
            Q(sku__icontains=q)
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
    return render(request, 'products/products_list.html', context)

@login_required
@permission_or_redirect('Products.view_product','dashboard', 'No teni permiso')
def product_view(request, id):
    product = product_service.get(id)
    return render(request, 'products/product.html', {'p': product})

@login_required
@permission_or_redirect('Products.add_product','dashboard', 'No teni permiso')
def product_create(request):
    form = product_service.form_class()
    if request.method == 'POST':
        success, obj = product_service.save(request.POST)
        if success:
            return redirect('products_list')
        else:
            return render(request, 'products/product_create.html', {'form': obj})
    return render(request, 'products/product_create.html', {'form': form})


@login_required
@permission_or_redirect('Products.change_product','dashboard', 'No teni permiso')
def product_update(request, id):
    if request.method == 'POST':
        success, obj = product_service.update(id, request.POST)
        if success:
            return redirect('products_list')
        else:
            return render(request, 'products/product_update.html', {'form': obj})
    else:
        product = product_service.get(id)
        form = product_service.form_class(instance=product)
    return render(request, 'products/product_update.html', {'form': form})

@login_required
@permission_or_redirect('Products.delete_product','dashboard', 'No teni permiso')
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
@permission_or_redirect('Products.view_product','dashboard', 'No teni permiso')
def export_product_excel(request):
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

    headers = ["Nombre", "Categoría", "Stock", "Perecible", "Creación", "Vencimiento"]
    data_rows = []
    
    for p in qs:
        is_perishable_str = "Sí" if p.is_perishable else "No"
        creation_date_str = p.created_at.strftime("%d-%m-%Y") if p.created_at else "N/A"
        expiration_date_str = p.expiration_date.strftime("%d-%m-%Y") if p.expiration_date else "N/A"
        
        data_rows.append([
            p.name,
            p.category.name,
            p.quantity,
            is_perishable_str,
            creation_date_str,
            expiration_date_str
        ])

    return generate_excel_response(headers, data_rows, "Lilis_Productos")


@login_required
@permission_or_redirect('Products.view_supplier','dashboard', 'No teni permiso')
def supplier_search(request):
    q = request.GET.get('q', '')
    suppliers = supplier_service.model.objects.filter( is_active=True ).filter(
        Q(bussiness_name__icontains=q) |
        Q(fantasy_name__icontains=q) |
        Q(rut__icontains=q)
    ).values('bussiness_name', 'email', 'fantasy_name', 'id', 'is_active', 'phone', 'rut', 'trade_terms')
    return JsonResponse(list(suppliers), safe=False)

@login_required
@permission_or_redirect('Products.view_supplier','dashboard', 'No teni permiso')
def supplier_view(request, id):
    supplier = supplier_service.get(id)
    raw_materials = raw_material_service.list().filter(supplier=supplier)
    return render(request, 'suppliers/supplier_view.html', {'p': supplier,'raw_materials': raw_materials})

@login_required
@permission_or_redirect('Products.view_supplier','dashboard', 'No teni permiso')
def supplier_list(request):
    q = (request.GET.get("q") or "").strip()
    default_per_page = 25
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except ValueError:
        per_page = default_per_page
    
    if per_page > 101 or per_page <= 0:
        per_page = default_per_page

    allowed_sort_fields = ['fantasy_name', 'bussiness_name', 'rut', 'email', 'phone']
    sort_by = request.GET.get('sort_by', 'fantasy_name')
    order = request.GET.get('order', 'asc')

    if sort_by not in allowed_sort_fields:
        sort_by = 'fantasy_name'
    if order not in ['asc', 'desc']:
        order = 'asc'
        
    order_by_field = f'-{sort_by}' if order == 'desc' else sort_by

    qs = supplier_service.list_actives()

    if q:
        qs = qs.filter(
            Q(fantasy_name__icontains=q) |
            Q(bussiness_name__icontains=q) |
            Q(rut__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q) |
            Q(trade_terms__icontains=q)
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
    return render(request, 'suppliers/supplier_list.html', context)

@login_required
@permission_or_redirect('Products.add_supplier','dashboard', 'No teni permiso')
def supplier_create(request):
    form = supplier_service.form_class()
    if request.method == 'POST':
        success, obj = supplier_service.save(request.POST)
        if success:
            return redirect('supplier_list')
        else:
            return render(request, 'suppliers/supplier_create.html', {'form': obj})
    return render(request, 'suppliers/supplier_create.html', {'form': form})

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
    return render(request, 'suppliers/supplier_update.html', {'form': form})

@login_required
@permission_or_redirect('Products.delete_supplier','dashboard', 'No teni permiso')
def supplier_delete(request, id):
    if request.method == 'GET':
        success, obj = supplier_service.make_inactive(id)
        if success:
            return redirect('supplier_list')
    return redirect('supplier_list')

@login_required
@permission_or_redirect('Products.view_supplier','dashboard', 'No teni permiso')
def export_suppliers_excel(request):
    q = (request.GET.get("q") or "").strip()
    qs = supplier_service.list().order_by('fantasy_name')
    if q:
        qs = qs.filter(
            Q(fantasy_name__icontains=q) |
            Q(bussiness_name__icontains=q) |
            Q(rut__icontains=q) |
            Q(email__icontains=q) |
            Q(phone__icontains=q) |
            Q(trade_terms__icontains=q)
        )
    qs_limit = request.GET.get("limit")
    if qs_limit:
        try:
            limit = int(qs_limit)
            if limit > 0:
                qs = qs[:limit] 
        except ValueError:
            pass
    headers = ["Nombre Fantasía", "Razón Social", "RUT", "Email", "Teléfono", "Términos"]
    data_rows = []
    for s in qs:
        data_rows.append([
            s.fantasy_name,
            s.bussiness_name,
            s.rut,
            s.email,
            s.phone,
            s.trade_terms
        ])
    return generate_excel_response(headers, data_rows, "Lilis_Proveedores")

@login_required
@permission_or_redirect('Products.view_rawmaterial','dashboard', 'No teni permiso')
def raw_material_list(request):
    q = (request.GET.get("q") or "").strip()
    default_per_page = request.user.profile.per_page
    try:
        per_page = int(request.GET.get("per_page", default_per_page))
    except ValueError:
        per_page = default_per_page
    if per_page > 101 or per_page <= 0:
        per_page = default_per_page
    allowed_sort_fields = ['name', 'supplier__fantasy_name']
    sort_by = request.GET.get('sort_by', 'name')
    order = request.GET.get('order', 'asc')
    if sort_by not in allowed_sort_fields:
        sort_by = 'name'
    if order not in ['asc', 'desc']:
        order = 'asc'
        
    order_by_field = f'-{sort_by}' if order == 'desc' else sort_by
    qs = raw_material_service.list_actives()
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(supplier__fantasy_name__icontains=q)
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
    return render(request, 'raw_material/raw_material_list.html', context)

@login_required
@permission_or_redirect('Products.view_rawmaterial','dashboard', 'No teni permiso')
def raw_material_search(request):
    q = request.GET.get('q', '')
    raw_materials = raw_material_service.model.objects.filter( is_active=True ).filter(
        Q(name__icontains=q) |
        Q(description__icontains=q)
    ).values(
        'id', 'name', 'description','supplier', 'category__name', 'quantity', 'is_perishable', 'created_at', 'expiration_date', 'category', 'is_active'
    )
    return JsonResponse(list(raw_materials), safe=False)

@login_required
@permission_or_redirect('Products.view_rawmaterial','dashboard', 'No teni permiso')
def raw_material_view(request, id):
    raw_material = raw_material_service.get(id)
    return render(request, 'raw_material/raw_material_view.html', {'p': raw_material})

@login_required()
@permission_or_redirect('Products.add_rawmaterial','dashboard', 'No teni permiso')
def raw_material_create(request):
    supplier = supplier_service.get(request.GET.get('supplier'))
    form = raw_material_service.form_class()
    if request.method == 'POST':
        if not supplier:
            success, obj = raw_material_service.save(request.POST)
            if success:
                return redirect('raw_material_list')
            else:
                render(request, 'raw_material/raw_material_create.html', {'form': obj})
        else:
            data = {
                'name': request.POST.get('name'),
                'description': request.POST.get('description'),
                'sku': request.POST.get('sku'),
                'expiration_date': request.POST.get('expiration_date'),
                'is_perishable': request.POST.get('is_perishable'),
                'supplier': supplier,
                'category': request.POST.get('category'),
                'measurement_unit': request.POST.get('measurement_unit'),
            }
            success, obj = raw_material_service.save_raw_material_class(data, supplier)
            if success:
                next = request.GET.get('next')
                return redirect(next)
            else:
                return render(request, 'raw_material/raw_material_create_class.html', {'form': obj, 'supplier': supplier.id})
    if not supplier:
        return render(request, 'raw_material/raw_material_create.html', {'form': form})
    return render(request, 'raw_material/raw_material_create.html', {'form': form, 'supplier': supplier.id})

@login_required()
@permission_or_redirect('Products.add_rawmaterial','dashboard', 'No teni permiso')
def raw_material_update(request, id):
    supplier = supplier_service.get(request.GET.get('supplier'))
    next = request.GET.get('next')
    instance = raw_material_service.get(id)
    form = raw_material_service.form_class(instance=instance)
    if request.method == 'POST':
        success, obj = raw_material_service.update(id, request.POST)
        if success and next:
            next = request.GET.get('next')
            return redirect(next)
        elif success and not next:
            return redirect('raw_material_list')
        elif not success and supplier:
            return render(request, 'raw_material/raw_material_update.html', {'form': obj, 'supplier': supplier.id})
        else:
            return render(request, 'raw_material/raw_material_update.html', {'form': obj})
    else:
        raw_material = raw_material_service.get(id)
        form = raw_material_service.form_class(instance=raw_material)
    if not supplier:
        return render(request, 'raw_material/raw_material_update.html', {'form': form})
    return render(request, 'raw_material/raw_material_update.html', {'form': form, 'supplier': supplier.id})

@login_required()
@permission_or_redirect('Products.delete_rawmaterial','dashboard', 'No teni permiso')
def raw_material_delete(request, id):
    next = request.GET.get('next')
    if request.method == 'GET':
        if next:
            success = raw_material_service.delete(id)
            if success:
                return redirect(next)
        else:
            success = raw_material_service.delete(id)
            if success:
                return redirect('raw_material_list')
    return redirect('raw_material_list')

@login_required
@permission_or_redirect('Products.view_rawmaterial','dashboard', 'No teni permiso')
def export_raw_materials_excel(request):
    q = (request.GET.get("q") or "").strip()
    qs = raw_material_service.list_actives().select_related(
        "supplier", 
        "category"
    ).order_by('name')

    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(supplier__fantasy_name__icontains=q) |
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

    headers = ["Nombre", "Proveedor", "Categoría", "Perecible", 'Unidad de medida']
    data_rows = []
    
    for rm in qs:
        data_rows.append([
            rm.name,
            rm.supplier.fantasy_name,
            rm.category.name,
            "Sí" if rm.is_perishable else "No",
            rm.measurement_unit,
        ])
    return generate_excel_response(headers, data_rows, "Lilis_Materias_Primas")
