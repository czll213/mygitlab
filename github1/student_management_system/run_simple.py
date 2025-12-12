from app import create_app
import os

# Create Flask application
app = create_app('development')

if __name__ == '__main__':
    print("=" * 60)
    print("Student Management System")
    print("=" * 60)
    print("Starting server at http://localhost:5000")
    print("Default admin login: admin / admin123")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)