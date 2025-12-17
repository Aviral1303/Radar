# VC Founder Transition Tracking System

A production-grade internal tool for venture capital firms to track when professionals transition into founder roles.

## Overview

This system continuously identifies professionals in the United States who:
- Are (or were) employed at specified companies
- Are located in specified U.S. states
- Graduated from undergraduate programs at least 7 years ago

And detects when they transition into entrepreneurial roles (Founder, Co-Founder, CEO, Founding Engineer, Owner), sending daily email notifications.

## Architecture

- **Backend**: FastAPI with SQLAlchemy ORM
- **Database**: SQLite (easily migratable to PostgreSQL/Supabase)
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Scheduler**: APScheduler for daily cron jobs
- **Data Provider**: Apollo.io (abstracted for easy provider swapping)
- **Notifications**: Resend email API (abstracted for easy provider swapping)

## Project Structure

```
linkedin-tool/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── jobs/         # Scheduled jobs
│   ├── alembic/          # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/          # API client
│   │   ├── components/   # React components
│   │   └── App.tsx
│   └── package.json
└── README.md
```

## Setup

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

5. Edit `.env` with your API keys:
```env
APOLLO_API_KEY=your_apollo_api_key
RESEND_API_KEY=your_resend_api_key
BASIC_AUTH_USERNAME=admin
BASIC_AUTH_PASSWORD=your_secure_password
EMAIL_FROM=notifications@yourdomain.com
EMAIL_TO=admin@yourdomain.com
```

6. Run database migrations:
```bash
alembic upgrade head
```

7. Start the backend server:
```bash
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file (optional, for custom API URL):
```env
VITE_API_URL=http://localhost:8000
VITE_AUTH_USERNAME=admin
VITE_AUTH_PASSWORD=your_secure_password
```

4. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Usage

### 1. Configure Target Companies and States

1. Navigate to the Configuration tab in the dashboard
2. Enter target companies (one per line)
3. Enter target states (comma-separated, e.g., `CA, NY, IL`)
4. Click "Save" for each section

### 2. Trigger Initial Ingestion

1. Go to the Transitions tab
2. Click "Trigger Ingestion" in the Actions panel
3. The system will fetch profiles from Apollo.io based on your configuration

### 3. Run Detection

1. Click "Run Detection" in the Actions panel
2. The system will compare current roles with previous snapshots
3. New founder transitions will be detected and notifications sent

### 4. View Transitions

All detected founder transitions are displayed in the Transitions table, showing:
- Name and location
- Previous role
- New founder role
- Company
- Detection date
- Notification status

## Scheduled Jobs

The system runs two daily cron jobs (configurable in `.env`):

- **Ingestion Job** (default: 2 AM): Fetches updated profiles from external API
- **Detection Job** (default: 3 AM): Detects founder transitions and sends notifications

Jobs can also be triggered manually via the dashboard or API.

## API Endpoints

### Configuration
- `GET /api/config` - Get current configuration
- `POST /api/config/companies` - Set target companies
- `PATCH /api/config/states` - Set target states

### Profiles
- `GET /api/profiles` - List tracked profiles (paginated)
- `POST /api/profiles/ingest` - Trigger manual ingestion

### Transitions
- `GET /api/transitions` - List founder events (paginated)

### Jobs
- `POST /api/jobs/run-detection` - Manually trigger detection

### Health
- `GET /api/health` - Health check

All endpoints require HTTP Basic Authentication.

## Database Schema

- **profiles**: Core profile information
- **education**: Educational background (for experience calculation)
- **work_history**: Historical employment snapshots
- **founder_events**: Detected founder transitions
- **tracking_metadata**: System configuration and timestamps

## Migration to Supabase/PostgreSQL

The system is designed for easy migration to PostgreSQL:

1. Update `DATABASE_URL` in `.env`:
```env
DATABASE_URL=postgresql://user:password@host:port/database
```

2. Run migrations:
```bash
alembic upgrade head
```

No code changes required - SQLAlchemy handles dialect differences.

## Extensibility

### Adding New Data Providers

1. Implement `PeopleDataProvider` interface in `app/services/ingestion/`
2. Add provider to factory in `app/services/ingestion/factory.py`
3. Update `PEOPLE_DATA_PROVIDER` setting

### Adding New Notification Providers

1. Implement `NotificationProvider` interface in `app/services/notifications/`
2. Add provider to factory in `app/services/notifications/factory.py`
3. Update `NOTIFICATION_PROVIDER` setting

## Security Notes

- Change default Basic Auth credentials in production
- Store API keys securely (use environment variables)
- Consider implementing proper authentication for production use
- Review CORS settings for production deployment

## License

Internal use only.

