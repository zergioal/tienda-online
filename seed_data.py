"""
Carga datos de prueba y crea los usuarios/roles por defecto.
Ejecutar una sola vez: python seed_data.py
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
    print("Roles creados")

    # ── Usuarios ────────────────────────────────────────────────────────────
    users = [
        ('admin',      'Admin',      'admin@techstore.com',      'Admin123!',  'Admin'),
        ('supervisor', 'Supervisor', 'super@techstore.com',      'Super123!',  'Supervisor'),
        ('usuario',    'Usuario',    'usuario@techstore.com',    'User123!',   'Usuario'),
    ]
    for uname, fname, email, pwd, role in users:
        if not ab.sm.find_user(username=uname):
            role_obj = ab.sm.find_role(role)
            ab.sm.add_user(
                username=uname, first_name=fname, last_name='TechStore',
                email=email, role=role_obj, password=pwd
            )
            print(f"Usuario creado: {uname} / {pwd}")

    # ── Categorías ──────────────────────────────────────────────────────────
    cats_data = [
        ('Teclados',    'Teclados mecánicos, membrana y gaming'),
        ('Mouse',       'Mouse ópticos, inalámbricos y gaming'),
        ('Auriculares', 'Headsets y auriculares para PC'),
        ('Almacenamiento', 'SSD, HDD y memorias USB'),
        ('Cámaras Web', 'Webcams HD y Full HD'),
        ('Cables',      'Cables HDMI, USB, adaptadores'),
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
    print("Categorías creadas")

    # ── Productos ────────────────────────────────────────────────────────────
    productos_data = [
        ('Teclado Mecánico RGB K70',     'Switch Cherry MX Red, retroiluminación RGB',       89.99,  15, 'Teclados'),
        ('Teclado Membrana Logitech K120', 'Teclado con cable USB silencioso',                19.99,  40, 'Teclados'),
        ('Mouse Gamer Razer DeathAdder',  '6400 DPI, 7 botones programables',                49.99,  20, 'Mouse'),
        ('Mouse Inalámbrico Logitech M705','Batería 3 años, receptor unifying',               34.99,  25, 'Mouse'),
        ('Headset HyperX Cloud II',       '7.1 Surround virtual, micrófono desmontable',      79.99,  10, 'Auriculares'),
        ('Auriculares Jabra Evolve',      'Cancelación de ruido activa',                      59.99,  12, 'Auriculares'),
        ('SSD Kingston 480GB',            'SATA III 2.5", 500 MB/s lectura',                  54.99,  30, 'Almacenamiento'),
        ('HDD Seagate 1TB',               '5400 RPM, caché 128MB',                            44.99,  18, 'Almacenamiento'),
        ('Memoria USB SanDisk 64GB',      'USB 3.0, velocidad 100 MB/s',                       9.99,  50, 'Almacenamiento'),
        ('Webcam Logitech C920',          'Full HD 1080p, micrófono estéreo',                 79.99,  14, 'Cámaras Web'),
        ('Webcam Trust Exis',             '720p HD, clip universal',                          24.99,  22, 'Cámaras Web'),
        ('Cable HDMI 2.0 2m',             '4K 60Hz, blindado',                                 8.99,  60, 'Cables'),
        ('Hub USB 3.0 7 puertos',         'Con alimentación externa',                         29.99,  20, 'Cables'),
    ]
    prods = {}
    for nombre, desc, precio, stock, cat in productos_data:
        p = db.session.query(Producto).filter_by(nombre=nombre).first()
        if not p:
            p = Producto(nombre=nombre, descripcion=desc, precio=precio, stock=stock, categoria=cats[cat])
            db.session.add(p)
            db.session.flush()
        prods[nombre] = p
    db.session.commit()
    print("Productos creados")

    # ── Clientes ─────────────────────────────────────────────────────────────
    clientes_data = [
        ('Carlos',  'Mendoza',  'carlos.mendoza@gmail.com',   '555-1001', 'Av. Principal 123'),
        ('María',   'López',    'maria.lopez@gmail.com',      '555-1002', 'Calle 5 #45'),
        ('Jorge',   'Ramírez',  'jorge.ramirez@gmail.com',    '555-1003', 'Col. Centro 78'),
        ('Ana',     'García',   'ana.garcia@gmail.com',       '555-1004', 'Blvd. Norte 200'),
        ('Luis',    'Torres',   'luis.torres@gmail.com',      '555-1005', 'Calle 8 #12'),
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
    print("Clientes creados")

    # ── Órdenes con detalles ─────────────────────────────────────────────────
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
        print("Órdenes y detalles creados")

    # ── Servicios Técnicos ────────────────────────────────────────────────────
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
                diagnostico='Revisión en proceso' if estado in ['En Proceso'] else None,
                costo=round(random.uniform(20, 150), 2) if estado in ['Listo', 'Entregado'] else 0,
                estado=estado,
                cliente=cliente
            )
            db.session.add(srv)
        db.session.commit()
        print("Servicios técnicos creados")

    print("\n✓ Seed completado exitosamente.")
    print("  admin / Admin123!")
    print("  supervisor / Super123!")
    print("  usuario / User123!")
