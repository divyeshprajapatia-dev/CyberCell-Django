# CyberCell - Cybercrime Reporting System

## Overview

CyberCell is a comprehensive web application built with Django that enables citizens to report cybercrimes, track case progress, and helps law enforcement agencies manage and investigate reported incidents. The system provides a user-friendly interface for reporting various types of cybercrimes and offers administrative tools for case management.

## Features

### For Citizens

- **User Registration & Authentication**: Create an account and securely log in
- **Crime Reporting**: Submit detailed cybercrime reports with evidence uploads
- **Case Tracking**: Monitor the status and progress of submitted reports
- **Profile Management**: Update personal information and view report history

### For Law Enforcement (Police/Admin)

- **Administrative Dashboard**: Overview of crime statistics and recent reports
- **Case Management**: Review, update status, and add notes to crime reports
- **User Management**: Assign user roles and manage account permissions
- **Statistical Analysis**: View crime trends by category, location, and time period

## Technology Stack

- **Backend**: Django (Python web framework)
- **Database**: SQLite (default), can be configured for PostgreSQL/MySQL
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Authentication**: Django's built-in authentication system
- **File Storage**: Django's file storage system for evidence uploads

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/cybercell.git
   cd cybercell
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```
   python manage.py migrate
   ```

5. Create a superuser (admin account):
   ```
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```
   python manage.py runserver
   ```

7. Access the application at http://127.0.0.1:8000/

## Project Structure

```
cybercell/
├── crime_report/           # Main application
│   ├── migrations/         # Database migrations
│   ├── static/             # Static files (CSS, JS, images)
│   ├── templates/          # HTML templates
│   ├── admin.py            # Admin panel configuration
│   ├── forms.py            # Form definitions
│   ├── models.py           # Database models
│   ├── urls.py             # URL routing
│   └── views.py            # View functions
├── cybercell/              # Project settings
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL routing
│   └── wsgi.py             # WSGI configuration
├── static/                 # Global static files
│   ├── css/                # CSS files
│   ├── js/                 # JavaScript files
│   └── img/                # Image files
├── templates/              # Global templates
├── manage.py               # Django management script
└── requirements.txt        # Project dependencies
```

## User Types

1. **Citizen**: Regular users who can report crimes and track their cases
2. **Police**: Law enforcement officers who can investigate and update case status
3. **Admin**: System administrators with full access to all features

## Crime Report Workflow

1. User submits a crime report with details and evidence
2. Report is assigned a unique ID and set to "Pending" status
3. Police/Admin reviews the report and updates status to "Investigating"
4. Investigation proceeds with status updates and notes
5. Case is eventually marked as "Resolved", "Closed", or "Rejected"

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

For any inquiries, please contact [divyeshprajapti.a@gmail.com]
