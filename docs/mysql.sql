-- Create database
CREATE DATABASE IF NOT EXISTS site_analyzer CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE site_analyzer;

-- User table
CREATE TABLE IF NOT EXISTS t_user (
    id BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique user identifier',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT 'User email address',
    password_hash VARCHAR(255) NOT NULL COMMENT 'Hashed password',
    role TINYINT NOT NULL DEFAULT 2 COMMENT 'User role. 1:ADMIN. 2:USER.',
    status TINYINT NOT NULL DEFAULT 1 COMMENT 'Account status. 1:ACTIVE. 2:LOCKED.',
    last_login DATETIME NULL COMMENT 'Last login timestamp',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Account creation timestamp',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Modification timestamp'
);

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