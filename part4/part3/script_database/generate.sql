-- Table User
CREATE TABLE users (
    id CHAR(36) PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    is_admin BOOLEAN DEFAULT FALSE
);

-- Table Place
CREATE TABLE places (
    id CHAR(36) PRIMARY KEY,
    title VARCHAR(255),
    description TEXT,
    price DECIMAL(10, 2),
    latitude FLOAT,
    longitude FLOAT,
    owner_id CHAR(36),
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table Review
CREATE TABLE reviews (
    id CHAR(36) PRIMARY KEY,
    text TEXT,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    user_id CHAR(36),
    place_id CHAR(36),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE,
    UNIQUE (user_id, place_id)
);

-- Table Amenity
CREATE TABLE amenities (
    id CHAR(36) PRIMARY KEY,
    name VARCHAR(255) UNIQUE
);

-- Table Place_Amenity (Association Many-to-Many)
CREATE TABLE amenities_places (
    place_id CHAR(36),
    amenity_id CHAR(36),
    PRIMARY KEY (place_id, amenity_id),
    FOREIGN KEY (place_id) REFERENCES places(id) ON DELETE CASCADE,
    FOREIGN KEY (amenity_id) REFERENCES amenities(id) ON DELETE CASCADE
);

-- Insert Administrator User
INSERT INTO users (id, email, first_name, last_name, password, is_admin) VALUES 
('36c9050e-ddd3-4c3b-9731-9f487208bbc1', 'admin@hbnb.io', 'Admin', 'HBnB', '$2b$12$XXXXXXXXXXXXXXX', TRUE);

-- Insert Initial Amenities
INSERT INTO amenities (id, name) VALUES
(UUID(), 'WiFi'),
(UUID(), 'Swimming Pool'),
(UUID(), 'Air Conditioning');

-- Vérifier les Tables
SELECT name FROM sqlite_master WHERE type='table';

-- Insérer un lieu
INSERT INTO places (id, title, description, price, latitude, longitude, owner_id) 
VALUES 
(UUID(), 'Luxury Villa', 'Beautiful beachfront villa', 250.00, 40.7128, -74.0060, '36c9050e-ddd3-4c3b-9731-9f487208bbc1');

-- Insérer un avis
INSERT INTO reviews (id, text, rating, user_id, place_id) 
VALUES 
(UUID(), 'Amazing place!', 5, '36c9050e-ddd3-4c3b-9731-9f487208bbc1', (SELECT id FROM places LIMIT 1));

-- Associer une commodité à un lieu
INSERT INTO amenities_places (place_id, amenity_id) 
VALUES 
((SELECT id FROM places LIMIT 1), (SELECT id FROM amenities WHERE name='WiFi'));

-- Lister les utilisateurs
SELECT * FROM users;

-- Lister les lieux
SELECT * FROM places;

-- Lister les avis d'un lieu
SELECT * FROM reviews WHERE place_id = (SELECT id FROM places LIMIT 1);

-- Lister les commodités d'un lieu
SELECT a.name 
FROM amenities a 
JOIN amenities_places ap ON a.id = ap.amenity_id 
WHERE ap.place_id = (SELECT id FROM places LIMIT 1);

-- Mettre à jour le titre d’un lieu
UPDATE places 
SET title = 'Luxury Villa Updated' 
WHERE id = (SELECT id FROM places LIMIT 1);

-- Modifier la note d’un avis
UPDATE reviews 
SET rating = 4 
WHERE id = (SELECT id FROM reviews LIMIT 1);

-- Supprimer un avis
DELETE FROM reviews WHERE id = (SELECT id FROM reviews LIMIT 1);

-- Supprimer une commodité d'un lieu
DELETE FROM amenities_places 
WHERE place_id = (SELECT id FROM places LIMIT 1) 
AND amenity_id = (SELECT id FROM amenities WHERE name='WiFi');

-- Supprimer un lieu
DELETE FROM places WHERE id = (SELECT id FROM places LIMIT 1);

-- Tester la contrainte d'unicité sur les avis
INSERT INTO reviews (id, text, rating, user_id, place_id) 
VALUES 
(UUID(), 'Another review', 3, '36c9050e-ddd3-4c3b-9731-9f487208bbc1', (SELECT id FROM places LIMIT 1)); -- Doit échouer

SELECT * FROM reviews;
