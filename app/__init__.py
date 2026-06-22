from flask import Flask
from flask_appbuilder import AppBuilder
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    db.init_app(app)

    with app.app_context():
        ab = AppBuilder(app, db.session)

        from .models import Categoria, Producto, Cliente, Orden, DetalleOrden, ServicioTecnico
        from .views import (
            CategoriaView, ProductoView, ClienteView,
            OrdenView, NuevaOrdenView, ServicioTecnicoView, ReportesView
        )

        ab.add_view(
            CategoriaView, 'Categorías',
            icon='fa-tags', category='Catálogo',
            category_icon='fa-list'
        )
        ab.add_view(
            ProductoView, 'Productos',
            icon='fa-laptop', category='Catálogo'
        )
        ab.add_view(
            ClienteView, 'Clientes',
            icon='fa-users', category='Ventas',
            category_icon='fa-shopping-cart'
        )
        ab.add_view(
            OrdenView, 'Órdenes',
            icon='fa-file-text', category='Ventas'
        )
        ab.add_view(
            NuevaOrdenView, 'Nueva Venta',
            icon='fa-plus-circle', category='Ventas',
            href='/nueva-orden/nueva'
        )
        ab.add_view(
            ServicioTecnicoView, 'Servicio Técnico',
            icon='fa-wrench', category='Servicios',
            category_icon='fa-cogs'
        )

        ab.add_view(
            ReportesView, 'Panel de Reportes',
            icon='fa-bar-chart', category='Reportes',
            category_icon='fa-pie-chart',
            href='/reportes/index'
        )
        ab.add_link(
            'Ventas por Mes',
            icon='fa-line-chart', category='Reportes',
            href='/reportes/ventas_por_mes'
        )
        ab.add_link(
            'Productos más Vendidos',
            icon='fa-trophy', category='Reportes',
            href='/reportes/productos_mas_vendidos'
        )
        ab.add_link(
            'Servicios por Estado',
            icon='fa-pie-chart', category='Reportes',
            href='/reportes/servicios_por_estado'
        )

        _ensure_roles(ab)
        db.create_all()

    return app


def _ensure_roles(ab):
    for role_name in ['Admin', 'Supervisor', 'Usuario']:
        if not ab.sm.find_role(role_name):
            ab.sm.add_role(role_name)
