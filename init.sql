-- AquaHub - Inicialización de Base de Datos
-- Este script se ejecuta automáticamente cuando el contenedor de PostgreSQL inicia por primera vez

-- Habilitar extensiones
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- Crear tipos enum
CREATE TYPE estado_pedido AS ENUM ('pendiente', 'aceptado', 'en_transito', 'entregado', 'cancelado');
CREATE TYPE tipo_incidente AS ENUM ('fuga', 'sin_agua', 'contaminacion', 'infraestructura', 'otro');
CREATE TYPE estado_incidente AS ENUM ('pendiente', 'reconocido', 'en_progreso', 'resuelto');
CREATE TYPE intensidad_demanda AS ENUM ('baja', 'media', 'alta', 'critica');
CREATE TYPE tipo_alerta AS ENUM ('escasez', 'conservacion', 'programa', 'emergencia');

-- Tabla de Proveedores (Pipas)
CREATE TABLE proveedores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(255) NOT NULL,
    calificacion DECIMAL(2,1) DEFAULT 0.0,
    precio_por_litro DECIMAL(10,2) NOT NULL,
    tiempo_estimado_llegada VARCHAR(50),
    latitud DECIMAL(10,8),
    longitud DECIMAL(11,8),
    direccion TEXT,
    colonia VARCHAR(255),
    alcaldia VARCHAR(255),
    tamano_flota INTEGER DEFAULT 1,
    disponible BOOLEAN DEFAULT true,
    certificaciones TEXT[],
    telefono VARCHAR(20),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Ciudadanos
CREATE TABLE ciudadanos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(255) NOT NULL,
    telefono VARCHAR(20),
    correo VARCHAR(255),
    latitud DECIMAL(10,8),
    longitud DECIMAL(11,8),
    direccion TEXT,
    colonia VARCHAR(255),
    alcaldia VARCHAR(255),
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Pedidos de Agua
CREATE TABLE pedidos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    proveedor_id UUID REFERENCES proveedores(id),
    ciudadano_id UUID REFERENCES ciudadanos(id),
    nombre_ciudadano VARCHAR(255),
    latitud DECIMAL(10,8),
    longitud DECIMAL(11,8),
    direccion TEXT,
    colonia VARCHAR(255),
    alcaldia VARCHAR(255),
    cantidad_litros INTEGER NOT NULL,
    precio_total DECIMAL(10,2) NOT NULL,
    subsidio_aplicado DECIMAL(10,2) DEFAULT 0.00,
    estado estado_pedido DEFAULT 'pendiente',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aceptado_en TIMESTAMP,
    entregado_en TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Reportes de Incidentes
CREATE TABLE incidentes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ciudadano_id UUID REFERENCES ciudadanos(id),
    tipo tipo_incidente NOT NULL,
    latitud DECIMAL(10,8),
    longitud DECIMAL(11,8),
    direccion TEXT,
    colonia VARCHAR(255),
    alcaldia VARCHAR(255),
    descripcion TEXT,
    hogares_afectados INTEGER DEFAULT 1,
    duracion VARCHAR(100),
    estado estado_incidente DEFAULT 'pendiente',
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reconocido_en TIMESTAMP,
    resuelto_en TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Puntos de Demanda
CREATE TABLE puntos_demanda (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    latitud DECIMAL(10,8),
    longitud DECIMAL(11,8),
    direccion TEXT,
    colonia VARCHAR(255),
    alcaldia VARCHAR(255),
    intensidad intensidad_demanda DEFAULT 'baja',
    cantidad_solicitudes INTEGER DEFAULT 0,
    registrado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Alertas Públicas
CREATE TABLE alertas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    titulo VARCHAR(255) NOT NULL,
    mensaje TEXT NOT NULL,
    zonas_objetivo TEXT[],
    cantidad_destinatarios INTEGER DEFAULT 0,
    tipo tipo_alerta NOT NULL,
    enviado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de Programas de Subsidio
CREATE TABLE programas_subsidio (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nombre VARCHAR(255) NOT NULL,
    presupuesto DECIMAL(12,2) NOT NULL,
    gastado DECIMAL(12,2) DEFAULT 0.00,
    beneficiarios INTEGER DEFAULT 0,
    porcentaje_descuento INTEGER NOT NULL,
    criterios_elegibilidad TEXT,
    activo BOOLEAN DEFAULT true,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Crear índices para consultas comunes
CREATE INDEX idx_pedidos_estado ON pedidos(estado);
CREATE INDEX idx_pedidos_proveedor ON pedidos(proveedor_id);
CREATE INDEX idx_pedidos_creado ON pedidos(creado_en DESC);
CREATE INDEX idx_incidentes_estado ON incidentes(estado);
CREATE INDEX idx_incidentes_tipo ON incidentes(tipo);
CREATE INDEX idx_incidentes_creado ON incidentes(creado_en DESC);
CREATE INDEX idx_proveedores_disponible ON proveedores(disponible);
CREATE INDEX idx_demanda_intensidad ON puntos_demanda(intensidad);

-- Insertar proveedores de ejemplo
INSERT INTO proveedores (nombre, calificacion, precio_por_litro, tiempo_estimado_llegada, latitud, longitud, direccion, colonia, alcaldia, tamano_flota, disponible, certificaciones, telefono) VALUES
('Agua Pura del Valle', 4.8, 0.15, '30-45 min', 19.4326, -99.1332, 'Av. Insurgentes Sur 1234', 'Del Valle', 'Benito Juárez', 12, true, ARRAY['ISO 9001', 'Certificación COFEPRIS'], '55-1234-5678'),
('HidroExpress CDMX', 4.5, 0.12, '45-60 min', 19.4200, -99.1500, 'Calle Reforma 567', 'Juárez', 'Cuauhtémoc', 8, true, ARRAY['Certificación COFEPRIS'], '55-2345-6789'),
('Pipas La Esperanza', 4.2, 0.10, '1-2 hrs', 19.3600, -99.1800, 'Av. Universidad 890', 'Copilco', 'Coyoacán', 5, true, ARRAY['Registro Municipal'], '55-3456-7890'),
('AquaRápido', 4.9, 0.18, '20-30 min', 19.4500, -99.1200, 'Paseo de la Reforma 1000', 'Polanco', 'Miguel Hidalgo', 15, true, ARRAY['ISO 9001', 'ISO 14001', 'Certificación COFEPRIS'], '55-4567-8901'),
('Distribuidora Tlalpan', 3.9, 0.08, '2-3 hrs', 19.2900, -99.1700, 'Calzada de Tlalpan 2345', 'Tlalpan Centro', 'Tlalpan', 3, true, ARRAY['Registro Municipal'], '55-5678-9012');

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO aquahub;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO aquahub;
