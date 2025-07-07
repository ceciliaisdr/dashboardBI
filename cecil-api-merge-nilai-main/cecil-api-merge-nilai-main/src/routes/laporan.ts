import { Router } from 'express';
import { LaporanController } from '@/controllers/LaporanController';
import { validateParams } from '@/middlewares/validation';
import { nilaiParamsSchema } from '@/schemas/nilai.schema';

const router = Router();
const laporanController = new LaporanController();

/**
 * @swagger
 * /api/laporan/transkrip/{nim}:
 *   get:
 *     summary: Generate academic transcript for a student
 *     tags: [Laporan]
 *     parameters:
 *       - in: path
 *         name: nim
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Academic transcript generated successfully
 *       404:
 *         description: Student not found
 */
router.get(
  '/transkrip/:nim',
  validateParams(nilaiParamsSchema),
  laporanController.getTranskrip
);

/**
 * @swagger
 * /api/laporan/semester-summary/{nim}:
 *   get:
 *     summary: Get semester summary for a student
 *     tags: [Laporan]
 *     parameters:
 *       - in: path
 *         name: nim
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Semester summary retrieved successfully
 *       404:
 *         description: Student not found
 */
router.get(
  '/semester-summary/:nim',
  validateParams(nilaiParamsSchema),
  laporanController.getSemesterSummary
);

/**
 * @swagger
 * /api/laporan/update-ipk:
 *   post:
 *     summary: Update IPK for all students
 *     tags: [Laporan]
 *     responses:
 *       200:
 *         description: IPK update completed successfully
 */
router.post('/update-ipk', laporanController.updateAllIPK);

export { router as laporanRoutes };