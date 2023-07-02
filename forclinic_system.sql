-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- Generation Time: May 17, 2023 at 01:59 AM
-- Server version: 10.4.25-MariaDB
-- PHP Version: 7.4.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `clinic_system`
--

-- --------------------------------------------------------

--
-- Table structure for table `disabled_dates`
--

CREATE TABLE `disabled_dates` (
  `ids` int(11) NOT NULL,
  `date` date NOT NULL,
  `Title` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `disabled_dates`
--

INSERT INTO `disabled_dates` (`ids`, `date`, `Title`) VALUES
(25, '2023-05-19', 'Date Unavailable');

-- --------------------------------------------------------

--
-- Table structure for table `disabled_dates_dental`
--

CREATE TABLE `disabled_dates_dental` (
  `id` int(11) NOT NULL,
  `date` date NOT NULL,
  `Title` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `disabled_dates_dental`
--

INSERT INTO `disabled_dates_dental` (`id`, `date`, `Title`) VALUES
(12, '2023-05-18', 'Date Unavailable'),
(13, '2023-05-22', 'Date Unavailable'),
(14, '2023-05-29', 'Date Unavailable'),
(15, '2023-05-17', 'Date Unavailable'),
(16, '2023-05-24', 'Date Unavailable'),
(17, '2023-05-31', 'Date Unavailable'),
(18, '2023-05-25', 'Date Unavailable'),
(19, '2023-05-19', 'Date Unavailable'),
(20, '2023-05-26', 'Date Unavailable'),
(21, '2023-06-05', 'Date Unavailable');

-- --------------------------------------------------------

--
-- Table structure for table `m_information`
--

CREATE TABLE `m_information` (
  `id` int(11) NOT NULL,
  `ID_Number` varchar(150) NOT NULL,
  `name` varchar(150) NOT NULL,
  `password` varchar(150) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `m_information`
--

INSERT INTO `m_information` (`id`, `ID_Number`, `name`, `password`) VALUES
(1, '10-00000', 'Admin', 'admin');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_adminapprover`
--

CREATE TABLE `tbl_adminapprover` (
  `id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `tbl_adminapprover`
--

INSERT INTO `tbl_adminapprover` (`id`, `username`, `password`) VALUES
(1, 'Superuser', 'Superuser');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_announcements`
--

CREATE TABLE `tbl_announcements` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `title` varchar(255) NOT NULL,
  `textarea` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_appointments`
--

CREATE TABLE `tbl_appointments` (
  `id` int(11) NOT NULL,
  `ID_Number` varchar(150) NOT NULL,
  `firstname` varchar(150) NOT NULL,
  `middlename` varchar(255) NOT NULL,
  `lastname` varchar(255) NOT NULL,
  `course` varchar(255) NOT NULL,
  `yearlevel` varchar(255) NOT NULL,
  `email` varchar(150) NOT NULL,
  `gender` varchar(255) NOT NULL,
  `mobile` varchar(255) NOT NULL,
  `address` varchar(255) NOT NULL,
  `Title` varchar(150) NOT NULL,
  `Start_date_time` varchar(255) NOT NULL,
  `time` varchar(255) NOT NULL,
  `status` varchar(255) NOT NULL,
  `status1` int(255) NOT NULL DEFAULT 5,
  `position` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_blog`
--

CREATE TABLE `tbl_blog` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `author` varchar(255) NOT NULL,
  `category` varchar(255) NOT NULL,
  `subcategory` varchar(255) NOT NULL,
  `tags` varchar(255) NOT NULL,
  `gender` varchar(255) NOT NULL,
  `about` longtext NOT NULL,
  `image` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_familybackground`
--

CREATE TABLE `tbl_familybackground` (
  `id` int(11) NOT NULL,
  `ID_Number` varchar(255) NOT NULL,
  `Gaurdian` varchar(150) NOT NULL,
  `Father_name` varchar(150) NOT NULL,
  `Father_age` varchar(150) NOT NULL,
  `Father_address` varchar(150) NOT NULL,
  `Father_occupation` varchar(150) NOT NULL,
  `Father_educational_attainment` varchar(150) NOT NULL,
  `Mother_name` varchar(150) NOT NULL,
  `Mother_age` varchar(150) NOT NULL,
  `Mother_Address` varchar(150) NOT NULL,
  `Mother_occupation` varchar(150) NOT NULL,
  `Mother_educational_attainment` varchar(150) NOT NULL,
  `status` int(12) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Stand-in structure for view `tbl_familybackgroundinfos`
-- (See below for the actual view)
--
CREATE TABLE `tbl_familybackgroundinfos` (
`idnumber` varchar(150)
,`Gaurdian` varchar(150)
,`Father_name` varchar(150)
,`Father_age` varchar(150)
,`Father_address` varchar(150)
,`Father_occupation` varchar(150)
,`Father_educational_attainment` varchar(150)
,`Mother_name` varchar(150)
,`Mother_age` varchar(150)
,`Mother_Address` varchar(150)
,`Mother_occupation` varchar(150)
,`Mother_educational_attainment` varchar(150)
,`id` int(11)
,`Course` varchar(150)
,`Year_level` varchar(150)
,`First_name` varchar(150)
,`Middle_name` varchar(150)
,`Last_name` varchar(150)
,`Gender` varchar(150)
,`Home_Address` varchar(150)
,`Civil_status` varchar(150)
,`Place_of_birth` varchar(150)
,`Birthdate` varchar(150)
,`Cp_number` varchar(150)
,`Boarding_address` varchar(150)
,`Nationality` varchar(150)
,`Religion` varchar(150)
,`Email` varchar(150)
,`status` int(11)
);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_headmoderator`
--

CREATE TABLE `tbl_headmoderator` (
  `id` int(11) NOT NULL,
  `idnumber` varchar(255) NOT NULL,
  `Fullname` varchar(255) NOT NULL,
  `Gender` varchar(255) NOT NULL,
  `Email` varchar(255) NOT NULL,
  `Education` varchar(255) NOT NULL,
  `Address` varchar(255) NOT NULL,
  `Mobile` varchar(255) NOT NULL,
  `Birthdate` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `status` int(11) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `tbl_headmoderator`
--

INSERT INTO `tbl_headmoderator` (`id`, `idnumber`, `Fullname`, `Gender`, `Email`, `Education`, `Address`, `Mobile`, `Birthdate`, `password`, `status`) VALUES
(1, '00-00000', 'Remylien C. Songco, RN.,MAN', 'Female', 'fordemopurposes@gmail.com', '', '', '', '', 'Doctor', 3);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_healthhistoryform1`
--

CREATE TABLE `tbl_healthhistoryform1` (
  `id` int(11) NOT NULL,
  `ID_Number` varchar(255) NOT NULL,
  `Asthma` varchar(150) NOT NULL,
  `Asthma_Age` varchar(150) NOT NULL,
  `Hepatitis` varchar(150) NOT NULL,
  `Hepatitis_Age` varchar(150) NOT NULL,
  `High_Cholesterol` varchar(150) NOT NULL,
  `High_Cholesterol_Age` varchar(150) NOT NULL,
  `Goiter` varchar(150) NOT NULL,
  `Goiter_Age` varchar(150) NOT NULL,
  `Leukemia` varchar(150) NOT NULL,
  `Leukemia_Age` varchar(150) NOT NULL,
  `Angina` varchar(150) NOT NULL,
  `Angina_Age` varchar(150) NOT NULL,
  `Heart_Murmur` varchar(150) NOT NULL,
  `Heart_Murmur_Age` varchar(150) NOT NULL,
  `Stroke` varchar(150) NOT NULL,
  `Stroke_Age` varchar(150) NOT NULL,
  `Kidney_Disease` varchar(150) NOT NULL,
  `Kidney_Disease_Age` varchar(150) NOT NULL,
  `Anemia` varchar(150) NOT NULL,
  `Anemia_Age` varchar(150) NOT NULL,
  `Stomach_or_Peptic_Ulcer` varchar(150) NOT NULL,
  `Stomach_or_Peptic_Ulcer_Age` varchar(150) NOT NULL,
  `status` int(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_healthhistoryform2`
--

CREATE TABLE `tbl_healthhistoryform2` (
  `id` int(11) NOT NULL,
  `ID_Number` varchar(255) NOT NULL,
  `Head_Injury` varchar(150) NOT NULL,
  `Head_Injury_Age` varchar(150) NOT NULL,
  `Surgery` varchar(150) NOT NULL,
  `Surgery_Type` varchar(150) NOT NULL,
  `Surgery_Age` varchar(150) NOT NULL,
  `Allergies` varchar(150) NOT NULL,
  `Allergies_Age` varchar(150) NOT NULL,
  `High_Blood_Pressure` varchar(150) NOT NULL,
  `High_Blood_Pressure_Age` varchar(150) NOT NULL,
  `Hypothyroidism` varchar(150) NOT NULL,
  `Hypothyroidism_Age` varchar(150) NOT NULL,
  `Cancer` varchar(150) NOT NULL,
  `Cancer_Type` varchar(150) NOT NULL,
  `Cancer_Age` varchar(150) NOT NULL,
  `Psoriasis` varchar(150) NOT NULL,
  `Psoriasis_Age` varchar(150) NOT NULL,
  `Heart_Problem` varchar(150) NOT NULL,
  `Heart_Problem_Age` varchar(150) NOT NULL,
  `Pneumonia` varchar(150) NOT NULL,
  `Pneumonia_Age` varchar(150) NOT NULL,
  `Epilepsy` varchar(150) NOT NULL,
  `Epilepsy_Age` varchar(150) NOT NULL,
  `Kidney_Stone` varchar(150) NOT NULL,
  `Kidney_Stone_Age` varchar(150) NOT NULL,
  `Jaundice` varchar(150) NOT NULL,
  `Jaundice_Age` varchar(150) NOT NULL,
  `Tuberculosis` varchar(150) NOT NULL,
  `Tuberculosis_Age` varchar(150) NOT NULL,
  `Fainting_Spell` varchar(150) NOT NULL,
  `Fainting_Spell_Age` varchar(150) NOT NULL,
  `Seizures` varchar(150) NOT NULL,
  `Seizures_Age` varchar(150) NOT NULL,
  `Allergies_Seasonal` varchar(150) NOT NULL,
  `Allergies_Seasonal_Age` varchar(150) NOT NULL,
  `status` int(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Stand-in structure for view `tbl_healthinformation1`
-- (See below for the actual view)
--
CREATE TABLE `tbl_healthinformation1` (
`id` int(11)
,`idnumber` varchar(150)
,`Asthma` varchar(150)
,`Asthma_Age` varchar(150)
,`Hepatitis` varchar(150)
,`Hepatitis_Age` varchar(150)
,`High_Cholesterol` varchar(150)
,`High_Cholesterol_Age` varchar(150)
,`Goiter` varchar(150)
,`Goiter_Age` varchar(150)
,`Leukemia` varchar(150)
,`Leukemia_Age` varchar(150)
,`Angina` varchar(150)
,`Angina_Age` varchar(150)
,`Heart_Murmur` varchar(150)
,`Heart_Murmur_Age` varchar(150)
,`Stroke` varchar(150)
,`Stroke_Age` varchar(150)
,`Kidney_Disease` varchar(150)
,`Kidney_Disease_Age` varchar(150)
,`Anemia` varchar(150)
,`Anemia_Age` varchar(150)
,`Stomach_or_Peptic_Ulcer` varchar(150)
,`Stomach_or_Peptic_Ulcer_Age` varchar(150)
);

-- --------------------------------------------------------

--
-- Stand-in structure for view `tbl_healtinformations2`
-- (See below for the actual view)
--
CREATE TABLE `tbl_healtinformations2` (
`id` int(11)
,`idnumber` varchar(150)
,`Head_Injury` varchar(150)
,`Head_Injury_Age` varchar(150)
,`Surgery` varchar(150)
,`Surgery_Type` varchar(150)
,`Surgery_Age` varchar(150)
,`Allergies` varchar(150)
,`Allergies_Age` varchar(150)
,`High_Blood_Pressure` varchar(150)
,`High_Blood_Pressure_Age` varchar(150)
,`Hypothyroidism` varchar(150)
,`Hypothyroidism_Age` varchar(150)
,`Cancer` varchar(150)
,`Cancer_Type` varchar(150)
,`Cancer_Age` varchar(150)
,`Psoriasis` varchar(150)
,`Psoriasis_Age` varchar(150)
,`Heart_Problem` varchar(150)
,`Heart_Problem_Age` varchar(150)
,`Pneumonia` varchar(150)
,`Pneumonia_Age` varchar(150)
,`Epilepsy` varchar(150)
,`Epilepsy_Age` varchar(150)
,`Kidney_Stone` varchar(150)
,`Kidney_Stone_Age` varchar(150)
,`Jaundice` varchar(150)
,`Jaundice_Age` varchar(150)
,`Tuberculosis` varchar(150)
,`Tuberculosis_Age` varchar(150)
,`Fainting_Spell` varchar(150)
,`Fainting_Spell_Age` varchar(150)
,`Seizures` varchar(150)
,`Seizures_Age` varchar(150)
,`Allergies_Seasonal` varchar(150)
,`Allergies_Seasonal_Age` varchar(150)
);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_images`
--

CREATE TABLE `tbl_images` (
  `id` int(11) NOT NULL,
  `file_name` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `uploaded_on` datetime NOT NULL,
  `status` enum('1','0') COLLATE utf8_unicode_ci NOT NULL DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `tbl_images`
--

INSERT INTO `tbl_images` (`id`, `file_name`, `uploaded_on`, `status`) VALUES
(0, 'IMG_1029.JPG', '2023-05-03 13:26:51', '1');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_lifestyle`
--

CREATE TABLE `tbl_lifestyle` (
  `id` int(11) NOT NULL,
  `ID_Number` varchar(255) NOT NULL,
  `Do_you_Smoke` varchar(150) NOT NULL,
  `How_many_stick` varchar(150) NOT NULL,
  `Do_someone` varchar(150) NOT NULL,
  `Do_drink_Alchohol` varchar(150) NOT NULL,
  `How_often` varchar(150) NOT NULL,
  `status` int(12) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Stand-in structure for view `tbl_lifestyleinfos`
-- (See below for the actual view)
--
CREATE TABLE `tbl_lifestyleinfos` (
`id` int(11)
,`idnumber` varchar(150)
,`Do_you_Smoke` varchar(150)
,`How_many_stick` varchar(150)
,`Do_someone` varchar(150)
,`Do_drink_Alchohol` varchar(150)
,`How_often` varchar(150)
);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_medical`
--

CREATE TABLE `tbl_medical` (
  `id` int(11) NOT NULL,
  `idnumber` varchar(11) NOT NULL,
  `First_name` varchar(255) NOT NULL,
  `Middle_name` varchar(255) NOT NULL,
  `Last_Name` varchar(255) NOT NULL,
  `Year_level` varchar(255) NOT NULL,
  `ID_Number` varchar(255) NOT NULL,
  `Course` varchar(255) NOT NULL,
  `Gender` varchar(255) NOT NULL,
  `Cp_Number` varchar(255) NOT NULL,
  `Address` varchar(255) NOT NULL,
  `Date` date NOT NULL,
  `Title` varchar(255) NOT NULL,
  `Diagnosis` longtext NOT NULL,
  `Treatment` longtext NOT NULL,
  `Physician` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_moderator`
--

CREATE TABLE `tbl_moderator` (
  `id` int(11) NOT NULL,
  `idnumber` varchar(255) DEFAULT NULL,
  `First_name` varchar(255) NOT NULL,
  `Middle_name` varchar(255) NOT NULL,
  `Last_name` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `gender` varchar(255) NOT NULL,
  `status` int(11) NOT NULL DEFAULT 0,
  `extension` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `tbl_moderator`
--

INSERT INTO `tbl_moderator` (`id`, `idnumber`, `First_name`, `Middle_name`, `Last_name`, `password`, `gender`, `status`, `extension`) VALUES
(8, '30-00001', 'Edgar', 'Asuncion', 'Ulep', 'nurse', 'Male', 2, 'Dr.');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_moderatorbackinfo`
--

CREATE TABLE `tbl_moderatorbackinfo` (
  `id` int(12) NOT NULL,
  `ID_Number` varchar(255) NOT NULL,
  `Phone` varchar(255) NOT NULL,
  `Email` varchar(255) NOT NULL,
  `Address` varchar(255) NOT NULL,
  `Birthdate` varchar(255) NOT NULL,
  `status` int(12) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Stand-in structure for view `tbl_moderatorbackinfos`
-- (See below for the actual view)
--
CREATE TABLE `tbl_moderatorbackinfos` (
`Phone` varchar(255)
,`Email` varchar(255)
,`Address` varchar(255)
,`Birthdate` varchar(255)
,`status` int(12)
,`id` int(11)
,`idnumber` varchar(255)
);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_students`
--

CREATE TABLE `tbl_students` (
  `id` int(11) NOT NULL,
  `Userlevel_ID` int(11) NOT NULL,
  `idnumber` varchar(150) NOT NULL,
  `Course` varchar(150) NOT NULL,
  `Year_level` varchar(150) NOT NULL,
  `First_name` varchar(150) NOT NULL,
  `Middle_name` varchar(150) NOT NULL,
  `Last_name` varchar(150) NOT NULL,
  `Gender` varchar(150) NOT NULL,
  `Home_Address` varchar(150) NOT NULL,
  `Civil_status` varchar(150) NOT NULL,
  `Place_of_birth` varchar(150) NOT NULL,
  `Birthdate` varchar(150) NOT NULL,
  `Cp_number` varchar(150) NOT NULL,
  `Boarding_address` varchar(150) NOT NULL,
  `Nationality` varchar(150) NOT NULL,
  `Religion` varchar(150) NOT NULL,
  `Email` varchar(150) NOT NULL,
  `Password` varchar(150) NOT NULL,
  `status` int(11) NOT NULL DEFAULT 0,
  `position` varchar(255) NOT NULL,
  `status1` int(255) NOT NULL DEFAULT 10
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_user`
--

CREATE TABLE `tbl_user` (
  `id` int(11) NOT NULL,
  `idnumber` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `usertype` varchar(150) NOT NULL,
  `status` int(11) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_userlevels`
--

CREATE TABLE `tbl_userlevels` (
  `userlevel_ID` int(11) NOT NULL,
  `user_level` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `tbl_userlevels`
--

INSERT INTO `tbl_userlevels` (`userlevel_ID`, `user_level`) VALUES
(1, 'Administrator'),
(2, 'Moderator'),
(3, 'Student'),
(4, 'Faculty');

-- --------------------------------------------------------

--
-- Structure for view `tbl_familybackgroundinfos`
--
DROP TABLE IF EXISTS `tbl_familybackgroundinfos`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `tbl_familybackgroundinfos`  AS SELECT `tbl_students`.`idnumber` AS `idnumber`, `tbl_familybackground`.`Gaurdian` AS `Gaurdian`, `tbl_familybackground`.`Father_name` AS `Father_name`, `tbl_familybackground`.`Father_age` AS `Father_age`, `tbl_familybackground`.`Father_address` AS `Father_address`, `tbl_familybackground`.`Father_occupation` AS `Father_occupation`, `tbl_familybackground`.`Father_educational_attainment` AS `Father_educational_attainment`, `tbl_familybackground`.`Mother_name` AS `Mother_name`, `tbl_familybackground`.`Mother_age` AS `Mother_age`, `tbl_familybackground`.`Mother_Address` AS `Mother_Address`, `tbl_familybackground`.`Mother_occupation` AS `Mother_occupation`, `tbl_familybackground`.`Mother_educational_attainment` AS `Mother_educational_attainment`, `tbl_students`.`id` AS `id`, `tbl_students`.`Course` AS `Course`, `tbl_students`.`Year_level` AS `Year_level`, `tbl_students`.`First_name` AS `First_name`, `tbl_students`.`Middle_name` AS `Middle_name`, `tbl_students`.`Last_name` AS `Last_name`, `tbl_students`.`Gender` AS `Gender`, `tbl_students`.`Home_Address` AS `Home_Address`, `tbl_students`.`Civil_status` AS `Civil_status`, `tbl_students`.`Place_of_birth` AS `Place_of_birth`, `tbl_students`.`Birthdate` AS `Birthdate`, `tbl_students`.`Cp_number` AS `Cp_number`, `tbl_students`.`Boarding_address` AS `Boarding_address`, `tbl_students`.`Nationality` AS `Nationality`, `tbl_students`.`Religion` AS `Religion`, `tbl_students`.`Email` AS `Email`, `tbl_students`.`status` AS `status` FROM (`tbl_students` join `tbl_familybackground` on(`tbl_students`.`idnumber` = `tbl_familybackground`.`ID_Number`))  ;

-- --------------------------------------------------------

--
-- Structure for view `tbl_healthinformation1`
--
DROP TABLE IF EXISTS `tbl_healthinformation1`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `tbl_healthinformation1`  AS SELECT `tbl_students`.`id` AS `id`, `tbl_students`.`idnumber` AS `idnumber`, `tbl_healthhistoryform1`.`Asthma` AS `Asthma`, `tbl_healthhistoryform1`.`Asthma_Age` AS `Asthma_Age`, `tbl_healthhistoryform1`.`Hepatitis` AS `Hepatitis`, `tbl_healthhistoryform1`.`Hepatitis_Age` AS `Hepatitis_Age`, `tbl_healthhistoryform1`.`High_Cholesterol` AS `High_Cholesterol`, `tbl_healthhistoryform1`.`High_Cholesterol_Age` AS `High_Cholesterol_Age`, `tbl_healthhistoryform1`.`Goiter` AS `Goiter`, `tbl_healthhistoryform1`.`Goiter_Age` AS `Goiter_Age`, `tbl_healthhistoryform1`.`Leukemia` AS `Leukemia`, `tbl_healthhistoryform1`.`Leukemia_Age` AS `Leukemia_Age`, `tbl_healthhistoryform1`.`Angina` AS `Angina`, `tbl_healthhistoryform1`.`Angina_Age` AS `Angina_Age`, `tbl_healthhistoryform1`.`Heart_Murmur` AS `Heart_Murmur`, `tbl_healthhistoryform1`.`Heart_Murmur_Age` AS `Heart_Murmur_Age`, `tbl_healthhistoryform1`.`Stroke` AS `Stroke`, `tbl_healthhistoryform1`.`Stroke_Age` AS `Stroke_Age`, `tbl_healthhistoryform1`.`Kidney_Disease` AS `Kidney_Disease`, `tbl_healthhistoryform1`.`Kidney_Disease_Age` AS `Kidney_Disease_Age`, `tbl_healthhistoryform1`.`Anemia` AS `Anemia`, `tbl_healthhistoryform1`.`Anemia_Age` AS `Anemia_Age`, `tbl_healthhistoryform1`.`Stomach_or_Peptic_Ulcer` AS `Stomach_or_Peptic_Ulcer`, `tbl_healthhistoryform1`.`Stomach_or_Peptic_Ulcer_Age` AS `Stomach_or_Peptic_Ulcer_Age` FROM (`tbl_students` join `tbl_healthhistoryform1` on(`tbl_students`.`idnumber` = `tbl_healthhistoryform1`.`ID_Number`))  ;

-- --------------------------------------------------------

--
-- Structure for view `tbl_healtinformations2`
--
DROP TABLE IF EXISTS `tbl_healtinformations2`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `tbl_healtinformations2`  AS SELECT `tbl_students`.`id` AS `id`, `tbl_students`.`idnumber` AS `idnumber`, `tbl_healthhistoryform2`.`Head_Injury` AS `Head_Injury`, `tbl_healthhistoryform2`.`Head_Injury_Age` AS `Head_Injury_Age`, `tbl_healthhistoryform2`.`Surgery` AS `Surgery`, `tbl_healthhistoryform2`.`Surgery_Type` AS `Surgery_Type`, `tbl_healthhistoryform2`.`Surgery_Age` AS `Surgery_Age`, `tbl_healthhistoryform2`.`Allergies` AS `Allergies`, `tbl_healthhistoryform2`.`Allergies_Age` AS `Allergies_Age`, `tbl_healthhistoryform2`.`High_Blood_Pressure` AS `High_Blood_Pressure`, `tbl_healthhistoryform2`.`High_Blood_Pressure_Age` AS `High_Blood_Pressure_Age`, `tbl_healthhistoryform2`.`Hypothyroidism` AS `Hypothyroidism`, `tbl_healthhistoryform2`.`Hypothyroidism_Age` AS `Hypothyroidism_Age`, `tbl_healthhistoryform2`.`Cancer` AS `Cancer`, `tbl_healthhistoryform2`.`Cancer_Type` AS `Cancer_Type`, `tbl_healthhistoryform2`.`Cancer_Age` AS `Cancer_Age`, `tbl_healthhistoryform2`.`Psoriasis` AS `Psoriasis`, `tbl_healthhistoryform2`.`Psoriasis_Age` AS `Psoriasis_Age`, `tbl_healthhistoryform2`.`Heart_Problem` AS `Heart_Problem`, `tbl_healthhistoryform2`.`Heart_Problem_Age` AS `Heart_Problem_Age`, `tbl_healthhistoryform2`.`Pneumonia` AS `Pneumonia`, `tbl_healthhistoryform2`.`Pneumonia_Age` AS `Pneumonia_Age`, `tbl_healthhistoryform2`.`Epilepsy` AS `Epilepsy`, `tbl_healthhistoryform2`.`Epilepsy_Age` AS `Epilepsy_Age`, `tbl_healthhistoryform2`.`Kidney_Stone` AS `Kidney_Stone`, `tbl_healthhistoryform2`.`Kidney_Stone_Age` AS `Kidney_Stone_Age`, `tbl_healthhistoryform2`.`Jaundice` AS `Jaundice`, `tbl_healthhistoryform2`.`Jaundice_Age` AS `Jaundice_Age`, `tbl_healthhistoryform2`.`Tuberculosis` AS `Tuberculosis`, `tbl_healthhistoryform2`.`Tuberculosis_Age` AS `Tuberculosis_Age`, `tbl_healthhistoryform2`.`Fainting_Spell` AS `Fainting_Spell`, `tbl_healthhistoryform2`.`Fainting_Spell_Age` AS `Fainting_Spell_Age`, `tbl_healthhistoryform2`.`Seizures` AS `Seizures`, `tbl_healthhistoryform2`.`Seizures_Age` AS `Seizures_Age`, `tbl_healthhistoryform2`.`Allergies_Seasonal` AS `Allergies_Seasonal`, `tbl_healthhistoryform2`.`Allergies_Seasonal_Age` AS `Allergies_Seasonal_Age` FROM (`tbl_students` join `tbl_healthhistoryform2` on(`tbl_students`.`idnumber` = `tbl_healthhistoryform2`.`ID_Number`))  ;

-- --------------------------------------------------------

--
-- Structure for view `tbl_lifestyleinfos`
--
DROP TABLE IF EXISTS `tbl_lifestyleinfos`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `tbl_lifestyleinfos`  AS SELECT `tbl_students`.`id` AS `id`, `tbl_students`.`idnumber` AS `idnumber`, `tbl_lifestyle`.`Do_you_Smoke` AS `Do_you_Smoke`, `tbl_lifestyle`.`How_many_stick` AS `How_many_stick`, `tbl_lifestyle`.`Do_someone` AS `Do_someone`, `tbl_lifestyle`.`Do_drink_Alchohol` AS `Do_drink_Alchohol`, `tbl_lifestyle`.`How_often` AS `How_often` FROM (`tbl_students` join `tbl_lifestyle` on(`tbl_students`.`idnumber` = `tbl_lifestyle`.`ID_Number`))  ;

-- --------------------------------------------------------

--
-- Structure for view `tbl_moderatorbackinfos`
--
DROP TABLE IF EXISTS `tbl_moderatorbackinfos`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `tbl_moderatorbackinfos`  AS SELECT `tbl_moderatorbackinfo`.`Phone` AS `Phone`, `tbl_moderatorbackinfo`.`Email` AS `Email`, `tbl_moderatorbackinfo`.`Address` AS `Address`, `tbl_moderatorbackinfo`.`Birthdate` AS `Birthdate`, `tbl_moderatorbackinfo`.`status` AS `status`, `tbl_moderator`.`id` AS `id`, `tbl_moderator`.`idnumber` AS `idnumber` FROM (`tbl_moderator` join `tbl_moderatorbackinfo` on(`tbl_moderator`.`idnumber` = `tbl_moderatorbackinfo`.`ID_Number`))  ;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `disabled_dates`
--
ALTER TABLE `disabled_dates`
  ADD PRIMARY KEY (`ids`);

--
-- Indexes for table `disabled_dates_dental`
--
ALTER TABLE `disabled_dates_dental`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `m_information`
--
ALTER TABLE `m_information`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tbl_adminapprover`
--
ALTER TABLE `tbl_adminapprover`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tbl_announcements`
--
ALTER TABLE `tbl_announcements`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tbl_appointments`
--
ALTER TABLE `tbl_appointments`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tbl_blog`
--
ALTER TABLE `tbl_blog`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tbl_familybackground`
--
ALTER TABLE `tbl_familybackground`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tbl_headmoderator`
--
ALTER TABLE `tbl_headmoderator`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tbl_healthhistoryform1`
--
ALTER TABLE `tbl_healthhistoryform1`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tbl_healthhistoryform2`
--
ALTER TABLE `tbl_healthhistoryform2`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tbl_lifestyle`
--
ALTER TABLE `tbl_lifestyle`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tbl_medical`
--
ALTER TABLE `tbl_medical`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tbl_moderator`
--
ALTER TABLE `tbl_moderator`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tbl_moderatorbackinfo`
--
ALTER TABLE `tbl_moderatorbackinfo`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tbl_students`
--
ALTER TABLE `tbl_students`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tbl_user`
--
ALTER TABLE `tbl_user`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `tbl_userlevels`
--
ALTER TABLE `tbl_userlevels`
  ADD PRIMARY KEY (`userlevel_ID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `disabled_dates`
--
ALTER TABLE `disabled_dates`
  MODIFY `ids` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=26;

--
-- AUTO_INCREMENT for table `disabled_dates_dental`
--
ALTER TABLE `disabled_dates_dental`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=22;

--
-- AUTO_INCREMENT for table `m_information`
--
ALTER TABLE `m_information`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `tbl_adminapprover`
--
ALTER TABLE `tbl_adminapprover`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `tbl_announcements`
--
ALTER TABLE `tbl_announcements`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `tbl_appointments`
--
ALTER TABLE `tbl_appointments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=99;

--
-- AUTO_INCREMENT for table `tbl_blog`
--
ALTER TABLE `tbl_blog`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tbl_familybackground`
--
ALTER TABLE `tbl_familybackground`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `tbl_headmoderator`
--
ALTER TABLE `tbl_headmoderator`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `tbl_healthhistoryform1`
--
ALTER TABLE `tbl_healthhistoryform1`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `tbl_healthhistoryform2`
--
ALTER TABLE `tbl_healthhistoryform2`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `tbl_lifestyle`
--
ALTER TABLE `tbl_lifestyle`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `tbl_medical`
--
ALTER TABLE `tbl_medical`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=50;

--
-- AUTO_INCREMENT for table `tbl_moderator`
--
ALTER TABLE `tbl_moderator`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `tbl_moderatorbackinfo`
--
ALTER TABLE `tbl_moderatorbackinfo`
  MODIFY `id` int(12) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `tbl_students`
--
ALTER TABLE `tbl_students`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT for table `tbl_user`
--
ALTER TABLE `tbl_user`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `tbl_userlevels`
--
ALTER TABLE `tbl_userlevels`
  MODIFY `userlevel_ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
