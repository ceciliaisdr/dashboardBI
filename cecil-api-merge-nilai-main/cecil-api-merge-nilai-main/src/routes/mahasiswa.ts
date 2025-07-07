import { Router } from 'express';
import multer from 'multer';
import { MahasiswaController } from '@/controllers/MahasiswaController';
import { validateBody, validateQuery, validateParams } from '@/middlewares/validation';
import {
  mahasiswaSyncSchema,
  mahasiswaListQuerySchema,
  mahasiswaParamsSchema,
} from '@/schemas/mahasiswa.schema';

const router = Router();
const mahasiswaController = new MahasiswaController();

/**
 * @swagger
 * /api/mahasiswa/sync:
 *   post:
 *     summary: Synchronize student data from external API
 *     tags: [Mahasiswa]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               angkatan:
 *                 type: string
 *                 description: Year of admission (4 digits)
 *                 example: "2020"
 *     responses:
 *       200:
 *         description: Synchronization completed successfully
 *       400:
 *         description: Bad request or validation error
 */
router.post(
  '/sync',
  validateBody(mahasiswaSyncSchema),
  mahasiswaController.syncMahasiswa
);

/**
 * @swagger
 * /api/mahasiswa:
 *   get:
 *     summary: Get list of students with pagination and filtering
 *     tags: [Mahasiswa]
 *     parameters:
 *       - in: query
 *         name: page
 *         schema:
 *           type: integer
 *           minimum: 1
 *           default: 1
 *       - in: query
 *         name: limit
 *         schema:
 *           type: integer
 *           minimum: 1
 *           maximum: 999999999
 *           default: 10
 *       - in: query
 *         name: angkatan
 *         schema:
 *           type: string
 *       - in: query
 *         name: program_studi
 *         schema:
 *           type: integer
 *       - in: query
 *         name: search
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: List of students retrieved successfully
 */
router.get(
  '/',
  validateQuery(mahasiswaListQuerySchema),
  mahasiswaController.getMahasiswa
);

/**
 * @swagger
 * /api/mahasiswa/{nim}:
 *   get:
 *     summary: Get student by NIM
 *     tags: [Mahasiswa]
 *     parameters:
 *       - in: path
 *         name: nim
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Student data retrieved successfully
 *       404:
 *         description: Student not found
 */
router.get(
  '/:nim',
  validateParams(mahasiswaParamsSchema),
  mahasiswaController.getMahasiswaByNim
);

/**
 * @swagger
 * /api/mahasiswa/{nim}/nilai:
 *   get:
 *     summary: Get student with all grades
 *     tags: [Mahasiswa]
 *     parameters:
 *       - in: path
 *         name: nim
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Student with grades retrieved successfully
 *       404:
 *         description: Student not found
 */
router.get(
  '/:nim/nilai',
  validateParams(mahasiswaParamsSchema),
  mahasiswaController.getMahasiswaWithNilai
);

export { router as mahasiswaRoutes };