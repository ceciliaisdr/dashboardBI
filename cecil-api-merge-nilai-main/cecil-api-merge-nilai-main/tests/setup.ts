import { prisma } from '../src/config/database';

// Setup test database
beforeAll(async () => {
  // Connect to test database
  await prisma.$connect();
});

afterAll(async () => {
  // Clean up and disconnect
  await prisma.$disconnect();
});

beforeEach(async () => {
  // Clean up data before each test
  await prisma.nilaiMahasiswa.deleteMany();
  await prisma.mahasiswa.deleteMany();
  await prisma.mataKuliah.deleteMany();
  await prisma.dosen.deleteMany();
});