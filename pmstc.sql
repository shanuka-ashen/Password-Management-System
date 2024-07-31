-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Feb 28, 2024 at 01:30 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `pmstc`
--

-- --------------------------------------------------------

--
-- Table structure for table `login`
--

CREATE TABLE `login` (
  `username` varchar(50) NOT NULL,
  `password` varchar(200) NOT NULL,
  `role` varchar(50) NOT NULL,
  `attempts` int(20) NOT NULL DEFAULT 3
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `login`
--

INSERT INTO `login` (`username`, `password`, `role`, `attempts`) VALUES
('', '', '', 3),
('Shanuka', 'pbkdf2:sha256:600000$XTNNyrmQsKWsnVTk$eba026337a2326c9f7ffcbc98933a0889086aa66b26e4ade80629e9445c6fb63', 'TL', 3),
('Kawya', 'pbkdf2:sha256:600000$4Gvi5UA4wmhiK1ne$c210072e96035dcb89374d044986fba1fd2ce8e40d40193af03bb31925cecd41', 'TM', 3),
('Mahesha', 'pbkdf2:sha256:600000$iifqRtxjY0xwKAT2$d6e65a776c094deabdcbeec32d321cc622854eae063391329b5c5fad1d2e2c0b', 'A', 3),
('Virajanie', 'pbkdf2:sha256:600000$B0kxlC2WtgemybHI$13ccea42945ff4d64b88c5871510c5ce3c2387c32784887fa69f3ebe3b927ea3', 'TL', 3),
('Ashen', 'pbkdf2:sha256:600000$faX2rYdPZSaB1MAv$c20484f258a9618335efe57a9204b48b128bf9c56ee2f6f7de28a1fdca42b5a2', 'U', 3);

-- --------------------------------------------------------

--
-- Table structure for table `passwords`
--

CREATE TABLE `passwords` (
  `projectname` varchar(100) NOT NULL,
  `purpose` varchar(200) NOT NULL,
  `password` varchar(300) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `passwords`
--

INSERT INTO `passwords` (`projectname`, `purpose`, `password`) VALUES
('Mobile', 'App 1', 'fJGcrWp3gfTFBNzWT4D1SNbNR288sU6ru+Cu4hshOZc='),
('Mobile', 'App 2 ', '6A9KXdpqCLTQyyvuMYjFJf0VUCqzS5DF+NFh/MDzx00='),
('Network', 'HQ', 'KKGU2IL0uEp8wTGjN99bATBK1rC39SRxsDF9bFfAb1w=');

-- --------------------------------------------------------

--
-- Table structure for table `project`
--

CREATE TABLE `project` (
  `name` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `project`
--

INSERT INTO `project` (`name`) VALUES
('Mobile'),
('PT'),
('Network');

-- --------------------------------------------------------

--
-- Table structure for table `userpasswords`
--

CREATE TABLE `userpasswords` (
  `username` varchar(100) NOT NULL,
  `purpose` varchar(100) NOT NULL,
  `password` varchar(500) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `userpasswords`
--

INSERT INTO `userpasswords` (`username`, `purpose`, `password`) VALUES
('mahesha', 'HRIS', 'dZ9vpqAvCFef6rDTKyo79rqz9D5DMp/TU7ypQhu6nVI='),
('Ashen', 'App 1', 'SWnaUOUysYC0rY8qR59Bs4CW6bg5u8Pi8XzRzcg8csM='),
('Ashen', 'HDD', 'd0u/bcSTjUXQ1ggUDO2U/ZHTRgsB8x4IEl5iotbIAi0='),
('Kawya', 'Social', 'eTMc1gf+CvCmmH7iHGth2Sq/iu94UjX/ZWDSmiPTGRw=');

-- --------------------------------------------------------

--
-- Table structure for table `userprojects`
--

CREATE TABLE `userprojects` (
  `username` varchar(100) NOT NULL,
  `projectname` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `userprojects`
--

INSERT INTO `userprojects` (`username`, `projectname`) VALUES
('Virajanie', 'PT'),
('Shanuka', 'Mobile'),
('Kawya', 'Mobile'),
('Mahesha', 'Network'),
('Shanuka', 'Network'),
('Kawya', 'PT');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
