# Database

## Introduction

This document describes the database for the `Solar Power Site Suitability Analysis Platform`, including the schema design and implementation SQL for MySQL (which will be used for this project). The main domains in this system are `User` and `MapTask`.
**Note:** Foreign keys will not be used in this project.

## Design

### `User` schema

**Table Name: `t_user`**
**Composite unique index: (provider, sub)**

| Column Name   | Data Type    | Constraints                                           | Description                                      |
| ------------- | ------------ | ----------------------------------------------------- | ------------------------------------------------ |
| id            | BIGINT       | PRIMARY KEY, AUTO_INCREMENT                           | Unique user identifier                           |
| provider      | VARCHAR(100) | NOT NULL                                              | OIDC provider name (e.g., 'cognito', 'keycloak') |
| sub           | VARCHAR(255) | NOT NULL                                              | OIDC subject identifier                          |
| email         | VARCHAR(100) | NOT NULL, UNIQUE                                      | User's email address                             |
| password_hash | VARCHAR(255) | NOT NULL                                              | Hashed password                                  |
| role          | TINYINT      | NOT NULL, DEFAULT 2                                   | User role. 1:ADMIN. 2:USER.                      |
| status        | TINYINT      | NOT NULL, DEFAULT 1                                   | Account status. 1:ACTIVE. 2:LOCKED.              |
| last_login    | DATETIME     | NULL                                                  | Last login timestamp                             |
| created_at    | DATETIME     | DEFAULT CURRENT_TIMESTAMP                             | Account creation timestamp                       |
| updated_at    | DATETIME     | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Modification timestamp                           |

### `MapTask` schema

**Table Name: `t_map_task`**
| Column Name | Data Type | Constraints | Description |
| ------------------- | ------------ | ------------------------------------------- | --------------------------------------------------- |
| id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | Unique map task identifier |
| user_id | BIGINT | NOT NULL | Reference to the user who created the map task |
| name | VARCHAR(150) | NOT NULL | Name of the map task |
| district | VARCHAR(10) | NOT NULL | District identifier for the map task |
| status | TINYINT | NOT NULL, DEFAULT 1 | Task status. 1:Pending, 2:Processing, 3:Success, 4:Failure, 5:Cancelled |
| error_msg | VARCHAR(255) | NULL | Error message if the task fails |
| constraint_factors | TEXT | NOT NULL | JSON describing constraint factors |
| suitability_factors | TEXT | NOT NULL | JSON describing suitability factors |
| started_at | DATETIME | NULL | Task start timestamp |
| ended_at | DATETIME | NULL | Task end timestamp |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | Task creation timestamp |
| updated_at | DATETIME | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Last modification timestamp |

### `MapTaskFiles` schema

**Table Name: `t_map_task_files`**

| Column Name | Data Type    | Constraints                                           | Description                                        |
| ----------- | ------------ | ----------------------------------------------------- | -------------------------------------------------- |
| id          | BIGINT       | PRIMARY KEY, AUTO_INCREMENT                           | Unique file record identifier                      |
| user_id     | BIGINT       | NOT NULL                                              | Reference to the user who created the map task     |
| map_task_id | BIGINT       | NOT NULL                                              | Reference to the related map task                  |
| file_type   | VARCHAR(15)  | NOT NULL                                              | Type of file (e.g., constraint,suitability,final ) |
| file_path   | VARCHAR(255) | NOT NULL                                              | Path to the file in the storage system             |
| created_at  | DATETIME     | DEFAULT CURRENT_TIMESTAMP                             | File upload timestamp                              |
| updated_at  | DATETIME     | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Last modification timestamp                        |

### `MapTaskProgress` schema

**Table Name: `t_map_task_progress`**

| Column Name | Data Type    | Constraints                                           | Description                                                |
| ----------- | ------------ | ----------------------------------------------------- | ---------------------------------------------------------- |
| id          | BIGINT       | PRIMARY KEY, AUTO_INCREMENT                           | Unique progress record identifier                          |
| user_id     | BIGINT       | NOT NULL                                              | Reference to the user who created the map task             |
| map_task_id | BIGINT       | NOT NULL                                              | Related map task identifier                                |
| percent     | TINYINT      | NOT NULL, DEFAULT 0                                   | Progress percentage (0–100)                                |
| description | VARCHAR(255) | NULL                                                  | Brief progress description (e.g., current phase or action) |
| phase       | VARCHAR(50)  | NULL                                                  | Optional phase tag (e.g., 'restrict', 'score', 'combine')  |
| error_msg   | VARCHAR(255) | NULL                                                  | Optional error information for failure/cancel events       |
| created_at  | DATETIME     | DEFAULT CURRENT_TIMESTAMP                             | Progress record creation timestamp                         |
| updated_at  | DATETIME     | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | Last modification timestamp                                |

> Note: This table is append-only to preserve progress history. No foreign keys are defined (consistent with project policy). Consider indexing `(map_task_id, created_at)` for efficient retrieval of the latest progress entries.

## SQL

### MySQL

**Database Name: site_analyzer**
**Database charset: utf8mb4**

[SQL File](./mysql.sql)
