import Papa from 'papaparse';
import { CSVNilaiRow, ProcessedNilaiData } from '@/types/nilai.types';
import { csvNilaiRowSchema } from '@/schemas/nilai.schema';
import { logger } from '@/utils/logger';

export class CSVParser {
  static async parseNilaiCSV(buffer: Buffer): Promise<{
    data: ProcessedNilaiData[];
    errors: Array<{ row: number; data: any; error: string }>;
  }> {
    return new Promise((resolve) => {
      const results: ProcessedNilaiData[] = [];
      const errors: Array<{ row: number; data: any; error: string }> = [];

      Papa.parse(buffer.toString(), {
        header: true,
        skipEmptyLines: true,
        delimiter: ',',
        complete: (parseResult) => {
          logger.info(`Parsing CSV with ${parseResult.data.length} rows`);

          parseResult.data.forEach((row, index) => {
            try {
              // Validate CSV row structure
              const validatedRow = csvNilaiRowSchema.parse(row);
              
              // Process and transform data
              const processedData: ProcessedNilaiData = {
                nim: validatedRow.f_nim.trim(),
                kode_mk: validatedRow.f_kodemk.trim(),
                nama_mk: validatedRow.f_namamk.trim(),
                dosen_nama: validatedRow.f_namapegawai?.trim(),
                dosen_title_depan: validatedRow.f_title_depan?.trim(),
                dosen_title_belakang: validatedRow.f_title_belakang?.trim(),
                sks: parseInt(validatedRow.f_sks),
                kelas: validatedRow.f_kelas?.trim(),
                total_nilai: validatedRow.f_totalnilai ? parseFloat(validatedRow.f_totalnilai) : undefined,
                nilai_huruf: validatedRow.f_nilaihuruf?.trim().toUpperCase(),
                tahun_akademik: validatedRow.f_thakad.trim(),
                semester: validatedRow.f_semester.trim(),
                kurikulum: validatedRow.f_kurikulum?.trim(),
              };

              // Additional business logic validation
              if (processedData.total_nilai && (processedData.total_nilai < 0 || processedData.total_nilai > 100)) {
                throw new Error('Total nilai must be between 0 and 100');
              }

              if (processedData.sks < 1 || processedData.sks > 6) {
                throw new Error('SKS must be between 1 and 6');
              }

              results.push(processedData);
            } catch (error) {
              logger.error(`Error processing row ${index + 1}:`, error);
              errors.push({
                row: index + 1,
                data: row,
                error: error instanceof Error ? error.message : 'Unknown error',
              });
            }
          });

          resolve({ data: results, errors });
        },
        error: (error: any) => {
          logger.error('CSV parsing error:', error);
          resolve({
            data: [],
            errors: [{ row: 0, data: {}, error: 'Failed to parse CSV file' }],
          });
        },
      });
    });
  }

  static validateCSVStructure(buffer: Buffer): Promise<boolean> {
    return new Promise((resolve) => {
      const requiredColumns = [
        'f_nim', 'f_kodemk', 'f_namamk', 'f_sks', 
        'f_thakad', 'f_semester'
      ];

      Papa.parse(buffer.toString(), {
        header: true,
        preview: 1,
        complete: (result) => {
          if (result.data.length === 0) {
            resolve(false);
            return;
          }

          const headers = Object.keys(result.data[0] as Record<string, unknown>);
          const hasAllRequiredColumns = requiredColumns.every(col => 
            headers.includes(col)
          );

          resolve(hasAllRequiredColumns);
        },
        error: () => resolve(false),
      });
    });
  }
}