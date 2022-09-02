/*
 Navicat Premium Data Transfer

 Source Server         : aliyun
 Source Server Type    : MySQL
 Source Server Version : 50735
 Source Host           : zhaosheng.mysql.rds.aliyuncs.com:27546
 Source Schema         : si2

 Target Server Type    : MySQL
 Target Server Version : 50735
 File Encoding         : 65001

 Date: 26/08/2022 02:27:06
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for hit
-- ----------------------------
DROP TABLE IF EXISTS `hit`;
CREATE TABLE `hit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `phone` varchar(128) NOT NULL,
  `file_url` varchar(256) NOT NULL,
  `preprocessed_file_url` varchar(256) NOT NULL,
  `province` varchar(10) DEFAULT NULL,
  `city` varchar(10) DEFAULT NULL,
  `phone_type` varchar(10) DEFAULT NULL,
  `area_code` varchar(10) DEFAULT NULL,
  `zip_code` varchar(10) DEFAULT NULL,
  `self_test_score_mean` float DEFAULT NULL,
  `self_test_score_min` float DEFAULT NULL,
  `self_test_score_max` float DEFAULT NULL,
  `call_begintime` datetime DEFAULT NULL,
  `call_endtime` datetime DEFAULT NULL,
  `span_time` int(11) DEFAULT NULL,
  `class_number` int(11) DEFAULT NULL,
  `hit_time` datetime DEFAULT NULL,
  `blackbase_phone` varchar(1280) DEFAULT NULL,
  `blackbase_id` varchar(12) DEFAULT NULL,
  `hit_status` int(11) DEFAULT NULL,
  `hit_score` varchar(512) DEFAULT NULL,
  `top_10` varchar(1280) DEFAULT NULL,
  `valid_length` int(11) DEFAULT NULL,
  `is_grey` int(11) DEFAULT '0',
  PRIMARY KEY (`id`,`phone`,`file_url`,`preprocessed_file_url`),
  UNIQUE KEY `phone` (`phone`),
  UNIQUE KEY `file_url` (`file_url`),
  UNIQUE KEY `preprocessed_file_url` (`preprocessed_file_url`)
) ENGINE=InnoDB AUTO_INCREMENT=8998 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for log
-- ----------------------------
DROP TABLE IF EXISTS `log`;
CREATE TABLE `log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `phone` varchar(128) DEFAULT NULL,
  `time` datetime DEFAULT NULL,
  `action_type` int(11) DEFAULT NULL,
  `err_type` int(11) DEFAULT NULL,
  `file_url` varchar(256) DEFAULT NULL,
  `preprocessed_file_url` varchar(256) DEFAULT NULL,
  `message` varchar(128) DEFAULT NULL,
  `valid_length` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=46182 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for speaker
-- ----------------------------
DROP TABLE IF EXISTS `speaker`;
CREATE TABLE `speaker` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(10) DEFAULT NULL,
  `file_url` varchar(256) NOT NULL,
  `preprocessed_file_url` varchar(256) NOT NULL,
  `phone` varchar(128) NOT NULL,
  `register_time` datetime DEFAULT NULL,
  `province` varchar(10) DEFAULT NULL,
  `city` varchar(10) DEFAULT NULL,
  `phone_type` varchar(10) DEFAULT NULL,
  `area_code` varchar(10) DEFAULT NULL,
  `zip_code` varchar(10) DEFAULT NULL,
  `self_test_score_mean` float DEFAULT NULL,
  `self_test_score_min` float DEFAULT NULL,
  `self_test_score_max` float DEFAULT NULL,
  `call_begintime` datetime DEFAULT NULL,
  `call_endtime` datetime DEFAULT NULL,
  `delete_time` datetime DEFAULT NULL,
  `span_time` int(11) DEFAULT NULL,
  `status` int(11) DEFAULT NULL,
  `class_number` int(11) DEFAULT NULL,
  `hit_count` int(11) DEFAULT NULL,
  `input_reason` int(11) DEFAULT NULL,
  `delete_reason` int(11) DEFAULT NULL,
  `delete_remark` varchar(255) DEFAULT NULL,
  `valid_length` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`,`file_url`,`preprocessed_file_url`,`phone`),
  UNIQUE KEY `file_url` (`file_url`),
  UNIQUE KEY `preprocessed_file_url` (`preprocessed_file_url`),
  UNIQUE KEY `phone` (`phone`)
) ENGINE=InnoDB AUTO_INCREMENT=11495 DEFAULT CHARSET=utf8;

SET FOREIGN_KEY_CHECKS = 1;
