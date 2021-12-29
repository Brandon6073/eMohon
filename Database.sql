-- MySQL dump 10.13  Distrib 8.0.24, for Win64 (x86_64)
--
-- Host: us-cdbr-west-04.cleardb.com    Database: heroku_b08c6055
-- ------------------------------------------------------
-- Server version	5.6.50-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `data`
--

DROP TABLE IF EXISTS `data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `data` (
  `data_ID` int(11) NOT NULL AUTO_INCREMENT,
  `Sumber_Peruntukan` varchar(25) NOT NULL,
  `Kampung_ID` int(100) NOT NULL,
  `No_SebutHarga` varchar(50) NOT NULL,
  `No_Suratkuasa_Waran` varchar(50) NOT NULL,
  `Nama_Projek` text NOT NULL,
  `No_Rujukan` int(25) NOT NULL,
  `Kontraktor` text NOT NULL,
  `Peruntukan_Diluluskan` int(50) NOT NULL,
  `Bayar` int(50) NOT NULL,
  `Baki` int(50) NOT NULL,
  `Tarikh_Tawaran` date NOT NULL,
  `Tarikh_Milik_Tapak` date NOT NULL,
  `Tempoh_Siap` varchar(25) NOT NULL,
  `Tarikh_Jangkaan_Siap` date NOT NULL,
  `Tarikh_Sebenar_Siap` date NOT NULL,
  `Status` varchar(25) NOT NULL,
  PRIMARY KEY (`data_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `data`
--

LOCK TABLES `data` WRITE;
/*!40000 ALTER TABLE `data` DISABLE KEYS */;
INSERT INTO `data` VALUES (15,'PERSEKUTUAN',95,'1234','H1234','PROJEK RUMAH',0,'JOHN CENA',2000,2000,0,'2012-12-21','2010-12-21','10 HARI','0002-01-22','0003-01-22','Diluluskan');
/*!40000 ALTER TABLE `data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jenispermohonan`
--

DROP TABLE IF EXISTS `jenispermohonan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `jenispermohonan` (
  `id_jenis_permohonan` int(100) NOT NULL AUTO_INCREMENT,
  `jenis_permohonan` text NOT NULL,
  PRIMARY KEY (`id_jenis_permohonan`)
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jenispermohonan`
--

LOCK TABLES `jenispermohonan` WRITE;
/*!40000 ALTER TABLE `jenispermohonan` DISABLE KEYS */;
INSERT INTO `jenispermohonan` VALUES (1,'JALAN KAMPUNG'),(2,'JALAN KEBUN'),(3,'JAMBATAN GANTUNG'),(4,'LALUAN PEJALAN KAKI'),(5,'BALAIRAYA'),(6,'MINI DEWAN'),(7,'RUMAH KOMUNITI'),(8,'BANGUNAN TASKA'),(9,'PENDAWAIAN ELEKTRIK'),(10,'BANGUNAN RUMAH IBADAT'),(11,'PONDOK KUBURAN'),(12,'PENYELANGGARAAN SUNGAI'),(13,'SISTEM PERPARITAN'),(14,'LAMPU JALAN'),(15,'BELB'),(16,'PAIP GRAVITI'),(17,'PPRT'),(18,'GELANGGANG PERMAINAN'),(19,'JAMBATAN KONKRIT'),(20,'LOW LEVEL CROSSING'),(21,'PONDOK TAGAL/REKREASI'),(22,'PERHENTIAN BAS'),(23,'BANGUNAN TANDAS');
/*!40000 ALTER TABLE `jenispermohonan` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `kampung`
--

DROP TABLE IF EXISTS `kampung`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `kampung` (
  `kampung_id` int(50) NOT NULL AUTO_INCREMENT,
  `nama_kampung` text NOT NULL,
  `nama_mukim` text NOT NULL,
  PRIMARY KEY (`kampung_id`)
) ENGINE=InnoDB AUTO_INCREMENT=135 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `kampung`
--

LOCK TABLES `kampung` WRITE;
/*!40000 ALTER TABLE `kampung` DISABLE KEYS */;
INSERT INTO `kampung` VALUES (95,'KAMPUNG 1','MUKIM 1'),(105,'KAMPUNG 2','MUKIM 2'),(115,'PEJABAT DAERAH (ADMIN TYPE 1)','PEJABAT DERAH'),(125,'PEJABAT DAERAH (ADMIN TYPE 2)','PEJABAT DAERAH');
/*!40000 ALTER TABLE `kampung` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pengguna`
--

DROP TABLE IF EXISTS `pengguna`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pengguna` (
  `ic_pengguna` varchar(50) NOT NULL,
  `kampung_id` int(50) NOT NULL,
  `nama_pengguna` text NOT NULL,
  `jenis_pengguna` int(10) NOT NULL,
  `kata_laluan` varchar(255) NOT NULL,
  PRIMARY KEY (`ic_pengguna`),
  UNIQUE KEY `ic_pengguna` (`ic_pengguna`),
  KEY `pengguna_ibfk_1` (`kampung_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pengguna`
--

LOCK TABLES `pengguna` WRITE;
/*!40000 ALTER TABLE `pengguna` DISABLE KEYS */;
INSERT INTO `pengguna` VALUES ('0000',125,'ADMIN',3,'sha256$4LMiU9KRVHppVzpq$4543f9f12dc9abef8b2b339234121d189dc146ce85f4743f60ff9bc70c652023'),('1111',95,'PEMOHON PROJEK 1',1,'sha256$vs71kLssNZECRZI3$7d4de728e410d8df962845d3089737255266bf83e9660103a36f8227940ed6ff'),('2222',105,'PEMOHON PROJEK 2',1,'sha256$VOvG8XiGit6cpXuE$c9f6c62fd081acd81af20ffb5ebf80bd0ffe3c3ed21b082018634a1e0f7f9ab4'),('3333',115,'PENGURUS PROJEK 1',2,'sha256$nKmEOaiVG4Hlbpr7$3e7d887afa561d7c29883330c9f8f9fe6c13a170fd70eb5a92e2a2828d2a9ecd');
/*!40000 ALTER TABLE `pengguna` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permohonan`
--

DROP TABLE IF EXISTS `permohonan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permohonan` (
  `id_permohonan` int(255) NOT NULL AUTO_INCREMENT,
  `nama_pengguna` varchar(100) NOT NULL,
  `kampung_id` int(255) NOT NULL,
  `jenis_permohonan` text NOT NULL,
  `bil_ukuran_keluasan` text NOT NULL,
  `justifikasi` text NOT NULL,
  `ic` varchar(50) NOT NULL,
  `tarikh` date NOT NULL,
  `gambar_1` varchar(100) NOT NULL,
  `gambar_2` varchar(100) NOT NULL,
  `gambar_3` varchar(100) NOT NULL,
  `dokumen_pdf` varchar(100) NOT NULL,
  PRIMARY KEY (`id_permohonan`),
  KEY `permohonan_ibfk_1` (`ic`)
) ENGINE=InnoDB AUTO_INCREMENT=326 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permohonan`
--

LOCK TABLES `permohonan` WRITE;
/*!40000 ALTER TABLE `permohonan` DISABLE KEYS */;
INSERT INTO `permohonan` VALUES (315,'ABDUL WAHAP BIN BATIN',1,'BALAIRAYA','100M X 200M','JUSTIFIKASI PERMOHONAN PROJEK UNTUK PEMBINAAN BALAI RAYA...','630305125637','2021-08-26','630305125637-2021-08-26-hadapan-download.jpg','630305125637-2021-08-26-belakang-balai_raya.jpg','630305125637-2021-08-26-sisi-balai_raya_sda.jpg','630305125637-2021-08-26-dokumen-Dokumen_Permohonan.pdf'),(325,'ABDUL WAHAP BIN BATIN',1,'JAMBATAN GANTUNG','1/20 KAKI','MENDESAK','630305125637','2021-08-26','630305125637-2021-08-26-hadapan-agm.jpg','630305125637-2021-08-26-belakang-agm.jpg','630305125637-2021-08-26-sisi-agm.jpg','630305125637-2021-08-26-dokumen-pemakluman_kelulusan_ppv_awam.pdf');
/*!40000 ALTER TABLE `permohonan` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-12-29 19:47:50
