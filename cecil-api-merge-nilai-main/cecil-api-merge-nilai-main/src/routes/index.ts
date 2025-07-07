import { Router } from 'express';
import { mahasiswaRoutes } from './mahasiswa';
import { nilaiRoutes } from './nilai';
import { laporanRoutes } from './laporan';

const router = Router();

// Health check endpoint
router.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV,
  });
});

// API routes
router.use('/mahasiswa', mahasiswaRoutes);
router.use('/nilai', nilaiRoutes);
router.use('/laporan', laporanRoutes);

export { router as apiRoutes };