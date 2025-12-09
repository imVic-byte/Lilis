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

    def agregar_lote_producto(self, data):
        data2 = data.copy()
        data2['origen'] = 'I'
        form = self.lote_form_class(data2)
        producto_id = data2.get('producto')
        bodega_id = data2.get('bodega')
        print("todo bien")
        if not producto_id or not bodega_id:
            print("producto o bodega no enviados.")
            return False, "Producto o bodega no enviados."
        try:
            producto = Producto.objects.get(id=producto_id)
        except Producto.DoesNotExist:
            print("producto inválido.")
            return False, "Producto inválido."
        
        bodega = next((b for b in self.bodegas.filter_by_rut(LILIS_RUT) if str(b.id) == str(bodega_id)), None)
        if not bodega:
            print("bodega inválida.")
            return False, "Bodega inválida."

        inventario, _ = self.model.objects.get_or_create(
            producto=producto,
            bodega=bodega,
            materia_prima=None,
            defaults={
                'stock_total': data.get('cantidad_actual'),
            }
        )
        print("inventario creado")
        if form.is_valid():
            lote = form.save(commit=False)
            lote.inventario = inventario
            lote.codigo = data.get('codigo')
            lote.save()
            self.actualizar_stock_total(lote.inventario)
            return True, lote
        return False, form

    def crear_lote_entrada(self, data):
        if not data:
            return False, None
        lote = self.lote.objects.create(**data)
        return True, lote
    
    def crear_serie_entrada(self, data):
        if not data:
            return False, None
        serie = self.serie.objects.create(**data)
        return True, serie
    
    def actualizar_stock_total(self, inventario):
        total = inventario.lotes.aggregate(total=Sum('cantidad_actual'))['total'] or 0.00
        total += inventario.series.filter(estado='A').count()
        if inventario.stock_total <= 0:
            inventario.stock_total += Decimal(total)
            inventario.save()
            return True, inventario
        inventario.stock_total = Decimal(total)
        inventario.save()
        return True, inventario
    
    def consumir_lotes(self, producto, cantidad):
        inventario = self.model.objects.get(producto=producto)
        lotes = inventario.lotes.order_by('fecha_expiracion', 'fecha_creacion')
        resta = Decimal(cantidad)
        for l in lotes:
            if l.cantidad_actual == 0:
                continue
            if l.cantidad_actual >= resta:
                l.cantidad_actual -= resta
                l.save()
                resta = 0
                break
            resta -= l.cantidad_actual
            l.cantidad_actual = 0
            l.save()
            self.actualizar_stock_total(inventario)
        if resta > 0:
            series = inventario.series.filter(estado='A')
            for s in series:
                s.estado = 'I'
                s.save()
                resta -= 1
                if resta <= 0:
                    break
                self.actualizar_stock_total(inventario)
        if resta > 0:
            inventario.stock_total -= Decimal(resta)
            inventario.save()
            return False
        return True
    
    def mover_lotes(self, transaction_obj, warehouse_destino, producto, materia_prima, cantidad):
        restar = Decimal(cantidad)
        cantidad_original = restar
        if producto:
            inventario_key = {'producto': producto}
        else:
            inventario_key = {'materia_prima': materia_prima}
            
        destino, _ = self.model.objects.get_or_create(
            bodega=warehouse_destino,
            **inventario_key,
            defaults={'stock_total': Decimal('0.00')}
        )
        if producto:
            inventarios_origen = self.model.objects.filter(
                producto=producto
            ).exclude(id=destino.id)
        else:
            inventarios_origen = self.model.objects.filter(
                materia_prima=materia_prima
            ).exclude(id=destino.id)
            
        try:
            with transaction.atomic():
                lotes_a_actualizar = []
                series_a_actualizar = []
                for i in inventarios_origen:
                    if restar <= 0:
                        break
                    lotes = i.lotes.order_by('fecha_expiracion', 'fecha_creacion')
                    for l in lotes:
                        if restar <= 0:
                            break
                        
                        consumo = min(l.cantidad_actual, restar)
                        l.cantidad_actual = F('cantidad_actual') - consumo
                        lotes_a_actualizar.append(l)
                        restar -= consumo
                    if restar > 0:
                        series = i.series.filter(estado='A')
                        for s in series:
                            if restar <= 0:
                                break
                            s.estado = 'I'
                            series_a_actualizar.append(s)
                            restar -= 1
                    self.actualizar_stock_total(i)
                if lotes_a_actualizar:
                    i.lotes.model.objects.bulk_update(lotes_a_actualizar, ['cantidad_actual'])
                if series_a_actualizar:
                    i.series.model.objects.bulk_update(series_a_actualizar, ['estado'])
                if restar > 0:
                    return False 
                for i in inventarios_origen:
                    i.stock_total = F('stock_total') - cantidad_original
                    i.save(update_fields=['stock_total'])
                if transaction_obj.batch_code:
                    batch_data = {
                        'codigo' : transaction_obj.batch_code,
                        'fecha_expiracion' : transaction_obj.expiration_date,
                        'fecha_creacion' : transaction_obj.date,
                        'inventario' : destino,
                        'cantidad_actual' : cantidad_original,
                        'origen' : "T"
                    }
                    self.crear_lote_entrada(batch_data)
                
                if transaction_obj.serie_code:
                    code = transaction_obj.serie_code
                    series_a_crear = []
                    for i in range(int(cantidad_original)):
                        series_a_crear.append(i.series.model(
                            codigo=f"{code}-{i+1}",
                            inventario=destino,
                            estado='A',
                            fecha_creacion=transaction_obj.date,
                            fecha_expiracion=transaction_obj.expiration_date,
                        ))
                    destino.series.model.objects.bulk_create(series_a_crear)

                destino.stock_total = F('stock_total') + cantidad_original
                destino.save(update_fields=['stock_total'])
                
                return True

        except Exception as e:
            print(f"Error en mover_lotes: {e}")
            return False
    
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
            ok = self.inventario.consumir_lotes(producto, cantidad)
            if not ok:
                return False, None
        if type_ == 'devolucion':
            ok = self.procesar_devolucion(transaction, producto, materia_prima, cantidad)
            if not ok:
                return False, None
        if type_ == 'transferencia':
            if not materia_prima:
                ok = self.inventario.mover_lotes(transaction, transaction.warehouse, producto, None, cantidad)
                if not ok:
                    return False, None
            else:
                ok = self.inventario.mover_lotes(transaction, transaction.warehouse, None, materia_prima, cantidad)
                if not ok:
                    return False, None
        if type_ == 'produccion':
            if not producto:
                return False, None
            ok = self.procesar_produccion(transaction, producto, cantidad)
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
            detail_data = {
                'transaction': transaction,
                'code': transaction.batch_code,
                'batch': lote,
                'serie': None
            }
            return self.crear_detalle_transaccion(detail_data)
        else:
            print('TRANSACCIONNNNNNNNNN- ',transaction.serie_code)
            detalles = []
            codigo = transaction.serie_code
            for i in range(int(cantidad)):
                code = codigo,'-',i
                print(code)
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