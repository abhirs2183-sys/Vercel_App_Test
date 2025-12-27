# yDatafix - SQL Datafix Package Maker

## Overview

yDatafix is a professional web-based SQL datafix package maker designed for MS SQL Server and Yardi systems. The application processes `.pkg` files through a drag-and-drop interface, automatically generating DataFixHistory backup statements and properly formatted SQL packages. It transforms raw SQL queries into production-ready datafix packages with proper metadata, backup tables, and audit trail capabilities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Technology Stack
- **Backend**: Python Flask web framework
- **Database**: PostgreSQL (Neon cloud database) with SQLAlchemy ORM
- **Frontend**: Vanilla HTML/CSS/JavaScript with responsive design
- **Templating**: Jinja2 templates

### Application Structure

The application follows a modular Flask architecture:

| Component | Purpose |
|-----------|---------|
| `app.py` | Flask app initialization, database config, model definitions |
| `main.py` | Application entry point for gunicorn |
| `routes.py` | API endpoints for file upload and feedback |
| `sql_processor.py` | Core SQL query processing and transformation logic |
| `case_processor.py` | CASE statement edge case handling |
| `templates/` | Jinja2 HTML templates |
| `static/` | CSS, JavaScript, and image assets |

### Core Processing Logic

The SQL processor handles three main query types:
1. **UPDATE queries** - Generates DataFixHistory INSERT statements per column
2. **DELETE queries** - Creates backup tables with naming convention `tablename_caseid`
3. **EXEC queries** - Preserved with appropriate formatting

Key processing rules:
- Foreign key column uses `hmyperson` for tenant tables, `hmy` for all others
- WHERE clauses are preserved exactly without merging
- SQL expressions and subqueries remain unchanged

### Frontend Architecture

Single-page application with:
- Dark/light theme toggle with localStorage persistence
- Drag-and-drop file upload interface
- Real-time processing feedback
- Responsive design following specific brand guidelines

### Data Flow

1. User uploads `.pkg` file via drag-and-drop
2. Backend parses metadata (created_by, case_id, client info, database credentials)
3. SQL queries are extracted and processed
4. DataFixHistory statements and backup queries are generated
5. Formatted package is returned for download
6. User activity is logged to `User_Logs.txt`

## External Dependencies

### Database
- **Neon PostgreSQL**: Cloud-hosted PostgreSQL database for storing feedback submissions
- Connection uses SSL with pooled connections

### Python Packages
- `Flask` - Web framework
- `Flask-SQLAlchemy` - Database ORM
- `pytz` - Timezone handling (IST for timestamps)
- `gunicorn` - Production WSGI server

### Frontend Libraries (CDN)
- Google Fonts (Inter)
- Font Awesome 6.4.0 (icons)

### File Storage
- `User_Logs.txt` - Activity logging fallback
- `feedback.txt` - Feedback storage fallback
- `logs/usage.txt` - Usage tracking