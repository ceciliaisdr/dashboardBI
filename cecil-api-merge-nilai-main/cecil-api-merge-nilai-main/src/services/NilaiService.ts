import { prisma } from '@/config/database';
import { Prisma } from '@prisma/client';
import { PrismaService } from './PrismaService';
import { CSVParser } from '@/utils/csvParser';
import {
  ProcessedNilaiData,
  NilaiUploadResponse,
} from '@/types/nilai.types';
import { logger } from '@/utils/logger';

export class NilaiService {
  private prismaService: PrismaService;

  constructor() {
    this.prismaService = new PrismaService();
  }

  async uploadNilaiFromCSV(buffer: Buffer): Promise<NilaiUploadResponse> {
    try {
      logger.info('Starting CSV nilai upload process');

      // Validate CSV structure
      const isValidStructure = await CSVParser.validateCSVStructure(buffer);
      if (!isValidStructure) {
        throw new Error('Invalid CSV structure. Missing required columns.');
      }

      // Parse CSV data
      const { data: parsedData, errors: parseErrors } = await CSVParser.parseNilaiCSV(buffer);

      if (parsedData.length === 0) {
        return {
          success: false,
          message: 'No valid data found in CSV file',
          data: {
            total_rows: 0,
            total_processed: 0,
            total_inserted: 0,
            total_updated: 0,
            mata_kuliah_created: 0,
            dosen_created: 0,
            errors: parseErrors,
          },
        };
      }

      let totalProcessed = 0;
      let totalInserted = 0;
      let totalUpdated = 0;
      let mataKuliahCreated = 0;
      let dosenCreated = 0;
      const processingErrors: any[] = [...parseErrors];

      // Process data in batches
      const batchSize = 50;
      for (let i = 0; i < parsedData.length; i += batchSize) {
        const batch = parsedData.slice(i, i + batchSize);
        
        await this.prismaService.executeInTransaction(async (tx) => {
          for (const nilaiData of batch) {
            try {
              // Check if mahasiswa exists
              const mahasiswa = await tx.mahasiswa.findUnique({
                where: { nim: nilaiData.nim },
              });

              if (!mahasiswa) {
                processingErrors.push({
                  row: i + 1,
                  data: nilaiData,
                  error: `Mahasiswa with NIM ${nilaiData.nim} not found`,
                });
                continue;
              }

              // Upsert mata kuliah
              const mataKuliah = await tx.mataKuliah.upsert({
                where: { kode_mk: nilaiData.kode_mk },
                update: {
                  nama_mk: nilaiData.nama_mk,
                  sks: nilaiData.sks,
                },
                create: {
                  kode_mk: nilaiData.kode_mk,
                  nama_mk: nilaiData.nama_mk,
                  sks: nilaiData.sks,
                },
              });

              // Check if mata kuliah was created
              const existingMK = await tx.mataKuliah.findUnique({
                where: { kode_mk: nilaiData.kode_mk },
                select: { created_at: true, updated_at: true },
              });

              if (existingMK && existingMK.created_at.getTime() === existingMK.updated_at.getTime()) {
                mataKuliahCreated++;
              }

              // Upsert dosen if provided
              let dosenId: number | null = null;
              if (nilaiData.dosen_nama) {
                const dosen = await tx.dosen.upsert({
                  where: { nama_dosen: nilaiData.dosen_nama },
                  update: {
                    title_depan: nilaiData.dosen_title_depan,
                    title_belakang: nilaiData.dosen_title_belakang,
                  },
                  create: {
                    nama_dosen: nilaiData.dosen_nama,
                    title_depan: nilaiData.dosen_title_depan,
                    title_belakang: nilaiData.dosen_title_belakang,
                  },
                });

                dosenId = dosen.id;

                // Check if dosen was created
                const existingDosen = await tx.dosen.findUnique({
                  where: { nama_dosen: nilaiData.dosen_nama },
                  select: { created_at: true, updated_at: true },
                });

                if (existingDosen && existingDosen.created_at.getTime() === existingDosen.updated_at.getTime()) {
                  dosenCreated++;
                }
              }

              // Upsert nilai mahasiswa
              const uniqueKey = {
                nim: nilaiData.nim,
                kode_mk: nilaiData.kode_mk,
                tahun_akademik: nilaiData.tahun_akademik,
                semester: nilaiData.semester,
              };

              const existingNilai = await tx.nilaiMahasiswa.findUnique({
                where: { unique_nilai: uniqueKey },
              });

              const nilaiMahasiswaData = {
                nim: nilaiData.nim,
                kode_mk: nilaiData.kode_mk,
                nama_mk: nilaiData.nama_mk,
                dosen_id: dosenId,
                sks: nilaiData.sks,
                kelas: nilaiData.kelas,
                total_nilai: nilaiData.total_nilai,
                nilai_huruf: nilaiData.nilai_huruf,
                tahun_akademik: nilaiData.tahun_akademik,
                semester: nilaiData.semester,
                kurikulum: nilaiData.kurikulum,
              };

              if (existingNilai) {
                await tx.nilaiMahasiswa.update({
                  where: { unique_nilai: uniqueKey },
                  data: nilaiMahasiswaData,
                });
                totalUpdated++;
              } else {
                await tx.nilaiMahasiswa.create({
                  data: nilaiMahasiswaData,
                });
                totalInserted++;
              }

              totalProcessed++;
            } catch (error) {
              logger.error('Error processing nilai data:', { data: nilaiData, error });
              processingErrors.push({
                row: i + 1,
                data: nilaiData,
                error: error instanceof Error ? error.message : 'Unknown error',
              });
            }
          }
        });
      }

      logger.info(`CSV processing completed: ${totalProcessed} processed, ${totalInserted} inserted, ${totalUpdated} updated`);

      return {
        success: true,
        message: 'CSV data processed successfully',
        data: {
          total_rows: parsedData.length + parseErrors.length,
          total_processed: totalProcessed,
          total_inserted: totalInserted,
          total_updated: totalUpdated,
          mata_kuliah_created: mataKuliahCreated,
          dosen_created: dosenCreated,
          errors: processingErrors,
        },
      };
    } catch (error) {
      logger.error('Error uploading nilai from CSV:', error);
      throw new Error('Failed to process CSV file');
    }
  }

  async getNilaiByNim(nim: string) {
    try {
      return await prisma.nilaiMahasiswa.findMany({
        where: { nim },
        include: {
          mata_kuliah: true,
          dosen: true,
        },
        orderBy: [
          { tahun_akademik: 'asc' },
          { semester: 'asc' },
        ],
      });
    } catch (error) {
      logger.error('Error getting nilai by NIM:', error);
      throw new Error('Failed to get nilai data');
    }
  }
}