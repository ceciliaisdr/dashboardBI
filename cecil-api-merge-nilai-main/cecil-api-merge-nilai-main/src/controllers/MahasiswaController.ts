import { Request, Response } from 'express';
import { MahasiswaService } from '@/services/MahasiswaService';
import { ResponseFormatter } from '@/utils/responseFormatter';
import { asyncHandler } from '@/middlewares/errorHandler';
import {
  MahasiswaSyncInput,
  MahasiswaListQuery,
  MahasiswaParams,
} from '@/schemas/mahasiswa.schema';

export class MahasiswaController {
  private mahasiswaService: MahasiswaService;

  constructor() {
    this.mahasiswaService = new MahasiswaService();
  }

  syncMahasiswa = asyncHandler(async (req: Request, res: Response) => {
    const { angkatan }: MahasiswaSyncInput = req.body;

    const result = await this.mahasiswaService.syncMahasiswaFromExternal(angkatan);

    if (result.success) {
      res.status(200).json(ResponseFormatter.success(result.message, result.data));
    } else {
      res.status(400).json(ResponseFormatter.error(result.message, result.data.errors));
    }
  });

  getMahasiswa = asyncHandler(async (req: Request, res: Response) => {
    const query: MahasiswaListQuery = {
      page: parseInt(req.query.page as string) || 1,
      limit: parseInt(req.query.limit as string) || 10,
      sort_by: (req.query.sort_by as "nim" | "nama_mahasiswa" | "tahun_angkatan") || "nim",
      sort_order: (req.query.sort_order as "asc" | "desc") || "asc",
      search: req.query.search as string,
      angkatan: req.query.angkatan as string,
      program_studi: req.query.program_studi ? parseInt(req.query.program_studi as string) : undefined
    };

    const result = await this.mahasiswaService.getMahasiswaList(query);

    // Convert BigInt values to strings to avoid serialization error
    const serializedData = JSON.parse(JSON.stringify(result.data, (_, value) =>
      typeof value === 'bigint' ? value.toString() : value
    ));
    
    res.status(200).json(
      ResponseFormatter.success(
        'Mahasiswa list retrieved successfully',
        serializedData,
        result.pagination
      )
    );
  });

  getMahasiswaByNim = asyncHandler(async (req: Request<MahasiswaParams>, res: Response) => {
    const { nim } = req.params;

    const mahasiswa = await this.mahasiswaService.getMahasiswaByNim(nim);

    if (!mahasiswa) {
      return res.status(404).json(
        ResponseFormatter.error('Mahasiswa not found')
      );
    }

    // Convert BigInt values to strings to avoid serialization error
    const serializedData = JSON.parse(JSON.stringify(mahasiswa, (_, value) =>
      typeof value === 'bigint' ? value.toString() : value
    ));

    res.status(200).json(
      ResponseFormatter.success('Mahasiswa retrieved successfully', serializedData)
    );
  });

  getMahasiswaWithNilai = asyncHandler(async (req: Request<MahasiswaParams>, res: Response) => {
    const { nim } = req.params;

    const mahasiswa = await this.mahasiswaService.getMahasiswaWithNilai(nim);

    if (!mahasiswa) {
      return res.status(404).json(
        ResponseFormatter.error('Mahasiswa not found')
      );
    }

    // Convert BigInt values to strings to avoid serialization error
    const serializedData = JSON.parse(JSON.stringify(mahasiswa, (_, value) =>
      typeof value === 'bigint' ? value.toString() : value
    ));

    res.status(200).json(
      ResponseFormatter.success(
        'Mahasiswa with grades retrieved successfully',
        serializedData
      )
    );
  });
}