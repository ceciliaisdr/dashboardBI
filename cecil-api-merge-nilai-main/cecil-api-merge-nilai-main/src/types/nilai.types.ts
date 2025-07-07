import { NilaiMahasiswa, MataKuliah, Dosen } from '@prisma/client';

export interface NilaiMahasiswaWithRelations extends NilaiMahasiswa {
  mata_kuliah: MataKuliah;
  dosen?: Dosen;
}

export interface CSVNilaiRow {
  f_nim: string;
  f_kodemk: string;
  f_namamk: string;
  f_namapegawai?: string;
  f_title_depan?: string;
  f_title_belakang?: string;
  f_sks: string;
  f_kelas?: string;
  f_totalnilai?: string;
  f_nilaihuruf?: string;
  f_thakad: string;
  f_semester: string;
  f_kurikulum?: string;
}

export interface ProcessedNilaiData {
  nim: string;
  kode_mk: string;
  nama_mk: string;
  dosen_nama?: string;
  dosen_title_depan?: string;
  dosen_title_belakang?: string;
  sks: number;
  kelas?: string;
  total_nilai?: number;
  nilai_huruf?: string;
  tahun_akademik: string;
  semester: string;
  kurikulum?: string;
}

export interface NilaiUploadResponse {
  success: boolean;
  message: string;
  data: {
    total_rows: number;
    total_processed: number;
    total_inserted: number;
    total_updated: number;
    mata_kuliah_created: number;
    dosen_created: number;
    errors: Array<{
      row: number;
      data: any;
      error: string;
    }>;
  };
}

export interface TranskripData {
  mahasiswa: {
    nim: string;
    nama_mahasiswa: string;
    nama_program_studi: string;
    tahun_angkatan: string;
  };
  semester_data: Array<{
    tahun_akademik: string;
    semester: string;
    mata_kuliah: Array<{
      kode_mk: string;
      nama_mk: string;
      sks: number;
      nilai_huruf: string;
      total_nilai: number;
      dosen_nama?: string;
    }>;
    total_sks: number;
    total_mutu: number;
    ips: number;
  }>;
  summary: {
    total_sks_lulus: number;
    total_mutu_lulus: number;
    ipk: number;
  };
}

export interface GradePoint {
  huruf: string;
  angka: number;
  min_nilai: number;
  max_nilai: number;
}