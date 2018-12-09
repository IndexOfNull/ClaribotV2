-- phpMyAdmin SQL Dump
-- version 4.5.2
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Dec 09, 2018 at 10:52 PM
-- Server version: 10.1.13-MariaDB
-- PHP Version: 5.6.23

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `Claribot`
--

-- --------------------------------------------------------

--
-- Table structure for table `blacklist_channels`
--

CREATE TABLE `blacklist_channels` (
  `server_id` bigint(32) NOT NULL,
  `channel_id` bigint(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- --------------------------------------------------------

--
-- Table structure for table `blacklist_commands`
--

CREATE TABLE `blacklist_commands` (
  `server_id` bigint(32) NOT NULL,
  `command` mediumtext COLLATE utf8mb4_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- --------------------------------------------------------

--
-- Table structure for table `blacklist_users`
--

CREATE TABLE `blacklist_users` (
  `server_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- --------------------------------------------------------

--
-- Table structure for table `bot_data`
--

CREATE TABLE `bot_data` (
  `var_name` varchar(60) COLLATE utf8mb4_bin NOT NULL,
  `value` mediumtext COLLATE utf8mb4_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

--
-- Dumping data for table `bot_data`
--

INSERT INTO `bot_data` (`var_name`, `value`) VALUES
('fatokens', 'c524e539-2f24-4df4-aeae-478e0a905aee;feacf803-363a-4271-9966-aadbcee2ffce'),
('playing', 'tackleglomps you');

-- --------------------------------------------------------

--
-- Table structure for table `owo_counter`
--

CREATE TABLE `owo_counter` (
  `server_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `count` bigint(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- --------------------------------------------------------

--
-- Table structure for table `personality`
--

CREATE TABLE `personality` (
  `server_id` bigint(32) NOT NULL,
  `personality` mediumtext COLLATE utf8mb4_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- --------------------------------------------------------

--
-- Table structure for table `prefix`
--

CREATE TABLE `prefix` (
  `server_id` bigint(32) NOT NULL,
  `prefix` text COLLATE utf8mb4_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- --------------------------------------------------------

--
-- Table structure for table `server_options`
--

CREATE TABLE `server_options` (
  `server_id` bigint(32) NOT NULL,
  `var` mediumtext COLLATE utf8mb4_bin NOT NULL,
  `value` mediumtext COLLATE utf8mb4_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- --------------------------------------------------------

--
-- Table structure for table `special_users`
--

CREATE TABLE `special_users` (
  `user_id` bigint(32) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- --------------------------------------------------------

--
-- Table structure for table `usage_data`
--

CREATE TABLE `usage_data` (
  `command` varchar(100) COLLATE utf8mb4_bin NOT NULL,
  `amount` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- --------------------------------------------------------

--
-- Table structure for table `user_messages`
--

CREATE TABLE `user_messages` (
  `server_id` bigint(20) NOT NULL,
  `user_id` bigint(20) NOT NULL,
  `message` text COLLATE utf8mb4_bin NOT NULL,
  `id` text COLLATE utf8mb4_bin NOT NULL,
  `timestamp` bigint(20) NOT NULL,
  `type` text COLLATE utf8mb4_bin NOT NULL,
  `been_read` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

-- --------------------------------------------------------

--
-- Table structure for table `warnings`
--

CREATE TABLE `warnings` (
  `server_id` bigint(32) NOT NULL,
  `user_id` bigint(32) NOT NULL,
  `reason` text COLLATE utf8mb4_bin NOT NULL,
  `warner` bigint(32) NOT NULL,
  `timestamp` bigint(32) NOT NULL,
  `issue_id` varchar(20) COLLATE utf8mb4_bin NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `blacklist_channels`
--
ALTER TABLE `blacklist_channels`
  ADD KEY `server_id` (`server_id`),
  ADD KEY `channel_id` (`channel_id`);

--
-- Indexes for table `blacklist_commands`
--
ALTER TABLE `blacklist_commands`
  ADD KEY `command_blacklist_serverid_index` (`server_id`);

--
-- Indexes for table `blacklist_users`
--
ALTER TABLE `blacklist_users`
  ADD KEY `server_id` (`server_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `bot_data`
--
ALTER TABLE `bot_data`
  ADD PRIMARY KEY (`var_name`);

--
-- Indexes for table `owo_counter`
--
ALTER TABLE `owo_counter`
  ADD KEY `server_id` (`server_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `personality`
--
ALTER TABLE `personality`
  ADD KEY `server_id` (`server_id`);

--
-- Indexes for table `prefix`
--
ALTER TABLE `prefix`
  ADD KEY `server_id` (`server_id`);

--
-- Indexes for table `server_options`
--
ALTER TABLE `server_options`
  ADD KEY `server_id` (`server_id`);

--
-- Indexes for table `special_users`
--
ALTER TABLE `special_users`
  ADD PRIMARY KEY (`user_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `usage_data`
--
ALTER TABLE `usage_data`
  ADD PRIMARY KEY (`command`);

--
-- Indexes for table `user_messages`
--
ALTER TABLE `user_messages`
  ADD KEY `user_id` (`user_id`),
  ADD KEY `server_id` (`server_id`),
  ADD KEY `been_read` (`been_read`),
  ADD KEY `timestamp` (`timestamp`);

--
-- Indexes for table `warnings`
--
ALTER TABLE `warnings`
  ADD KEY `server_id` (`server_id`),
  ADD KEY `user_id` (`user_id`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
