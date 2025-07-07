import { Mahasiswa, JenisKelamin, NilaiMahasiswa } from '@prisma/client';

export interface MahasiswaWithNilai extends Mahasiswa {
  nilai_mahasiswa: NilaiMahasiswa[];
}

export interface ExternalMahasiswaData {
  nim: string;
  nama_mahasiswa: string;
  jenis_kelamin: 'L' | 'P';
  jalur_penerimaan?: string;
  tahun_angkatan: string;
  semester_masuk?: string;
  tanggal_mulai_masuk?: string;
  id_program_studi: number;
  kode_program_studi?: string;
  nama_program_studi: string;
  propinsi?: string;
  kota_kab?: string;
  kecamatan?: string;
  ipk?: number;
  status_mahasiswa_terakhir?: string;
  penerima_beasiswa_kipk?: string;
  penerima_beasiswa_kjmu?: string;
  kelompok_ukt?: string;
  nominal_ukt?: number;
}

export interface MahasiswaSyncRequest {
  angkatan: string;
}

export interface MahasiswaSyncResponse {
  success: boolean;
  message: string;
  data: {
    total_received: number;
    total_processed: number;
    total_inserted: number;
    total_updated: number;
    errors: any[];
  };
}

export interface MahasiswaListQuery {
  page?: number;
  limit?: number;
  angkatan?: string;
  program_studi?: number;
  search?: string;
  sort_by?: 'nim' | 'nama_mahasiswa' | 'tahun_angkatan';
  sort_order?: 'asc' | 'desc';
}

export interface PaginatedMahasiswaResponse {
  data: Mahasiswa[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}