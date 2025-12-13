# Import all models to ensure they are registered with SQLAlchemy
from .user import User
from .admin import Administrator
from .student import Student
from .course import Course
from .enrollment import Enrollment

__all__ = ['User', 'Administrator', 'Student', 'Course', 'Enrollment']