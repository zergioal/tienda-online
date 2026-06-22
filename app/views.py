from flask_appbuilder import ModelView, expose
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.baseviews import BaseView
from flask_appbuilder.security.decorators import has_access
from flask import render_template
from sqlalchemy import func
from . import db
from .models import Categoria, Producto, Cliente, Orden, DetalleOrden, ServicioTecnico
import json


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
