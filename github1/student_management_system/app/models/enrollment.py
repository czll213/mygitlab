from app import db
from datetime import datetime, date

class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrollment_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.Enum('enrolled', 'completed', 'dropped', 'withdrawn', name='enrollment_status'),
                       default='enrolled')
    grade = db.Column(db.Numeric(5, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Unique constraint to prevent duplicate enrollments
    __table_args__ = (db.UniqueConstraint('student_id', 'course_id', name='unique_enrollment'),)

    def to_dict(self):
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'enrollment_date': self.enrollment_date.isoformat() if self.enrollment_date else None,
            'status': self.status,
            'grade': float(self.grade) if self.grade else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'student': self.student.to_dict() if self.student else None,
            'course': self.course.to_dict() if self.course else None
        }

    def __repr__(self):
        return f'<Enrollment {self.student_id}-{self.course_id}>'