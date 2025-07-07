import { MahasiswaService } from '../../src/services/MahasiswaService';
import { ExternalApiService } from '../../src/services/ExternalApiService';
import { prisma } from '../../src/config/database';

// Mock external API service
jest.mock('../../src/services/ExternalApiService');

describe('MahasiswaService', () => {
  let mahasiswaService: MahasiswaService;
  let mockExternalApiService: jest.Mocked<ExternalApiService>;

  beforeEach(() => {
    mahasiswaService = new MahasiswaService();
    mockExternalApiService = new ExternalApiService() as jest.Mocked<ExternalApiService>;
  });

  describe('syncMahasiswaFromExternal', () => {
    it('should sync mahasiswa data successfully', async () => {
      const mockData = [
        {
          nim: '2020123001',
          nama_mahasiswa: 'Test Student',
          jenis_kelamin: 'L' as const,
          tahun_angkatan: '2020',
          id_program_studi: 3,
          nama_program_studi: 'S1 Informatika',
        },
      ];

      mockExternalApiService.getMahasiswaByAngkatan.mockResolvedValue(mockData);

      const result = await mahasiswaService.syncMahasiswaFromExternal('2020');

      expect(result.success).toBe(true);
      expect(result.data.total_processed).toBe(1);
      expect(result.data.total_inserted).toBe(1);
    });

    it('should handle empty external data', async () => {
      mockExternalApiService.getMahasiswaByAngkatan.mockResolvedValue([]);

      const result = await mahasiswaService.syncMahasiswaFromExternal('2020');

      expect(result.success).toBe(false);
      expect(result.data.total_received).toBe(0);
    });
  });

  describe('getMahasiswaList', () => {
    beforeEach(async () => {
      await prisma.mahasiswa.create({
        data: {
          nim: '2020123001',
          nama_mahasiswa: 'Test Student',
          jenis_kelamin: 'L',
          tahun_angkatan: '2020',
          id_program_studi: 3,
          nama_program_studi: 'S1 Informatika',
        },
      });
    });

    it('should return paginated mahasiswa list', async () => {
      const result = await mahasiswaService.getMahasiswaList({
        page: 1,
        limit: 10,
      });

      expect(result.data).toHaveLength(1);
      expect(result.pagination.total).toBe(1);
      expect(result.data[0].nim).toBe('2020123001');
    });

    it('should filter by angkatan', async () => {
      const result = await mahasiswaService.getMahasiswaList({
        page: 1,
        limit: 10,
        angkatan: '2020',
      });

      expect(result.data).toHaveLength(1);
      expect(result.data[0].tahun_angkatan).toBe('2020');
    });

    it('should search by name or nim', async () => {
      const result = await mahasiswaService.getMahasiswaList({
        page: 1,
        limit: 10,
        search: 'Test',
      });

      expect(result.data).toHaveLength(1);
      expect(result.data[0].nama_mahasiswa).toContain('Test');
    });
  });
});