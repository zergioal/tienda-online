"""
Datos de demo para TechStore.
Ejecutar: python seed_data.py
Regenera ordenes y servicios cada vez que se corre.
"""
from app import create_app, db
from app.models import Categoria, Producto, Cliente, Orden, DetalleOrden, ServicioTecnico
from datetime import datetime, timedelta, timezone

def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)

app = create_app()

with app.app_context():
    ab = app.extensions.get('appbuilder') or __import__('app', fromlist=['appbuilder']).appbuilder

    # ── Roles ────────────────────────────────────────────────────────────────
    for role_name in ['Admin', 'Supervisor', 'Usuario']:
        if not ab.sm.find_role(role_name):
            ab.sm.add_role(role_name)

    # ── Usuarios ─────────────────────────────────────────────────────────────
    users = [
        ('admin',      'Admin',      'admin@techstore.com',   'admin123',      'Admin'),
        ('supervisor', 'Supervisor', 'super@techstore.com',   'supervisor123', 'Supervisor'),
        ('usuario',    'Usuario',    'usuario@techstore.com', 'user123',       'Usuario'),
    ]
    for uname, fname, email, pwd, role in users:
        role_obj = ab.sm.find_role(role)
        existing = ab.sm.find_user(username=uname)
        if existing:
            ab.sm.reset_password(existing.id, pwd)
        else:
            ab.sm.add_user(username=uname, first_name=fname, last_name='TechStore',
                           email=email, role=role_obj, password=pwd)
    print("Usuarios OK")

    # ── Categorias ────────────────────────────────────────────────────────────
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

    # ── Productos ─────────────────────────────────────────────────────────────
    # (nombre, descripcion, precio Bs., stock, categoria)
    productos_data = [
        ('Teclado Mecanico RGB K70',       'Switch Cherry MX Red, retroiluminacion RGB',  620.00, 15, 'Teclados'),
        ('Teclado Membrana Logitech K120', 'Teclado con cable USB silencioso',             140.00, 40, 'Teclados'),
        ('Mouse Gamer Razer DeathAdder',   '6400 DPI, 7 botones programables',            345.00, 20, 'Mouse'),
        ('Mouse Inalambrico Logitech M705','Bateria 3 anios, receptor unifying',           240.00, 25, 'Mouse'),
        ('Headset HyperX Cloud II',        '7.1 Surround virtual, microfono desmontable', 550.00, 10, 'Auriculares'),
        ('Auriculares Jabra Evolve',       'Cancelacion de ruido activa',                 415.00, 12, 'Auriculares'),
        ('SSD Kingston 480GB',             'SATA III 2.5", 500 MB/s lectura',             380.00, 30, 'Almacenamiento'),
        ('HDD Seagate 1TB',                '5400 RPM, cache 128MB',                       310.00, 18, 'Almacenamiento'),
        ('Memoria USB SanDisk 64GB',       'USB 3.0, velocidad 100 MB/s',                  70.00, 50, 'Almacenamiento'),
        ('Webcam Logitech C920',           'Full HD 1080p, microfono estereo',            550.00, 14, 'Camaras Web'),
        ('Webcam Trust Exis',              '720p HD, clip universal',                     175.00, 22, 'Camaras Web'),
        ('Cable HDMI 2.0 2m',              '4K 60Hz, blindado',                            65.00, 60, 'Cables'),
        ('Hub USB 3.0 7 puertos',          'Con alimentacion externa',                    210.00, 20, 'Cables'),
    ]
    prods = {}
    for nombre, desc, precio, stock, cat in productos_data:
        p = db.session.query(Producto).filter_by(nombre=nombre).first()
        if p:
            p.precio = precio
            p.stock  = stock
        else:
            p = Producto(nombre=nombre, descripcion=desc, precio=precio,
                         stock=stock, categoria=cats[cat])
            db.session.add(p)
            db.session.flush()
        prods[nombre] = p
    db.session.commit()
    print("Productos OK")

    # ── Clientes ──────────────────────────────────────────────────────────────
    clientes_data = [
        ('Carlos',   'Mendoza',   'carlos.mendoza@gmail.com',   '70011001', 'Av. Montes 123, La Paz'),
        ('Maria',    'Lopez',     'maria.lopez@gmail.com',      '70011002', 'Calle Sucre 45, Cochabamba'),
        ('Jorge',    'Ramirez',   'jorge.ramirez@gmail.com',    '70011003', 'Av. Brasil 78, Santa Cruz'),
        ('Ana',      'Garcia',    'ana.garcia@gmail.com',       '70011004', 'Calle Potosi 200, Oruro'),
        ('Luis',     'Torres',    'luis.torres@gmail.com',      '70011005', 'Av. 6 de Agosto 12, La Paz'),
        ('Patricia', 'Flores',    'patricia.flores@gmail.com',  '70011006', 'Calle Junin 88, Sucre'),
        ('Roberto',  'Gutierrez', 'roberto.gutierrez@gmail.com','70011007', 'Av. Arce 340, La Paz'),
        ('Daniela',  'Vargas',    'daniela.vargas@gmail.com',   '70011008', 'Calle Bolivar 55, Tarija'),
    ]
    clientes = []
    for nombre, apellido, email, tel, dir in clientes_data:
        c = db.session.query(Cliente).filter_by(email=email).first()
        if not c:
            c = Cliente(nombre=nombre, apellido=apellido, email=email,
                        telefono=tel, direccion=dir)
            db.session.add(c)
            db.session.flush()
        clientes.append(c)
    db.session.commit()
    print("Clientes OK")

    # ── Limpiar ordenes y servicios anteriores ────────────────────────────────
    db.session.query(DetalleOrden).delete()
    db.session.query(Orden).delete()
    db.session.query(ServicioTecnico).delete()
    db.session.commit()

    # ── Ordenes — distribuidas en los ultimos 6 meses ─────────────────────────
    # Script fijo (sin random) para que los graficos siempre se vean igual.
    # Cada tupla: (dias_atras, cliente_idx, estado, [(nombre_prod, cantidad), ...])
    ordenes_script = [
        # Enero (160-180 dias atras)
        (175, 0, 'Pagada',   [('Mouse Gamer Razer DeathAdder', 2), ('Cable HDMI 2.0 2m', 3)]),
        (172, 1, 'Pagada',   [('Teclado Mecanico RGB K70', 1), ('Headset HyperX Cloud II', 1)]),
        (168, 2, 'Pagada',   [('SSD Kingston 480GB', 2)]),
        (165, 3, 'Pagada',   [('Memoria USB SanDisk 64GB', 5), ('Hub USB 3.0 7 puertos', 1)]),
        # Febrero (130-150 dias atras)
        (148, 4, 'Pagada',   [('Webcam Logitech C920', 1), ('Auriculares Jabra Evolve', 1)]),
        (140, 5, 'Pagada',   [('Mouse Inalambrico Logitech M705', 2)]),
        (135, 0, 'Pagada',   [('Teclado Membrana Logitech K120', 3)]),
        (132, 6, 'Cancelada',[('SSD Kingston 480GB', 1)]),
        # Marzo (100-125 dias atras)
        (122, 1, 'Pagada',   [('Mouse Gamer Razer DeathAdder', 1), ('Headset HyperX Cloud II', 1)]),
        (118, 2, 'Pagada',   [('Cable HDMI 2.0 2m', 5), ('Memoria USB SanDisk 64GB', 4)]),
        (110, 7, 'Pagada',   [('Teclado Mecanico RGB K70', 2)]),
        (105, 3, 'Pendiente',[('Webcam Trust Exis', 2)]),
        # Abril (70-95 dias atras)
        (92,  4, 'Pagada',   [('SSD Kingston 480GB', 1), ('HDD Seagate 1TB', 1)]),
        (85,  5, 'Pagada',   [('Mouse Gamer Razer DeathAdder', 3)]),
        (80,  6, 'Pagada',   [('Hub USB 3.0 7 puertos', 2), ('Cable HDMI 2.0 2m', 2)]),
        (75,  0, 'Pagada',   [('Auriculares Jabra Evolve', 1), ('Webcam Logitech C920', 1)]),
        # Mayo (35-65 dias atras)
        (62,  1, 'Pagada',   [('Teclado Mecanico RGB K70', 1), ('Mouse Gamer Razer DeathAdder', 1)]),
        (55,  7, 'Pagada',   [('Memoria USB SanDisk 64GB', 6)]),
        (48,  2, 'Pagada',   [('SSD Kingston 480GB', 2), ('Headset HyperX Cloud II', 1)]),
        (42,  3, 'Pendiente',[('Teclado Membrana Logitech K120', 2)]),
        # Junio (1-30 dias atras)
        (28,  4, 'Pagada',   [('Webcam Logitech C920', 2)]),
        (22,  5, 'Pagada',   [('Mouse Inalambrico Logitech M705', 1), ('Cable HDMI 2.0 2m', 4)]),
        (15,  6, 'Pagada',   [('Mouse Gamer Razer DeathAdder', 2), ('Hub USB 3.0 7 puertos', 1)]),
        (10,  7, 'Pagada',   [('SSD Kingston 480GB', 1), ('Memoria USB SanDisk 64GB', 3)]),
        (5,   0, 'Pendiente',[('Teclado Mecanico RGB K70', 1)]),
        (2,   1, 'Pagada',   [('Auriculares Jabra Evolve', 1)]),
    ]

    for dias, cli_idx, estado, items in ordenes_script:
        fecha = now() - timedelta(days=dias)
        orden = Orden(cliente=clientes[cli_idx], estado=estado, fecha=fecha, total=0)
        db.session.add(orden)
        db.session.flush()
        total = 0
        for nombre_prod, qty in items:
            prod = prods[nombre_prod]
            subtotal = round(prod.precio * qty, 2)
            total += subtotal
            db.session.add(DetalleOrden(
                orden_id=orden.id, producto_id=prod.id,
                cantidad=qty, precio_unitario=prod.precio, subtotal=subtotal
            ))
        orden.total = round(total, 2)
    db.session.commit()
    print(f"Ordenes OK ({len(ordenes_script)} registradas en 6 meses)")

    # ── Servicios Tecnicos ────────────────────────────────────────────────────
    servicios_script = [
        # Entregados (terminados)
        (55, 0, 'Entregado', 'PC no enciende al presionar el boton de encendido',
                             'Fuente de poder danada, se reemplazo', 280.00,
                             now() - timedelta(days=48)),
        (50, 1, 'Entregado', 'Pantalla negra al iniciar Windows',
                             'Drivers de video corruptos, se reinstalo el sistema', 150.00,
                             now() - timedelta(days=44)),
        (40, 2, 'Entregado', 'Teclado no detectado por el sistema',
                             'Puerto USB danado, se cambio el conector', 120.00,
                             now() - timedelta(days=35)),
        (35, 3, 'Entregado', 'Sistema operativo lento y con errores',
                             'Virus y malware, limpieza y reinstalacion', 200.00,
                             now() - timedelta(days=28)),
        # Listos (para recoger)
        (18, 4, 'Listo',     'Ruido extraño en el ventilador del CPU',
                             'Acumulacion de polvo, limpieza profunda realizada', 180.00, None),
        (14, 5, 'Listo',     'Webcam no reconocida en videollamadas',
                             'Driver desactualizado, se actualizo y configuro', 90.00, None),
        (10, 6, 'Listo',     'Mouse con lag y movimiento erratico',
                             'Sensor optico sucio, se limpio y calibro', 80.00, None),
        # En Proceso
        (7,  7, 'En Proceso','No enciende el monitor al conectar la PC',
                             'Diagnostico en curso, se sospecha de tarjeta de video', 0.00, None),
        (5,  0, 'En Proceso','USB no funciona en ninguno de los puertos',
                             'Revisando controladora USB en placa madre', 0.00, None),
        (3,  1, 'En Proceso','Pantalla parpadea con lineas horizontales',
                             'Pendiente verificar cable de video y GPU', 0.00, None),
        # Pendientes
        (2,  2, 'Pendiente', 'PC se apaga sola despues de 10 minutos de uso', None, 0.00, None),
        (1,  3, 'Pendiente', 'No carga Windows, muestra pantalla azul (BSOD)', None, 0.00, None),
        (1,  4, 'Pendiente', 'Teclado escribe doble al presionar una tecla',   None, 0.00, None),
    ]

    for dias, cli_idx, estado, problema, diagnostico, costo, fecha_entrega in servicios_script:
        fecha_ing = now() - timedelta(days=dias)
        srv = ServicioTecnico(
            cliente=clientes[cli_idx],
            fecha_ingreso=fecha_ing,
            descripcion_problema=problema,
            diagnostico=diagnostico,
            costo=costo,
            estado=estado,
            fecha_entrega=fecha_entrega,
        )
        db.session.add(srv)
    db.session.commit()
    print(f"Servicios OK ({len(servicios_script)} registrados)")

    print("")
    print("Demo listo. Credenciales:")
    print("  admin       / admin123")
    print("  supervisor  / supervisor123")
    print("  usuario     / user123")
