-- Create database
CREATE DATABASE IF NOT EXISTS site_analyzer CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE site_analyzer;

-- User table
CREATE TABLE IF NOT EXISTS t_user (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique user identifier',
    provider VARCHAR(100) NOT NULL COMMENT 'OIDC provider name (e.g., cognito, keycloak)',
    sub VARCHAR(255) NOT NULL COMMENT 'OIDC subject identifier',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT 'User email address',
    password_hash VARCHAR(255) NOT NULL COMMENT 'Hashed password',
    role TINYINT NOT NULL DEFAULT 2 COMMENT 'User role. 1:ADMIN. 2:USER.',
    status TINYINT NOT NULL DEFAULT 1 COMMENT 'Account status. 1:ACTIVE. 2:LOCKED.',
    last_login DATETIME NULL COMMENT 'Last login timestamp',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Account creation timestamp',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Modification timestamp'
);
CREATE UNIQUE INDEX user_provider_sub_idx ON t_user(provider, sub);

-- MapTask table
CREATE TABLE IF NOT EXISTS t_map_task (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique map task identifier',
    user_id BIGINT NOT NULL COMMENT 'Reference to the user who created the map task',
    name VARCHAR(150) NOT NULL COMMENT 'Name of the map task',
    district VARCHAR(10) NOT NULL COMMENT 'District identifier for the map task',
    status TINYINT NOT NULL DEFAULT 1 COMMENT 'Task status. 1:Pending, 2:Processing, 3:Success, 4:Failure, 5:Cancelled',
    error_msg VARCHAR(255) NULL COMMENT 'Error message if the task fails',
    constraint_factors TEXT NOT NULL COMMENT 'JSON describing constraint factors',
    suitability_factors TEXT NOT NULL COMMENT 'JSON describing suitability factors',
    started_at DATETIME NULL COMMENT 'Task start timestamp',
    ended_at DATETIME NULL COMMENT 'Task end timestamp',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Task creation timestamp',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last modification timestamp'
);

-- MapTaskFiles table
CREATE TABLE IF NOT EXISTS t_map_task_files (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique file record identifier',
    user_id BIGINT NOT NULL COMMENT 'Reference to the user who created the map task',
    map_task_id BIGINT NOT NULL COMMENT 'Reference to the related map task',
    file_type VARCHAR(15) NOT NULL COMMENT 'Type of file (e.g., constraint,suitability,final )',
    file_path VARCHAR(255) NOT NULL COMMENT 'Path to the file in the storage system',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'File upload timestamp',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last modification timestamp'
);

-- MapTaskProgress table (append-only progress events; no foreign keys by project policy)
CREATE TABLE IF NOT EXISTS t_map_task_progress (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique progress record identifier',
    map_task_id BIGINT NOT NULL COMMENT 'Related map task identifier',
    percent TINYINT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Progress percentage (0-100)',
    description VARCHAR(255) NULL COMMENT 'Brief progress description',
    phase VARCHAR(50) NULL COMMENT 'Optional phase tag (e.g., restrict, score, combine)',
    error_msg VARCHAR(255) NULL COMMENT 'Optional error information for failure/cancel events',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Progress record creation timestamp',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last modification timestamp'
);

-- Helpful index for retrieving the latest progress entries quickly
CREATE INDEX IF NOT EXISTS idx_map_task_progress_task_time ON t_map_task_progress(map_task_id, created_at);