from django.shortcuts import render
from Main.CRUD import CRUD
from .models import Client, Location, Warehouse, WareClient, Transaction, SaleOrder, SaleOrderDetail
from .forms import ClientForm, LocationForm, WarehouseForm,  SaleOrderForm, SaleOrderDetailForm
import datetime
from Products.services import ProductService, BatchService, RawMaterialService
from decimal import Decimal

class ClientService(CRUD):  
    def __init__(self):
        self.model = Client
        self.form_class = ClientForm

    def search_by_rut(self, rut):
        return self.model.objects.filter(rut=rut)
    
    def search_by_trade_terms(self, trade_terms):
        return self.model.objects.contains(trade_terms)
    
    def list_actives(self):
        return self.model.objects.filter(is_suspended=False)
    
    def list_suspended(self):
        return self.models.objects.filter(is_suspended=True)
    
    def to_suspend(self, id):
        client = self.model.objects.get(id=id)
        if client:
            client.is_suspended = True
            client.save()
            return True, client
        return False, client
    
    def reinstate(self, id):
        client = self.model.objects.get(id=id)
        if client:
            client.is_suspended = False
            client.save()
            return True, client
        return False, client
    
    def count_actives(self):
        return self.model.objects.filter(is_suspended=False).count()
    
    def count_suspended(self):
        return self.model.objects.filter(is_suspended=True).count()

class WarehouseService(CRUD):
    def __init__(self):
        self.model = Warehouse
        self.wareclient_model = WareClient
        self.location_model = Location
        self.form_class = WarehouseForm
        self.location_form_class = LocationForm
    
    def filter_by_client(self, client):
        wareclients = self.wareclient_model.objects.filter(client=client)
        warehouses = []
        if wareclients:
            for w in wareclients:
                warehouses.append(w.warehouse)
            return warehouses
        return []
    
    def warehouse_assign(self, client, warehouse_id):
        warehouse = self.model.objects.get(id=warehouse_id)
        if warehouse:
            wareclient = self.wareclient_model.objects.create(client=client, warehouse=warehouse, status='A', association_date=datetime.datetime.today())
            return True, wareclient
        return False, None
    
    def warehouse_unassign(self,client_id, warehouse_id):
        wareclient = self.wareclient_model.objects.get(client=client_id, warehouse=warehouse_id)
        if wareclient:
            wareclient.delete()
            warehouse = self.model.objects.get(id=warehouse_id)
            warehouse.delete()
            return True, warehouse
        return False, None

    
    
class SaleOrderService(CRUD):
    def __init__(self):
        self.model = SaleOrder
        self.detail_model = SaleOrderDetail
        self.form_class = SaleOrderForm
        self.detail_form_class = SaleOrderDetailForm

    def add_detail(self, saleorder_id, detail):
        saleorder = self.model.objects.get(id=saleorder_id)
        if saleorder:
            detail = self.detail_model.objects.create(saleorder=saleorder, product=detail['product'], quantity=detail['quantity'], price=detail['price'], total=detail['total'])
            return True, detail
        return False, None
    
    def remove_detail(self, detail_id):
        detail = self.detail_model.objects.get(id=detail_id)
        if detail:
            detail.delete()
            return True, detail
        return False, None
    
    def update_detail(self, detail_id, data):
        detail = self.detail_model.objects.get(id=detail_id)
        if detail:
            form = self.detail_form_class(data, instance=detail)
            if form.is_valid():
                form.save()
                return True, form
            return False, form
        
    def get_pending_orders(self):
        return self.model.objects.filter(status='P')
    
    def get_confirmed_orders(self):
        return self.model.objects.filter(status='C')
    
    def get_cancelled_orders(self):
        return self.model.objects.filter(status='A')
    
    def confirm_order(self, order_id):
        order = self.model.objects.get(id=order_id)
        if order:
            order.status = 'C'
            order.save()
            return True, order
        return False, None
    
    def cancel_order(self, order_id):
        order = self.model.objects.get(id=order_id)
        if order:
            order.status = 'A'
            order.save()
            return True, order
        return False, None
    
    def get_by_client(self, client_id):
        return self.model.objects.filter(client=client_id)

class TransactionService(CRUD):
    def __init__(self):
        self.model = Transaction

    def create_transaction(self, data):
        warehouse_service = WarehouseService()
        client_service = ClientService()
        product_service = ProductService()
        batch_service = BatchService()
        raw_material_service = RawMaterialService()
        warehouse = warehouse_service.get(data['warehouse'])
        client = client_service.get(data['client'])
        data['warehouse'] = warehouse
        data['client'] = client
        if data['type'] == 'salida' and data['batch_code']:
            product = product_service.get(data['product'])
            data['product'] = product
            batch = batch_service.model.objects.create(product=product, raw_material=None, batch_code=data['batch_code'], current_quantity=data['quantity'])
            transaction = self.model.objects.create(**data)
            if transaction:
                self.discount_stock(transaction, batch)
                return True, transaction
            return False, None
        elif data['type'] == 'ingreso' and data['batch_code']:
            product = raw_material_service.get(data['product'])
            data['raw_material'] = product
            data['product'] = None
            batch = batch_service.model.objects.create(product=None , raw_material=product, batch_code=data['batch_code'], current_quantity=data['quantity'])
            transaction = self.model.objects.create(**data)
            if transaction:
                self.increase_stock(transaction, batch)
                return True, transaction
            return False, None
        elif data['type'] == 'salida' and data['batch_code'] == None:
            product = product_service.get(data['product'])
            data['product'] = product
            batch = batch_service.model.objects.create(product=product, raw_material=None, batch_code=data['serie_code'], current_quantity=data['quantity'], serie=True)
            transaction = self.model.objects.create(**data)
            if transaction:
                self.discount_stock(transaction, batch)
                return True, transaction
            return False, None
        elif data['type'] == 'ingreso' and data['batch_code'] == None:
            product = raw_material_service.get(data['product'])
            data['raw_material'] = product
            data['product'] = None
            batch = batch_service.model.objects.create(product=None , raw_material=product, batch_code=data['serie_code'], current_quantity=data['quantity'], serie=True)
            transaction = self.model.objects.create(**data)
            if transaction:
                self.increase_stock(transaction, batch)
                return True, transaction
            return False, None
        else:
            return False, None

    def get_by_warehouse(self, warehouse_id):
        return self.model.objects.filter(warehouse=warehouse_id)
    
    def get_by_client(self, client_id):
        return self.model.objects.filter(client=client_id)
    
    def discount_stock(self, transaction, batch):
        product = transaction.product
        if product:
            product_stock = product.quantity
            if batch:
                batch_stock = batch.current_quantity
                product_stock -= Decimal(batch_stock)
                product.quantity = product_stock
                product.save()
                return True, product
            return False, None
        return False, None

    def increase_stock(self, transaction, batch):
        product = transaction.raw_material
        if product:
            product_stock = product.quantity
            if batch:
                product_stock += batch.current_quantity
                product.quantity = Decimal(product_stock)
                product.save()
                return True, product
            return False, None
        return False, None
    
    def validate_code(self, code):
        if self.model.objects.filter(serie_code=code).count() > 0:
            return False
        if self.model.objects.filter(batch_code=code).count() > 0:
            return False
        return True