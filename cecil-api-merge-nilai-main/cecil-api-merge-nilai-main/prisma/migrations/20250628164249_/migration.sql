-- CreateTable
CREATE TABLE `mahasiswa` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `nim` VARCHAR(20) NOT NULL,
    `nama_mahasiswa` VARCHAR(255) NOT NULL,
    `jenis_kelamin` ENUM('L', 'P') NOT NULL,
    `jalur_penerimaan` VARCHAR(50) NULL,
    `tahun_angkatan` VARCHAR(4) NOT NULL,
    `semester_masuk` VARCHAR(2) NULL,
    `tanggal_mulai_masuk` DATE NULL,
    `id_program_studi` INTEGER NOT NULL,
    `kode_program_studi` VARCHAR(10) NULL,
    `nama_program_studi` VARCHAR(255) NOT NULL,
    `propinsi` VARCHAR(100) NULL,
    `kota_kab` VARCHAR(100) NULL,
    `kecamatan` VARCHAR(100) NULL,
    `ipk` DECIMAL(3, 2) NULL,
    `status_mahasiswa_terakhir` VARCHAR(20) NULL,
    `penerima_beasiswa_kipk` VARCHAR(50) NULL,
    `penerima_beasiswa_kjmu` VARCHAR(50) NULL,
    `kelompok_ukt` VARCHAR(50) NULL,
    `nominal_ukt` BIGINT NULL,
    `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updated_at` DATETIME(3) NOT NULL,

    UNIQUE INDEX `mahasiswa_nim_key`(`nim`),
    INDEX `mahasiswa_nim_idx`(`nim`),
    INDEX `mahasiswa_id_program_studi_idx`(`id_program_studi`),
    INDEX `mahasiswa_tahun_angkatan_idx`(`tahun_angkatan`),
    INDEX `mahasiswa_nama_mahasiswa_idx`(`nama_mahasiswa`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `mata_kuliah` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `kode_mk` VARCHAR(20) NOT NULL,
    `nama_mk` VARCHAR(255) NOT NULL,
    `sks` INTEGER NOT NULL,
    `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updated_at` DATETIME(3) NOT NULL,

    UNIQUE INDEX `mata_kuliah_kode_mk_key`(`kode_mk`),
    INDEX `mata_kuliah_kode_mk_idx`(`kode_mk`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `dosen` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `nama_dosen` VARCHAR(255) NOT NULL,
    `title_depan` VARCHAR(50) NULL,
    `title_belakang` VARCHAR(50) NULL,
    `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updated_at` DATETIME(3) NOT NULL,

    INDEX `dosen_nama_dosen_idx`(`nama_dosen`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `nilai_mahasiswa` (
    `id` INTEGER NOT NULL AUTO_INCREMENT,
    `nim` VARCHAR(20) NOT NULL,
    `kode_mk` VARCHAR(20) NOT NULL,
    `nama_mk` VARCHAR(255) NOT NULL,
    `dosen_id` INTEGER NULL,
    `sks` INTEGER NOT NULL,
    `kelas` VARCHAR(10) NULL,
    `total_nilai` DECIMAL(5, 2) NULL,
    `nilai_huruf` VARCHAR(2) NULL,
    `tahun_akademik` VARCHAR(9) NOT NULL,
    `semester` VARCHAR(2) NOT NULL,
    `kurikulum` VARCHAR(50) NULL,
    `created_at` DATETIME(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3),
    `updated_at` DATETIME(3) NOT NULL,

    INDEX `nilai_mahasiswa_nim_kode_mk_idx`(`nim`, `kode_mk`),
    INDEX `nilai_mahasiswa_tahun_akademik_semester_idx`(`tahun_akademik`, `semester`),
    UNIQUE INDEX `nilai_mahasiswa_nim_kode_mk_tahun_akademik_semester_key`(`nim`, `kode_mk`, `tahun_akademik`, `semester`),
    PRIMARY KEY (`id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AddForeignKey
ALTER TABLE `nilai_mahasiswa` ADD CONSTRAINT `nilai_mahasiswa_nim_fkey` FOREIGN KEY (`nim`) REFERENCES `mahasiswa`(`nim`) ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `nilai_mahasiswa` ADD CONSTRAINT `nilai_mahasiswa_kode_mk_fkey` FOREIGN KEY (`kode_mk`) REFERENCES `mata_kuliah`(`kode_mk`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `nilai_mahasiswa` ADD CONSTRAINT `nilai_mahasiswa_dosen_id_fkey` FOREIGN KEY (`dosen_id`) REFERENCES `dosen`(`id`) ON DELETE SET NULL ON UPDATE CASCADE;
