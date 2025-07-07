import { Request, Response, NextFunction } from 'express';
import { logger } from '@/utils/logger';

interface LogRequest extends Request {
  startTime?: number;
}

export function requestLogger(req: LogRequest, res: Response, next: NextFunction): void {
  req.startTime = Date.now();

  // Log incoming request
  logger.info('Incoming request', {
    method: req.method,
    url: req.url,
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    contentType: req.get('Content-Type'),
  });

  // Override res.json to log response
  const originalJson = res.json;
  res.json = function(body: any) {
    const duration = req.startTime ? Date.now() - req.startTime : 0;
    
    logger.info('Outgoing response', {
      method: req.method,
      url: req.url,
      statusCode: res.statusCode,
      duration: `${duration}ms`,
      ip: req.ip,
    });

    return originalJson.call(this, body);
  };

  next();
}

export function errorLogger(error: any, req: Request, res: Response, next: NextFunction): void {
  logger.error('Request error', {
    error: {
      message: error.message,
      stack: error.stack,
      name: error.name,
    },
    request: {
      method: req.method,
      url: req.url,
      ip: req.ip,
      userAgent: req.get('User-Agent'),
      body: req.body,
      params: req.params,
      query: req.query,
    },
  });

  next(error);
}