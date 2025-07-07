import { z } from 'zod';

export const csvNilaiRowSchema = z.object({
  f_nim: z.string().min(1, 'NIM is required'),
  f_kodemk: z.string().min(1, 'Kode MK is required'),
  f_namamk: z.string().min(1, 'Nama MK is required'),
  f_namapegawai: z.string().optional(),
  f_title_depan: z.string().optional(),
  f_title_belakang: z.string().optional(),
  f_sks: z.string().regex(/^\d+$/, 'SKS must be a number'),
  f_kelas: z.string().optional(),
  f_totalnilai: z.string()
    .regex(/^\d+(\.\d{1,2})?$/, 'Total nilai must be a valid number')
    .optional(),
  f_nilaihuruf: z.string()
    .regex(/^([ABCDE][\+\-]?)?$/, 'Nilai huruf must be valid grade (A, B+, B, etc.)')
    .optional(),
  f_thakad: z.string()
    .regex(/^\d{4}\/\d{4}$/, 'Tahun akademik must be in format YYYY/YYYY'),
  f_semester: z.string()
    .regex(/^[12]$/, 'Semester must be 1 or 2'),
  f_kurikulum: z.string().optional(),
});

export const nilaiParamsSchema = z.object({
  nim: z.string()
    .min(1, 'NIM is required')
    .max(20, 'NIM must not exceed 20 characters'),
});

export const fileUploadSchema = z.object({
  fieldname: z.string(),
  originalname: z.string().regex(/\.csv$/i, 'File must be a CSV'),
  encoding: z.string(),
  mimetype: z.string().regex(/^text\/csv|application\/vnd\.ms-excel/, 'Invalid MIME type for CSV'),
  size: z.number().max(10485760, 'File size must not exceed 10MB'),
  buffer: z.instanceof(Buffer),
});

export type CSVNilaiRowInput = z.infer<typeof csvNilaiRowSchema>;
export type NilaiParams = z.infer<typeof nilaiParamsSchema>;
export type FileUploadInput = z.infer<typeof fileUploadSchema>;