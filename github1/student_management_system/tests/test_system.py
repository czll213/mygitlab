import unittest
import requests
import json
import time
from datetime import datetime

class StudentManagementSystemTest(unittest.TestCase):
    """Functional tests for Student Management System"""

    BASE_URL = "http://localhost:5000"
    session = None

    @classmethod
    def setUpClass(cls):
        """Setup test session"""
        cls.session = requests.Session()

    def setUp(self):
        """Setup for each test"""
        pass

    def test_01_homepage_access(self):
        """Test that homepage is accessible"""
        print("\n[Test 01] Testing homepage access...")
        response = self.session.get(f"{self.BASE_URL}/")

        # Should redirect to login page when not authenticated
        self.assertEqual(response.status_code, 302)
        print("✓ Homepage redirects to login when not authenticated")

    def test_02_user_registration(self):
        """Test user registration functionality"""
        print("\n[Test 02] Testing user registration...")

        test_user = {
            'username': f'teststudent_{int(time.time())}',
            'email': f'test_{int(time.time())}@example.com',
            'password': 'test123456',
            'confirm_password': 'test123456',
            'full_name': 'Test Student',
            'phone': '1234567890',
            'role': 'student'
        }

        response = self.session.post(
            f"{self.BASE_URL}/auth/register",
            data=test_user,
            allow_redirects=False
        )

        # Check if registration was successful
        self.assertIn(response.status_code, [200, 302])
        print("✓ User registration form processed")

    def test_03_user_login(self):
        """Test user login functionality"""
        print("\n[Test 03] Testing user login...")

        # Try to login with default admin
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }

        response = self.session.post(
            f"{self.BASE_URL}/auth/login",
            data=login_data,
            allow_redirects=False
        )

        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)
        print("✓ Admin login successful")

    def test_04_admin_dashboard_access(self):
        """Test admin dashboard access"""
        print("\n[Test 04] Testing admin dashboard access...")

        response = self.session.get(f"{self.BASE_URL}/admin/dashboard")
        self.assertEqual(response.status_code, 200)

        # Check for dashboard elements
        self.assertIn(b"Admin Dashboard", response.content)
        print("✓ Admin dashboard accessible")

    def test_05_create_student(self):
        """Test student creation"""
        print("\n[Test 05] Testing student creation...")

        student_data = {
            'student_id': f'STU{int(time.time())}',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': f'john.doe{int(time.time())}@example.com',
            'phone': '9876543210',
            'major': 'Computer Science',
            'enrollment_year': '2024'
        }

        response = self.session.post(
            f"{self.BASE_URL}/admin/students/create",
            data=student_data,
            allow_redirects=False
        )

        # Should redirect after successful creation
        self.assertIn(response.status_code, [200, 302])
        print("✓ Student creation form processed")

    def test_06_create_course(self):
        """Test course creation"""
        print("\n[Test 06] Testing course creation...")

        course_data = {
            'course_code': f'CS{int(time.time())}',
            'course_name': 'Introduction to Testing',
            'description': 'A course about software testing',
            'credits': '3',
            'department': 'Computer Science',
            'instructor': 'Dr. Test'
        }

        response = self.session.post(
            f"{self.BASE_URL}/admin/courses/create",
            data=course_data,
            allow_redirects=False
        )

        # Should redirect after successful creation
        self.assertIn(response.status_code, [200, 302])
        print("✓ Course creation form processed")

    def test_07_view_users_list(self):
        """Test viewing users list"""
        print("\n[Test 07] Testing users list view...")

        response = self.session.get(f"{self.BASE_URL}/admin/users")
        self.assertEqual(response.status_code, 200)

        # Check for table elements
        self.assertIn(b"Users List", response.content)
        print("✓ Users list accessible")

    def test_08_api_endpoints(self):
        """Test API endpoints"""
        print("\n[Test 08] Testing API endpoints...")

        # Test students API
        response = self.session.get(f"{self.BASE_URL}/admin/api/students")
        self.assertEqual(response.status_code, 200)

        # Test courses API
        response = self.session.get(f"{self.BASE_URL}/admin/api/courses")
        self.assertEqual(response.status_code, 200)

        print("✓ API endpoints accessible")

    def test_09_logout(self):
        """Test logout functionality"""
        print("\n[Test 09] Testing logout...")

        response = self.session.get(f"{self.BASE_URL}/auth/logout", allow_redirects=False)
        self.assertEqual(response.status_code, 302)
        print("✓ Logout successful")

    def test_10_protected_routes(self):
        """Test that protected routes require authentication"""
        print("\n[Test 10] Testing protected routes...")

        # Create new session (not logged in)
        temp_session = requests.Session()

        protected_routes = [
            "/admin/dashboard",
            "/admin/users",
            "/admin/students",
            "/admin/courses",
            "/student/dashboard",
            "/student/courses"
        ]

        for route in protected_routes:
            response = temp_session.get(f"{self.BASE_URL}{route}")
            # Should redirect to login
            self.assertEqual(response.status_code, 302)

        print("✓ Protected routes properly require authentication")

    def test_11_search_functionality(self):
        """Test search functionality"""
        print("\n[Test 11] Testing search functionality...")

        # Test users search
        response = self.session.get(f"{self.BASE_URL}/admin/users?search=admin")
        self.assertEqual(response.status_code, 200)

        # Test students search
        response = self.session.get(f"{self.BASE_URL}/admin/students?search=test")
        self.assertEqual(response.status_code, 200)

        print("✓ Search functionality working")

    def test_12_pagination(self):
        """Test pagination functionality"""
        print("\n[Test 12] Testing pagination...")

        response = self.session.get(f"{self.BASE_URL}/admin/users?page=1")
        self.assertEqual(response.status_code, 200)

        response = self.session.get(f"{self.BASE_URL}/admin/students?page=1")
        self.assertEqual(response.status_code, 200)

        print("✓ Pagination functionality working")

def run_tests():
    """Run all tests and generate report"""
    print("=" * 60)
    print("Student Management System - Functional Tests")
    print("=" * 60)

    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(StudentManagementSystemTest)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Generate report
    print("\n" + "=" * 60)
    print("TEST REPORT")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")

    # Save report to file
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': result.testsRun,
        'failures': len(result.failures),
        'errors': len(result.errors),
        'success_rate': (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100,
        'tests_passed': result.testsRun - len(result.failures) - len(result.errors)
    }

    with open('test_report.json', 'w') as f:
        json.dump(report_data, f, indent=2)

    print(f"\n✓ Test report saved to test_report.json")

    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)