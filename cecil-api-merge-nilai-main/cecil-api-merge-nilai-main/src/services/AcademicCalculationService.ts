import { prisma } from '@/config/database';
import { TranskripData } from '@/types/nilai.types';
import { GradeCalculator } from '@/utils/gradeCalculator';
import { logger } from '@/utils/logger';

interface SemesterSummary {
  tahun_akademik: string;
  semester: string;
  total_sks: number;
  total_mutu: number;
  ips: number;
}

export class AcademicCalculationService {
  async generateTranskrip(nim: string): Promise<TranskripData | null> {
    try {
      // Get mahasiswa data
      const mahasiswa = await prisma.mahasiswa.findUnique({
        where: { nim },
        select: {
          nim: true,
          nama_mahasiswa: true,
          nama_program_studi: true,
          tahun_angkatan: true,
        },
      });

      if (!mahasiswa) {
        return null;
      }

      // Get all nilai for this mahasiswa
      const nilaiList = await prisma.nilaiMahasiswa.findMany({
        where: { 
          nim,
          nilai_huruf: { not: null }, // Only include records with grades
        },
        include: {
          mata_kuliah: true,
          dosen: true,
        },
        orderBy: [
          { tahun_akademik: 'asc' },
          { semester: 'asc' },
          { kode_mk: 'asc' },
        ],
      });

      if (nilaiList.length === 0) {
        return {
          mahasiswa,
          semester_data: [],
          summary: {
            total_sks_lulus: 0,
            total_mutu_lulus: 0,
            ipk: 0,
          },
        };
      }

      // Group by semester
      const semesterGroups = new Map<string, typeof nilaiList>();
      nilaiList.forEach(nilai => {
        const key = `${nilai.tahun_akademik}-${nilai.semester}`;
        if (!semesterGroups.has(key)) {
          semesterGroups.set(key, []);
        }
        semesterGroups.get(key)!.push(nilai);
      });

      // Calculate semester data
      const semesterData = Array.from(semesterGroups.entries()).map(([key, values]) => {
        const [tahun_akademik, semester] = key.split('-');
        
        const mataKuliahData = values.map(nilai => ({
          kode_mk: nilai.kode_mk,
          nama_mk: nilai.nama_mk,
          sks: nilai.sks,
          nilai_huruf: nilai.nilai_huruf || 'E',
          total_nilai: nilai.total_nilai ? parseFloat(nilai.total_nilai.toString()) : 0,
          dosen_nama: nilai.dosen ? 
            `${nilai.dosen.title_depan || ''} ${nilai.dosen.nama_dosen} ${nilai.dosen.title_belakang || ''}`.trim() :
            undefined,
        }));

        // Calculate semester totals
        let totalSks = 0;
        let totalMutu = 0;

        mataKuliahData.forEach(mk => {
          const gradePoint = GradeCalculator.getGradePoint(mk.nilai_huruf);
          totalSks += mk.sks;
          totalMutu += mk.sks * gradePoint;
        });

        const ips = totalSks > 0 ? Math.round((totalMutu / totalSks) * 100) / 100 : 0;

        return {
          tahun_akademik,
          semester,
          mata_kuliah: mataKuliahData,
          total_sks: totalSks,
          total_mutu: totalMutu,
          ips,
        };
      });

      // Calculate overall summary
      let totalSksLulus = 0;
      let totalMutuLulus = 0;

      nilaiList.forEach(nilai => {
        if (nilai.nilai_huruf && GradeCalculator.isPassingGrade(nilai.nilai_huruf)) {
          const gradePoint = GradeCalculator.getGradePoint(nilai.nilai_huruf);
          totalSksLulus += nilai.sks;
          totalMutuLulus += nilai.sks * gradePoint;
        }
      });

      const ipk = totalSksLulus > 0 ? Math.round((totalMutuLulus / totalSksLulus) * 100) / 100 : 0;

      // Update IPK in mahasiswa record
      await prisma.mahasiswa.update({
        where: { nim },
        data: { ipk },
      });

      return {
        mahasiswa,
        semester_data: semesterData,
        summary: {
          total_sks_lulus: totalSksLulus,
          total_mutu_lulus: totalMutuLulus,
          ipk,
        },
      };
    } catch (error) {
      logger.error('Error generating transkrip:', error);
      throw new Error('Failed to generate academic transcript');
    }
  }

  async updateAllIPK(): Promise<{ updated: number; errors: number }> {
    try {
      const allMahasiswa = await prisma.mahasiswa.findMany({
        select: { nim: true },
      });

      let updated = 0;
      let errors = 0;

      for (const mahasiswa of allMahasiswa) {
        try {
          const transkrip = await this.generateTranskrip(mahasiswa.nim);
          if (transkrip) {
            updated++;
          }
        } catch (error) {
          logger.error(`Error updating IPK for ${mahasiswa.nim}:`, error);
          errors++;
        }
      }

      logger.info(`IPK update completed: ${updated} updated, ${errors} errors`);
      return { updated, errors };
    } catch (error) {
      logger.error('Error updating all IPK:', error);
      throw new Error('Failed to update IPK for all students');
    }
  }

  async getSemesterSummary(nim: string): Promise<SemesterSummary[]> {
    try {
      const result = await prisma.$queryRaw<SemesterSummary[]>`
        SELECT 
          tahun_akademik,
          semester,
          SUM(sks) as total_sks,
          SUM(
            CASE 
              WHEN nilai_huruf = 'A' THEN sks * 4.0
              WHEN nilai_huruf = 'A-' THEN sks * 3.7
              WHEN nilai_huruf = 'B+' THEN sks * 3.3
              WHEN nilai_huruf = 'B' THEN sks * 3.0
              WHEN nilai_huruf = 'B-' THEN sks * 2.7
              WHEN nilai_huruf = 'C+' THEN sks * 2.3
              WHEN nilai_huruf = 'C' THEN sks * 2.0
              WHEN nilai_huruf = 'C-' THEN sks * 1.7
              WHEN nilai_huruf = 'D' THEN sks * 1.0
              ELSE 0
            END
          ) as total_mutu,
          ROUND(
            SUM(
              CASE 
                WHEN nilai_huruf = 'A' THEN sks * 4.0
                WHEN nilai_huruf = 'A-' THEN sks * 3.7
                WHEN nilai_huruf = 'B+' THEN sks * 3.3
                WHEN nilai_huruf = 'B' THEN sks * 3.0
                WHEN nilai_huruf = 'B-' THEN sks * 2.7
                WHEN nilai_huruf = 'C+' THEN sks * 2.3
                WHEN nilai_huruf = 'C' THEN sks * 2.0
                WHEN nilai_huruf = 'C-' THEN sks * 1.7
                WHEN nilai_huruf = 'D' THEN sks * 1.0
                ELSE 0
              END
            ) / SUM(sks), 2
          ) as ips
        FROM nilai_mahasiswa 
        WHERE nim = ${nim} AND nilai_huruf IS NOT NULL
        GROUP BY tahun_akademik, semester
        ORDER BY tahun_akademik ASC, semester ASC
      `;

      return result;
    } catch (error) {
      logger.error('Error getting semester summary:', error);
      throw new Error('Failed to get semester summary');
    }
  }
}