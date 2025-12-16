import re
from typing import Tuple

class StudentValidator:
    @staticmethod
    def validate_student_id(student_id: str) -> Tuple[bool, str]:
        if not student_id:
            return False, "Student ID is required"
        if len(student_id) < 3:
            return False, "Student ID must be at least 3 characters"
        return True, ""

    @staticmethod
    def validate_name(name: str) -> Tuple[bool, str]:
        if not name:
            return False, "Name is required"
        if len(name) < 2:
            return False, "Name must be at least 2 characters"
        if not name.replace(" ", "").isalpha():
            return False, "Name can only contain letters and spaces"
        return True, ""

    @staticmethod
    def validate_age(age_str: str) -> Tuple[bool, str, int]:
        if not age_str:
            return False, "Age is required", 0
        try:
            age = int(age_str)
            if age < 5 or age > 100:
                return False, "Age must be between 5 and 100", 0
            return True, "", age
        except ValueError:
            return False, "Age must be a valid number", 0

    @staticmethod
    def validate_gender(gender: str) -> Tuple[bool, str]:
        if not gender:
            return False, "Gender is required"
        gender = gender.lower()
        if gender not in ['male', 'female', 'other']:
            return False, "Gender must be 'male', 'female', or 'other'"
        return True, ""

    @staticmethod
    def validate_grade(grade: str) -> Tuple[bool, str]:
        if not grade:
            return False, "Grade is required"
        valid_grades = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
                       'freshman', 'sophomore', 'junior', 'senior', 'graduate']
        if grade.lower() not in valid_grades:
            return False, f"Grade must be one of: {', '.join(valid_grades)}"
        return True, ""

    @staticmethod
    def validate_phone(phone: str) -> Tuple[bool, str]:
        if not phone:
            return False, "Phone number is required"
        phone_pattern = r'^[\d\s\-\+\(\)]{10,20}$'
        if not re.match(phone_pattern, phone):
            return False, "Please enter a valid phone number"
        return True, ""

    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        if not email:
            return False, "Email is required"
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Please enter a valid email address"
        return True, ""