from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.admin import Administrator
from app.models.student import Student
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.views.auth import admin_required
from functools import wraps
import re

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_students': Student.query.count(),
        'total_courses': Course.query.count(),
        'total_enrollments': Enrollment.query.count(),
        'active_users': User.query.filter_by(is_active=True).count()
    }

    recent_enrollments = Enrollment.query.order_by(Enrollment.created_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html', stats=stats, recent_enrollments=recent_enrollments)

# User Management
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')

    query = User.query
    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.email.contains(search)) |
            (User.full_name.contains(search))
        )

    users = query.paginate(
        page=page,
        per_page=20,
        error_out=False
    )

    return render_template('admin/users/index.html', users=users, search=search)

@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('admin/users/view.html', user=user)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form

        # Validation
        errors = {}

        if not data.get('username') or len(data['username']) < 4:
            errors['username'] = '用户名必须至少4个字符'

        if not data.get('email') or not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            errors['email'] = '请输入有效的邮箱地址'

        if not data.get('password') or len(data['password']) < 6:
            errors['password'] = '密码必须至少6个字符'

        if not data.get('full_name'):
            errors['full_name'] = '请输入全名'

        # Check if username or email already exists
        if User.query.filter_by(username=data.get('username')).first():
            errors['username'] = '用户名已存在'

        if User.query.filter_by(email=data.get('email')).first():
            errors['email'] = '邮箱已存在'

        if errors and request.is_json:
            return jsonify({'success': False, 'errors': errors}), 400

        if errors:
            for field, error in errors.items():
                flash(error, 'error')
            return render_template('admin/users/create.html')

        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            full_name=data['full_name'],
            phone=data.get('phone', ''),
            role=data.get('role', 'student'),
            is_active=data.get('is_active', 'on') == 'on'
        )
        user.set_password(data['password'])

        try:
            db.session.add(user)
            db.session.commit()

            # If creating an admin, create administrator record
            if user.is_admin():
                admin = Administrator(
                    user_id=user.id,
                    admin_code=data.get('admin_code', f'ADMIN{user.id:03d}'),
                    department=data.get('department', '')
                )
                db.session.add(admin)
                db.session.commit()

            if request.is_json:
                return jsonify({'success': True, 'message': '用户创建成功', 'user': user.to_dict()})

            flash('用户创建成功', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'success': False, 'message': '用户创建失败'}), 500
            flash('用户创建失败', 'error')

    return render_template('admin/users/create.html')

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form

        # Validation
        errors = {}

        if not data.get('username') or len(data['username']) < 4:
            errors['username'] = '用户名必须至少4个字符'

        if not data.get('email') or not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            errors['email'] = '请输入有效的邮箱地址'

        if not data.get('full_name'):
            errors['full_name'] = '请输入全名'

        # Check if username or email already exists (excluding current user)
        if User.query.filter(User.username == data.get('username'), User.id != user.id).first():
            errors['username'] = '用户名已存在'

        if User.query.filter(User.email == data.get('email'), User.id != user.id).first():
            errors['email'] = '邮箱已存在'

        if errors and request.is_json:
            return jsonify({'success': False, 'errors': errors}), 400

        if errors:
            for field, error in errors.items():
                flash(error, 'error')
            return render_template('admin/users/edit.html', user=user)

        # Update user
        user.username = data['username']
        user.email = data['email']
        user.full_name = data['full_name']
        user.phone = data.get('phone', '')
        user.role = data.get('role', 'student')
        user.is_active = data.get('is_active', 'off') == 'on'

        if data.get('password'):
            user.set_password(data['password'])

        try:
            db.session.commit()

            # Handle administrator record
            if user.is_admin() and not user.administrator:
                admin = Administrator(
                    user_id=user.id,
                    admin_code=data.get('admin_code', f'ADMIN{user.id:03d}'),
                    department=data.get('department', '')
                )
                db.session.add(admin)
            elif not user.is_admin() and user.administrator:
                db.session.delete(user.administrator)

            db.session.commit()

            if request.is_json:
                return jsonify({'success': True, 'message': '用户更新成功', 'user': user.to_dict()})

            flash('用户更新成功', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'success': False, 'message': '用户更新失败'}), 500
            flash('用户更新失败', 'error')

    return render_template('admin/users/edit.html', user=user)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        if request.is_json:
            return jsonify({'success': False, 'message': '不能删除自己的账户'}), 400
        flash('不能删除自己的账户', 'error')
        return redirect(url_for('admin.users'))

    try:
        db.session.delete(user)
        db.session.commit()

        if request.is_json:
            return jsonify({'success': True, 'message': '用户删除成功'})

        flash('用户删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'message': '用户删除失败'}), 500
        flash('用户删除失败', 'error')

    return redirect(url_for('admin.users'))

# Student Management
@admin_bp.route('/students')
@login_required
@admin_required
def students():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')

    query = Student.query
    if search:
        query = query.filter(
            (Student.student_id.contains(search)) |
            (Student.first_name.contains(search)) |
            (Student.last_name.contains(search)) |
            (Student.email.contains(search))
        )

    students = query.paginate(
        page=page,
        per_page=20,
        error_out=False
    )

    return render_template('admin/students/index.html', students=students, search=search)

@admin_bp.route('/students/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_student():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form

        # Validation
        errors = {}

        if not data.get('student_id'):
            errors['student_id'] = '学号是必填项'

        if not data.get('first_name'):
            errors['first_name'] = '名字是必填项'

        if not data.get('last_name'):
            errors['last_name'] = '姓氏是必填项'

        if not data.get('email') or not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            errors['email'] = '请输入有效的邮箱地址'

        # Check if student ID or email already exists
        if Student.query.filter_by(student_id=data.get('student_id')).first():
            errors['student_id'] = '学号已存在'

        if Student.query.filter_by(email=data.get('email')).first():
            errors['email'] = '邮箱已存在'

        if errors and request.is_json:
            return jsonify({'success': False, 'errors': errors}), 400

        if errors:
            for field, error in errors.items():
                flash(error, 'error')
            return render_template('admin/students/create.html')

        # Create new student
        student = Student(
            student_id=data['student_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            birth_date=data.get('birth_date'),
            gender=data.get('gender'),
            email=data['email'],
            phone=data.get('phone'),
            address=data.get('address'),
            major=data.get('major'),
            enrollment_year=data.get('enrollment_year')
        )

        try:
            db.session.add(student)
            db.session.commit()

            if request.is_json:
                return jsonify({'success': True, 'message': '学生创建成功', 'student': student.to_dict()})

            flash('学生创建成功', 'success')
            return redirect(url_for('admin.students'))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'success': False, 'message': '学生创建失败'}), 500
            flash('学生创建失败', 'error')

    return render_template('admin/students/create.html')

@admin_bp.route('/students/<int:student_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form

        # Validation
        errors = {}

        if not data.get('first_name'):
            errors['first_name'] = '名字是必填项'

        if not data.get('last_name'):
            errors['last_name'] = '姓氏是必填项'

        if not data.get('email') or not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            errors['email'] = '请输入有效的邮箱地址'

        # Check if email already exists (excluding current student)
        if Student.query.filter(Student.email == data.get('email'), Student.id != student_id).first():
            errors['email'] = '邮箱已存在'

        if errors and request.is_json:
            return jsonify({'success': False, 'errors': errors}), 400

        if errors:
            for field, error in errors.items():
                flash(error, 'error')
            return render_template('admin/students/edit.html', student=student)

        # Update student
        student.first_name = data['first_name']
        student.last_name = data['last_name']
        student.birth_date = data.get('birth_date')
        student.gender = data.get('gender')
        student.email = data['email']
        student.phone = data.get('phone')
        student.address = data.get('address')
        student.major = data.get('major')
        student.enrollment_year = data.get('enrollment_year')

        try:
            db.session.commit()

            if request.is_json:
                return jsonify({'success': True, 'message': '学生更新成功', 'student': student.to_dict()})

            flash('学生更新成功', 'success')
            return redirect(url_for('admin.students'))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'success': False, 'message': '学生更新失败'}), 500
            flash('学生更新失败', 'error')

    return render_template('admin/students/edit.html', student=student)

@admin_bp.route('/students/<int:student_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)

    try:
        db.session.delete(student)
        db.session.commit()

        if request.is_json:
            return jsonify({'success': True, 'message': '学生删除成功'})

        flash('学生删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'message': '学生删除失败'}), 500
        flash('学生删除失败', 'error')

    return redirect(url_for('admin.students'))

# Course Management
@admin_bp.route('/courses')
@login_required
@admin_required
def courses():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')

    query = Course.query
    if search:
        query = query.filter(
            (Course.course_code.contains(search)) |
            (Course.course_name.contains(search)) |
            (Course.instructor.contains(search))
        )

    courses = query.paginate(
        page=page,
        per_page=20,
        error_out=False
    )

    return render_template('admin/courses/index.html', courses=courses, search=search)

@admin_bp.route('/courses/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_course():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form

        # Validation
        errors = {}

        if not data.get('course_code'):
            errors['course_code'] = '课程代码是必填项'

        if not data.get('course_name'):
            errors['course_name'] = '课程名称是必填项'

        if not data.get('credits') or int(data.get('credits', 0)) <= 0:
            errors['credits'] = '学分必须大于0'

        # Check if course code already exists
        if Course.query.filter_by(course_code=data.get('course_code')).first():
            errors['course_code'] = '课程代码已存在'

        if errors and request.is_json:
            return jsonify({'success': False, 'errors': errors}), 400

        if errors:
            for field, error in errors.items():
                flash(error, 'error')
            return render_template('admin/courses/create.html')

        # Create new course
        course = Course(
            course_code=data['course_code'],
            course_name=data['course_name'],
            description=data.get('description'),
            credits=int(data.get('credits', 3)),
            department=data.get('department'),
            instructor=data.get('instructor')
        )

        try:
            db.session.add(course)
            db.session.commit()

            if request.is_json:
                return jsonify({'success': True, 'message': '课程创建成功', 'course': course.to_dict()})

            flash('课程创建成功', 'success')
            return redirect(url_for('admin.courses'))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'success': False, 'message': '课程创建失败'}), 500
            flash('课程创建失败', 'error')

    return render_template('admin/courses/create.html')

@admin_bp.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form

        # Validation
        errors = {}

        if not data.get('course_name'):
            errors['course_name'] = '课程名称是必填项'

        if not data.get('credits') or int(data.get('credits', 0)) <= 0:
            errors['credits'] = '学分必须大于0'

        if errors and request.is_json:
            return jsonify({'success': False, 'errors': errors}), 400

        if errors:
            for field, error in errors.items():
                flash(error, 'error')
            return render_template('admin/courses/edit.html', course=course)

        # Update course
        course.course_name = data['course_name']
        course.description = data.get('description')
        course.credits = int(data.get('credits', 3))
        course.department = data.get('department')
        course.instructor = data.get('instructor')

        try:
            db.session.commit()

            if request.is_json:
                return jsonify({'success': True, 'message': '课程更新成功', 'course': course.to_dict()})

            flash('课程更新成功', 'success')
            return redirect(url_for('admin.courses'))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'success': False, 'message': '课程更新失败'}), 500
            flash('课程更新失败', 'error')

    return render_template('admin/courses/edit.html', course=course)

@admin_bp.route('/courses/<int:course_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)

    try:
        db.session.delete(course)
        db.session.commit()

        if request.is_json:
            return jsonify({'success': True, 'message': '课程删除成功'})

        flash('课程删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'message': '课程删除失败'}), 500
        flash('课程删除失败', 'error')

    return redirect(url_for('admin.courses'))

# Enrollment Management
@admin_bp.route('/enrollments')
@login_required
@admin_required
def enrollments():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')

    query = Enrollment.query.join(Student).join(Course)

    if search:
        query = query.filter(
            (Student.student_id.contains(search)) |
            (Student.first_name.contains(search)) |
            (Student.last_name.contains(search)) |
            (Course.course_code.contains(search)) |
            (Course.course_name.contains(search))
        )

    if status_filter:
        query = query.filter(Enrollment.status == status_filter)

    enrollments = query.paginate(
        page=page,
        per_page=20,
        error_out=False
    )

    return render_template('admin/enrollments/index.html', enrollments=enrollments, search=search, status_filter=status_filter)

@admin_bp.route('/enrollments/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_enrollment():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form

        # Validation
        errors = {}

        if not data.get('student_id'):
            errors['student_id'] = '学生是必填项'

        if not data.get('course_id'):
            errors['course_id'] = '课程是必填项'

        # Check if enrollment already exists
        existing = Enrollment.query.filter_by(
            student_id=data.get('student_id'),
            course_id=data.get('course_id')
        ).first()

        if existing:
            errors['general'] = '该学生已经选修了这门课程'

        if errors and request.is_json:
            return jsonify({'success': False, 'errors': errors}), 400

        if errors:
            for field, error in errors.items():
                flash(error, 'error')
            from datetime import datetime
            students = Student.query.all()
            courses = Course.query.all()
            return render_template('admin/enrollments/create.html', students=students, courses=courses, today=datetime.now().strftime('%Y-%m-%d'))

        # Create new enrollment (without grade)
        from datetime import datetime
        enrollment = Enrollment(
            student_id=data['student_id'],
            course_id=data['course_id'],
            enrollment_date=datetime.strptime(data.get('enrollment_date'), '%Y-%m-%d').date() if data.get('enrollment_date') else None,
            status=data.get('status', 'enrolled'),
            grade=None  # 移除成绩录入，成绩需要单独录入
        )

        try:
            db.session.add(enrollment)
            db.session.commit()

            if request.is_json:
                return jsonify({'success': True, 'message': '选课信息创建成功', 'enrollment': enrollment.to_dict()})

            flash('选课信息创建成功', 'success')
            return redirect(url_for('admin.enrollments'))
        except Exception as e:
            db.session.rollback()
            print(f"选课创建错误: {e}")  # 调试信息
            if request.is_json:
                return jsonify({'success': False, 'message': f'选课信息创建失败: {str(e)}'}), 500
            flash(f'选课信息创建失败: {str(e)}', 'error')

    from datetime import datetime
    students = Student.query.all()
    courses = Course.query.all()
    return render_template('admin/enrollments/create.html', students=students, courses=courses, today=datetime.now().strftime('%Y-%m-%d'))

@admin_bp.route('/grades/record', methods=['GET', 'POST'])
@login_required
@admin_required
def record_grade():
    """独立的录入成绩功能"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form

        # Validation
        errors = {}

        if not data.get('student_id'):
            errors['student_id'] = '学生是必填项'

        if not data.get('course_id'):
            errors['course_id'] = '课程是必填项'

        if not data.get('grade'):
            errors['grade'] = '成绩是必填项'

        # Check if enrollment already exists
        existing = Enrollment.query.filter_by(
            student_id=data.get('student_id'),
            course_id=data.get('course_id')
        ).first()

        if not existing:
            errors['enrollment'] = '该学生尚未选课，请先添加选课记录'

        if errors:
            if request.is_json:
                return jsonify({'success': False, 'errors': errors}), 400
            for field, error in errors.items():
                flash(error, 'error')
            students = Student.query.all()
            courses = Course.query.all()
            return render_template('admin/grades/record.html',
                                 students=students,
                                 courses=courses,
                                 errors=errors,
                                 form_data=data)

        try:
            # Update existing enrollment with grade
            existing.grade = float(data.get('grade'))
            existing.status = 'completed'  # 录入成绩后自动设为已完成

            if data.get('remarks'):
                existing.remarks = data.get('remarks')

            db.session.commit()

            if request.is_json:
                return jsonify({'success': True, 'message': '成绩录入成功', 'enrollment': existing.to_dict()})

            flash('成绩录入成功', 'success')
            return redirect(url_for('admin.grades'))

        except Exception as e:
            db.session.rollback()
            error_msg = f'成绩录入失败: {str(e)}'
            if request.is_json:
                return jsonify({'success': False, 'message': error_msg}), 500
            flash(error_msg, 'error')

    # GET request - show form
    students = Student.query.all()
    courses = Course.query.all()
    return render_template('admin/grades/record.html', students=students, courses=courses)

@admin_bp.route('/api/check-enrollment')
@login_required
@admin_required
def check_enrollment():
    """检查学生是否已选指定课程"""
    student_id = request.args.get('student_id')
    course_id = request.args.get('course_id')

    if not student_id or not course_id:
        return jsonify({'exists': False, 'error': '参数不完整'}), 400

    enrollment = Enrollment.query.filter_by(
        student_id=student_id,
        course_id=course_id
    ).first()

    return jsonify({
        'exists': enrollment is not None,
        'has_grade': enrollment.grade is not None if enrollment else False
    })

@admin_bp.route('/api/student-courses/<int:student_id>')
@login_required
@admin_required
def get_student_courses(student_id):
    """获取指定学生已选的课程"""

    # 获取学生的选课记录
    enrollments = Enrollment.query.filter_by(student_id=student_id).join(Course).all()

    courses = []
    for enrollment in enrollments:
        course = {
            'id': enrollment.course.id,
            'course_code': enrollment.course.course_code,
            'course_name': enrollment.course.course_name,
            'credits': enrollment.course.credits,
            'instructor': enrollment.course.instructor,
            'has_grade': enrollment.grade is not None,
            'grade': enrollment.grade,
            'enrollment_date': enrollment.enrollment_date.strftime('%Y-%m-%d') if enrollment.enrollment_date else None
        }
        courses.append(course)

    return jsonify({'courses': courses})

@admin_bp.route('/enrollments/<int:enrollment_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_enrollment(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form

        # Update enrollment
        enrollment.status = data.get('status', 'enrolled')
        if data.get('grade'):
            enrollment.grade = float(data.get('grade'))
            # 如果录入了成绩，自动将状态更新为已完成
            if enrollment.status == 'enrolled':
                enrollment.status = 'completed'

        try:
            db.session.commit()

            if request.is_json:
                return jsonify({'success': True, 'message': '选课信息更新成功', 'enrollment': enrollment.to_dict()})

            flash('选课信息更新成功', 'success')
            return redirect(url_for('admin.enrollments'))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'success': False, 'message': '选课信息更新失败'}), 500
            flash('选课信息更新失败', 'error')

    return render_template('admin/enrollments/edit.html', enrollment=enrollment)

@admin_bp.route('/enrollments/<int:enrollment_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_enrollment(enrollment_id):
    enrollment = Enrollment.query.get_or_404(enrollment_id)

    try:
        db.session.delete(enrollment)
        db.session.commit()

        if request.is_json:
            return jsonify({'success': True, 'message': '选课信息删除成功'})

        flash('选课信息删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'message': '选课信息删除失败'}), 500
        flash('选课信息删除失败', 'error')

    return redirect(url_for('admin.enrollments'))

# Grade Management
@admin_bp.route('/grades')
@login_required
@admin_required
def grades():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    course_filter = request.args.get('course', '')
    status_filter = request.args.get('status', 'completed')

    query = Enrollment.query.join(Student).join(Course)

    # 只显示有成绩的记录
    query = query.filter(Enrollment.grade.isnot(None))

    if search:
        query = query.filter(
            (Student.student_id.contains(search)) |
            (Student.first_name.contains(search)) |
            (Student.last_name.contains(search)) |
            (Course.course_code.contains(search)) |
            (Course.course_name.contains(search))
        )

    if course_filter:
        query = query.filter(Course.id == course_filter)

    if status_filter:
        query = query.filter(Enrollment.status == status_filter)

    # 按成绩降序排列
    enrollments = query.order_by(Enrollment.grade.desc()).paginate(
        page=page,
        per_page=20,
        error_out=False
    )

    # 获取所有课程用于筛选
    courses = Course.query.order_by(Course.course_name).all()

    return render_template('admin/grades/index.html',
                         enrollments=enrollments,
                         search=search,
                         course_filter=course_filter,
                         status_filter=status_filter,
                         courses=courses)

@admin_bp.route('/grades/<int:enrollment_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_grade(enrollment_id):
    """删除成绩记录"""
    enrollment = Enrollment.query.get_or_404(enrollment_id)

    # 记录删除信息用于日志
    student_name = f"{enrollment.student.first_name} {enrollment.student.last_name}"
    course_name = enrollment.course.course_name
    grade = enrollment.grade

    try:
        db.session.delete(enrollment)
        db.session.commit()

        if request.is_json:
            return jsonify({
                'success': True,
                'message': f'成功删除 {student_name} 在 {course_name} 课程中的成绩记录'
            })

        flash(f'成功删除 {student_name} 在 {course_name} 课程中的成绩记录', 'success')
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({
                'success': False,
                'message': '删除成绩记录失败，请重试'
            }), 500
        flash('删除成绩记录失败，请重试', 'error')

    return redirect(url_for('admin.grades'))

# API endpoints for data
@admin_bp.route('/api/students')
@login_required
@admin_required
def api_students():
    students = Student.query.all()
    return jsonify([s.to_dict() for s in students])

@admin_bp.route('/api/courses')
@login_required
@admin_required
def api_courses():
    courses = Course.query.all()
    return jsonify([c.to_dict() for c in courses])

@admin_bp.route('/api/enrollments')
@login_required
@admin_required
def api_enrollments():
    enrollments = Enrollment.query.all()
    return jsonify([e.to_dict() for e in enrollments])