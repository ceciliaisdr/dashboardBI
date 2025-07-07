import { prisma } from '@/config/database';
import { Prisma } from '@prisma/client';
import { ExternalApiService } from './ExternalApiService';
import { PrismaService } from './PrismaService';
import {
  ExternalMahasiswaData,
  MahasiswaSyncResponse,
  MahasiswaListQuery,
  PaginatedMahasiswaResponse,
  MahasiswaWithNilai,
} from '@/types/mahasiswa.types';
import { ResponseFormatter } from '@/utils/responseFormatter';
import { logger } from '@/utils/logger';

export class MahasiswaService {
  private externalApiService: ExternalApiService;
  private prismaService: PrismaService;

  constructor() {
    this.externalApiService = new ExternalApiService();
    this.prismaService = new PrismaService();
  }

  async syncMahasiswaFromExternal(angkatan: string): Promise<MahasiswaSyncResponse> {
    try {
      logger.info(`Starting mahasiswa sync for angkatan: ${angkatan}`);

      // Fetch data from external API
      const externalData = await this.externalApiService.getMahasiswaByAngkatan(angkatan);

      if (!externalData || externalData.length === 0) {
        return {
          success: false,
          message: 'No data received from external API',
          data: {
            total_received: 0,
            total_processed: 0,
            total_inserted: 0,
            total_updated: 0,
            errors: [],
          },
        };
      }

      let totalProcessed = 0;
      let totalInserted = 0;
      let totalUpdated = 0;
      const errors: any[] = [];

      // Process data in batches
      const batchSize = 100;
      for (let i = 0; i < externalData.length; i += batchSize) {
        const batch = externalData.slice(i, i + batchSize);
        
        await this.prismaService.executeInTransaction(async (tx) => {
          for (const mahasiswaData of batch) {
            try {
              const processedData = this.transformExternalData(mahasiswaData);
              
              const existingMahasiswa = await tx.mahasiswa.findUnique({
                where: { nim: processedData.nim },
              });

              if (existingMahasiswa) {
                await tx.mahasiswa.update({
                  where: { nim: processedData.nim },
                  data: processedData,
                });
                totalUpdated++;
              } else {
                await tx.mahasiswa.create({
                  data: processedData,
                });
                totalInserted++;
              }

              totalProcessed++;
            } catch (error) {
              logger.error('Error processing mahasiswa:', { data: mahasiswaData, error });
              errors.push({
                nim: mahasiswaData.nim,
                error: error instanceof Error ? error.message : 'Unknown error',
              });
            }
          }
        });
      }

      logger.info(`Sync completed: ${totalProcessed} processed, ${totalInserted} inserted, ${totalUpdated} updated`);

      return {
        success: true,
        message: 'Mahasiswa data synchronized successfully',
        data: {
          total_received: externalData.length,
          total_processed: totalProcessed,
          total_inserted: totalInserted,
          total_updated: totalUpdated,
          errors,
        },
      };
    } catch (error) {
      logger.error('Error syncing mahasiswa:', error);
      throw new Error('Failed to synchronize mahasiswa data');
    }
  }

  async getMahasiswaList(query: MahasiswaListQuery): Promise<PaginatedMahasiswaResponse> {
    try {
      const { page = 1, limit = 10, angkatan, program_studi, search, sort_by = 'nim', sort_order = 'asc' } = query;
      
      const skip = (page - 1) * limit;
      
      // Build where condition
      const whereCondition: Prisma.MahasiswaWhereInput = {};
      
      if (angkatan) {
        whereCondition.tahun_angkatan = angkatan;
      }
      
      if (program_studi) {
        whereCondition.id_program_studi = program_studi;
      }
      
      if (search) {
        whereCondition.OR = [
          { nim: { contains: search } },
          { nama_mahasiswa: { contains: search } },
        ];
      }

      // Get total count
      const total = await prisma.mahasiswa.count({ where: whereCondition });

      // Get paginated data
      const mahasiswa = await prisma.mahasiswa.findMany({
        where: whereCondition,
        include: {
          nilai_mahasiswa: {
            include: {
              mata_kuliah: true,
              dosen: true,
            },
            orderBy: [
              { tahun_akademik: 'asc' },
              { semester: 'asc' },
            ],
          },
        },
        skip,
        take: limit,
        orderBy: { [sort_by]: sort_order },
      });

      const pagination = ResponseFormatter.paginate(page, limit, total);

      return {
        data: mahasiswa,
        pagination,
      };
    } catch (error) {
      logger.error('Error getting mahasiswa list:', error);
      throw new Error('Failed to get mahasiswa list');
    }
  }

  async getMahasiswaWithNilai(nim: string): Promise<MahasiswaWithNilai | null> {
    try {
      const mahasiswa = await prisma.mahasiswa.findUnique({
        where: { nim },
        include: {
          nilai_mahasiswa: {
            include: {
              mata_kuliah: true,
              dosen: true,
            },
            orderBy: [
              { tahun_akademik: 'asc' },
              { semester: 'asc' },
            ],
          },
        },
      });

      return mahasiswa;
    } catch (error) {
      logger.error('Error getting mahasiswa with nilai:', error);
      throw new Error('Failed to get mahasiswa data');
    }
  }

  async getMahasiswaByNim(nim: string) {
    try {
      return await prisma.mahasiswa.findUnique({
        where: { nim },
        include: {
          nilai_mahasiswa: {
            include: {
              mata_kuliah: true,
              dosen: true,
            },
            orderBy: [
              { tahun_akademik: 'asc' },
              { semester: 'asc' },
            ],
          },
        },
      });
    } catch (error) {
      logger.error('Error getting mahasiswa by NIM:', error);
      throw new Error('Failed to get mahasiswa');
    }
  }

  private transformExternalData(data: ExternalMahasiswaData): Prisma.MahasiswaCreateInput {
    return {
      nim: data.nim,
      nama_mahasiswa: data.nama_mahasiswa,
      jenis_kelamin: data.jenis_kelamin,
      jalur_penerimaan: data.jalur_penerimaan,
      tahun_angkatan: data.tahun_angkatan,
      semester_masuk: data.semester_masuk,
      tanggal_mulai_masuk: data.tanggal_mulai_masuk ? new Date(data.tanggal_mulai_masuk) : null,
      id_program_studi: Number(data.id_program_studi),
      kode_program_studi: data.kode_program_studi,
      nama_program_studi: data.nama_program_studi,
      propinsi: data.propinsi,
      kota_kab: data.kota_kab,
      kecamatan: data.kecamatan,
      ipk: data.ipk,
      status_mahasiswa_terakhir: data.status_mahasiswa_terakhir,
      penerima_beasiswa_kipk: data.penerima_beasiswa_kipk,
      penerima_beasiswa_kjmu: data.penerima_beasiswa_kjmu,
      kelompok_ukt: data.kelompok_ukt,
      nominal_ukt: data.nominal_ukt,
    };
  }
}