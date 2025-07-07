/*
  Warnings:

  - A unique constraint covering the columns `[nama_dosen]` on the table `dosen` will be added. If there are existing duplicate values, this will fail.

*/
-- CreateIndex
CREATE UNIQUE INDEX `dosen_nama_dosen_key` ON `dosen`(`nama_dosen`);
