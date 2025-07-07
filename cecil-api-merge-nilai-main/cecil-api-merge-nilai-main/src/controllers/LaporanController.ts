import { Request, Response } from 'express';
import { AcademicCalculationService } from '@/services/AcademicCalculationService';
import { ResponseFormatter } from '@/utils/responseFormatter';
import { asyncHandler } from '@/middlewares/errorHandler';
import { NilaiParams } from '@/schemas/nilai.schema';

export class LaporanController {
  private academicService: AcademicCalculationService;

  constructor() {
    this.academicService = new AcademicCalculationService();
  }

  getTranskrip = asyncHandler(async (req: Request, res: Response) => {
    const { nim } = req.params as unknown as NilaiParams;

    const transkrip = await this.academicService.generateTranskrip(nim);

    if (!transkrip) {
      return res.status(404).json(
        ResponseFormatter.error('Mahasiswa not found')
      );
    }

    res.status(200).json(
      ResponseFormatter.success('Academic transcript generated successfully', transkrip)
    );
  });

  updateAllIPK = asyncHandler(async (req: Request, res: Response) => {
    const result = await this.academicService.updateAllIPK();

    res.status(200).json(
      ResponseFormatter.success('IPK update completed', result)
    );
  });

  getSemesterSummary = asyncHandler(async (req: Request, res: Response) => {
    const { nim } = req.params as unknown as NilaiParams;

    const summary = await this.academicService.getSemesterSummary(nim);

    res.status(200).json(
      ResponseFormatter.success('Semester summary retrieved successfully', summary)
    );
  });
}