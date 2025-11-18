from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from Accounts.services import UserService
from Products.services import SupplierService, ProductService
from Sells.services import ClientService, TransactionService

user_service = UserService()
supplier_service = SupplierService()
product_service = ProductService()
client_service = ClientService()
transaction_service = TransactionService()


@login_required
def dashboard(request):
    usuarios = user_service.count()
    proveedores_activos = supplier_service.count_actives()
    proveedores = supplier_service.count()
    productos = product_service.count()
    clientes_activos = client_service.count_actives()
    clientes= client_service.count()
    transacciones = transaction_service.list().order_by('-date')[:5]
    return render(request, 'main/dashboard.html',
                  {
                      'productos': productos,
                      'proveedores_activos': proveedores_activos,
                      'proveedores': proveedores,
                      'usuarios': usuarios,
                      'clientes_activos': clientes_activos,
                      'clientes': clientes,
                      'transacciones': transacciones
                  })