import { ApiResponse, ErrorResponse } from '@/types/api.types';

export class ResponseFormatter {
  static success<T>(
    message: string,
    data?: T,
    pagination?: any
  ): ApiResponse<T> {
    const response: ApiResponse<T> = {
      success: true,
      message,
    };

    if (data !== undefined) {
      response.data = data;
    }

    if (pagination) {
      response.pagination = pagination;
    }

    return response;
  }

  static error(
    message: string,
    errors?: any[],
    stack?: string
  ): ErrorResponse {
    const response: ErrorResponse = {
      success: false,
      message,
    };

    if (errors && errors.length > 0) {
      response.errors = errors;
    }

    if (stack && process.env.NODE_ENV === 'development') {
      response.stack = stack;
    }

    return response;
  }

  static paginate(
    page: number,
    limit: number,
    total: number
  ) {
    const total_pages = Math.ceil(total / limit);
    const has_next = page < total_pages;
    const has_prev = page > 1;

    return {
      page,
      limit,
      total,
      total_pages,
      has_next,
      has_prev,
    };
  }
}