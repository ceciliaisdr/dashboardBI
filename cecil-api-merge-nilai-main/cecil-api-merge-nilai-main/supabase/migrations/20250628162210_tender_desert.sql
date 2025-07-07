-- Create additional users and permissions if needed
CREATE USER IF NOT EXISTS 'student_api'@'%' IDENTIFIED BY 'password123';
GRANT ALL PRIVILEGES ON mahasiswa_db.* TO 'student_api'@'%';

-- Set MySQL configuration for better performance
SET GLOBAL innodb_buffer_pool_size = 256M;
SET GLOBAL max_connections = 200;
SET GLOBAL query_cache_size = 32M;
SET GLOBAL query_cache_type = ON;

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS mahasiswa_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

FLUSH PRIVILEGES;