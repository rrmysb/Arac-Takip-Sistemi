USE `Aractakip`;

-- Araç Takip Günlük Veri Tablosu
CREATE TABLE IF NOT EXISTS `vehicle_daily_tracking` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `plaka` VARCHAR(20) NOT NULL,
  `tarih` DATE NOT NULL,
  `mesafe` INT(11) DEFAULT 0,
  `mesai_ici` INT(11) DEFAULT 0,
  `mesai_disi` INT(11) DEFAULT 0,
  `maxhid` INT(11) DEFAULT 0,
  `ilk_kontak` DATETIME DEFAULT NULL,
  `son_kontak` DATETIME DEFAULT NULL,
  `isim` VARCHAR(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_plaka_tarih` (`plaka`, `tarih`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_turkish_ci;