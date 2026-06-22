from . import db
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime


class Categoria(db.Model):
    __tablename__ = 'categoria'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text)
    productos = relationship('Producto', back_populates='categoria')

    def __repr__(self):
        return self.nombre


class Producto(db.Model):
    __tablename__ = 'producto'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text)
    precio = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    categoria_id = Column(Integer, ForeignKey('categoria.id'), nullable=False)
    categoria = relationship('Categoria', back_populates='productos')
    detalles = relationship('DetalleOrden', back_populates='producto')

    def __repr__(self):
        return self.nombre


class Cliente(db.Model):
    __tablename__ = 'cliente'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    telefono = Column(String(20))
    direccion = Column(Text)
    ordenes = relationship('Orden', back_populates='cliente')
    servicios = relationship('ServicioTecnico', back_populates='cliente')

    def __repr__(self):
        return f'{self.nombre} {self.apellido}'


class Orden(db.Model):
    __tablename__ = 'orden'
    id = Column(Integer, primary_key=True)
    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
    total = Column(Float, default=0.0)
    estado = Column(String(20), default='Pendiente')
    cliente_id = Column(Integer, ForeignKey('cliente.id'), nullable=False)
    cliente = relationship('Cliente', back_populates='ordenes')
    detalles = relationship('DetalleOrden', back_populates='orden', cascade='all, delete-orphan')

    def __repr__(self):
        return f'Orden #{self.id}'


class DetalleOrden(db.Model):
    __tablename__ = 'detalle_orden'
    id = Column(Integer, primary_key=True)
    cantidad = Column(Integer, nullable=False, default=1)
    precio_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    orden_id = Column(Integer, ForeignKey('orden.id'), nullable=False)
    producto_id = Column(Integer, ForeignKey('producto.id'), nullable=False)
    orden = relationship('Orden', back_populates='detalles')
    producto = relationship('Producto', back_populates='detalles')

    def __repr__(self):
        return f'Detalle #{self.id}'


class ServicioTecnico(db.Model):
    __tablename__ = 'servicio_tecnico'
    id = Column(Integer, primary_key=True)
    fecha_ingreso = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_entrega = Column(DateTime)
    descripcion_problema = Column(Text, nullable=False)
    diagnostico = Column(Text)
    costo = Column(Float, default=0.0)
    estado = Column(String(20), default='Pendiente')
    cliente_id = Column(Integer, ForeignKey('cliente.id'), nullable=False)
    cliente = relationship('Cliente', back_populates='servicios')

    def __repr__(self):
        return f'Servicio #{self.id} - {self.estado}'
