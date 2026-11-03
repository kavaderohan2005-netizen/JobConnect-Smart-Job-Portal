-- ===================================================================
-- JobConnect – Smart Job Portal Database Schema (MySQL 8.0+)
-- Database: jobconnect_db
-- ===================================================================

CREATE DATABASE IF NOT EXISTS `jobconnect_db` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE `jobconnect_db`;

-- Drop existing tables with respect to foreign keys
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `contact_messages`;
DROP TABLE IF EXISTS `notifications`;
DROP TABLE IF EXISTS `saved_jobs`;
DROP TABLE IF EXISTS `applications`;
DROP TABLE IF EXISTS `resumes`;
DROP TABLE IF EXISTS `jobs`;
DROP TABLE IF EXISTS `employers`;
DROP TABLE IF EXISTS `job_seekers`;
DROP TABLE IF EXISTS `companies`;
DROP TABLE IF EXISTS `categories`;
DROP TABLE IF EXISTS `users`;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. Table: users
CREATE TABLE `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(80) NOT NULL UNIQUE,
  `email` VARCHAR(120) NOT NULL UNIQUE,
  `password_hash` VARCHAR(255) NOT NULL,
  `role` ENUM('job_seeker', 'employer', 'admin') NOT NULL DEFAULT 'job_seeker',
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
  `avatar` VARCHAR(255) NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX `idx_users_role` (`role`),
  INDEX `idx_users_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Table: companies
CREATE TABLE `companies` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(150) NOT NULL UNIQUE,
  `logo` VARCHAR(255) DEFAULT 'default_company.png',
  `website` VARCHAR(200) NULL,
  `location` VARCHAR(100) NULL,
  `industry` VARCHAR(100) NULL,
  `company_size` VARCHAR(50) NULL,
  `description` TEXT NULL,
  `founded_year` INT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Table: categories
CREATE TABLE `categories` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL UNIQUE,
  `slug` VARCHAR(100) NOT NULL UNIQUE,
  `icon` VARCHAR(80) DEFAULT 'fa-briefcase',
  `description` TEXT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Table: job_seekers
CREATE TABLE `job_seekers` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL UNIQUE,
  `full_name` VARCHAR(120) NOT NULL,
  `headline` VARCHAR(200) NULL,
  `phone` VARCHAR(20) NULL,
  `location` VARCHAR(100) NULL,
  `bio` TEXT NULL,
  `github_url` VARCHAR(200) NULL,
  `linkedin_url` VARCHAR(200) NULL,
  `portfolio_url` VARCHAR(200) NULL,
  `skills` TEXT NULL,
  `experience_years` FLOAT DEFAULT 0.0,
  `current_company` VARCHAR(120) NULL,
  `current_salary` VARCHAR(50) NULL,
  `expected_salary` VARCHAR(50) NULL,
  `education_data` LONGTEXT NULL,
  `experience_data` LONGTEXT NULL,
  `projects_data` LONGTEXT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_job_seekers_user` FOREIGN KEY (`user_id`) 
    REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Table: employers
CREATE TABLE `employers` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL UNIQUE,
  `company_id` INT NULL,
  `full_name` VARCHAR(120) NOT NULL,
  `designation` VARCHAR(100) NULL,
  `phone` VARCHAR(20) NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_employers_user` FOREIGN KEY (`user_id`) 
    REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_employers_company` FOREIGN KEY (`company_id`) 
    REFERENCES `companies` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Table: jobs
CREATE TABLE `jobs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `employer_id` INT NOT NULL,
  `company_id` INT NOT NULL,
  `category_id` INT NULL,
  `title` VARCHAR(150) NOT NULL,
  `description` LONGTEXT NOT NULL,
  `requirements` TEXT NULL,
  `benefits` TEXT NULL,
  `job_type` VARCHAR(50) NOT NULL DEFAULT 'Full-time',
  `work_mode` VARCHAR(50) NOT NULL DEFAULT 'Hybrid',
  `experience_level` VARCHAR(50) NOT NULL DEFAULT 'Mid Level',
  `min_salary` INT NOT NULL DEFAULT 0,
  `max_salary` INT NOT NULL DEFAULT 0,
  `location` VARCHAR(100) NOT NULL,
  `skills_required` TEXT NULL,
  `openings` INT NOT NULL DEFAULT 1,
  `status` ENUM('active', 'closed', 'pending_approval') NOT NULL DEFAULT 'active',
  `views_count` INT NOT NULL DEFAULT 0,
  `deadline` DATE NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX `idx_jobs_title` (`title`),
  INDEX `idx_jobs_location` (`location`),
  INDEX `idx_jobs_status` (`status`),
  CONSTRAINT `fk_jobs_employer` FOREIGN KEY (`employer_id`) 
    REFERENCES `employers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_jobs_company` FOREIGN KEY (`company_id`) 
    REFERENCES `companies` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_jobs_category` FOREIGN KEY (`category_id`) 
    REFERENCES `categories` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Table: resumes
CREATE TABLE `resumes` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `seeker_id` INT NOT NULL,
  `original_filename` VARCHAR(255) NOT NULL,
  `stored_filename` VARCHAR(255) NOT NULL,
  `file_path` VARCHAR(300) NOT NULL,
  `file_size` INT NOT NULL DEFAULT 0,
  `is_primary` BOOLEAN NOT NULL DEFAULT TRUE,
  `uploaded_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_resumes_seeker` FOREIGN KEY (`seeker_id`) 
    REFERENCES `job_seekers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Table: applications
CREATE TABLE `applications` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `job_id` INT NOT NULL,
  `seeker_id` INT NOT NULL,
  `resume_id` INT NULL,
  `cover_letter` TEXT NULL,
  `status` ENUM('applied', 'under_review', 'shortlisted', 'interview', 'rejected', 'accepted') NOT NULL DEFAULT 'applied',
  `recruiter_notes` TEXT NULL,
  `applied_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX `idx_applications_status` (`status`),
  CONSTRAINT `fk_applications_job` FOREIGN KEY (`job_id`) 
    REFERENCES `jobs` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_applications_seeker` FOREIGN KEY (`seeker_id`) 
    REFERENCES `job_seekers` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_applications_resume` FOREIGN KEY (`resume_id`) 
    REFERENCES `resumes` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. Table: saved_jobs
CREATE TABLE `saved_jobs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `job_id` INT NOT NULL,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uq_user_saved_job` (`user_id`, `job_id`),
  CONSTRAINT `fk_saved_jobs_user` FOREIGN KEY (`user_id`) 
    REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_saved_jobs_job` FOREIGN KEY (`job_id`) 
    REFERENCES `jobs` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. Table: notifications
CREATE TABLE `notifications` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `title` VARCHAR(150) NOT NULL,
  `message` TEXT NOT NULL,
  `link` VARCHAR(200) NULL,
  `is_read` BOOLEAN NOT NULL DEFAULT FALSE,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_notifications_user` FOREIGN KEY (`user_id`) 
    REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 11. Table: contact_messages
CREATE TABLE `contact_messages` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(120) NOT NULL,
  `subject` VARCHAR(200) NOT NULL,
  `message` TEXT NOT NULL,
  `is_resolved` BOOLEAN NOT NULL DEFAULT FALSE,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
