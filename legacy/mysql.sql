SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

DROP TABLE IF EXISTS `feeds`;
CREATE TABLE IF NOT EXISTS `feeds` (
  `id` int(6) NOT NULL auto_increment,
  `uri` varchar(255) character set latin1 NOT NULL,
  `filter` enum('1','2','3') character set latin1 NOT NULL,
  `format` enum('0','1') collate utf8_unicode_ci NOT NULL default '0',
  `description` varchar(1000) character set latin1 NOT NULL,
  `active` enum('0','1') character set latin1 NOT NULL default '1',
  PRIMARY KEY  (`id`),
  UNIQUE KEY `uri` (`uri`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

DROP TABLE IF EXISTS `items`;
CREATE TABLE IF NOT EXISTS `items` (
  `id` int(6) NOT NULL auto_increment,
  `link` varchar(1000) character set latin1 NOT NULL,
  `feed_id` int(6) NOT NULL,
  `title` varchar(1000) character set latin1 NOT NULL,
  `description` text collate utf8_unicode_ci,
  `time_published` datetime NOT NULL,
  `time_found` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `link` (`link`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
