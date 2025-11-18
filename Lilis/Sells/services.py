from django.shortcuts import render
from Main.CRUD import CRUD
from .models import Client, Location, Warehouse, WareClient, Transaction, SaleOrder, SaleOrderDetail
from .forms import TransactionForm,ClientForm, LocationForm, WarehouseForm,  SaleOrderForm, SaleOrderDetailForm
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
    
    def filter_by_supplier(self, supplier):
        wareclients = self.wareclient_model.objects.filter(client=supplier)
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
        self.form_class = TransactionForm

    def create_transaction(self, data):
        warehouse_service = WarehouseService()
        client_service = ClientService()
        product_service = ProductService()
        batch_service = BatchService()
        raw_material_service = RawMaterialService()
        data['warehouse'] = warehouse_service.get(data['warehouse'])
        data['client'] = client_service.get(data['client'])
        type_ = data['type']
        is_salida = type_ == 'salida'
        is_ingreso = type_ == 'ingreso'
        is_devolucion = type_ == 'devolucion'
        is_lote = bool(data['batch_code'])
        code = data['batch_code'] if is_lote else data['serie_code']
        try:
            data['quantity'] = float(data['quantity'])
        except (ValueError, TypeError):
            return False, None
        if is_salida:
            tipo, id = data['product'].split('-')
            product = product_service.get(id)
            data['product'] = product
            data['raw_material'] = None
        elif is_ingreso:
            tipo, id = data['raw_material'].split('-')
            raw_material_class = raw_material_service.raw_material_class.objects.get(id=id)
            raw_data = {
                'raw_material_class': raw_material_class,
                'expiration_date': data['expiration_date'],
                'created_at': data['date'],
                'quantity': data['quantity'],
            }
            raw = raw_material_service.model.objects.create(**raw_data)
            data['raw_material'] = raw
            data['product'] = None
        else:
            if data['product']:
                tipo, id = data['product'].split('-')
                product = product_service.get(id)
                data['product'] = product
                data['raw_material'] = None
            else:
                tipo, id = data['raw_material'].split('-')
                raw_material_class = raw_material_service.raw_material_class.objects.get(id=id)
                data['raw_material'] = raw_material_class
                data['product'] = None 
        batch = batch_service.model.objects.create(
            product=data.get('product'),
            raw_material=data.get('raw_material'),
            batch_code=code,
            current_quantity=data['quantity'],
            serie=not is_lote
        )
        transaction = self.model.objects.create(**data)
        if not transaction:
            return False, None
        if is_salida:
            self.discount_stock(transaction, batch)
        elif is_ingreso or is_devolucion:
            self.increase_stock(transaction, batch)
        return True, transaction

    def get_by_warehouse(self, warehouse_id):
        return self.model.objects.filter(warehouse=warehouse_id)
    
    def get_by_client(self, client_id):
        return self.model.objects.filter(client=client_id)
    
    def discount_stock(self, transaction, batch):
        product = transaction.product or transaction.raw_material
        if not product or not batch:
            return False, None

        product_stock = Decimal(product.quantity)
        batch_stock = Decimal(batch.current_quantity)

        product_stock -= batch_stock
        product.quantity = product_stock
        product.save()

        return True, product


    def increase_stock(self, transaction, batch):
        product = transaction.raw_material or transaction.product
        if not product or not batch:
            return False, None

        product_stock = Decimal(product.quantity)
        batch_stock = Decimal(batch.current_quantity)

        product_stock += batch_stock
        product.quantity = product_stock
        product.save()

        return True, product
    
    def validate_code(self, code):
        if self.model.objects.filter(serie_code=code).count() > 0:
            return False
        if self.model.objects.filter(batch_code=code).count() > 0:
            return False
        return True