import { prisma } from '@/config/database';
import { Prisma } from '@prisma/client';
import { logger } from '@/utils/logger';

export class PrismaService {
  async executeInTransaction<T>(
    operations: (tx: Prisma.TransactionClient) => Promise<T>
  ): Promise<T> {
    try {
      return await prisma.$transaction(operations, {
        maxWait: 5000,
        timeout: 10000,
      });
    } catch (error) {
      logger.error('Transaction failed:', error);
      throw error;
    }
  }

  async bulkUpsert<T extends Record<string, any>>(
    tableName: string,
    data: T[],
    uniqueKeys: string[]
  ): Promise<{ inserted: number; updated: number }> {
    let inserted = 0;
    let updated = 0;

    await this.executeInTransaction(async (tx) => {
      for (const item of data) {
        try {
          // Build where condition for unique keys
          const whereCondition: Record<string, any> = {};
          uniqueKeys.forEach(key => {
            whereCondition[key] = item[key];
          });

          // Use upsert operation
          const result = await (tx as any)[tableName].upsert({
            where: whereCondition,
            update: item,
            create: item,
          });

          // Check if record was created or updated
          const existingRecord = await (tx as any)[tableName].findUnique({
            where: whereCondition,
            select: { created_at: true, updated_at: true },
          });

          if (existingRecord && existingRecord.created_at.getTime() === existingRecord.updated_at.getTime()) {
            inserted++;
          } else {
            updated++;
          }
        } catch (error) {
          logger.error(`Error upserting record:`, { item, error });
          throw error;
        }
      }
    });

    return { inserted, updated };
  }

  async healthCheck(): Promise<boolean> {
    try {
      await prisma.$queryRaw`SELECT 1`;
      return true;
    } catch (error) {
      logger.error('Database health check failed:', error);
      return false;
    }
  }

  async getConnectionInfo(): Promise<any> {
    try {
      const result = await prisma.$queryRaw`
        SELECT 
          CONNECTION_ID() as connection_id,
          USER() as user,
          DATABASE() as database_name,
          VERSION() as mysql_version
      `;
      return result;
    } catch (error) {
      logger.error('Failed to get connection info:', error);
      return null;
    }
  }
}