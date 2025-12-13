from app import db
from datetime import datetime

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    birth_date = db.Column(db.Date)
    gender = db.Column(db.Enum('Male', 'Female', 'Other', name='gender'))
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    major = db.Column(db.String(100))
    enrollment_year = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    enrollments = db.relationship('Enrollment', backref='student', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def to_dict(self):
        # 翻译性别显示值
        gender_map = {
            'Male': '男',
            'Female': '女',
            'Other': '其他'
        }

        return {
            'id': self.id,
            'student_id': self.student_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.full_name,
            'birth_date': self.birth_date.isoformat() if self.birth_date else None,
            'gender': gender_map.get(self.gender, self.gender) if self.gender else None,
            'gender_raw': self.gender,  # 保留原始英文值
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'major': self.major,
            'enrollment_year': self.enrollment_year,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Student {self.student_id}>'