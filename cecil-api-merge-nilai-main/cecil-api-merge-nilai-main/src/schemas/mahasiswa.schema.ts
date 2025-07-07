import { z } from 'zod';

export const mahasiswaSyncSchema = z.object({
  angkatan: z.string()
    .min(4, 'Angkatan must be 4 characters')
    .max(4, 'Angkatan must be 4 characters')
    .regex(/^\d{4}$/, 'Angkatan must be a valid year'),
});

export const mahasiswaListQuerySchema = z.object({
  page: z.coerce.number().min(1).default(1),
  limit: z.coerce.number().min(1).max(999999999).default(10),
  angkatan: z.string().optional(),
  program_studi: z.coerce.number().optional(),
  search: z.string().optional(),
  sort_by: z.enum(['nim', 'nama_mahasiswa', 'tahun_angkatan']).default('nim'),
  sort_order: z.enum(['asc', 'desc']).default('asc'),
});

export const mahasiswaParamsSchema = z.object({
  nim: z.string()
    .min(1, 'NIM is required')
    .max(20, 'NIM must not exceed 20 characters'),
});

export const externalMahasiswaSchema = z.object({
  nim: z.string(),
  nama_mahasiswa: z.string(),
  jenis_kelamin: z.enum(['L', 'P']),
  jalur_penerimaan: z.string().optional(),
  tahun_angkatan: z.string(),
  semester_masuk: z.string().optional(),
  tanggal_mulai_masuk: z.string().optional(),
  id_program_studi: z.number(),
  kode_program_studi: z.string().optional(),
  nama_program_studi: z.string(),
  propinsi: z.string().optional(),
  kota_kab: z.string().optional(),
  kecamatan: z.string().optional(),
  ipk: z.number().optional(),
  status_mahasiswa_terakhir: z.string().optional(),
  penerima_beasiswa_kipk: z.string().optional(),
  penerima_beasiswa_kjmu: z.string().optional(),
  kelompok_ukt: z.string().optional(),
  nominal_ukt: z.number().optional(),
});

export type MahasiswaSyncInput = z.infer<typeof mahasiswaSyncSchema>;
export type MahasiswaListQuery = z.infer<typeof mahasiswaListQuerySchema>;
export type MahasiswaParams = z.infer<typeof mahasiswaParamsSchema>;
export type ExternalMahasiswaInput = z.infer<typeof externalMahasiswaSchema>;