-- Creación de la base de datos
CREATE DATABASE QCM;
\c QCM;

-- Tabla USUARIO (tabla base)
CREATE TABLE USUARIO (
    id_usuario SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    contrasena VARCHAR(255) NOT NULL
);

-- Tabla ADMINISTRADOR (hereda de USUARIO)
CREATE TABLE ADMINISTRADOR (
    id_usuario INT PRIMARY KEY,
    acceso BOOLEAN NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario) ON DELETE CASCADE
);

-- Tabla CLIENTE (hereda de USUARIO)
CREATE TABLE CLIENTE (
    id_usuario INT PRIMARY KEY,
    saldo INT NOT NULL DEFAULT 0 CHECK (saldo >= 0),
    excliente BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario) ON DELETE CASCADE
);

-- Tabla TIPO_ARCHIVO
CREATE TABLE TIPO_ARCHIVO (
    id_tipo_archivo SERIAL PRIMARY KEY,
    extension VARCHAR(10) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    formato VARCHAR(50) NOT NULL
);

-- Tabla CATEGORIA
CREATE TABLE CATEGORIA (
    id_categoria SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    id_categoria_padre INT,
    FOREIGN KEY (id_categoria_padre) REFERENCES CATEGORIA(id_categoria)
);

-- Tabla PROMOCION
CREATE TABLE PROMOCION (
    id_promocion SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descuento INT NOT NULL CHECK (descuento >= 0 AND descuento <= 100),
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    CHECK (fecha_fin >= fecha_inicio)
);

-- Tabla CONTENIDO
CREATE TABLE CONTENIDO (
    id_contenido SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    autor VARCHAR(100) NOT NULL,
    precio INT NOT NULL CHECK (precio >= 0),
    descripcion TEXT,
    tamano_archivo FLOAT NOT NULL CHECK (tamano_archivo > 0),
    archivo BYTEA NOT NULL,
    id_tipo_archivo INT NOT NULL,
    id_categoria INT NOT NULL,
    id_promocion INT,
    FOREIGN KEY (id_tipo_archivo) REFERENCES TIPO_ARCHIVO(id_tipo_archivo),
    FOREIGN KEY (id_categoria) REFERENCES CATEGORIA(id_categoria),
    FOREIGN KEY (id_promocion) REFERENCES PROMOCION(id_promocion)
);

-- Tabla CARRITO
CREATE TABLE CARRITO (
    id_carrito SERIAL PRIMARY KEY,
    descuento_aplicado INT DEFAULT 0 CHECK (descuento_aplicado >= 0),
    id_usuario INT NOT NULL UNIQUE,
    FOREIGN KEY (id_usuario) REFERENCES CLIENTE(id_usuario)
);

-- Tabla CONTENIDO_CARRITO (relación N:M)
CREATE TABLE CONTENIDO_CARRITO (
    id_contenido INT NOT NULL,
    id_carrito INT NOT NULL,
    cantidad INT NOT NULL DEFAULT 1 CHECK (cantidad > 0),
    PRIMARY KEY (id_contenido, id_carrito),
    FOREIGN KEY (id_contenido) REFERENCES CONTENIDO(id_contenido),
    FOREIGN KEY (id_carrito) REFERENCES CARRITO(id_carrito)
);

-- Tabla COMPRA
CREATE TABLE COMPRA (
    id_compra SERIAL PRIMARY KEY,
    fecha_y_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_usuario INT NOT NULL,
    id_contenido INT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES CLIENTE(id_usuario),
    FOREIGN KEY (id_contenido) REFERENCES CONTENIDO(id_contenido)
);

-- Tabla REGALO
CREATE TABLE REGALO (
    id_regalo SERIAL PRIMARY KEY,
    abierto BOOLEAN NOT NULL DEFAULT FALSE,
    id_compra INT UNIQUE,
    id_usuario_envia INT NOT NULL,
    id_usuario_recibe INT NOT NULL,
    id_contenido INT NOT NULL,
    FOREIGN KEY (id_compra) REFERENCES COMPRA(id_compra),
    FOREIGN KEY (id_usuario_envia) REFERENCES CLIENTE(id_usuario),
    FOREIGN KEY (id_usuario_recibe) REFERENCES CLIENTE(id_usuario),
    FOREIGN KEY (id_contenido) REFERENCES CONTENIDO(id_contenido),
    CHECK (id_usuario_envia != id_usuario_recibe)
);

-- Tabla DESCARGA
CREATE TABLE DESCARGA (
    id_descarga SERIAL PRIMARY KEY,
    fecha_y_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_usuario INT NOT NULL,
    id_contenido INT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES CLIENTE(id_usuario),
    FOREIGN KEY (id_contenido) REFERENCES CONTENIDO(id_contenido)
);

-- Tabla RANKING
CREATE TABLE RANKING (
    id_ranking SERIAL PRIMARY KEY,
    fecha DATE NOT NULL,
    tipo VARCHAR(20) NOT NULL,
    posicion_actual INT NOT NULL CHECK (posicion_actual > 0),
    posicion_anterior INT CHECK (posicion_anterior > 0),
    tipo_ranking VARCHAR(20) NOT NULL CHECK (tipo_ranking IN ('contenido', 'cliente'))
);

-- Tabla RANKING_CONTENIDO
CREATE TABLE RANKING_CONTENIDO (
    id_ranking_contenido SERIAL PRIMARY KEY,
    id_ranking INT NOT NULL,
    id_contenido INT NOT NULL,
    FOREIGN KEY (id_ranking) REFERENCES RANKING(id_ranking),
    FOREIGN KEY (id_contenido) REFERENCES CONTENIDO(id_contenido),
    UNIQUE (id_ranking, id_contenido)
);

-- Tabla RANKING_CLIENTE
CREATE TABLE RANKING_CLIENTE (
    id_ranking_cliente SERIAL PRIMARY KEY,
    id_ranking INT NOT NULL,
    id_usuario INT NOT NULL,
    FOREIGN KEY (id_ranking) REFERENCES RANKING(id_ranking),
    FOREIGN KEY (id_usuario) REFERENCES CLIENTE(id_usuario),
    UNIQUE (id_ranking, id_usuario)
);

-- Tabla VALORACION
CREATE TABLE VALORACION (
    id_valoracion SERIAL PRIMARY KEY,
    fecha TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    puntuacion DECIMAL(2,1) NOT NULL CHECK (puntuacion >= 0 AND puntuacion <= 1),
    id_usuario INT NOT NULL,
    id_contenido INT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES CLIENTE(id_usuario),
    FOREIGN KEY (id_contenido) REFERENCES CONTENIDO(id_contenido),
    UNIQUE (id_usuario, id_contenido)
);

-- Índices para mejorar el rendimiento
CREATE INDEX idx_contenido_tipo ON CONTENIDO(id_tipo_archivo);
CREATE INDEX idx_contenido_categoria ON CONTENIDO(id_categoria);
CREATE INDEX idx_contenido_promocion ON CONTENIDO(id_promocion);
CREATE INDEX idx_valoracion_contenido ON VALORACION(id_contenido);
CREATE INDEX idx_valoracion_usuario ON VALORACION(id_usuario);
CREATE INDEX idx_descarga_usuario ON DESCARGA(id_usuario);
CREATE INDEX idx_descarga_contenido ON DESCARGA(id_contenido);
CREATE INDEX idx_compra_usuario ON COMPRA(id_usuario);
CREATE INDEX idx_regalo_usuario_recibe ON REGALO(id_usuario_recibe);
CREATE INDEX idx_regalo_contenido ON REGALO(id_contenido);

-- Agregar la columna id_descarga
ALTER TABLE VALORACION ADD COLUMN id_descarga INT NOT NULL;

-- Agregar la FK a DESCARGA
ALTER TABLE VALORACION ADD CONSTRAINT fk_valoracion_descarga FOREIGN KEY (id_descarga) REFERENCES DESCARGA(id_descarga);

-- Agregar la nueva restricción UNIQUE
ALTER TABLE VALORACION ADD CONSTRAINT valoracion_unica UNIQUE (id_usuario, id_contenido, id_descarga);