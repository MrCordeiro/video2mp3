CREATE ROLE auth_user WITH LOGIN PASSWORD 'Auth123';

CREATE DATABASE auth;
GRANT ALL PRIVILEGES ON DATABASE auth TO auth_user;

\connect auth;

CREATE TABLE "user" (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL
);

-- Fixtures
INSERT INTO "user" VALUES (DEFAULT, 'test@email.com', 'fake_pwd');