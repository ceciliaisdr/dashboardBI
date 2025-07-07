import { Request, Response, NextFunction } from 'express';
import { ZodSchema, ZodError } from 'zod';
import { ResponseFormatter } from '@/utils/responseFormatter';
import { logger } from '@/utils/logger';

export function validateBody(schema: ZodSchema) {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      req.body = schema.parse(req.body);
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        const validationErrors = error.errors.map(err => ({
          field: err.path.join('.'),
          message: err.message,
          value: err.input,
        }));

        logger.warn('Validation error in request body:', validationErrors);

        return res.status(400).json(
          ResponseFormatter.error('Validation failed', validationErrors)
        );
      }
      next(error);
    }
  };
}

export function validateQuery(schema: ZodSchema) {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      req.query = schema.parse(req.query);
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        const validationErrors = error.errors.map(err => ({
          field: err.path.join('.'),
          message: err.message,
          value: err.input,
        }));

        logger.warn('Validation error in query parameters:', validationErrors);

        return res.status(400).json(
          ResponseFormatter.error('Query validation failed', validationErrors)
        );
      }
      next(error);
    }
  };
}

export function validateParams(schema: ZodSchema) {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      req.params = schema.parse(req.params);
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        const validationErrors = error.errors.map(err => ({
          field: err.path.join('.'),
          message: err.message,
          value: err.input,
        }));

        logger.warn('Validation error in path parameters:', validationErrors);

        return res.status(400).json(
          ResponseFormatter.error('Parameter validation failed', validationErrors)
        );
      }
      next(error);
    }
  };
}

export function validateFile(schema: ZodSchema) {
  return (req: Request, res: Response, next: NextFunction) => {
    try {
      if (!req.file) {
        return res.status(400).json(
          ResponseFormatter.error('File is required')
        );
      }

      schema.parse(req.file);
      next();
    } catch (error) {
      if (error instanceof ZodError) {
        const validationErrors = error.errors.map(err => ({
          field: err.path.join('.'),
          message: err.message,
          value: err.input,
        }));

        logger.warn('File validation error:', validationErrors);

        return res.status(400).json(
          ResponseFormatter.error('File validation failed', validationErrors)
        );
      }
      next(error);
    }
  };
}