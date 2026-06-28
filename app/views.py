from flask_appbuilder import ModelView, expose, IndexView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.baseviews import BaseView
from flask_appbuilder.security.decorators import has_access
from flask import request, redirect, flash, jsonify, session
from sqlalchemy import func
from . import db
from .models import Categoria, Producto, Cliente, Orden, DetalleOrden, ServicioTecnico
import json


# ── Dashboard (Index) ────────────────────────────────────────────────────────

class DashboardView(IndexView):
    index_template = 'index.html'

    @expose('/')
    def index(self):
        from flask_login import current_user
        from flask import render_template as flask_render
        if not current_user.is_authenticated:
            return flask_render('landing.html')
        roles = [r.name for r in current_user.roles]
        if 'Admin' not in roles and 'Supervisor' not in roles:
            return redirect('/catalogo/')
        stats = {
            'productos':           db.session.query(Producto).count(),
            'ordenes':             db.session.query(Orden).count(),
            'clientes':            db.session.query(Cliente).count(),
            'servicios_pendientes': db.session.query(ServicioTecnico)
                                     .filter(ServicioTecnico.estado.in_(['Pendiente', 'En Proceso']))
                                     .count(),
            'ingresos_total':      db.session.query(func.sum(Orden.total))
                                     .filter(Orden.estado == 'Pagada').scalar() or 0,
        }
        ultimas_ordenes = (
            db.session.query(Orden)
            .order_by(Orden.fecha.desc())
            .limit(8).all()
        )
        servicios_estados = (
            db.session.query(
                ServicioTecnico.estado,
                func.count(ServicioTecnico.id).label('cantidad')
            )
            .group_by(ServicioTecnico.estado).all()
        )
        return self.render_template(
            'index.html',
            stats=stats,
            ultimas_ordenes=ultimas_ordenes,
            servicios_estados=servicios_estados,
        )


# ── CRUD Views ──────────────────────────────────────────────────────────────

class CategoriaView(ModelView):
    datamodel = SQLAInterface(Categoria)
    list_title = 'Categorías'
    add_title = 'Nueva Categoría'
    edit_title = 'Editar Categoría'
    list_columns = ['nombre', 'descripcion']
    add_columns = ['nombre', 'descripcion']
    edit_columns = ['nombre', 'descripcion']


class ProductoView(ModelView):
    datamodel = SQLAInterface(Producto)
    list_title = 'Productos'
    add_title = 'Nuevo Producto'
    edit_title = 'Editar Producto'
    list_columns = ['nombre', 'precio', 'stock', 'categoria']
    add_columns = ['nombre', 'descripcion', 'precio', 'stock', 'categoria']
    edit_columns = ['nombre', 'descripcion', 'precio', 'stock', 'categoria']
    related_views = []


class ClienteView(ModelView):
    datamodel = SQLAInterface(Cliente)
    list_title = 'Clientes'
    add_title = 'Nuevo Cliente'
    edit_title = 'Editar Cliente'
    list_columns = ['nombre', 'apellido', 'email', 'telefono']
    add_columns = ['nombre', 'apellido', 'email', 'telefono', 'direccion']
    edit_columns = ['nombre', 'apellido', 'email', 'telefono', 'direccion']


class DetalleOrdenView(ModelView):
    datamodel = SQLAInterface(DetalleOrden)
    list_columns = ['producto', 'cantidad', 'precio_unitario', 'subtotal']
    add_columns = ['producto', 'cantidad', 'precio_unitario', 'subtotal']
    edit_columns = ['producto', 'cantidad', 'precio_unitario', 'subtotal']


class OrdenView(ModelView):
    datamodel = SQLAInterface(Orden)
    list_title = 'Órdenes'
    add_title = 'Nueva Orden'
    edit_title = 'Editar Orden'
    list_columns = ['id', 'fecha', 'cliente', 'total', 'estado']
    add_columns = ['fecha', 'cliente', 'total', 'estado']
    edit_columns = ['fecha', 'cliente', 'total', 'estado']
    related_views = [DetalleOrdenView]


class CatalogoView(BaseView):
    """Tienda pública: catálogo + carrito + checkout para el rol Usuario."""
    route_base = '/catalogo'
    default_view = 'index'

    # ── Catálogo ─────────────────────────────────────────────────────────────
    @expose('/')
    @has_access
    def index(self):
        from flask_wtf.csrf import generate_csrf
        cats = db.session.query(Categoria).order_by(Categoria.nombre).all()
        cat_id = request.args.get('cat', type=int)
        q = db.session.query(Producto).filter(Producto.stock > 0)
        if cat_id:
            q = q.filter(Producto.categoria_id == cat_id)
        productos = q.order_by(Producto.nombre).all()
        carrito = session.get('carrito', {})
        total_items = sum(carrito.values())
        return self.render_template('catalogo/index.html',
                                    categorias=cats,
                                    productos=productos,
                                    cat_seleccionada=cat_id,
                                    total_items=total_items,
                                    csrf_token=generate_csrf())

    # ── Agregar al carrito ────────────────────────────────────────────────────
    @expose('/agregar/<int:prod_id>', methods=['POST'])
    @has_access
    def agregar(self, prod_id):
        prod = db.session.get(Producto, prod_id)
        if not prod or prod.stock <= 0:
            flash('Producto no disponible.', 'danger')
            return redirect('/catalogo/')
        carrito = session.get('carrito', {})
        key = str(prod_id)
        qty_actual = carrito.get(key, 0)
        if qty_actual >= prod.stock:
            flash(f'Solo hay {prod.stock} unidades disponibles de {prod.nombre}.', 'warning')
        else:
            carrito[key] = qty_actual + 1
            session['carrito'] = carrito
            flash(f'{prod.nombre} agregado al carrito.', 'success')
        return redirect(request.referrer or '/catalogo/')

    # ── Quitar del carrito ────────────────────────────────────────────────────
    @expose('/quitar/<int:prod_id>', methods=['POST'])
    @has_access
    def quitar(self, prod_id):
        carrito = session.get('carrito', {})
        carrito.pop(str(prod_id), None)
        session['carrito'] = carrito
        return redirect('/catalogo/carrito')

    # ── Actualizar cantidad ───────────────────────────────────────────────────
    @expose('/actualizar/<int:prod_id>', methods=['POST'])
    @has_access
    def actualizar(self, prod_id):
        cantidad = request.form.get('cantidad', 1, type=int)
        prod = db.session.get(Producto, prod_id)
        carrito = session.get('carrito', {})
        if prod and 1 <= cantidad <= prod.stock:
            carrito[str(prod_id)] = cantidad
        session['carrito'] = carrito
        return redirect('/catalogo/carrito')

    # ── Ver carrito ───────────────────────────────────────────────────────────
    @expose('/carrito')
    @has_access
    def carrito(self):
        from flask_wtf.csrf import generate_csrf
        carrito = session.get('carrito', {})
        items, total = [], 0
        for prod_id, qty in carrito.items():
            prod = db.session.get(Producto, int(prod_id))
            if prod:
                subtotal = round(prod.precio * qty, 2)
                total += subtotal
                items.append({'producto': prod, 'cantidad': qty, 'subtotal': subtotal})
        return self.render_template('catalogo/carrito.html',
                                    items=items, total=round(total, 2),
                                    csrf_token=generate_csrf())

    # ── Checkout ──────────────────────────────────────────────────────────────
    @expose('/checkout', methods=['POST'])
    @has_access
    def checkout(self):
        carrito = session.get('carrito', {})
        if not carrito:
            flash('El carrito está vacío.', 'warning')
            return redirect('/catalogo/')
        nombre   = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        telefono = request.form.get('telefono', '').strip()
        if not nombre or not apellido:
            flash('Completa tu nombre y apellido para continuar.', 'warning')
            items, total = [], 0
            for prod_id, qty in carrito.items():
                prod = db.session.get(Producto, int(prod_id))
                if prod:
                    subtotal = round(prod.precio * qty, 2)
                    total += subtotal
                    items.append({'producto': prod, 'cantidad': qty, 'subtotal': subtotal})
            return self.render_template('catalogo/carrito.html',
                                        items=items, total=round(total, 2))

        # Buscar o crear cliente
        cliente = db.session.query(Cliente).filter_by(
            nombre=nombre, apellido=apellido).first()
        if not cliente:
            cliente = Cliente(nombre=nombre, apellido=apellido,
                              telefono=telefono,
                              email=f'{nombre.lower()}.{apellido.lower()}@techstore.com')
            db.session.add(cliente)
            db.session.flush()

        # Crear orden
        from datetime import datetime, timezone
        orden = Orden(cliente=cliente, estado='Pagada',
                      fecha=datetime.now(timezone.utc).replace(tzinfo=None), total=0)
        db.session.add(orden)
        db.session.flush()

        total = 0
        for prod_id, qty in carrito.items():
            prod = db.session.get(Producto, int(prod_id))
            if not prod or prod.stock < qty:
                continue
            subtotal = round(prod.precio * qty, 2)
            total += subtotal
            db.session.add(DetalleOrden(
                orden_id=orden.id, producto_id=prod.id,
                cantidad=qty, precio_unitario=prod.precio, subtotal=subtotal
            ))
            prod.stock -= qty

        orden.total = round(total, 2)
        db.session.commit()
        session.pop('carrito', None)
        flash(f'¡Compra realizada! Orden #{orden.id} — Total: Bs. {orden.total:.2f}', 'success')
        return redirect('/catalogo/confirmacion/' + str(orden.id))

    # ── Confirmación ──────────────────────────────────────────────────────────
    @expose('/confirmacion/<int:orden_id>')
    @has_access
    def confirmacion(self, orden_id):
        orden = db.session.get(Orden, orden_id)
        return self.render_template('catalogo/confirmacion.html', orden=orden)


class NuevaOrdenView(BaseView):
    """Vista personalizada para registrar una orden con sus productos en un solo formulario."""
    route_base = '/nueva-orden'
    default_view = 'nueva'

    @expose('/nueva', methods=['GET'])
    @has_access
    def nueva(self):
        from flask_wtf.csrf import generate_csrf
        clientes = db.session.query(Cliente).order_by(Cliente.apellido).all()
        productos = db.session.query(Producto).filter(Producto.stock > 0).order_by(Producto.nombre).all()
        return self.render_template('orden_nueva.html',
                                    clientes=clientes,
                                    productos=productos,
                                    csrf_token=generate_csrf())

    @expose('/guardar', methods=['POST'])
    @has_access
    def guardar(self):
        cliente_id = request.form.get('cliente_id')
        estado = request.form.get('estado', 'Pendiente')
        productos_ids = request.form.getlist('producto_id[]')
        cantidades = request.form.getlist('cantidad[]')

        if not cliente_id:
            flash('Debe seleccionar un cliente.', 'warning')
            return redirect('/nueva-orden/nueva')
        if not productos_ids:
            flash('Debe agregar al menos un producto.', 'warning')
            return redirect('/nueva-orden/nueva')

        orden = Orden(cliente_id=int(cliente_id), estado=estado, total=0)
        db.session.add(orden)
        db.session.flush()

        total = 0
        errores = []
        for prod_id, qty_str in zip(productos_ids, cantidades):
            prod = db.session.get(Producto, int(prod_id))
            qty = int(qty_str) if qty_str.isdigit() else 1
            if qty <= 0:
                continue
            if prod.stock < qty:
                errores.append(f'Stock insuficiente para {prod.nombre} (disponible: {prod.stock})')
                continue
            subtotal = round(prod.precio * qty, 2)
            total += subtotal
            db.session.add(DetalleOrden(
                orden_id=orden.id, producto_id=prod.id,
                cantidad=qty, precio_unitario=prod.precio, subtotal=subtotal
            ))
            prod.stock -= qty

        if errores:
            db.session.rollback()
            for e in errores:
                flash(e, 'danger')
            return redirect('/nueva-orden/nueva')

        orden.total = round(total, 2)
        db.session.commit()
        flash(f'Orden #{orden.id} registrada correctamente — Total: Bs. {orden.total:.2f}', 'success')
        return redirect('/ordenview/list/')

    @expose('/precio/<int:producto_id>')
    @has_access
    def precio(self, producto_id):
        prod = db.session.get(Producto, producto_id)
        if prod:
            return jsonify({'precio': prod.precio, 'stock': prod.stock})
        return jsonify({'precio': 0, 'stock': 0})


class ServicioTecnicoView(ModelView):
    datamodel = SQLAInterface(ServicioTecnico)
    list_title = 'Servicios Técnicos'
    add_title = 'Nuevo Servicio'
    edit_title = 'Editar Servicio'
    list_columns = ['id', 'cliente', 'fecha_ingreso', 'estado', 'costo']
    add_columns = ['cliente', 'descripcion_problema', 'estado', 'costo']
    edit_columns = ['cliente', 'descripcion_problema', 'diagnostico', 'fecha_entrega', 'costo', 'estado']


# ── Reports & Charts ────────────────────────────────────────────────────────

class ReportesView(BaseView):
    route_base = '/reportes'
    default_view = 'index'

    @expose('/index')
    @has_access
    def index(self):
        return self.render_template('reports/index.html')

    # Reporte 1: Ventas por mes
    @expose('/ventas_por_mes')
    @has_access
    def ventas_por_mes(self):
        from sqlalchemy import extract
        resultados = (
            db.session.query(
                extract('year', Orden.fecha).label('anio'),
                extract('month', Orden.fecha).label('mes'),
                func.count(Orden.id).label('total_ordenes'),
                func.sum(Orden.total).label('total_ventas')
            )
            .filter(Orden.estado != 'Cancelada')
            .group_by('anio', 'mes')
            .order_by('anio', 'mes')
            .all()
        )
        meses = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
        datos = [
            {
                'periodo': f"{meses[int(r.mes)-1]} {int(r.anio)}",
                'ordenes': r.total_ordenes,
                'ventas': round(r.total_ventas or 0, 2)
            }
            for r in resultados
        ]
        labels = json.dumps([d['periodo'] for d in datos])
        valores = json.dumps([d['ventas'] for d in datos])
        return self.render_template('reports/ventas_por_mes.html',
                                    datos=datos, labels=labels, valores=valores)

    @expose('/pronostico/ventas')
    @has_access
    def pronostico_ventas_json(self):
        from sqlalchemy import extract
        from .ai_service import pronostico_ventas
        resultados = (
            db.session.query(
                extract('year', Orden.fecha).label('anio'),
                extract('month', Orden.fecha).label('mes'),
                func.count(Orden.id).label('total_ordenes'),
                func.sum(Orden.total).label('total_ventas')
            )
            .filter(Orden.estado != 'Cancelada')
            .group_by('anio', 'mes')
            .order_by('anio', 'mes')
            .all()
        )
        meses = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
        datos = [
            {
                'periodo': f"{meses[int(r.mes)-1]} {int(r.anio)}",
                'ordenes': r.total_ordenes,
                'ventas': round(r.total_ventas or 0, 2)
            }
            for r in resultados
        ]
        return jsonify({'pronosticos': pronostico_ventas(datos)})

    # Reporte 2: Productos más vendidos
    @expose('/productos_mas_vendidos')
    @has_access
    def productos_mas_vendidos(self):
        resultados = (
            db.session.query(
                Producto.nombre,
                func.sum(DetalleOrden.cantidad).label('total_vendido'),
                func.sum(DetalleOrden.subtotal).label('total_ingreso')
            )
            .join(DetalleOrden, Producto.id == DetalleOrden.producto_id)
            .join(Orden, Orden.id == DetalleOrden.orden_id)
            .filter(Orden.estado != 'Cancelada')
            .group_by(Producto.id, Producto.nombre)
            .order_by(func.sum(DetalleOrden.cantidad).desc())
            .limit(10)
            .all()
        )
        datos = [
            {
                'producto': r.nombre,
                'cantidad': r.total_vendido,
                'ingreso': round(r.total_ingreso or 0, 2)
            }
            for r in resultados
        ]
        labels = json.dumps([d['producto'] for d in datos])
        valores = json.dumps([d['cantidad'] for d in datos])
        return self.render_template('reports/productos_mas_vendidos.html',
                                    datos=datos, labels=labels, valores=valores)

    @expose('/pronostico/productos')
    @has_access
    def pronostico_productos_json(self):
        from .ai_service import pronostico_productos
        resultados = (
            db.session.query(
                Producto.nombre,
                func.sum(DetalleOrden.cantidad).label('total_vendido'),
                func.sum(DetalleOrden.subtotal).label('total_ingreso')
            )
            .join(DetalleOrden, Producto.id == DetalleOrden.producto_id)
            .join(Orden, Orden.id == DetalleOrden.orden_id)
            .filter(Orden.estado != 'Cancelada')
            .group_by(Producto.id, Producto.nombre)
            .order_by(func.sum(DetalleOrden.cantidad).desc())
            .limit(10)
            .all()
        )
        datos = [
            {
                'producto': r.nombre,
                'cantidad': r.total_vendido,
                'ingreso': round(r.total_ingreso or 0, 2)
            }
            for r in resultados
        ]
        return jsonify({'pronosticos': pronostico_productos(datos)})

    # Reporte 3: Servicios técnicos por estado
    @expose('/servicios_por_estado')
    @has_access
    def servicios_por_estado(self):
        resultados = (
            db.session.query(
                ServicioTecnico.estado,
                func.count(ServicioTecnico.id).label('cantidad'),
                func.sum(ServicioTecnico.costo).label('total_costo')
            )
            .group_by(ServicioTecnico.estado)
            .all()
        )
        datos = [
            {
                'estado': r.estado,
                'cantidad': r.cantidad,
                'costo': round(r.total_costo or 0, 2)
            }
            for r in resultados
        ]
        labels = json.dumps([d['estado'] for d in datos])
        valores = json.dumps([d['cantidad'] for d in datos])
        return self.render_template('reports/servicios_por_estado.html',
                                    datos=datos, labels=labels, valores=valores)

    @expose('/pronostico/servicios')
    @has_access
    def pronostico_servicios_json(self):
        from .ai_service import pronostico_servicios
        resultados = (
            db.session.query(
                ServicioTecnico.estado,
                func.count(ServicioTecnico.id).label('cantidad'),
                func.sum(ServicioTecnico.costo).label('total_costo')
            )
            .group_by(ServicioTecnico.estado)
            .all()
        )
        datos = [
            {
                'estado': r.estado,
                'cantidad': r.cantidad,
                'costo': round(r.total_costo or 0, 2)
            }
            for r in resultados
        ]
        return jsonify({'pronosticos': pronostico_servicios(datos)})
