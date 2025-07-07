import { Request, Response } from 'express';
import { NilaiService } from '@/services/NilaiService';
import { ResponseFormatter } from '@/utils/responseFormatter';
import { asyncHandler } from '@/middlewares/errorHandler';
import { NilaiParams } from '@/schemas/nilai.schema';

export class NilaiController {
  private nilaiService: NilaiService;

  constructor() {
    this.nilaiService = new NilaiService();
  }

  uploadNilai = asyncHandler(async (req: Request, res: Response) => {
    if (!req.file) {
      return res.status(400).json(
        ResponseFormatter.error('CSV file is required')
      );
    }

    const result = await this.nilaiService.uploadNilaiFromCSV(req.file.buffer);

    if (result.success) {
      res.status(200).json(ResponseFormatter.success(result.message, result.data));
    } else {
      res.status(400).json(ResponseFormatter.error(result.message, result.data.errors));
    }
  });

  getNilaiByNim = asyncHandler(async (req: Request, res: Response) => {
    const { nim } = req.params as unknown as NilaiParams;

    const nilai = await this.nilaiService.getNilaiByNim(nim);

    res.status(200).json(
      ResponseFormatter.success('Grades retrieved successfully', nilai)
    );
  });
}