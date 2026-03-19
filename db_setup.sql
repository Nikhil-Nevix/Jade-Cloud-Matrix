-- JADE Cloud Matrix Database Setup Script
-- Run this as PostgreSQL superuser (postgres) before starting the application

-- Create database user
CREATE USER jade_user WITH PASSWORD 'jade_pass';

-- Create database
CREATE DATABASE jade_db OWNER jade_user;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE jade_db TO jade_user;

-- Connect to the database
\c jade_db

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO jade_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO jade_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO jade_user;

-- Note: Alembic migrations will create all tables and enums
-- Run: cd backend && alembic upgrade head
