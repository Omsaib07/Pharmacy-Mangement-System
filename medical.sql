-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jan 24, 2023 at 08:31 AM
-- Server version: 10.4.11-MariaDB
-- PHP Version: 7.2.29
Create database Medical;
USE Medical;
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `medical`
--

-- --------------------------------------------------------

--
-- Table structure for table `addmp`
--

CREATE TABLE `addmp` (
  `sno` int(11) NOT NULL,
  `medicine` varchar(500) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `addmp`
--

INSERT INTO `addmp` (`sno`, `medicine`) VALUES
(1, 'Dolo 650'),
(2, 'Carpel 250 mg'),
(3, 'Azythromycin 500'),
(4, 'Azythromycin 250'),
(5, 'Rantac 300'),
(6, 'Omez'),
(7, 'Okacet'),
(8, 'Paracetomol');

-- --------------------------------------------------------

--
-- Table structure for table `addpd`
--

CREATE TABLE `addpd` (
  `sno` int(11) NOT NULL,
  `product` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `addpd`
--

INSERT INTO `addpd` (`sno`, `product`) VALUES
(1, 'colgate'),
(2, 'perfume'),
(3, 'garnier face wash'),
(4, 'garnier face wash');

-- --------------------------------------------------------

--
-- Table structure for table `logs`
--

CREATE TABLE `logs` (
  `id` int(11) NOT NULL,
  `mid` int(11) NOT NULL,
  `action` varchar(500) NOT NULL,
  `date` varchar(500) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `logs`
--

INSERT INTO `logs` (`id`, `mid`, `action`, `date`) VALUES
(1, 1001, ' INSERTED', '2023-01-24 12:54:41'),
(2, 1001, ' DELETED', '2023-01-24 12:57:48');

-- --------------------------------------------------------

--
-- Table structure for table `medicines`
--

CREATE TABLE `medicines` (
  `id` int(11) NOT NULL,
  `amount` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `medicines` varchar(500) NOT NULL,
  `products` varchar(500) NOT NULL,
  `email` varchar(50) NOT NULL,
  `mid` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Triggers `medicines`
--
DELIMITER $$
CREATE TRIGGER `Delete` BEFORE DELETE ON `medicines` FOR EACH ROW INSERT INTO Logs VALUES(null,OLD.mid,' DELETED',NOW())
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `Insert` AFTER INSERT ON `medicines` FOR EACH ROW INSERT INTO Logs VALUES(null,NEW.mid,' INSERTED',NOW())
$$
DELIMITER ;
DELIMITER $$
CREATE TRIGGER `Update` AFTER UPDATE ON `medicines` FOR EACH ROW INSERT INTO Logs VALUES(null,NEW.mid,' UPDATED',NOW())
$$
DELIMITER ;

DELIMITER //

CREATE TRIGGER check_negative_quantity
BEFORE INSERT ON medicines
FOR EACH ROW
BEGIN
    IF NEW.mid < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Negative values cannot be inserted into the quantity column.';
    END IF;
END//

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `posts`
--

CREATE TABLE `posts` (
  `mid` int(11) NOT NULL,
  `medical_name` varchar(100) NOT NULL,
  `owner_name` varchar(100) NOT NULL,
  `phone_no` varchar(20) NOT NULL,
  `address` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `posts`
--

INSERT INTO `posts` (`mid`, `medical_name`, `owner_name`, `phone_no`, `address`) VALUES
(1001, 'ARK PROCODER MEDICAL', 'ANEES', '7896541230', 'Bangalore');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `addmp`
--
ALTER TABLE `addmp`
  ADD PRIMARY KEY (`sno`);

--
-- Indexes for table `addpd`
--
ALTER TABLE `addpd`
  ADD PRIMARY KEY (`sno`);

--
-- Indexes for table `logs`
--
ALTER TABLE `logs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `medicines`
--
ALTER TABLE `medicines`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `posts`
--
ALTER TABLE `posts`
  ADD PRIMARY KEY (`mid`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `addmp`
--
ALTER TABLE `addmp`
  MODIFY `sno` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `addpd`
--
ALTER TABLE `addpd`
  MODIFY `sno` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `logs`
--
ALTER TABLE `logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `medicines`
--
ALTER TABLE `medicines`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--


ALTER TABLE addmp ADD COLUMN quantity INT DEFAULT 0;
ALTER TABLE addpd ADD COLUMN quantity INT DEFAULT 0;

-- AUTO_INCREMENT for table `posts`
--

ALTER TABLE `posts`
  MODIFY `mid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1002;
COMMIT;

DELIMITER //

CREATE PROCEDURE upsert_medicine(IN med_name VARCHAR(500), IN new_quantity INT)
BEGIN
    DECLARE existing_id INT;

    -- Check if the medicine exists
    SELECT id INTO existing_id
    FROM Medicines
    WHERE name = med_name;

    -- If it exists, update the quantity; if not, insert a new row
    IF existing_id IS NOT NULL THEN
        UPDATE Medicines
        SET amount = amount + new_quantity
        WHERE id = existing_id;
    ELSE
        INSERT INTO Medicines (name, amount)
        VALUES (med_name, new_quantity);
    END IF;
END //

DELIMITER ;
CREATE TABLE Users (
    id INT AUTO_INCREMENT PRIMARY KEY,   -- Primary key for unique identification
    username VARCHAR(255) NOT NULL UNIQUE, -- Username column, unique for each user
    password VARCHAR(255) NOT NULL,       -- Password column, storing password
    role ENUM('admin', 'user') DEFAULT 'user' -- Role column, either 'admin' or 'user', default is 'user'
);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
