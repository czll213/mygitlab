import json
import os
from typing import List, Optional
from .student import Student

class StudentDatabase:
    def __init__(self, file_path: str = "data/students.json"):
        self.file_path = file_path
        self.students: List[Student] = []
        self.load_data()

    def load_data(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.students = [Student.from_dict(student_data) for student_data in data]
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error loading data: {e}")
                self.students = []
        else:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            self.students = []

    def save_data(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump([student.to_dict() for student in self.students], f, indent=2, ensure_ascii=False)

    def add_student(self, student: Student) -> bool:
        if self.get_student_by_id(student.student_id):
            return False
        self.students.append(student)
        self.save_data()
        return True

    def get_student_by_id(self, student_id: str) -> Optional[Student]:
        for student in self.students:
            if student.student_id == student_id:
                return student
        return None

    def update_student(self, student_id: str, **kwargs) -> bool:
        student = self.get_student_by_id(student_id)
        if student:
            student.update(**kwargs)
            self.save_data()
            return True
        return False

    def delete_student(self, student_id: str) -> bool:
        student = self.get_student_by_id(student_id)
        if student:
            self.students.remove(student)
            self.save_data()
            return True
        return False

    def get_all_students(self) -> List[Student]:
        return self.students

    def search_students(self, keyword: str) -> List[Student]:
        keyword = keyword.lower()
        results = []
        for student in self.students:
            if (keyword in student.name.lower() or
                keyword in student.student_id.lower() or
                keyword in student.grade.lower() or
                keyword in student.email.lower()):
                results.append(student)
        return results

    def filter_by_grade(self, grade: str) -> List[Student]:
        return [student for student in self.students if student.grade.lower() == grade.lower()]

    def get_student_count(self) -> int:
        return len(self.students)