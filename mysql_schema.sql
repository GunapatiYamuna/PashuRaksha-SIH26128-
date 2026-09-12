CREATE DATABASE IF NOT EXISTS pashuraksha CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; USE pashuraksha;
CREATE TABLE users(id BIGINT AUTO_INCREMENT PRIMARY KEY,username VARCHAR(100) UNIQUE NOT NULL,password_hash VARCHAR(255) NOT NULL,role VARCHAR(50) NOT NULL,active BOOLEAN DEFAULT TRUE,created_at DATETIME);
\1,\n  animal_tag_id VARCHAR(128)\2);
CREATE INDEX idx_reports_district ON reports(district); CREATE INDEX idx_reports_risk ON reports(risk_level); CREATE INDEX idx_reports_created ON reports(created_at);
