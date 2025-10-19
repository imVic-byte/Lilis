from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from .services import ClientService, WarehouseService, SaleOrderService, TransactionService

client_service = ClientService()
warehouse_service = WarehouseService()
sale_order_service = SaleOrderService()
transaction_service = TransactionService()

#CLIENTESSS
def client_list_all(request):
    clients = client_service.list()
    return render(request, 'sells/client_list.html', {'clients': clients})

def client_list_actives(request):
    clients = client_service.list_actives()
    return render(request, 'sells/client_list.html', {'clients': clients})

def client_list_inactives(request):
    clients = client_service.list_inactives()
    return render(request, 'sells/client_list.html', {'clients': clients})

def client_view(request, id):
    if request.method == 'GET':
        client = client_service.get(id)
        return render(request, 'sells/client_view.html', {'b': client})
    else:
        return redirect('client_list_actives')

def client_create(request):
    form = client_service.form_class()
    if request.method == 'POST':
        success, obj = client_service.save(request.POST)
        if success:
            return redirect('client_list_actives')
        else:
            return render(request, 'sells/client_create.html', {'form': obj})
    return render(request, 'sells/client_create.html', {'form': form})

def client_update(request, id):
    if request.method == 'POST':
        success, obj = client_service.update(id, request.POST)
        if success:
            return redirect('client_list_actives')
        else:
            return render(request, 'sells/client_update.html', {'form': obj})
    else:
        client = client_service.get(id)
        form = client_service.form_class(instance=client)
    return render(request, 'sells/client_update.html', {'form': form})
    
def client_delete(request, id):
    if request.method == 'GET':
        success = client_service.delete(id)
        if success:
            return redirect('client_list_actives')
    return redirect('client_list_actives')

#LOCATIONS
def location_list(request):
    locations = warehouse_service.location_model.objects.all()
    return render(request, 'warehouse_list.html', {'locations': locations})

def location_view(request, id):
    if request.method == 'GET':
        location = warehouse_service.location_model.objects.get(id=id)
        return render(request, 'warehouse_view.html', {'location': location})
    else:
        return redirect('list_locations')

def location_create(request):
    form = warehouse_service.location_form_class()
    if request.method == 'POST':
        success, obj = warehouse_service.create_location(request.POST)
        if success:
            return redirect('list_locations')
        else:
            return render(request, 'warehouse_create.html', {'form': obj})
    return render(request, 'warehouse_create.html', {'form': form})

def location_update(request, id):
    if request.method == 'POST':
        success, obj = warehouse_service.update_location(id, request.POST)
        if success:
            return redirect('list_locations')
        else:
            return render(request, 'warehouse_update.html', {'form': obj})
    else:
        location = warehouse_service.location_model.objects.get(id=id)
        form = warehouse_service.location_form_class(instance=location)
    return render(request, 'warehouse_update.html', {'form': form})

def location_delete(request, id):
    if request.method == 'GET':
        success = warehouse_service.delete_location(id)
        if success:
            return redirect('list_locations')
    return redirect('list_locations')

##warehouses
def warehouse_list(request):
    warehouses = warehouse_service.model.objects.all()
    return render(request, 'warehouse_list.html', {'warehouses': warehouses})

def warehouse_view(request, id):
    if request.method == 'GET':
        warehouse = warehouse_service.model.objects.get(id=id)
        return render(request, 'warehouse_view.html', {'warehouse': warehouse})
    else:
        return redirect('list_warehouses')

def warehouse_create(request):
    form = warehouse_service.form_class()
    if request.method == 'POST':
        success, obj = warehouse_service.save(request.POST)
        if success:
            return redirect('list_warehouses')
        else:
            return render(request, 'warehouse_create.html', {'form': obj})
    return render(request, 'warehouse_create.html', {'form': form})

def warehouse_update(request, id):
    if request.method == 'POST':
        success, obj = warehouse_service.update(id, request.POST)
        if success:
            return redirect('list_warehouses')
        else:
            return render(request, 'warehouse_update.html', {'form': obj})
    else:
        warehouse = warehouse_service.model.objects.get(id=id)
        form = warehouse_service.form_class(instance=warehouse)
    return render(request, 'warehouse_update.html', {'form': form})

def warehouse_delete(request, id):
    if request.method == 'GET':
        success = warehouse_service.delete(id)
        if success:
            return redirect('list_warehouses')
    return redirect('list_warehouses')

###