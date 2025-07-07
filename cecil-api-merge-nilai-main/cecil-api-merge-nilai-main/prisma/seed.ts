import { PrismaClient } from '@prisma/client';
import { logger } from '../src/utils/logger';

const prisma = new PrismaClient();

async function main() {
  try {
    logger.info('🌱 Starting database seeding...');

    // Create sample mata kuliah
    const mataKuliah = await prisma.mataKuliah.createMany({
      data: [
        { kode_mk: 'IF101', nama_mk: 'Algoritma dan Pemrograman', sks: 3 },
        { kode_mk: 'IF102', nama_mk: 'Struktur Data', sks: 3 },
        { kode_mk: 'IF103', nama_mk: 'Basis Data', sks: 3 },
        { kode_mk: 'IF104', nama_mk: 'Pemrograman Web', sks: 3 },
        { kode_mk: 'IF105', nama_mk: 'Rekayasa Perangkat Lunak', sks: 3 },
        { kode_mk: 'SI101', nama_mk: 'Sistem Informasi Manajemen', sks: 3 },
        { kode_mk: 'SI102', nama_mk: 'Analisis dan Perancangan Sistem', sks: 3 },
        { kode_mk: 'DS101', nama_mk: 'Statistika Dasar', sks: 3 },
        { kode_mk: 'DS102', nama_mk: 'Machine Learning', sks: 3 },
        { kode_mk: 'MK101', nama_mk: 'Matematika Diskrit', sks: 3 },
      ],
      skipDuplicates: true,
    });

    // Create sample dosen
    const dosen = await prisma.dosen.createMany({
      data: [
        { nama_dosen: 'Ahmad Sutanto', title_depan: 'Dr.', title_belakang: 'M.Kom' },
        { nama_dosen: 'Siti Nurhaliza', title_depan: 'Ir.', title_belakang: 'M.T' },
        { nama_dosen: 'Budi Prakoso', title_depan: 'Prof.', title_belakang: 'Ph.D' },
        { nama_dosen: 'Diana Sari', title_depan: 'Dr.', title_belakang: 'M.Sc' },
        { nama_dosen: 'Eko Wijaya', title_belakang: 'M.Kom' },
      ],
      skipDuplicates: true,
    });

    // Create sample mahasiswa
    const mahasiswa = await prisma.mahasiswa.createMany({
      data: [
        {
          nim: '2020123001',
          nama_mahasiswa: 'John Doe',
          jenis_kelamin: 'L',
          jalur_penerimaan: 'SNMPTN',
          tahun_angkatan: '2020',
          semester_masuk: '1',
          tanggal_mulai_masuk: new Date('2020-08-01'),
          id_program_studi: 3,
          kode_program_studi: 'IF',
          nama_program_studi: 'S1 Informatika',
          propinsi: 'DKI Jakarta',
          kota_kab: 'Jakarta Selatan',
          kecamatan: 'Pondok Labu',
          status_mahasiswa_terakhir: 'Aktif',
          kelompok_ukt: 'UKT 3',
          nominal_ukt: 2500000,
        },
        {
          nim: '2020123002',
          nama_mahasiswa: 'Jane Smith',
          jenis_kelamin: 'P',
          jalur_penerimaan: 'SBMPTN',
          tahun_angkatan: '2020',
          semester_masuk: '1',
          tanggal_mulai_masuk: new Date('2020-08-01'),
          id_program_studi: 4,
          kode_program_studi: 'SI',
          nama_program_studi: 'S1 Sistem Informasi',
          propinsi: 'DKI Jakarta',
          kota_kab: 'Jakarta Timur',
          kecamatan: 'Cakung',
          status_mahasiswa_terakhir: 'Aktif',
          kelompok_ukt: 'UKT 4',
          nominal_ukt: 3000000,
        },
        {
          nim: '2021123003',
          nama_mahasiswa: 'Bob Johnson',
          jenis_kelamin: 'L',
          jalur_penerimaan: 'Mandiri',
          tahun_angkatan: '2021',
          semester_masuk: '1',
          tanggal_mulai_masuk: new Date('2021-08-01'),
          id_program_studi: 58,
          kode_program_studi: 'DS',
          nama_program_studi: 'S1 Sains Data',
          propinsi: 'Jawa Barat',
          kota_kab: 'Depok',
          kecamatan: 'Beji',
          status_mahasiswa_terakhir: 'Aktif',
          kelompok_ukt: 'UKT 5',
          nominal_ukt: 3500000,
        },
      ],
      skipDuplicates: true,
    });

    // Create sample nilai
    const dosenList = await prisma.dosen.findMany();
    const mataKuliahList = await prisma.mataKuliah.findMany();

    await prisma.nilaiMahasiswa.createMany({
      data: [
        // John Doe - Semester 1
        {
          nim: '2020123001',
          kode_mk: 'IF101',
          nama_mk: 'Algoritma dan Pemrograman',
          dosen_id: dosenList[0].id,
          sks: 3,
          kelas: 'A',
          total_nilai: 85,
          nilai_huruf: 'A',
          tahun_akademik: '2020/2021',
          semester: '1',
          kurikulum: '2020',
        },
        {
          nim: '2020123001',
          kode_mk: 'MK101',
          nama_mk: 'Matematika Diskrit',
          dosen_id: dosenList[1].id,
          sks: 3,
          kelas: 'A',
          total_nilai: 78,
          nilai_huruf: 'B+',
          tahun_akademik: '2020/2021',
          semester: '1',
          kurikulum: '2020',
        },
        // John Doe - Semester 2
        {
          nim: '2020123001',
          kode_mk: 'IF102',
          nama_mk: 'Struktur Data',
          dosen_id: dosenList[2].id,
          sks: 3,
          kelas: 'A',
          total_nilai: 88,
          nilai_huruf: 'A',
          tahun_akademik: '2020/2021',
          semester: '2',
          kurikulum: '2020',
        },
        // Jane Smith - Semester 1
        {
          nim: '2020123002',
          kode_mk: 'SI101',
          nama_mk: 'Sistem Informasi Manajemen',
          dosen_id: dosenList[3].id,
          sks: 3,
          kelas: 'B',
          total_nilai: 82,
          nilai_huruf: 'A-',
          tahun_akademik: '2020/2021',
          semester: '1',
          kurikulum: '2020',
        },
        {
          nim: '2020123002',
          kode_mk: 'MK101',
          nama_mk: 'Matematika Diskrit',
          dosen_id: dosenList[1].id,
          sks: 3,
          kelas: 'B',
          total_nilai: 75,
          nilai_huruf: 'B+',
          tahun_akademik: '2020/2021',
          semester: '1',
          kurikulum: '2020',
        },
        // Bob Johnson - Semester 1
        {
          nim: '2021123003',
          kode_mk: 'DS101',
          nama_mk: 'Statistika Dasar',
          dosen_id: dosenList[4].id,
          sks: 3,
          kelas: 'A',
          total_nilai: 90,
          nilai_huruf: 'A',
          tahun_akademik: '2021/2022',
          semester: '1',
          kurikulum: '2021',
        },
      ],
      skipDuplicates: true,
    });

    logger.info('✅ Database seeding completed successfully');
    logger.info(`Created ${mataKuliah.count} mata kuliah records`);
    logger.info(`Created ${dosen.count} dosen records`);
    logger.info(`Created ${mahasiswa.count} mahasiswa records`);
    logger.info('Created sample nilai records');

  } catch (error) {
    logger.error('❌ Error during seeding:', error);
    throw error;
  } finally {
    await prisma.$disconnect();
  }
}

main()
  .then(async () => {
    await prisma.$disconnect();
  })
  .catch(async (e) => {
    logger.error(e);
    await prisma.$disconnect();
    process.exit(1);
  });