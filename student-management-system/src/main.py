import os
import sys
from typing import Optional
from .database import StudentDatabase
from .student import Student
from .validator import StudentValidator

class StudentManagementSystem:
    def __init__(self):
        self.db = StudentDatabase()
        self.validator = StudentValidator()

    def display_menu(self):
        print("\n" + "="*50)
        print("STUDENT INFORMATION MANAGEMENT SYSTEM")
        print("="*50)
        print("1. Add Student")
        print("2. View All Students")
        print("3. Search Student")
        print("4. Update Student")
        print("5. Delete Student")
        print("6. Filter by Grade")
        print("7. View Statistics")
        print("8. Exit")
        print("="*50)

    def get_input(self, prompt: str, required: bool = True) -> str:
        while True:
            value = input(prompt).strip()
            if value or not required:
                return value
            print("This field is required. Please enter a value.")

    def add_student(self):
        print("\n--- Add New Student ---")

        while True:
            student_id = self.get_input("Enter Student ID: ")
            is_valid, error_msg = self.validator.validate_student_id(student_id)
            if is_valid and not self.db.get_student_by_id(student_id):
                break
            elif not is_valid:
                print(f"Error: {error_msg}")
            else:
                print("Error: Student ID already exists!")

        while True:
            name = self.get_input("Enter Full Name: ")
            is_valid, error_msg = self.validator.validate_name(name)
            if is_valid:
                break
            print(f"Error: {error_msg}")

        while True:
            age_str = self.get_input("Enter Age: ")
            is_valid, error_msg, age = self.validator.validate_age(age_str)
            if is_valid:
                break
            print(f"Error: {error_msg}")

        while True:
            gender = self.get_input("Enter Gender (male/female/other): ").lower()
            is_valid, error_msg = self.validator.validate_gender(gender)
            if is_valid:
                break
            print(f"Error: {error_msg}")

        while True:
            grade = self.get_input("Enter Grade: ")
            is_valid, error_msg = self.validator.validate_grade(grade)
            if is_valid:
                break
            print(f"Error: {error_msg}")

        while True:
            phone = self.get_input("Enter Phone Number: ")
            is_valid, error_msg = self.validator.validate_phone(phone)
            if is_valid:
                break
            print(f"Error: {error_msg}")

        while True:
            email = self.get_input("Enter Email Address: ")
            is_valid, error_msg = self.validator.validate_email(email)
            if is_valid:
                break
            print(f"Error: {error_msg}")

        address = self.get_input("Enter Address (optional): ", required=False)

        student = Student(student_id, name, age, gender, grade, phone, email, address)
        if self.db.add_student(student):
            print(f"\n✓ Student '{name}' added successfully!")
        else:
            print(f"\n✗ Failed to add student '{name}'")

    def view_all_students(self):
        print("\n--- All Students ---")
        students = self.db.get_all_students()

        if not students:
            print("No students found in the database.")
            return

        print(f"\nTotal Students: {len(students)}")
        print("-" * 80)
        print(f"{'ID':<10} {'Name':<20} {'Age':<5} {'Gender':<8} {'Grade':<10} {'Phone':<15} {'Email':<25}")
        print("-" * 80)

        for student in students:
            print(f"{student.student_id:<10} {student.name:<20} {student.age:<5} "
                  f"{student.gender:<8} {student.grade:<10} {student.phone:<15} "
                  f"{student.email:<25}")

    def search_student(self):
        print("\n--- Search Student ---")
        keyword = self.get_input("Enter search keyword (name, ID, grade, or email): ")

        if not keyword:
            print("Please enter a search keyword.")
            return

        results = self.db.search_students(keyword)

        if not results:
            print(f"No students found matching '{keyword}'.")
            return

        print(f"\nFound {len(results)} student(s) matching '{keyword}':")
        print("-" * 80)
        for student in results:
            print(f"ID: {student.student_id} | Name: {student.name} | "
                  f"Age: {student.age} | Gender: {student.gender} | "
                  f"Grade: {student.grade} | Phone: {student.phone} | "
                  f"Email: {student.email}")

    def update_student(self):
        print("\n--- Update Student ---")
        student_id = self.get_input("Enter Student ID to update: ")

        student = self.db.get_student_by_id(student_id)
        if not student:
            print(f"No student found with ID '{student_id}'.")
            return

        print(f"\nCurrent Student Information:")
        print(f"Name: {student.name}")
        print(f"Age: {student.age}")
        print(f"Gender: {student.gender}")
        print(f"Grade: {student.grade}")
        print(f"Phone: {student.phone}")
        print(f"Email: {student.email}")
        print(f"Address: {student.address}")

        print("\nEnter new values (leave blank to keep current value):")

        updates = {}

        name = self.get_input(f"Name [{student.name}]: ", required=False)
        if name:
            is_valid, error_msg = self.validator.validate_name(name)
            if is_valid:
                updates['name'] = name
            else:
                print(f"Error: {error_msg}")
                return

        age_str = self.get_input(f"Age [{student.age}]: ", required=False)
        if age_str:
            is_valid, error_msg, age = self.validator.validate_age(age_str)
            if is_valid:
                updates['age'] = age
            else:
                print(f"Error: {error_msg}")
                return

        gender = self.get_input(f"Gender [{student.gender}]: ", required=False)
        if gender:
            is_valid, error_msg = self.validator.validate_gender(gender)
            if is_valid:
                updates['gender'] = gender
            else:
                print(f"Error: {error_msg}")
                return

        grade = self.get_input(f"Grade [{student.grade}]: ", required=False)
        if grade:
            is_valid, error_msg = self.validator.validate_grade(grade)
            if is_valid:
                updates['grade'] = grade
            else:
                print(f"Error: {error_msg}")
                return

        phone = self.get_input(f"Phone [{student.phone}]: ", required=False)
        if phone:
            is_valid, error_msg = self.validator.validate_phone(phone)
            if is_valid:
                updates['phone'] = phone
            else:
                print(f"Error: {error_msg}")
                return

        email = self.get_input(f"Email [{student.email}]: ", required=False)
        if email:
            is_valid, error_msg = self.validator.validate_email(email)
            if is_valid:
                updates['email'] = email
            else:
                print(f"Error: {error_msg}")
                return

        address = self.get_input(f"Address [{student.address}]: ", required=False)
        if address:
            updates['address'] = address

        if updates:
            if self.db.update_student(student_id, **updates):
                print(f"\n✓ Student '{student.name}' updated successfully!")
            else:
                print(f"\n✗ Failed to update student")
        else:
            print("\nNo changes made.")

    def delete_student(self):
        print("\n--- Delete Student ---")
        student_id = self.get_input("Enter Student ID to delete: ")

        student = self.db.get_student_by_id(student_id)
        if not student:
            print(f"No student found with ID '{student_id}'.")
            return

        print(f"\nStudent to delete: {student.name} (ID: {student.student_id})")
        confirm = input("Are you sure you want to delete this student? (yes/no): ").lower()

        if confirm in ['yes', 'y']:
            if self.db.delete_student(student_id):
                print(f"\n✓ Student '{student.name}' deleted successfully!")
            else:
                print(f"\n✗ Failed to delete student")
        else:
            print("Delete operation cancelled.")

    def filter_by_grade(self):
        print("\n--- Filter by Grade ---")
        grade = self.get_input("Enter grade to filter: ")

        if not grade:
            print("Please enter a grade.")
            return

        students = self.db.filter_by_grade(grade)

        if not students:
            print(f"No students found in grade '{grade}'.")
            return

        print(f"\nStudents in Grade '{grade}':")
        print("-" * 80)
        for student in students:
            print(f"ID: {student.student_id} | Name: {student.name} | "
                  f"Age: {student.age} | Gender: {student.gender} | "
                  f"Phone: {student.phone} | Email: {student.email}")

    def view_statistics(self):
        print("\n--- System Statistics ---")
        total_students = self.db.get_student_count()
        print(f"Total Students: {total_students}")

        if total_students == 0:
            return

        students = self.db.get_all_students()

        grade_counts = {}
        gender_counts = {}
        age_groups = {'5-12': 0, '13-18': 0, '19-25': 0, '26+': 0}

        for student in students:
            grade_counts[student.grade] = grade_counts.get(student.grade, 0) + 1
            gender_counts[student.gender] = gender_counts.get(student.gender, 0) + 1

            if student.age <= 12:
                age_groups['5-12'] += 1
            elif student.age <= 18:
                age_groups['13-18'] += 1
            elif student.age <= 25:
                age_groups['19-25'] += 1
            else:
                age_groups['26+'] += 1

        print(f"\nGrade Distribution:")
        for grade, count in grade_counts.items():
            print(f"  {grade}: {count} students")

        print(f"\nGender Distribution:")
        for gender, count in gender_counts.items():
            print(f"  {gender}: {count} students")

        print(f"\nAge Group Distribution:")
        for group, count in age_groups.items():
            print(f"  {group}: {count} students")

    def run(self):
        print("Welcome to Student Information Management System!")

        while True:
            self.display_menu()
            choice = input("Enter your choice (1-8): ")

            if choice == '1':
                self.add_student()
            elif choice == '2':
                self.view_all_students()
            elif choice == '3':
                self.search_student()
            elif choice == '4':
                self.update_student()
            elif choice == '5':
                self.delete_student()
            elif choice == '6':
                self.filter_by_grade()
            elif choice == '7':
                self.view_statistics()
            elif choice == '8':
                print("\nThank you for using Student Information Management System!")
                print("Goodbye!")
                break
            else:
                print("\nInvalid choice! Please enter a number between 1-8.")

            input("\nPress Enter to continue...")

def main():
    sms = StudentManagementSystem()
    sms.run()

if __name__ == "__main__":
    main()