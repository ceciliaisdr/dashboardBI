import dotenv from 'dotenv';

dotenv.config();

export const config = {
  port: parseInt(process.env.PORT || '3000'),
  nodeEnv: process.env.NODE_ENV || 'development',
  database: {
    url: process.env.DATABASE_URL!,
  },
  externalApi: {
    baseUrl: process.env.EXTERNAL_API_BASE_URL!,
    username: process.env.EXTERNAL_API_USERNAME!,
    password: process.env.EXTERNAL_API_PASSWORD!,
    apiKey: process.env.EXTERNAL_API_KEY!,
  },
  jwt: {
    secret: process.env.JWT_SECRET!,
    expiresIn: process.env.JWT_EXPIRES_IN || '24h',
  },
  rateLimit: {
    windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS || '900000'),
    maxRequests: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS || '100'),
  },
  upload: {
    maxFileSize: parseInt(process.env.MAX_FILE_SIZE || '10485760'), // 10MB
    uploadPath: process.env.UPLOAD_PATH || './uploads',
  },
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    file: process.env.LOG_FILE || './logs/app.log',
  },
};

// Validate required environment variables
const requiredEnvVars = [
  'DATABASE_URL',
  'EXTERNAL_API_BASE_URL',
  'EXTERNAL_API_USERNAME',
  'EXTERNAL_API_PASSWORD',
  'EXTERNAL_API_KEY',
  'JWT_SECRET',
];

for (const envVar of requiredEnvVars) {
  if (!process.env[envVar]) {
    throw new Error(`Missing required environment variable: ${envVar}`);
  }
}