from django.shortcuts import render, redirect
from .services import CategoryService, ProductService, SupplierService, RawMaterialService, BatchService, PriceHistoriesService
from django.contrib.auth.decorators import login_required, permission_required
from Main.decorator import permission_or_redirect

category_service = CategoryService()
product_service = ProductService()
supplier_service = SupplierService()
raw_material_service = RawMaterialService()
batch_service = BatchService()
price_histories_service = PriceHistoriesService()

@login_required
@permission_or_redirect('Products.view_category','dashboard', 'No teni permiso')
def category_list(request):
    categories = category_service.list()
    return render(request, 'main/category_list.html', {'categories': categories})

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
    products = product_service.list()
    return render(request, 'main/products_list.html', {'products': products})

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
def supplier_list(request):
    suppliers = supplier_service.list()
    return render(request, 'main/supplier_list.html', {'suppliers': suppliers})

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
    raw_materials = raw_material_service.list_actives()
    return render(request, 'main/raw_material_list.html', {'raw_materials': raw_materials})

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
    batches = batch_service.list_products()
    return render(request, 'main/product_batch_list.html', {'batches': batches})

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
    batches = batch_service.list_raw_materials()
    return render(request, 'main/raw_batch_list.html', {'batches': batches})

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







        