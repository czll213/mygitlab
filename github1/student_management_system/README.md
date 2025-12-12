# Student Management System

A comprehensive web application for managing student information, courses, and enrollments.

## Features

### User Management
- User registration and login
- Password encryption with bcrypt
- Session management
- Role-based access control (Admin/Student)

### Administrator Module
- Dashboard with system statistics
- User management (CRUD operations)
- Student management (CRUD operations)
- Course management (CRUD operations)
- Enrollment management
- Search and pagination

### Student Module
- Personal dashboard
- Profile management
- Course browsing and enrollment
- Enrollment history and grades
- Academic progress tracking

### Technical Features
- Flask web framework
- SQLAlchemy ORM
- Database design following 3NF
- Responsive Bootstrap UI
- RESTful API endpoints
- AJAX functionality
- Security best practices

## Database Design

### Tables (5 Main Tables)
1. **users** - User accounts and authentication
2. **administrators** - Administrator information
3. **students** - Student personal information
4. **courses** - Course catalog
5. **enrollments** - Student course enrollments

### ER Diagram
See [database_design.md](database_design.md) for detailed ER diagram and table structures.

## Installation

### Prerequisites
- Python 3.8+
- pip
- MySQL or SQLite (for production or development)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd student_management_system
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

4. Set environment variables (optional):
```bash
export FLASK_ENV=development
export SECRET_KEY=your-secret-key
export DATABASE_URL=sqlite:///student_management.db
```

5. Run the application:
```bash
python run.py
```

The application will be available at http://localhost:5000

## Default Admin Account
- **Username:** admin
- **Password:** admin123

## Testing

Run the functional tests:

```bash
python tests/test_system.py
```

This will test all major functionality and generate a report in `test_report.json`.

## Project Structure

```
student_management_system/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models/              # Database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── admin.py
│   │   ├── student.py
│   │   ├── course.py
│   │   └── enrollment.py
│   ├── views/               # Route handlers
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── admin.py
│   │   ├── student.py
│   │   └── main.py
│   ├── static/              # Static files
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/           # HTML templates
│       ├── auth/
│       ├── admin/
│       ├── student/
│       └── base.html
├── config/
│   └── config.py            # Configuration settings
├── tests/
│   └── test_system.py       # Functional tests
├── database_design.md       # Database documentation
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
└── README.md                # This file
```

## API Endpoints

### Admin Endpoints
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/api/students` - Get all students
- `GET /admin/api/courses` - Get all courses
- `GET /admin/api/enrollments` - Get all enrollments

### Student Endpoints
- `GET /student/dashboard` - Student dashboard
- `GET /student/api/courses/available` - Get available courses
- `GET /student/api/enrollments` - Get student enrollments

## Security Features

- Password hashing with bcrypt
- Session management with Flask-Login
- CSRF protection
- SQL injection prevention with SQLAlchemy ORM
- XSS protection with template escaping
- Input validation and sanitization

## Browser Support

- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests to ensure everything works
6. Submit a pull request

## License

This project is licensed under the MIT License.

## Contact

For support or questions, please contact the development team.

## Change Log

### Version 1.0.0
- Initial release
- Complete student management functionality
- Admin and student modules
- Responsive web interface
- RESTful API
- Comprehensive testing