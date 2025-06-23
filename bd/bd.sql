-- Tabla de usuarios
CREATE TABLE users (
    id INT PRIMARY KEY IDENTITY,
    name NVARCHAR(100) NOT NULL,
    email NVARCHAR(100) NOT NULL UNIQUE,
    password_hash NVARCHAR(256) NOT NULL,
    role NVARCHAR(20) NOT NULL CHECK (role IN ('admin', 'cliente', 'operador')),
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    valido int NOT NULL,
    verification_token UNIQUEIDENTIFIER DEFAULT NEWID()
);

-- Tabla de zonas de camping
CREATE TABLE zones (
    id INT PRIMARY KEY IDENTITY,
    name NVARCHAR(100) NOT NULL,
    geojson NVARCHAR(MAX) NOT NULL,
    size_m2 FLOAT NOT NULL,
    capacity INT NOT NULL,
    terrain_type NVARCHAR(50),
    rules NVARCHAR(MAX),
    main_image_url NVARCHAR(500),
    nearby_features NVARCHAR(MAX),
    current_state NVARCHAR(20) NOT NULL CHECK (current_state IN ('disponible', 'reservado', 'ocupado')),
    precio DECIMAL(7,2) NOT NULL
);

-- Reservas
CREATE TABLE reservations (
    id INT PRIMARY KEY IDENTITY,
    user_id INT NOT NULL,
    zone_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status NVARCHAR(20) NOT NULL CHECK (status IN ('pendiente', 'pagado', 'cancelado')),
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    activado int,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (zone_id) REFERENCES zones(id) ON DELETE CASCADE
);

-- Archivos multimedia asociados a zonas
CREATE TABLE images (
    id INT PRIMARY KEY IDENTITY,
    zone_id INT NOT NULL,
    url NVARCHAR(500) NOT NULL,
    type NVARCHAR(20) NOT NULL CHECK (type IN ('foto', 'video', 'pdf', 'audio')),
    FOREIGN KEY (zone_id) REFERENCES zones(id) ON DELETE CASCADE
);

-----V2 Cambios para la version 2.0
-- Tabla de Servicios
CREATE TABLE services (
    id INT PRIMARY KEY IDENTITY,
    name NVARCHAR(100) NOT NULL,
    icon NVARCHAR(100), -- opcional: para iconos tipo "fa-tree", "fa-bath", etc.
);

-- Tabla de Servicios por Zona
CREATE TABLE zone_services (
    id INT PRIMARY KEY IDENTITY,
    zone_id INT NOT NULL,
    service_id INT NOT NULL,
    FOREIGN KEY (zone_id) REFERENCES zones(id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
);

INSERT INTO services (name, icon) VALUES 
('Estacionamiento', 'fa-product-hunt'), 
('Baños', 'fa-bath'),
('Estacionamiento', 'fa-product-hunt'), 
('Agua potable', 'fa-tint'),
('Zona de Fogatas', 'fa-fire'),
('Wifi', 'fa-wifi'),
('Buena Recepcion', 'fa-signal'),
('Senderos', 'fa-tree'),
('Mascotas permitidas', 'fa-paw'),
('Zona de picnic', 'fa-cutlery'),
('Actividades recreativas', 'fa-gamepad'),
('Alquiler de equipo', 'fa-bicycle'),
('Guías turísticos', 'fa-users'),
('Restaurante', 'fa-cutlery'),
('Tienda de conveniencia', 'fa-shopping-cart'),
('Transporte al campamento', 'fa-bus'),
('Museos', 'fa-university'),
('Zona de pesca', 'fa-fish'),
('Zona de natación', 'fa-swimming-pool'),
('Zona de deportes acuáticos', 'fa-anchor'),
('Zona de fotografía', 'fa-camera'),
('Zona de relajación', 'fa-bed'),
('Frente al Lago', 'fa-globe');