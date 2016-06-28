create database plugin_doctor;
use plugin_doctor;

CREATE TABLE `plugin_doctor`.`header_info` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `hook_id` VARCHAR(128) NULL,
  `timestamps` INT NULL,
  `tag` VARCHAR(128) NULL,
  `sequence` INT NULL,
  `client_request` VARCHAR(4096) NULL,
  `server_request` VARCHAR(4096) NULL,
  `server_response` VARCHAR(4096) NULL,
  `client_response` VARCHAR(4096) NULL,
  PRIMARY KEY (`id`));


