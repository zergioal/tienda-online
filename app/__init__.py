from flask import Flask
from flask_appbuilder import AppBuilder
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    db.init_app(app)

    with app.app_context():
        from .models import Categoria, Producto, Cliente, Orden, DetalleOrden, ServicioTecnico
        from .views import (
            DashboardView,
            CategoriaView, ProductoView, ClienteView,
            OrdenView, NuevaOrdenView, ServicioTecnicoView, ReportesView
        )

        ab = AppBuilder(app, db.session, indexview=DashboardView)

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

        db.create_all()
        _setup_roles(ab)

    return app


def _setup_roles(ab):
    # Crear roles si no existen
    for role_name in ['Admin', 'Supervisor', 'Usuario']:
        if not ab.sm.find_role(role_name):
            ab.sm.add_role(role_name)

    # ── Supervisor: servicios técnicos + órdenes/clientes (lectura) + reportes ──
    _assign_perms(ab, 'Supervisor', [
        # Servicios técnicos — gestión completa
        ('can_list',                    'ServicioTecnicoView'),
        ('can_show',                    'ServicioTecnicoView'),
        ('can_add',                     'ServicioTecnicoView'),
        ('can_edit',                    'ServicioTecnicoView'),
        ('menu_access',                 'Servicios'),
        ('menu_access',                 'Servicio Técnico'),
        # Órdenes — solo lectura
        ('can_list',                    'OrdenView'),
        ('can_show',                    'OrdenView'),
        # Clientes — solo lectura
        ('can_list',                    'ClienteView'),
        ('can_show',                    'ClienteView'),
        ('menu_access',                 'Ventas'),
        ('menu_access',                 'Órdenes'),
        ('menu_access',                 'Clientes'),
        # Reportes — acceso total
        ('can_index',                   'ReportesView'),
        ('can_ventas_por_mes',          'ReportesView'),
        ('can_productos_mas_vendidos',  'ReportesView'),
        ('can_servicios_por_estado',    'ReportesView'),
        ('menu_access',                 'Reportes'),
        ('menu_access',                 'Panel de Reportes'),
        ('menu_access',                 'Ventas por Mes'),
        ('menu_access',                 'Productos más Vendidos'),
        ('menu_access',                 'Servicios por Estado'),
    ])

    # ── Usuario: catálogo (lectura) + realizar compras ──────────────────────────
    _assign_perms(ab, 'Usuario', [
        # Catálogo — solo lectura
        ('can_list',    'ProductoView'),
        ('can_show',    'ProductoView'),
        ('can_list',    'CategoriaView'),
        ('can_show',    'CategoriaView'),
        ('menu_access', 'Catálogo'),
        ('menu_access', 'Productos'),
        ('menu_access', 'Categorías'),
        # Nueva Venta — puede comprar
        ('can_nueva',   'NuevaOrdenView'),
        ('can_guardar', 'NuevaOrdenView'),
        ('can_precio',  'NuevaOrdenView'),
        ('menu_access', 'Ventas'),
        ('menu_access', 'Nueva Venta'),
    ])


def _assign_perms(ab, role_name, perms):
    role = ab.sm.find_role(role_name)
    if not role:
        return
    for perm_name, view_name in perms:
        pv = ab.sm.find_permission_view_menu(perm_name, view_name)
        if pv:
            ab.sm.add_permission_role(role, pv)
