import 'module-alias/register';
import App from './app';
import { logger } from '@/utils/logger';
import { prisma } from '@/config/database';

// Handle uncaught exceptions
process.on('uncaughtException', (error: Error) => {
  logger.error('Uncaught Exception:', error);
  process.exit(1);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason: any, promise: Promise<any>) => {
  logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  logger.info('SIGTERM received. Starting graceful shutdown...');
  await prisma.$disconnect();
  process.exit(0);
});

process.on('SIGINT', async () => {
  logger.info('SIGINT received. Starting graceful shutdown...');
  await prisma.$disconnect();
  process.exit(0);
});

// Start the application
async function bootstrap() {
  try {
    // Test database connection
    await prisma.$connect();
    logger.info('✅ Database connected successfully');

    // Start server
    const app = new App();
    app.listen();
  } catch (error) {
    logger.error('❌ Failed to start application:', error);
    process.exit(1);
  }
}

bootstrap();