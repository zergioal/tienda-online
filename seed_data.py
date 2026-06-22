"""
Carga datos de prueba y crea los usuarios/roles por defecto.
Ejecutar: python seed_data.py
"""
from app import create_app, db
from app.models import Categoria, Producto, Cliente, Orden, DetalleOrden, ServicioTecnico
from datetime import datetime, timedelta
import random

app = create_app()

with app.app_context():
    ab = app.extensions.get('appbuilder') or __import__('app', fromlist=['appbuilder']).appbuilder

    # ── Roles ──────────────────────────────────────────────────────────────
    for role_name in ['Admin', 'Supervisor', 'Usuario']:
        if not ab.sm.find_role(role_name):
            ab.sm.add_role(role_name)
    print("Roles OK")

    # ── Usuarios (crea o actualiza contrasena) ────────────────────────────
    users = [
        ('admin',      'Admin',      'admin@techstore.com',      'admin123',      'Admin'),
        ('supervisor', 'Supervisor', 'super@techstore.com',      'supervisor123', 'Supervisor'),
        ('usuario',    'Usuario',    'usuario@techstore.com',    'user123',       'Usuario'),
    ]
    for uname, fname, email, pwd, role in users:
        role_obj = ab.sm.find_role(role)
        existing = ab.sm.find_user(username=uname)
        if existing:
            ab.sm.reset_password(existing.id, pwd)
            print(f"Contrasena actualizada: {uname} / {pwd}")
        else:
            ab.sm.add_user(
                username=uname, first_name=fname, last_name='TechStore',
                email=email, role=role_obj, password=pwd
            )
            print(f"Usuario creado: {uname} / {pwd}")

    # ── Categorias ──────────────────────────────────────────────────────────
    cats_data = [
        ('Teclados',       'Teclados mecanicos, membrana y gaming'),
        ('Mouse',          'Mouse opticos, inalambricos y gaming'),
        ('Auriculares',    'Headsets y auriculares para PC'),
        ('Almacenamiento', 'SSD, HDD y memorias USB'),
        ('Camaras Web',    'Webcams HD y Full HD'),
        ('Cables',         'Cables HDMI, USB, adaptadores'),
    ]
    cats = {}
    for nombre, desc in cats_data:
        c = db.session.query(Categoria).filter_by(nombre=nombre).first()
        if not c:
            c = Categoria(nombre=nombre, descripcion=desc)
            db.session.add(c)
            db.session.flush()
        cats[nombre] = c
    db.session.commit()
    print("Categorias OK")

    # ── Productos con precios en Bolivianos ───────────────────────────────
    productos_data = [
        ('Teclado Mecanico RGB K70',      'Switch Cherry MX Red, retroiluminacion RGB',  620.00, 15, 'Teclados'),
        ('Teclado Membrana Logitech K120','Teclado con cable USB silencioso',             140.00, 40, 'Teclados'),
        ('Mouse Gamer Razer DeathAdder',  '6400 DPI, 7 botones programables',            345.00, 20, 'Mouse'),
        ('Mouse Inalambrico Logitech M705','Bateria 3 anios, receptor unifying',          240.00, 25, 'Mouse'),
        ('Headset HyperX Cloud II',       '7.1 Surround virtual, microfono desmontable', 550.00, 10, 'Auriculares'),
        ('Auriculares Jabra Evolve',      'Cancelacion de ruido activa',                 415.00, 12, 'Auriculares'),
        ('SSD Kingston 480GB',            'SATA III 2.5", 500 MB/s lectura',             380.00, 30, 'Almacenamiento'),
        ('HDD Seagate 1TB',               '5400 RPM, cache 128MB',                       310.00, 18, 'Almacenamiento'),
        ('Memoria USB SanDisk 64GB',      'USB 3.0, velocidad 100 MB/s',                  70.00, 50, 'Almacenamiento'),
        ('Webcam Logitech C920',          'Full HD 1080p, microfono estereo',            550.00, 14, 'Camaras Web'),
        ('Webcam Trust Exis',             '720p HD, clip universal',                     175.00, 22, 'Camaras Web'),
        ('Cable HDMI 2.0 2m',             '4K 60Hz, blindado',                            65.00, 60, 'Cables'),
        ('Hub USB 3.0 7 puertos',         'Con alimentacion externa',                    210.00, 20, 'Cables'),
    ]
    prods = {}
    for nombre, desc, precio, stock, cat in productos_data:
        p = db.session.query(Producto).filter_by(nombre=nombre).first()
        if p:
            p.precio = precio
        else:
            p = Producto(nombre=nombre, descripcion=desc, precio=precio, stock=stock, categoria=cats[cat])
            db.session.add(p)
            db.session.flush()
        prods[nombre] = p
    db.session.commit()
    print("Productos OK (precios en Bs.)")

    # ── Clientes ─────────────────────────────────────────────────────────────
    clientes_data = [
        ('Carlos', 'Mendoza', 'carlos.mendoza@gmail.com', '70011001', 'Av. Montes 123, La Paz'),
        ('Maria',  'Lopez',   'maria.lopez@gmail.com',    '70011002', 'Calle Sucre #45, Cochabamba'),
        ('Jorge',  'Ramirez', 'jorge.ramirez@gmail.com',  '70011003', 'Av. Brasil 78, Santa Cruz'),
        ('Ana',    'Garcia',  'ana.garcia@gmail.com',     '70011004', 'Calle Potosi 200, Oruro'),
        ('Luis',   'Torres',  'luis.torres@gmail.com',    '70011005', 'Av. 6 de Agosto #12, La Paz'),
    ]
    clientes = []
    for nombre, apellido, email, tel, dir in clientes_data:
        c = db.session.query(Cliente).filter_by(email=email).first()
        if not c:
            c = Cliente(nombre=nombre, apellido=apellido, email=email, telefono=tel, direccion=dir)
            db.session.add(c)
            db.session.flush()
        clientes.append(c)
    db.session.commit()
    print("Clientes OK")

    # ── Ordenes con detalles ─────────────────────────────────────────────────
    if db.session.query(Orden).count() == 0:
        prod_list = list(prods.values())
        estados = ['Pagada', 'Pagada', 'Pagada', 'Pendiente', 'Cancelada']
        for i in range(15):
            cliente = random.choice(clientes)
            fecha = datetime.utcnow() - timedelta(days=random.randint(1, 180))
            orden = Orden(fecha=fecha, cliente=cliente, estado=random.choice(estados), total=0)
            db.session.add(orden)
            db.session.flush()
            total = 0
            for _ in range(random.randint(1, 3)):
                prod = random.choice(prod_list)
                qty = random.randint(1, 3)
                subtotal = round(prod.precio * qty, 2)
                total += subtotal
                det = DetalleOrden(orden=orden, producto=prod, cantidad=qty,
                                   precio_unitario=prod.precio, subtotal=subtotal)
                db.session.add(det)
            orden.total = round(total, 2)
        db.session.commit()
        print("Ordenes y detalles creados")

    # ── Servicios Tecnicos ────────────────────────────────────────────────────
    if db.session.query(ServicioTecnico).count() == 0:
        problemas = [
            'PC no enciende', 'Teclado no detectado', 'Mouse con lag',
            'Pantalla negra al iniciar', 'Ruido en auriculares',
            'Webcam no reconocida', 'USB no funciona', 'Sistema lento'
        ]
        estados_srv = ['Pendiente', 'En Proceso', 'Listo', 'Entregado']
        for i in range(12):
            cliente = random.choice(clientes)
            fecha = datetime.utcnow() - timedelta(days=random.randint(1, 90))
            estado = random.choice(estados_srv)
            srv = ServicioTecnico(
                fecha_ingreso=fecha,
                descripcion_problema=random.choice(problemas),
                diagnostico='Revision en proceso' if estado == 'En Proceso' else None,
                costo=round(random.uniform(150, 800), 2) if estado in ['Listo', 'Entregado'] else 0,
                estado=estado,
                cliente=cliente
            )
            db.session.add(srv)
        db.session.commit()
        print("Servicios tecnicos creados")

    print("\nSeed completado.")
    print("  admin       / admin123")
    print("  supervisor  / supervisor123")
    print("  usuario     / user123")
