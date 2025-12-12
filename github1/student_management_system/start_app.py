import os
import sys
import subprocess
import webbrowser
from threading import Timer
import time

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Requirements installed successfully")
    except subprocess.CalledProcessError:
        print("✗ Failed to install requirements")
        return False
    return True

def create_initial_data():
    """Create initial database with default admin"""
    from app import create_app
    from app.models.user import User
    from app.models.admin import Administrator
    from app import db

    app = create_app('development')
    with app.app_context():
        # Create tables
        db.create_all()

        # Check if admin exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            # Create default admin
            admin_user = User(
                username='admin',
                email='admin@example.com',
                full_name='System Administrator',
                role='admin',
                is_active=True
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()

            # Create admin record
            admin = Administrator(
                user_id=admin_user.id,
                admin_code='ADMIN001',
                department='System Administration'
            )
            db.session.add(admin)
            db.session.commit()
            print("✓ Default admin account created (admin/admin123)")
        else:
            print("✓ Database already initialized")

def open_browser():
    """Open browser after a delay"""
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

def main():
    print("=" * 60)
    print("Student Management System - Starting Application")
    print("=" * 60)

    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        sys.exit(1)

    print(f"✓ Python {sys.version.split()[0]} detected")

    # Install requirements
    if not install_requirements():
        sys.exit(1)

    # Initialize database
    print("\nInitializing database...")
    try:
        create_initial_data()
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Application is starting...")
    print("URL: http://localhost:5000")
    print("Default Admin Login: admin / admin123")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)

    # Open browser after a delay
    Timer(3, open_browser).start()

    # Start the Flask application
    try:
        from run import app
        app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print("\n✓ Application stopped by user")
    except Exception as e:
        print(f"\n✗ Failed to start application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()