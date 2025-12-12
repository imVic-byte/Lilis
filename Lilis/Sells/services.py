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
        return self.model.objects.filter(is_active=True).count()
    
    def count_suspended(self):
        return self.model.objects.filter(is_active=False).count()

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
    
    def actualizar_stock(self, inventario):
        if inventario.lotes.exists():
            print("actualizando stock, lotes")
            lotes = inventario.lotes.all()
            stock_total = lotes.aggregate(stock_total=Sum('cantidad_actual'))['stock_total'] or 0
            inventario.stock_total = stock_total
            inventario.save()
            print("nuevo stock", inventario.stock_total)
        else:
            print("actualizando stock, series")
            series = inventario.series.all().filter(estado='A')
            stock_total = series.count()
            inventario.stock_total = stock_total
            inventario.save()
            print("nuevo stock ", inventario.stock_total)
        try:
            deficit = Decimal(inventario.producto.deficit)
            if inventario.stock_total > deficit:
                inventario.stock_total -= deficit
                inventario.producto.deficit = 0
                inventario.producto.save()
        except:
            deficit = Decimal(inventario.materia_prima.deficit)
            if inventario.stock_total > deficit:
                inventario.stock_total -= deficit
                inventario.materia_prima.deficit = 0
                inventario.materia_prima.save()

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
        print("serie creada ",serie)
        self.actualizar_stock(serie.inventario)
        return True, serie

    def consumir_series_p(self, producto, cantidad):
        resta = Decimal(cantidad)
        series = self.serie.objects.filter(inventario__producto=producto, estado='A').order_by('-fecha_expiracion')
        for s in series:
            if resta == 0:
                break
            s.estado = 'I'
            s.save()
            resta -= 1
            self.actualizar_stock(s.inventario)
        if resta > 0:
            producto.deficit += resta
            producto.save()
        return True
    
    def consumir_series_m(self, materia_prima, cantidad):
        resta = Decimal(cantidad)
        series = self.serie.objects.filter(inventario__materia_prima=materia_prima, estado='A').order_by('-fecha_expiracion')
        for s in series:
            if resta == 0:
                break
            s.estado = 'I'
            s.save()
            resta -= 1
            self.actualizar_stock(s.inventario)
        if resta > 0:
            materia_prima.deficit += resta
            materia_prima.save()
        return True

    def consumir_lotes_p(self, producto, cantidad):
        resta = Decimal(cantidad)
        lotes = self.lote.objects.filter(inventario__producto=producto).order_by('-fecha_expiracion')
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

    def consumir_lotes_m(self, materia_prima, cantidad):
        resta = Decimal(cantidad)
        lotes = self.lote.objects.filter(inventario__materia_prima=materia_prima).order_by('-fecha_expiracion')
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
            materia_prima.deficit += resta
            materia_prima.save()
        return True

    def consumir_lotes_inventario(self, inventario, cantidad):
        cantidad = Decimal(cantidad)
        print("consumiendo lotes")
        lotes = self.lote.objects.filter(inventario=inventario).order_by('-fecha_expiracion')
        print("estos son los lotes",lotes)
        for l in lotes:
            print("lote ",l)
            if l.cantidad_actual == 0:
                print("lote sin stock")
                continue
            if l.cantidad_actual >= cantidad:
                print("lote con stock suficiente")
                l.cantidad_actual -= cantidad
                l.save()
                self.actualizar_stock(l.inventario)
                return True
            print("lote con stock insuficiente")
            cantidad -= l.cantidad_actual
            l.cantidad_actual = 0
            l.save()
            self.actualizar_stock(l.inventario)
        if cantidad > 0:
            try: 
                inventario.producto.deficit += cantidad
                inventario.producto.save()
                print("deficit actualizado",inventario.deficit)
                return True
            except:
                inventario.materia_prima.deficit += cantidad
                inventario.materia_prima.save()
                print("deficit actualizado",inventario.deficit)
                return True
        return False
    
    def consumir_series_inventario(self, inventario, cantidad):
        cantidad = Decimal(cantidad)
        print("consumiendo series")
        series = self.serie.objects.filter(inventario=inventario).order_by('-fecha_expiracion')
        print(series)
        i = 0
        for s in series:
            if cantidad == 0:
                break
            i += 1
            print(i,"- serie ",s.id)
            if s.estado == 'I':
                print("serie inactiva")
                continue
            s.estado = 'I'
            s.save()
            cantidad -= 1
            print('serie activa ',s.id)
            self.actualizar_stock(s.inventario)
            print("cantidad restante ",cantidad)
        if cantidad > 0:
            try:
                inventario.producto.deficit += cantidad
                inventario.producto.save()
                print("deficit actualizado",inventario.producto.deficit)
                return True
            except:
                inventario.materia_prima.deficit += cantidad
                inventario.materia_prima.save()
                print("deficit actualizado",inventario.materia_prima.deficit)
                return True
        return False
  
    def transferir(self, transaction, inventario, cantidad):
        item = None
        control = None
        controles = []
        batch = False
        nuevo_inventario = None
        print("transferiendo")
        match inventario:
            case inventario if inventario.producto:
                print("es un producto")
                item = inventario.producto
                nuevo_inventario = self.model.objects.get_or_create(producto=item, materia_prima=None, bodega=transaction.warehouse)[0]
            case inventario if inventario.materia_prima:
                print("es una materia prima")
                item = inventario.materia_prima
                nuevo_inventario = self.model.objects.get_or_create(materia_prima=item, producto=None, bodega=transaction.warehouse)[0]
        if item:
            match item:
                case item if item.batch_control:
                    print("es un producto con control de lotes")
                    control = "lotes"
                    self.consumir_lotes_inventario(inventario, cantidad)
                case item if item.serie_control:
                    print("es un producto con control de series")
                    control = "series"
                    self.consumir_series_inventario(inventario, cantidad)
        print("transferencia exitosa")
        print("creando control")
        match control:
            case "lotes":
                print("creando lote")
                data = {
                    "codigo": transaction.code,
                    "inventario":nuevo_inventario,
                    "cantidad_actual": cantidad,
                    "fecha_expiracion": transaction.expiration_date,
                    "fecha_creacion": transaction.date,
                    "origen": "T"
                }
                ok, l = self.crear_lote_entrada(data)
                controles.append(l)
                batch = True
            case "series":
                for i in range(int(cantidad)):
                    print("creando serie", i+1)
                    data = {
                        "codigo": transaction.code + "-" + str(i+1),
                        "inventario":nuevo_inventario,
                        "fecha_expiracion": transaction.expiration_date,
                        "fecha_creacion": transaction.date,
                        "estado": "A"
                    }
                    ok, s = self.crear_serie_entrada(data)
                    controles.append(s)
        self.actualizar_stock(nuevo_inventario)
        self.actualizar_stock(inventario)
        return True, controles, batch
            
    def inventarios_por_producto(self, producto):
        return self.model.objects.all().filter(producto=producto)
            
    def inventarios_por_materia_prima(self, materia_prima):
        return self.model.objects.all().filter(materia_prima=materia_prima)
                
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
            return None, mp, None
        if data['product']:
            tipo, id = data['product'].split('-')
            if tipo == 'producto' or tipo =='product':
                product = self.inventario.product_class.objects.get(id=id)
                data['product'] = product
                data['raw_material'] = None
                return product, None, None
            elif tipo == 'materia_prima' or tipo =='raw_material':
                raw_material = self.inventario.raw_class.objects.get(id=id)
                data['product'] = None
                data['raw_material'] = raw_material
                return None, raw_material, None
            else:
                inventory = self.inventario.model.objects.get(id=id)
                data['product'] = None
                data['raw_material'] = None
                data['inventory'] = inventory
                return None, None, inventory

    def create_transaction(self, request):
        data = {
            'warehouse':request.POST.get('warehouse'),
            'client':request.POST.get('client'),
            'user':request.user.profile,
            'notes':request.POST.get('observaciones'),
            'type':request.POST.get('tipo'),
            'quantity':request.POST.get('cantidad'),
            'product':request.POST.get('producto'),
            'code':request.POST.get('codigo'),
            'expiration_date':request.POST.get('vencimiento'),
            'date':request.POST.get('fecha'),
        }
        if not data['expiration_date']:
            data['expiration_date'] = None
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
        producto, materia_prima, inventario = self.resolver(data)
        transaction_data = {
            'warehouse': data['warehouse'],
            'client': data['client'],
            'user': data['user'],
            'notes': data['notes'],
            'quantity': cantidad,
            'code': data['code'],
            'expiration_date': data['expiration_date'],
            'type': type_
        }
        try:
            transaction = self.model.objects.create(**transaction_data)
        except:
            return False, None
        if type_ == 'ingreso':
            ok, ingresos = self.procesar_ingreso(transaction, materia_prima, cantidad)
            if not ok:
                return False, None
        if type_ == 'salida':
            ok = self.procesar_salida(transaction,producto, cantidad)
            if not ok:
                return False, None
        if type_ == 'devolucion':
            ok = self.procesar_devolucion(transaction, producto, materia_prima, cantidad)
            if not ok:
                return False, None
        if type_ == 'transferencia':
            ok = self.procesar_transferencia(transaction, inventario, cantidad)
            if not ok:
                return False, None
        if type_ == 'produccion':
            if not producto:
                return False, None
            ok = self.procesar_produccion(transaction, producto, cantidad)
            if not ok:
                return False, None
        return True, transaction

    def procesar_transferencia(self, transaction, inventario, cantidad):
        ok, control, batch = self.inventario.transferir(transaction, inventario, cantidad)
        if not ok:
            return False
        if batch:
            for c in control:
                detail_data = {
                    'transaction': transaction,
                    'code': transaction.code,
                    'batch': c,
                    'serie': None
                }
                self.crear_detalle_transaccion(detail_data)
        else:
            for c in control:
                detail_data = {
                    'transaction': transaction,
                    'code': transaction.code,
                    'batch': None,
                    'serie': c
                }
                self.crear_detalle_transaccion(detail_data)
        return True


    def procesar_salida(self, transaction, producto, cantidad):
        if producto.batch_control:
            self.inventario.consumir_lotes_p(producto, cantidad)
        else:
            self.inventario.consumir_series_p(producto, cantidad)
        detail_data = {
            'transaction': transaction,
            'code': transaction.code,
            'batch': None,
            'serie': None
        }
        self.crear_detalle_transaccion(detail_data)
        return True

    def procesar_produccion(self, transaction, product, cantidad):
        inventario = self.inventario.model.objects.get_or_create(producto=product, materia_prima=None, bodega=transaction.warehouse)[0]
        if product.batch_control:
            data_lote = {
                'inventario': inventario,
                'cantidad_actual': cantidad,
                'fecha_creacion': timezone.localdate(),
                'fecha_expiracion': transaction.expiration_date,
                'origen': "devolucion"
            }
            ok, lote = self.inventario.crear_lote_entrada(data_lote)
            if not ok:
                print("algo paso")
                return False, None
            detail_data = {
                'transaction': transaction,
                'code': transaction.code,
                'batch': lote,
                'serie': None
            }
            ok, detalle = self.crear_detalle_transaccion(detail_data)
            if not ok:
                print("algo paso2")
                return False, None
            return True, detalle
        else:
            detalles = []
            codigo = transaction.code
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
            return True, detalles
    
    def procesar_ingreso(self, transaction, materia_prima, cantidad):
        inventario = self.inventario.model.objects.get_or_create(materia_prima=materia_prima, producto=None, bodega=transaction.warehouse)[0]
        if materia_prima.batch_control:
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
            detail_data = {
                'transaction': transaction,
                'code': transaction.code,
                'batch': lote,
                'serie': None
            }
            return self.crear_detalle_transaccion(detail_data)
        else:
            detalles = []
            codigo = transaction.code
            for i in range(int(cantidad)):
                code = f'{codigo}-{i}'
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
            return True, detalles
    
    def crear_detalle_transaccion(self, data):
        detalle = self.transaction_detail.objects.create(**data)
        if not detalle:
            return False, None
        return True, detalle
    
    def procesar_devolucion(self, transaction, product, materia_prima, cantidad):
        if product:
            inventario = self.inventario.model.objects.get_or_create(producto=product, materia_prima=None, bodega=transaction.warehouse)[0]
            if product.batch_control:
                data_lote = {
                    'inventario': inventario,
                    'cantidad_actual': cantidad,
                    'fecha_creacion': timezone.localdate(),
                    'fecha_expiracion': transaction.expiration_date,
                    'origen': "devolucion"
                }
                ok,lote = self.inventario.crear_lote_entrada(data_lote)
                if not ok:
                    return False, None
                detail_data = {
                    'transaction': transaction,
                    'code': transaction.code,
                    'batch': lote,
                    'serie': None
                }
                self.crear_detalle_transaccion(detail_data)
                return True, None
            else:
                detalles = []
                for i in range(int(cantidad)):
                    data_serie = {
                        'inventario': inventario,
                        'codigo': f"{transaction.code} - {i+1}",
                        'estado': 'A',
                        'fecha_creacion': timezone.localdate(),
                        'fecha_expiracion': transaction.expiration_date,
                    }
                    ok, serie = self.inventario.crear_serie_entrada(data_serie)
                    if not ok:
                        return False, None
                    detail_data = {
                        'transaction': transaction,
                        'code': transaction.code,
                        'batch': None,
                        'serie': serie
                    }
                    ok, detalle = self.crear_detalle_transaccion(detail_data)
                    if not ok:
                        return False, None
                    detalles.append(detalle)
                return True, detalles
        else:
            inventario = self.inventario.model.objects.get_or_create(materia_prima=materia_prima, producto=None, bodega=transaction.warehouse)[0]
            if materia_prima.batch_control:
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
                detail_data = {
                    'transaction': transaction,
                    'code': transaction.code,
                    'batch': lote,
                    'serie': None
                }
                ok, detalle = self.crear_detalle_transaccion(detail_data)
                if not ok:
                    return False, None
                return True, detalle
            else:
                detalles = []
                for i in range(int(cantidad)):
                    data_serie = {
                        'inventario': inventario,
                        'codigo': f"{transaction.code} - {i+1}",
                        'estado': 'A',
                        'fecha_creacion': timezone.localdate(),
                        'fecha_expiracion': transaction.expiration_date,
                }
                ok, serie = self.inventario.crear_serie_entrada(data_serie)
                if not ok:
                    return False, None
                detail_data = {
                    'transaction': transaction,
                    'code': transaction.code,
                    'batch': None,
                    'serie': serie
                }
                ok, detalle = self.crear_detalle_transaccion(detail_data)
                if not ok:
                    return False, None
                detalles.append(detalle)
                return True, detalle

    def get_by_warehouse(self, warehouse_id):
        return self.model.objects.filter(warehouse=warehouse_id)
    
    def get_by_client(self, client_id):
        return self.model.objects.filter(client=client_id)

    def validate_code(self, code):
        used = self.model.objects.filter(code=code).exists()
        if used:
            return False
        return True