-- Database Schema Generated from SQLAlchemy Models


CREATE TABLE features (
	id BIGSERIAL NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (name)
);

CREATE INDEX ix_features_id ON features (id);

CREATE TABLE users (
	id BIGSERIAL NOT NULL, 
	full_name VARCHAR(255) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	phone_number VARCHAR(50),
	hashed_password VARCHAR(255) NOT NULL, 
	role VARCHAR(20), 
	is_active BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id)
);

CREATE INDEX ix_users_id ON users (id);

CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE TABLE properties (
	id BIGSERIAL NOT NULL, 
	title VARCHAR(255) NOT NULL, 
	slug VARCHAR(255) NOT NULL, 
	description TEXT NOT NULL, 
	property_type VARCHAR(50) NOT NULL, 
	listing_type VARCHAR(20) NOT NULL, 
	status VARCHAR(20), 
	price NUMERIC(15, 2) NOT NULL, 
	currency VARCHAR(10), 
	area NUMERIC(10, 2), 
	bedrooms INTEGER, 
	bathrooms INTEGER, 
	kitchens INTEGER, 
	living_rooms INTEGER, 
	floors INTEGER, 
	floor_number INTEGER, 
	country VARCHAR(100) NOT NULL, 
	state VARCHAR(100), 
	city VARCHAR(100) NOT NULL, 
	neighborhood VARCHAR(150), 
	address TEXT, 
	postal_code VARCHAR(20), 
	latitude NUMERIC(10, 8), 
	longitude NUMERIC(11, 8), 
	is_featured BOOLEAN, 
	published_at TIMESTAMP WITHOUT TIME ZONE, 
	rent_start_date TIMESTAMP WITHOUT TIME ZONE, 
	rent_end_date TIMESTAMP WITHOUT TIME ZONE, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	owner_id BIGINT, 
	agent_id BIGINT, 
	buyer_id BIGINT, 
	PRIMARY KEY (id), 
	FOREIGN KEY(owner_id) REFERENCES users (id) ON DELETE SET NULL, 
	FOREIGN KEY(agent_id) REFERENCES users (id) ON DELETE SET NULL,
	FOREIGN KEY(buyer_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE UNIQUE INDEX ix_properties_slug ON properties (slug);

CREATE INDEX ix_properties_id ON properties (id);

CREATE TABLE property_features (
	property_id BIGINT NOT NULL, 
	feature_id BIGINT NOT NULL, 
	PRIMARY KEY (property_id, feature_id), 
	FOREIGN KEY(property_id) REFERENCES properties (id) ON DELETE CASCADE, 
	FOREIGN KEY(feature_id) REFERENCES features (id) ON DELETE CASCADE
);

CREATE TABLE property_images (
	id BIGSERIAL NOT NULL, 
	property_id BIGINT, 
	image_url VARCHAR NOT NULL, 
	is_primary BOOLEAN, 
	created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(), 
	PRIMARY KEY (id), 
	FOREIGN KEY(property_id) REFERENCES properties (id) ON DELETE CASCADE
);

CREATE INDEX ix_property_images_id ON property_images (id);



CREATE TABLE visits (
    id BIGSERIAL PRIMARY KEY,
    property_id BIGINT REFERENCES properties(id) ON DELETE CASCADE,
    client_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    agent_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    visit_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    status VARCHAR(50) DEFAULT 'scheduled',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);


