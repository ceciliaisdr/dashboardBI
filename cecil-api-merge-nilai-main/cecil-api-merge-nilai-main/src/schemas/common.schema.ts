import { z } from 'zod';

export const paginationSchema = z.object({
  page: z.coerce.number().min(1).default(1),
  limit: z.coerce.number().min(1).max(100).default(10),
});

export const idParamsSchema = z.object({
  id: z.coerce.number().min(1, 'ID must be a positive number'),
});

export const responseSchema = z.object({
  success: z.boolean(),
  message: z.string(),
  data: z.any().optional(),
  errors: z.array(z.any()).optional(),
  pagination: z.object({
    page: z.number(),
    limit: z.number(),
    total: z.number(),
    total_pages: z.number(),
    has_next: z.boolean(),
    has_prev: z.boolean(),
  }).optional(),
});

export type PaginationInput = z.infer<typeof paginationSchema>;
export type IdParams = z.infer<typeof idParamsSchema>;
export type ResponseOutput = z.infer<typeof responseSchema>;