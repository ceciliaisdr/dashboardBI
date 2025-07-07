import { Request, Response, NextFunction } from 'express';
import { Prisma } from '@prisma/client';
import { ResponseFormatter } from '@/utils/responseFormatter';
import { logger } from '@/utils/logger';

export class AppError extends Error {
  public statusCode: number;
  public isOperational: boolean;

  constructor(message: string, statusCode: number = 500, isOperational: boolean = true) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = isOperational;

    Error.captureStackTrace(this, this.constructor);
  }
}

export function handlePrismaError(error: any): AppError {
  if (error instanceof Prisma.PrismaClientKnownRequestError) {
    switch (error.code) {
      case 'P2002':
        return new AppError('A record with this data already exists', 409);
      case 'P2025':
        return new AppError('Record not found', 404);
      case 'P2003':
        return new AppError('Foreign key constraint failed', 400);
      case 'P2014':
        return new AppError('The change you are trying to make would violate the required relation', 400);
      case 'P2021':
        return new AppError('The table does not exist in the current database', 500);
      case 'P2022':
        return new AppError('The column does not exist in the current database', 500);
      default:
        logger.error('Unknown Prisma error:', { code: error.code, message: error.message });
        return new AppError('Database operation failed', 500);
    }
  }

  if (error instanceof Prisma.PrismaClientUnknownRequestError) {
    return new AppError('Unknown database error occurred', 500);
  }

  if (error instanceof Prisma.PrismaClientRustPanicError) {
    return new AppError('Database engine error', 500);
  }

  if (error instanceof Prisma.PrismaClientInitializationError) {
    return new AppError('Database connection failed', 503);
  }

  if (error instanceof Prisma.PrismaClientValidationError) {
    return new AppError('Invalid data provided', 400);
  }

  return new AppError('Internal server error', 500);
}

export function globalErrorHandler(
  error: any,
  req: Request,
  res: Response,
  next: NextFunction
): void {
  let appError: AppError;

  // Handle different types of errors
  if (error instanceof AppError) {
    appError = error;
  } else if (error.name === 'ValidationError') {
    appError = new AppError('Validation failed', 400);
  } else if (error.name === 'CastError') {
    appError = new AppError('Invalid data format', 400);
  } else if (error.code === 'LIMIT_FILE_SIZE') {
    appError = new AppError('File too large', 413);
  } else if (error.code === 'ECONNREFUSED') {
    appError = new AppError('Database connection refused', 503);
  } else if (error instanceof Prisma.PrismaClientKnownRequestError ||
             error instanceof Prisma.PrismaClientUnknownRequestError ||
             error instanceof Prisma.PrismaClientRustPanicError ||
             error instanceof Prisma.PrismaClientInitializationError ||
             error instanceof Prisma.PrismaClientValidationError) {
    appError = handlePrismaError(error);
  } else {
    appError = new AppError(error.message || 'Internal server error', 500, false);
  }

  // Log error details
  logger.error('Error occurred:', {
    error: {
      message: appError.message,
      statusCode: appError.statusCode,
      stack: appError.stack,
      isOperational: appError.isOperational,
    },
    request: {
      method: req.method,
      url: req.url,
      ip: req.ip,
      userAgent: req.get('User-Agent'),
    },
    originalError: error,
  });

  // Send error response
  res.status(appError.statusCode).json(
    ResponseFormatter.error(
      appError.message,
      undefined,
      appError.stack
    )
  );
}

export function notFoundHandler(req: Request, res: Response): void {
  res.status(404).json(
    ResponseFormatter.error(
      `Route ${req.method} ${req.path} not found`
    )
  );
}

// Async error handler wrapper
export function asyncHandler(fn: Function) {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}