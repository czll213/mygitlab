import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class Student:
    def __init__(self, student_id: str, name: str, age: int, gender: str,
                 grade: str, phone: str, email: str, address: str = ""):
        self.student_id = student_id
        self.name = name
        self.age = age
        self.gender = gender
        self.grade = grade
        self.phone = phone
        self.email = email
        self.address = address
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_at = self.created_at

    def to_dict(self) -> Dict:
        return {
            "student_id": self.student_id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "grade": self.grade,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Student':
        student = cls(
            student_id=data["student_id"],
            name=data["name"],
            age=data["age"],
            gender=data["gender"],
            grade=data["grade"],
            phone=data["phone"],
            email=data["email"],
            address=data.get("address", "")
        )
        student.created_at = data.get("created_at", student.created_at)
        student.updated_at = data.get("updated_at", student.updated_at)
        return student

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key) and key not in ["student_id", "created_at"]:
                setattr(self, key, value)
        self.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self):
        return f"ID: {self.student_id} | Name: {self.name} | Age: {self.age} | Grade: {self.grade} | Phone: {self.phone}"