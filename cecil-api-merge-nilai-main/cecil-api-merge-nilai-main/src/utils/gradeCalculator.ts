import { GradePoint } from '@/types/nilai.types';

export class GradeCalculator {
  private static gradePoints: GradePoint[] = [
    { huruf: 'A', angka: 4.0, min_nilai: 85, max_nilai: 100 },
    { huruf: 'A-', angka: 3.7, min_nilai: 80, max_nilai: 84 },
    { huruf: 'B+', angka: 3.3, min_nilai: 75, max_nilai: 79 },
    { huruf: 'B', angka: 3.0, min_nilai: 70, max_nilai: 74 },
    { huruf: 'B-', angka: 2.7, min_nilai: 65, max_nilai: 69 },
    { huruf: 'C+', angka: 2.3, min_nilai: 60, max_nilai: 64 },
    { huruf: 'C', angka: 2.0, min_nilai: 55, max_nilai: 59 },
    { huruf: 'C-', angka: 1.7, min_nilai: 50, max_nilai: 54 },
    { huruf: 'D', angka: 1.0, min_nilai: 40, max_nilai: 49 },
    { huruf: 'E', angka: 0.0, min_nilai: 0, max_nilai: 39 },
  ];

  static getGradePoint(nilaiHuruf: string): number {
    const grade = this.gradePoints.find(g => g.huruf === nilaiHuruf.toUpperCase());
    return grade ? grade.angka : 0;
  }

  static getGradeFromNumber(totalNilai: number): string {
    const grade = this.gradePoints.find(
      g => totalNilai >= g.min_nilai && totalNilai <= g.max_nilai
    );
    return grade ? grade.huruf : 'E';
  }

  static calculateIPS(nilaiData: Array<{ sks: number; nilai_huruf: string }>): number {
    let totalMutu = 0;
    let totalSks = 0;

    for (const nilai of nilaiData) {
      const gradePoint = this.getGradePoint(nilai.nilai_huruf);
      totalMutu += nilai.sks * gradePoint;
      totalSks += nilai.sks;
    }

    return totalSks > 0 ? Math.round((totalMutu / totalSks) * 100) / 100 : 0;
  }

  static calculateIPK(semesterData: Array<{ total_sks: number; total_mutu: number }>): number {
    let totalMutu = 0;
    let totalSks = 0;

    for (const semester of semesterData) {
      totalMutu += semester.total_mutu;
      totalSks += semester.total_sks;
    }

    return totalSks > 0 ? Math.round((totalMutu / totalSks) * 100) / 100 : 0;
  }

  static isPassingGrade(nilaiHuruf: string): boolean {
    const gradePoint = this.getGradePoint(nilaiHuruf);
    return gradePoint >= 2.0; // C or better
  }
}