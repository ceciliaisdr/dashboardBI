import winston from 'winston';
import { config } from '@/config/app';

const logFormat = winston.format.combine(
  winston.format.timestamp(),
  winston.format.errors({ stack: true }),
  winston.format.colorize(),
  winston.format.printf(({ timestamp, level, message, stack }) => {
    return `${timestamp} [${level}]: ${message}${stack ? '\n' + stack : ''}`;
  })
);

export const logger = winston.createLogger({
  level: config.logging.level,
  format: logFormat,
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      ),
    }),
    new winston.transports.File({
      filename: config.logging.file,
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      ),
    }),
  ],
  exceptionHandlers: [
    new winston.transports.File({ filename: './logs/exceptions.log' }),
  ],
  rejectionHandlers: [
    new winston.transports.File({ filename: './logs/rejections.log' }),
  ],
});

// If we're not in production then log to the `console`
if (config.nodeEnv !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple()
  }));
}