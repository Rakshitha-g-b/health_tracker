# Health Tracker Web Application

A Django-based web application that helps users monitor their mental and physical health by tracking daily mood, health symptoms, and habits.

## Features

- Daily mood tracking
- Health symptoms logging
- Habit tracking (sleep, water intake, etc.)
- AI-powered mood analysis and suggestions
- User authentication and personal dashboard

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up MySQL database:
- Create a new MySQL database
- Update the database settings in `healthtracker/settings.py`

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

## Project Structure

- `healthtracker/` - Main project configuration
- `tracker/` - Core application
  - `models/` - Database models
  - `views/` - View functions
  - `templates/` - HTML templates
  - `static/` - CSS, JavaScript, and other static files
  - `ai/` - AI analysis components

## Environment Variables

Create a `.env` file in the project root with:
```
DEBUG=True
SECRET_KEY=your-secret-key
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306
``` 