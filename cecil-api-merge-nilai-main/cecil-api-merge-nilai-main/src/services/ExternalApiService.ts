import axios, { AxiosInstance } from 'axios';
import { config } from '@/config/app';
import { ExternalMahasiswaData, MahasiswaSyncRequest } from '@/types/mahasiswa.types';
import { ExternalApiResponse } from '@/types/api.types';
import { logger } from '@/utils/logger';

export class ExternalApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: config.externalApi.baseUrl,
      timeout: 30000,
      headers: {
        // 'API_KEY_NAME': 'X-UPNVJ-API-KEY',
        'X-UPNVJ-API-KEY': config.externalApi.apiKey,
      },
      auth: {
        username: config.externalApi.username,
        password: config.externalApi.password,
      },
    });

    // Request interceptor for logging
    this.api.interceptors.request.use(
      (config) => {
        logger.info(`External API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        logger.error('External API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor for logging
    this.api.interceptors.response.use(
      (response) => {
        logger.info(`External API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        logger.error('External API Response Error:', {
          url: error.config?.url,
          status: error.response?.status,
          message: error.message,
          data: error.response?.data,
        });
        return Promise.reject(error);
      }
    );
  }

  async getMahasiswaByAngkatan(angkatan: string): Promise<ExternalMahasiswaData[]> {
    try {
      const formData = new FormData();
      formData.append('angkatan', angkatan);
      
      const response = await this.api.post<ExternalApiResponse<ExternalMahasiswaData[]>>(
        '/data/list_mahasiswa',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      if (!response.data.success) {
        throw new Error(`External API Error: ${response.data.message}`);
      }

      const allowedProgramStudi = ['3', '4', '6', '58']; // S1 Informatika, S1 SI, DIII SI, S1 Sains Data
      const filteredData = response.data.data.filter(mahasiswa => 
        allowedProgramStudi.includes(mahasiswa.id_program_studi.toString())
      );

      logger.info(`Received ${response.data.data.length} mahasiswa, filtered to ${filteredData.length}`);
      return filteredData;
    } catch (error) {
      logger.error('Error fetching mahasiswa from external API:', error);
      throw new Error('Failed to fetch mahasiswa data from external API');
    }
  }

  async testConnection(): Promise<boolean> {
    try {
      // Test with a small request
      await this.getMahasiswaByAngkatan('2024');
      return true;
    } catch (error) {
      logger.error('External API connection test failed:', error);
      return false;
    }
  }
}