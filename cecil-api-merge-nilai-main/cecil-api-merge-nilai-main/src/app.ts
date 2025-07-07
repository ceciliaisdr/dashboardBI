import express, { Application } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import swaggerJsdoc from 'swagger-jsdoc';
import swaggerUi from 'swagger-ui-express';
import { config } from '@/config/app';
import { apiRoutes } from '@/routes';
import { requestLogger, errorLogger } from '@/middlewares/logger';
import { globalErrorHandler, notFoundHandler } from '@/middlewares/errorHandler';
import { logger } from '@/utils/logger';

class App {
  public app: Application;

  constructor() {
    this.app = express();
    this.initializeMiddlewares();
    this.initializeRoutes();
    this.initializeSwagger();
    this.initializeErrorHandling();
  }

  private initializeMiddlewares(): void {
    // Security middleware
    this.app.use(helmet());
    this.app.use(cors({
      origin: process.env.ALLOWED_ORIGINS?.split(',') || '*',
      credentials: true,
    }));

    // Rate limiting
    const limiter = rateLimit({
      windowMs: config.rateLimit.windowMs,
      max: config.rateLimit.maxRequests,
      message: {
        success: false,
        message: 'Too many requests, please try again later.',
      },
      standardHeaders: true,
      legacyHeaders: false,
    });
    this.app.use('/api', limiter);

    // Body parsing middleware
    this.app.use(express.json({ limit: '10mb' }));
    this.app.use(express.urlencoded({ extended: true, limit: '10mb' }));

    // Logging middleware
    this.app.use(requestLogger);
  }

  private initializeRoutes(): void {
    // API routes
    this.app.use('/api', apiRoutes);

    // Root endpoint
    this.app.get('/', (req, res) => {
      res.json({
        name: 'Student Grade Management API',
        version: '1.0.0',
        description: 'API for managing student data and grades with external integration',
        documentation: '/api-docs',
        health: '/api/health',
      });
    });
  }

  private initializeSwagger(): void {
    const options = {
      definition: {
        openapi: '3.0.0',
        info: {
          title: 'Student Grade Management API',
          version: '1.0.0',
          description: 'API for managing student data and grades with external integration',
          contact: {
            name: 'API Support',
            email: 'support@example.com',
          },
        },
        servers: [
          {
            url: `http://localhost:${config.port}`,
            description: 'Development server',
          },
        ],
        components: {
          securitySchemes: {
            bearerAuth: {
              type: 'http',
              scheme: 'bearer',
              bearerFormat: 'JWT',
            },
          },
        },
      },
      apis: ['./src/routes/*.ts'],
    };

    const specs = swaggerJsdoc(options);
    this.app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(specs, {
      explorer: true,
      customCss: '.swagger-ui .topbar { display: none }',
      customSiteTitle: 'Student API Documentation',
    }));
  }

  private initializeErrorHandling(): void {
    // Error logging middleware
    this.app.use(errorLogger);

    // 404 handler
    this.app.use(notFoundHandler);

    // Global error handler
    this.app.use(globalErrorHandler);
  }

  public listen(): void {
    this.app.listen(config.port, () => {
      logger.info(`🚀 Server running on port ${config.port}`);
      logger.info(`📚 API Documentation: http://localhost:${config.port}/api-docs`);
      logger.info(`🏥 Health Check: http://localhost:${config.port}/api/health`);
      logger.info(`🌍 Environment: ${config.nodeEnv}`);
    });
  }
}

export default App;