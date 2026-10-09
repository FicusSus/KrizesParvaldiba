# Crisis Prediction and Warning System

A full-stack web application for processing large datasets, predicting crises, and sending warnings to users. Built with **FastAPI (Python)** backend and **React + TypeScript + Vite** frontend.

## Project Structure

```
KrizesParvaldiba/
├── backend/                  # Python FastAPI Backend
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   │   └── v1/           # API version 1
│   │   ├── core/             # Core utilities
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   └── services/         # Business logic services
│   ├── pyproject.toml        # Python project config
│   └── requirements.txt      # Python dependencies
│
├── frontend/                 # React Frontend
│   ├── src/
│   │   ├── components/       # Reusable components
│   │   │   ├── Common/      # Generic components (DataTable, Badges, etc.)
│   │   │   ├── Layout/      # Layout components
│   │   │   ├── Charts/      # Chart components
│   │   │   └── Auth/        # Authentication components
│   │   ├── pages/           # Page components
│   │   │   ├── Data/        # Data management pages
│   │   │   ├── Crisis/      # Crisis detection pages
│   │   │   ├── Warnings/    # Warning management pages
│   │   │   ├── Auth/        # Authentication pages
│   │   │   └── Dashboard/   # Dashboard page
│   │   ├── stores/          # Zustand state stores
│   │   ├── services/       # API service layer
│   │   ├── types/          # TypeScript type definitions
│   │   └── utils/          # Utility functions
│   ├── vite.config.ts       # Vite configuration
│   ├── tailwind.config.js   # Tailwind CSS theme
│   └── package.json         # Frontend dependencies
│
├── .env.example             # Example environment variables
└── README.md
```

## Features

### Backend (FastAPI)

- **Data Processing**: High-performance data processing with Polars for large datasets
- **Crisis Prediction**: Machine learning models using scikit-learn for crisis detection and severity prediction
- **Warning System**: Multi-channel notification system (Email, SMS, Push, Webhook, In-App)
- **REST API**: Well-designed API with proper validation and error handling
- **Async Database**: SQLAlchemy with asyncpg for PostgreSQL
- **Authentication**: JWT-based authentication with token refresh
- **Rate Limiting**: Built-in rate limiting for API protection
- **Logging**: Structured logging with structlog

### Frontend (React + TypeScript)

- **Modern UI**: Clean, responsive design with Tailwind CSS
- **Data Visualization**: Charts and statistics using Recharts
- **State Management**: Zustand for lightweight state management
- **Data Fetching**: TanStack Query (React Query v5) for server state
- **Routing**: React Router v6 for client-side routing
- **Type Safety**: Full TypeScript support with comprehensive type definitions
- **Reusable Components**: Generic DataTable, Badges, Modals, etc.

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis (optional, for caching)

### Backend Setup

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy and configure environment file:
   ```bash
   cp .env.example .env
   # Edit .env with your database and other settings
   ```

5. Initialize database:
   ```bash
   # This will create the database tables
   # Note: Make sure PostgreSQL is running and .env is configured
   python -c "from app.core.database import Base, engine; from app.models.user import User; Base.metadata.create_all(engine)"
   ```

6. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Copy and configure environment file:
   ```bash
   cp .env.example .env
   # Edit .env if needed
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

   The frontend will be available at `http://localhost:3000`

## API Documentation

API documentation is automatically generated using FastAPI and available at:
- `http://localhost:8000/docs` - Interactive Swagger UI
- `http://localhost:8000/redoc` - Alternative Redoc documentation

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/health | Health check |
| POST | /api/v1/users/register | Register a new user |
| POST | /api/v1/users/login | Login and get JWT token |
| GET | /api/v1/users/me | Get current user |
| GET | /api/v1/data | List all datasets |
| POST | /api/v1/data/upload | Upload a dataset |
| DELETE | /api/v1/data/{id} | Delete a dataset |
| GET | /api/v1/crisis | List all crises |
| POST | /api/v1/crisis/predict | Run crisis prediction |
| GET | /api/v1/crisis/{id} | Get crisis details |
| DELETE | /api/v1/crisis/{id} | Delete a crisis |
| GET | /api/v1/warnings | List all warnings |
| POST | /api/v1/warnings | Create a warning |
| DELETE | /api/v1/warnings/{id} | Delete a warning |

## Data Processing

The system supports processing large datasets in multiple formats:
- CSV
- JSON
- Excel (XLSX, XLS)
- Parquet

### Features:
- Chunked processing for memory efficiency
- Automatic feature extraction
- Data cleaning and validation
- Statistical analysis
- Progress tracking

## Crisis Prediction

### Supported Models:
- **Crisis Detection**: Identify if a crisis is occurring
- **Severity Prediction**: Predict the severity level (Low, Medium, High, Critical)
- **Type Classification**: Classify crisis type (Financial, Economic, Political, Social, Environmental, Health, Security)
- **Timeline Prediction**: Predict crisis duration and timeline
- **Impact Assessment**: Assess the potential impact

### Model Training:
- Random Forest classifiers
- Gradient Boosting classifiers
- Customizable model parameters
- Model persistence and versioning

## Warning System

### Warning Channels:
- **Email**: SMTP-based email notifications
- **SMS**: Twilio integration for SMS alerts
- **Push Notifications**: Browser push notifications
- **Webhook**: HTTP webhook integrations
- **In-App**: In-application notifications

### Warning Priority:
- Urgent: Critical crises requiring immediate attention
- High: High-severity crises
- Medium: Moderate-severity crises
- Low: Low-severity informational alerts

## Project Configuration

### Environment Variables

#### Backend (.env)
```env
# Application
APP_NAME="Crisis Prediction Backend"
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/crisis_db

# Security
SECRET_KEY=your-secret-key-here

# Notifications
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=user@example.com
SMTP_PASSWORD=password
```

#### Frontend (.env)
```env
VITE_APP_NAME="Crisis Prediction"
VITE_API_BASE_URL=http://localhost:8000
VITE_API_VERSION=/api/v1
```

## Running Tests

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm run test
```

## Technology Stack

### Backend
- **Framework**: FastAPI
- **Database**: SQLAlchemy ORM with asyncpg (PostgreSQL)
- **Data Processing**: Polars, Pandas, NumPy
- **Machine Learning**: scikit-learn, joblib
- **Async**: anyio
- **Configuration**: pydantic-settings
- **Logging**: structlog

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **Bundler**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Data Fetching**: TanStack Query v5
- **Routing**: React Router v6
- **Charts**: Recharts, Chart.js
- **Icons**: Lucide React

## Directory Structure Explained

### Backend Structure
- `app/core/`: Configuration, database, logging, security utilities
- `app/models/`: SQLAlchemy database models
- `app/schemas/`: Pydantic schemas for request/response validation
- `app/api/`: FastAPI route handlers
- `app/services/`: Business logic services (DataProcessor, CrisisPredictor, WarningService)

### Frontend Structure
- `src/components/`: Reusable UI components
- `src/pages/`: Page-level components with routes
- `src/stores/`: Zustand state stores
- `src/services/`: API service layer
- `src/types/`: TypeScript type definitions

## Deployment

### Docker (Recommended)

Create a `Dockerfile` and `docker-compose.yml` for containerized deployment.

### Production Considerations
- Use `DEBUG=false` in production
- Generate a strong `SECRET_KEY`
- Configure proper CORS origins
- Set up a reverse proxy (Nginx, Apache)
- Use a production database (PostgreSQL, MySQL)
- Enable HTTPS

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Contact

For questions or support, please contact the development team.

---

**Version**: 0.1.0  
**Last Updated**: 2026-10-09  
**Maintainers**: Crisis Prediction Team
