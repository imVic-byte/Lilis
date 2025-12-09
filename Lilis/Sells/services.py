from django.shortcuts import render
from Main.CRUD import CRUD
from .models import Client, Warehouse, WareClient
from Products.models import Transaction, Inventario, Lote, Serie, TransactionDetail
from .forms import LoteProductoForm,TransactionForm,ClientForm, WarehouseForm
from Products.models import RawMaterialClass, Producto
from Products.services import ProductService,RawMaterialService
from decimal import Decimal
from django.db.models import Sum
from django.utils import timezone
import datetime
from django.db.models import Q
from django.db.models import F
from itertools import chain

LILIS_RUT = "2519135-8"


class ClientService(CRUD):  
    def __init__(self):
        self.model = Client
        self.form_class = ClientForm

    def search_by_rut(self, rut):
        return self.model.objects.filter(rut=rut)
    
    def search_by_trade_terms(self, trade_terms):
        return self.model.objects.contains(trade_terms)
    
    def list_actives(self):
        return self.model.objects.filter(is_active=True)
    
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
        return self.model.objects.filter(is_active=False).count()
    
    def count_suspended(self):
        return self.model.objects.filter(is_active=True).count()

class WarehouseService(CRUD):
    def __init__(self):
        self.model = Warehouse
        self.wareclient_model = WareClient
        self.form_class = WarehouseForm
    
    def filter_by_client(self, client):
        wareclients = self.wareclient_model.objects.filter(client=client)
        warehouses = []
        if wareclients:
            for w in wareclients:
                warehouses.append(w.warehouse)
            return warehouses
        return []
    
    def filter_by_rut(self, rut):
        wareclients = self.wareclient_model.objects.filter(client__rut=rut)
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
            wareclient = self.wareclient_model.objects.create(client=client, warehouse=warehouse,is_active=True, association_date=datetime.datetime.today())
            return True, wareclient
        return False, None
    
    def warehouse_unassign(self,client_id, warehouse_id):
        wareclient = self.wareclient_model.objects.get(client=client_id, warehouse=warehouse_id)
        if wareclient:
            wareclient.delete()
            return True, None
        return False, None

    def warehouse_list_without_this_client(self, id):
        warehouses = self.model.objects.filter(is_active=True)
        w_list = []
        for w in warehouses:
            if w.is_active == False:
                continue
            if not w.wareclients.exists():
                w_list.append(w)
            for wc in w.wareclients.all():
                if wc.client.id != id:
                    print(wc.client.id, "-", id)
                    w_list.append(w)
        return self.model.objects.exclude(wareclients__client_id=id)

    def delete_warehouse(self, warehouse):
        warehouse.wareclients.all().delete()
        warehouse.is_active = False
        warehouse.save()

class InventarioService(CRUD):
    def __init__(self):
        self.model = Inventario
        self.lote = Lote
        self.lote_form_class = LoteProductoForm
        self.raw_class = RawMaterialClass
        self.product_class = Producto
        self.serie = Serie
        self.bodegas = WarehouseService
    
    def actualizar_stock(inventario):
        lotes = inventario.lotes.all()
        stock_total = lotes.aggregate(stock_total=Sum('cantidad_actual'))['stock_total'] or 0
        series = inventario.series.all().filter(status='A')
        stock_total += series.count()
        inventario.stock_total = stock_total
        inventario.save()

    def crear_lote_entrada(self, data):
        if not data:
            return False, None
        lote = self.lote.objects.create(**data)
        self.actualizar_stock(lote.inventario)
        return True, lote
    
    def crear_serie_entrada(self, data):
        if not data:
            return False, None
        serie = self.serie.objects.create(**data)
        self.actualizar_stock(serie.inventario)
        return True, serie

    def consumir_series(self, producto, cantidad):
        resta = Decimal(cantidad)
        series = self.serie.objects.filter(producto=producto, status='A').order_by('-fecha_vencimiento')
        for s in series:
            if resta == 0:
                break
            s.status = 'I'
            s.save()
            resta -= 1
            self.actualizar_stock(s.inventario)
        if resta > 0:
            producto.deficit += resta
            producto.save()
        return True

    def consumir_lotes(self, producto, cantidad):
        resta = Decimal(cantidad)
        lotes = self.lote.objects.filter(producto=producto).order_by('-fecha_vencimiento')
        for l in lotes:
            if resta == 0:
                break
            if l.cantidad_actual == 0:
                continue
            if l.cantidad_actual >= resta:
                l.cantidad_actual -= resta
                l.save()
                self.actualizar_stock(l.inventario)
                return True
            resta -= l.cantidad_actual
            l.cantidad_actual = 0
            l.save()
            self.actualizar_stock(l.inventario)
        if resta > 0:
            producto.deficit += resta
            producto.save()
        return True
                
            
        
                
                    
    

    
    def list_actives(self):
        return (
            self.model.objects.filter(
                Q(producto__is_active=True) |
                Q(materia_prima__is_active=True)
            )
            .select_related("materia_prima", "producto", "bodega")
        )
    
class TransactionService(CRUD):
    def __init__(self):
        self.model = Transaction
        self.form_class = TransactionForm
        self.inventario = InventarioService()
        self.warehouse_service = WarehouseService()
        self.client_service = ClientService()
        self.product_service = ProductService()
        self.raw_material_service = RawMaterialService()
        self.transaction_detail = TransactionDetail

    def resolver(self, data):
        if data['type'] == 'ingreso':
            mp = self.inventario.raw_class.objects.get(id=data['product'])
            data['product'] = None
            data['raw_material'] = mp
            return None, mp
        if data['product']:
            tipo, id = data['product'].split('-')
            product = self.inventario.product_class.objects.get(id=id)
            data['product'] = product
            data['raw_material'] = None
            return product, None
        tipo, id = data['raw_material'].split('-')
        mp = self.inventario.raw_class.objects.get(materia_prima=id)
        data['product'] = None
        data['raw_material'] = mp
        return None, mp

    def create_transaction(self, request):
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
        type_ = data['type']
        data['warehouse'] = self.warehouse_service.get(data['warehouse'])
        try:
            data['client'] = self.client_service.get(data['client'])
        except:
            data['client'] = None
        try:
            cantidad = float(data['quantity'])
        except (ValueError, TypeError):
            return False, None
        if type_ != 'transferencia':
            producto, materia_prima = self.resolver(data)
        transaction_data = {
            'warehouse': data['warehouse'],
            'client': data['client'],
            'user': data['user'],
            'notes': data['notes'],
            'quantity': cantidad,
            'batch_code': data['batch_code'],
            'serie_code': data['serie_code'],
            'expiration_date': data['expiration_date'],
            'type': type_
        }
        transaction = self.model.objects.create(**transaction_data)
        if not transaction:
            return False, None
        if type_ == 'ingreso':
            ok, ingresos = self.procesar_ingreso(transaction, materia_prima, cantidad)
            if not ok:
                return False, None
        if type_ == 'salida':
            ok = self.inventario.procesar_salida(transaction,producto, cantidad)
            if not ok:
                return False, None
        if type_ == 'devolucion':
            ok = self.procesar_devolucion(transaction, producto, materia_prima, cantidad)
            if not ok:
                return False, None
        if type_ == 'transferencia':
            ok = self.procesar_transferencia(transaction, data['product'])
            if not ok:
                return False, None
        if type_ == 'produccion':
            if not producto:
                return False, None
            ok = self.procesar_produccion(transaction, producto, cantidad)
            if not ok:
                return False, None
        return True, transaction

    def procesar_transferencia(self, transaction, inventario):
        p, id = inventario.split('-')
        inv = self.inventario.get(id)
        ok, series, lote = self.inventario.transferir_lote(transaction, inv)
        if series:
            for i in series:
                detail_data = {
                    'transaction': transaction,
                    'code': i.codigo,
                    'batch': None,
                    'serie': i
                }
                self.crear_detalle_transaccion(detail_data)
        if lote:
            detail_data = {
                'transaction': transaction,
                'code': transaction.batch_code,
                'batch': lote,
                'serie': None
            }
            self.crear_detalle_transaccion(detail_data)
        return True, transaction

    def procesar_salida(self, transaction, producto, cantidad):
        ok = self.inventario.consumir_lotes(producto, cantidad)
        if not ok:
            return False, None
        return True, transaction

    def procesar_produccion(self, transaction, product, cantidad):
        if product:
            producto = self.inventario.product_class.objects.get(id=product.id)
            inventario = self.inventario.model.objects.get_or_create(materia_prima=None, producto=producto, bodega=transaction.warehouse)[0]
        if transaction.batch_code:
            data_lote = {
                'inventario': inventario,
                'cantidad_actual': cantidad,
                'fecha_creacion': timezone.localdate(),
                'fecha_expiracion': transaction.expiration_date,
                'origen': "devolucion"
            }
            ok, lote = self.inventario.crear_lote_entrada(data_lote)
            if not ok:
                return False, None
            self.inventario.actualizar_stock_total(inventario)
            detail_data = {
                'transaction': transaction,
                'code': transaction.batch_code,
                'batch': lote,
                'serie': None
            }
            return self.crear_detalle_transaccion(detail_data)
        else:
            detalles = []
            codigo = transaction.serie_code
            for i in range(int(cantidad)):
                code = codigo,'-',i+1
                data_serie = {
                    'codigo': code,
                    'inventario': inventario,
                    'estado': 'A',
                    'fecha_creacion': timezone.localdate(),
                    'fecha_expiracion': transaction.expiration_date,
                }
                ok, serie = self.inventario.crear_serie_entrada(data_serie)
                if not ok:
                    return False, None
                detail_data = {
                    'transaction': transaction,
                    'code': code,
                    'batch': None,
                    'serie': serie
                }
                ok, detalle = self.crear_detalle_transaccion(detail_data)
                if not ok:
                    return False, None
                detalles.append(detalle)
            self.inventario.actualizar_stock_total(inventario)
            return True, detalles
    
    def procesar_ingreso(self, transaction, materia_prima, cantidad):
        inventario = self.inventario.model.objects.get_or_create(materia_prima=materia_prima, producto=None, bodega=transaction.warehouse)[0]
        if transaction.batch_code:
            data_lote = {
                'inventario': inventario,
                'cantidad_actual': cantidad,
                'fecha_creacion': timezone.localdate(),
                'fecha_expiracion': transaction.expiration_date,
                'origen': "ingreso"
            }
            ok, lote = self.inventario.crear_lote_entrada(data_lote)
            if not ok:
                return False, None
            try:
                inventario.stock_total += Decimal(cantidad)
                inventario.save()
            except:
                inventario.stock_total = float(cantidad)
                inventario.save()
            detail_data = {
                'transaction': transaction,
                'code': transaction.batch_code,
                'batch': lote,
                'serie': None
            }
            return self.crear_detalle_transaccion(detail_data)
        else:
            detalles = []
            codigo = transaction.serie_code
            for i in range(int(cantidad)):
                code = codigo,'-',i
                data_serie = {
                    'codigo': code,
                    'inventario': inventario,
                    'estado': 'A',
                    'fecha_creacion': timezone.localdate(),
                    'fecha_expiracion': transaction.expiration_date,
                }
                ok, serie = self.inventario.crear_serie_entrada(data_serie)
                if not ok:
                    return False, None
                detail_data = {
                    'transaction': transaction,
                    'code': code,
                    'batch': None,
                    'serie': serie
                }
                ok, detalle = self.crear_detalle_transaccion(detail_data)
                if not ok:
                    return False, None
                detalles.append(detalle)
            try:
                inventario.stock_total += Decimal(cantidad)
                inventario.save()
            except:
                inventario.stock_total = float(cantidad)
                inventario.save()
            return True, detalles
    
    def crear_detalle_transaccion(self, data):
        detalle = self.transaction_detail.objects.create(**data)
        if not detalle:
            return False, None
        return True, detalle
    
    def procesar_devolucion(self, transaction, product, materia_prima, cantidad):
        if product:
            producto = self.inventario.product_class.objects.get(id=product.id)
            inventario = self.inventario.model.objects.get_or_create(materia_prima=None, producto=producto, bodega=transaction.warehouse)[0]
        if materia_prima:
            mat_prima = self.inventario.raw_class.objects.get(materia_prima.id)
            inventario = self.inventario.model.objects.get_or_create(materia_prima=mat_prima, producto=None, bodega=transaction.warehouse)[0]
        if transaction.batch_code:
            data_lote = {
                'inventario': inventario,
                'cantidad_actual': cantidad,
                'fecha_creacion': timezone.localdate(),
                'fecha_expiracion': transaction.expiration_date,
                'origen': "devolucion"
            }
            self.inventario.crear_lote_entrada(data_lote)
        if transaction.serie_code:
            for i in range(int(cantidad)):
                data_serie = {
                    'inventario': inventario,
                    'codigo': f"{transaction.serie_code} - {i+1}",
                    'estado': 'A',
                    'fecha_creacion': timezone.localdate(),
                    'fecha_expiracion': transaction.expiration_date,
                }
                self.inventario.crear_serie_entrada(data_serie)
        self.inventario.actualizar_stock_total(inventario)
        return True, None

    def get_by_warehouse(self, warehouse_id):
        return self.model.objects.filter(warehouse=warehouse_id)
    
    def get_by_client(self, client_id):
        return self.model.objects.filter(client=client_id)

    def validate_code(self, code):
        used = self.model.objects.filter(batch_code=code).exists()
        if used:
            return False
        return True