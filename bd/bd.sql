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
