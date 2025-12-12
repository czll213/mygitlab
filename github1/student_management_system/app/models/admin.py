from app import db
from datetime import datetime

class Administrator(db.Model):
    __tablename__ = 'administrators'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    admin_code = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100))
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'admin_code': self.admin_code,
            'department': self.department,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'user': self.user.to_dict() if self.user else None
        }

    def __repr__(self):
        return f'<Administrator {self.admin_code}>'