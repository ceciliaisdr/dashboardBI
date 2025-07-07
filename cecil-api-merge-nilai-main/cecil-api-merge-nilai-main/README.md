## 📋 Prerequisites

- Node.js 18+ 
- MySQL 8.0+
- Docker & Docker Compose (optional)

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/draft-coding-id/cecil-api-merge-nilai.git
cd cecil-api-merge-nilai
```

### 2. Environment Setup

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Database Setup

#### Using Docker (Optional)

```bash
# Start MySQL with Docker Compose
docker-compose up -d mysql

#Wait for MySQL to be ready, then run migrations
npm run prisma:migrate
npm run prisma:seed
```

#### Manual MySQL Setup

```bash
# Create database
mysql -u root -p
CREATE DATABASE mahasiswa_db;

# Run migrations
npm run prisma:migrate
npm run prisma:seed (optional)
```

### 4. Install Dependencies

```bash
npm install
```

### 5. Generate Prisma Client

```bash
npm run prisma:generate
```

### 6. Start Development Server

```bash
npm run dev
```

The API will be available at:
- **API**: http://localhost:9000
- **Documentation**: http://localhost:9000/api-docs
- **Health Check**: http://localhost:9000/api/health

## 🐳 Docker Deployment

### Full Stack with Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### Production Build

```bash
# Build production image
docker build -t student-api .

# Run container
docker run -p 9000:9000 --env-file .env student-api
```

## 📚 API Documentation

### Core Endpoints

#### Student Management
- `POST /api/mahasiswa/sync` - Sync students from external API
- `GET /api/mahasiswa` - List students with pagination/filtering
- `GET /api/mahasiswa/:nim` - Get student by NIM
- `GET /api/mahasiswa/:nim/nilai` - Get student with grades

#### Grade Management
- `POST /api/nilai/upload` - Upload CSV grade data
- `GET /api/nilai/:nim` - Get grades by student NIM

#### Reports
- `GET /api/laporan/transkrip/:nim` - Generate academic transcript
- `GET /api/laporan/semester-summary/:nim` - Get semester summary
- `POST /api/laporan/update-ipk` - Update GPA for all students

### External API Integration

The system integrates with UPNVJ API to sync student data:

```bash
# Sync students for specific year
curl -X POST http://localhost:9000/api/mahasiswa/sync \
  -H "Content-Type: application/json" \
  -d '{"angkatan": "2020"}'
```

### CSV Upload Format

Upload grade data using CSV with these columns:

```csv
f_nim,f_kodemk,f_namamk,f_namapegawai,f_title_depan,f_title_belakang,f_sks,f_kelas,f_totalnilai,f_nilaihuruf,f_thakad,f_semester,f_kurikulum
2020123001,IF101,Algoritma dan Pemrograman,Ahmad Sutanto,Dr.,M.Kom,3,A,85,A,2020/2021,1,2020
```

## 🗄 Database Schema

### Key Tables

- **mahasiswa**: Student information
- **mata_kuliah**: Course catalog
- **dosen**: Faculty information  
- **nilai_mahasiswa**: Student grades with relationships

### Prisma Commands

```bash
# Generate client
npm run prisma:generate

# Run migrations
npm run prisma:migrate

# Deploy to production
npm run prisma:deploy

# Seed database
npm run prisma:seed

# Open Prisma Studio
npm run prisma:studio

# Reset database
npm run prisma:reset
```

## 🧪 Testing

```bash
# Run all tests
npm test

# Run tests in watch mode
npm run test:watch

# Generate coverage report
npm run test:coverage
```

### Test Structure

```
tests/
├── setup.ts              # Test configuration
├── services/             # Service layer tests
├── controllers/          # Controller tests
├── utils/               # Utility function tests
└── integration/         # API integration tests
```

## 📊 Performance Features

### Database Optimization
- **Indexing**: Strategic indexes on frequently queried columns
- **Bulk Operations**: Efficient batch processing for large datasets
- **Connection Pooling**: Optimized database connections
- **Query Optimization**: Proper use of Prisma select/include

### Application Performance
- **Rate Limiting**: Configurable request throttling
- **Caching**: Redis integration for frequently accessed data
- **Compression**: Response compression middleware
- **Memory Management**: Efficient CSV processing for large files

## 🔒 Security Features

- **Helmet**: Security headers
- **CORS**: Configurable cross-origin requests
- **Rate Limiting**: DDoS protection
- **Input Validation**: Comprehensive request validation
- **Error Handling**: Secure error responses without data leakage

## 📝 Logging & Monitoring

### Winston Logging
- **Structured Logging**: JSON format for production
- **Log Levels**: Configurable logging levels
- **File Rotation**: Automatic log file management
- **Error Tracking**: Comprehensive error logging

### Health Monitoring
```bash
# Check application health
curl http://localhost:9000/api/health
```

## 🚀 Production Deployment

### Environment Variables

```env
NODE_ENV=production
DATABASE_URL=mysql://user:password@host:port/database
EXTERNAL_API_BASE_URL=https://api.upnvj.ac.id
EXTERNAL_API_USERNAME=your_username
EXTERNAL_API_PASSWORD=your_password
EXTERNAL_API_KEY=your_api_key
JWT_SECRET=your_jwt_secret
```

### Production Checklist

- [ ] Set `NODE_ENV=production`
- [ ] Configure production database
- [ ] Set secure JWT secret
- [ ] Configure external API credentials
- [ ] Set up SSL/TLS
- [ ] Configure reverse proxy (nginx)
- [ ] Set up monitoring and alerting
- [ ] Configure log aggregation
- [ ] Set up automated backups