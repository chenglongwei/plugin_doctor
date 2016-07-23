create database plugin_doctor;
use plugin_doctor;

CREATE TABLE `header_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `state_machine_id` int(22) DEFAULT NULL,
  `plugin_name` varchar(1024) DEFAULT NULL,
  `sequence` int(11) DEFAULT NULL,
  `timestamps` int(11) DEFAULT NULL,
  `hook_id` varchar(128) DEFAULT NULL,
  `tag` varchar(128) DEFAULT NULL,
  `client_request` varchar(4096) DEFAULT NULL,
  `server_request` varchar(4096) DEFAULT NULL,
  `server_response` varchar(4096) DEFAULT NULL,
  `client_response` varchar(4096) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
