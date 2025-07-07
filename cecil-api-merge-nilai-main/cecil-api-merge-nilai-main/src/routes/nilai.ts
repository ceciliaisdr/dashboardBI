import { Router } from 'express';
import multer from 'multer';
import { NilaiController } from '@/controllers/NilaiController';
import { validateParams, validateFile } from '@/middlewares/validation';
import { nilaiParamsSchema, fileUploadSchema } from '@/schemas/nilai.schema';
import { config } from '@/config/app';

const router = Router();
const nilaiController = new NilaiController();

// Configure multer for file upload
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: config.upload.maxFileSize,
  },
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'text/csv' || file.mimetype === 'application/vnd.ms-excel') {
      cb(null, true);
    } else {
      cb(new Error('Only CSV files are allowed'));
    }
  },
});

/**
 * @swagger
 * /api/nilai/upload:
 *   post:
 *     summary: Upload and process CSV file with student grades
 *     tags: [Nilai]
 *     requestBody:
 *       required: true
 *       content:
 *         multipart/form-data:
 *           schema:
 *             type: object
 *             properties:
 *               file:
 *                 type: string
 *                 format: binary
 *                 description: CSV file with grade data
 *     responses:
 *       200:
 *         description: CSV processed successfully
 *       400:
 *         description: Invalid file or processing error
 */
router.post(
  '/upload',
  upload.single('file'),
  validateFile(fileUploadSchema),
  nilaiController.uploadNilai
);

/**
 * @swagger
 * /api/nilai/{nim}:
 *   get:
 *     summary: Get all grades for a student
 *     tags: [Nilai]
 *     parameters:
 *       - in: path
 *         name: nim
 *         required: true
 *         schema:
 *           type: string
 *     responses:
 *       200:
 *         description: Grades retrieved successfully
 *       404:
 *         description: Student not found
 */
router.get(
  '/:nim',
  validateParams(nilaiParamsSchema),
  nilaiController.getNilaiByNim
);

export { router as nilaiRoutes };