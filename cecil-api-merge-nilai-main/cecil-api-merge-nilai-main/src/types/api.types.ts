export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  errors?: any[];
  pagination?: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
}

export interface ErrorResponse {
  success: false;
  message: string;
  errors?: any[];
  stack?: string;
}

export interface ExternalApiResponse<T = any> {
  success: boolean;
  message: string;
  data: T;
}

export interface ValidationError {
  field: string;
  message: string;
  value?: any;
}

export interface DatabaseError {
  code: string;
  message: string;
  meta?: any;
}