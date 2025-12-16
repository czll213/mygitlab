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
    # 基础统计
    stats = {
        'total_users': User.query.count(),
        'total_students': Student.query.count(),
        'total_courses': Course.query.count(),
        'total_enrollments': Enrollment.query.count(),
        'active_users': User.query.filter_by(is_active=True).count()
    }

    # 成绩统计
    grade_stats = {
        'total_grades': Enrollment.query.filter(Enrollment.grade.isnot(None)).count(),
        'avg_grade': db.session.query(db.func.avg(Enrollment.grade)).filter(Enrollment.grade.isnot(None)).scalar() or 0,
        'highest_grade': db.session.query(db.func.max(Enrollment.grade)).filter(Enrollment.grade.isnot(None)).scalar() or 0,
        'lowest_grade': db.session.query(db.func.min(Enrollment.grade)).filter(Enrollment.grade.isnot(None)).scalar() or 0,
        'completed_courses': Enrollment.query.filter_by(status='completed').count()
    }

    # 最近活动
    recent_enrollments = Enrollment.query.order_by(Enrollment.created_at.desc()).limit(5).all()
    recent_grades = Enrollment.query.filter(Enrollment.grade.isnot(None)).order_by(Enrollment.updated_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                         stats=stats,
                         grade_stats=grade_stats,
                         recent_enrollments=recent_enrollments,
                         recent_grades=recent_grades)

# Batch activate inactive users
@admin_bp.route('/users/activate-inactive', methods=['POST'])
@login_required
@admin_required
def activate_inactive_users():
    """激活所有未激活的用户"""
    try:
        # 获取所有未激活的用户
        inactive_users = User.query.filter_by(is_active=False).all()
        activated_count = 0

        for user in inactive_users:
            user.is_active = True
            activated_count += 1

        db.session.commit()

        message = f'成功激活 {activated_count} 个用户账户'
        if request.is_json:
            return jsonify({'success': True, 'message': message})

        flash(message, 'success')

    except Exception as e:
        db.session.rollback()
        error_message = f'激活用户失败: {str(e)}'
        if request.is_json:
            return jsonify({'success': False, 'message': error_message}), 500
        flash(error_message, 'error')

    return redirect(url_for('admin.users'))

# Batch sync user and student data
@admin_bp.route('/users/sync-student-data', methods=['POST'])
@login_required
@admin_required
def sync_student_data():
    """同步用户和学生数据"""
    try:
        # 获取所有学生用户
        student_users = User.query.filter_by(role='student').all()
        synced_count = 0
        error_count = 0

        for user in student_users:
            try:
                # 查找对应的学生记录
                student = Student.query.filter_by(email=user.email).first()
                if not student:
                    # 如果通过邮箱找不到，尝试通过姓名匹配
                    students_by_name = Student.query.filter(
                        (Student.first_name == user.full_name.split()[0]) if user.full_name.split() else False
                    ).all()

                    # 如果找到匹配的，取第一个
                    if students_by_name:
                        student = students_by_name[0]
                        student.email = user.email  # 同步邮箱

                if student:
                    # 同步基本信息
                    student.email = user.email
                    student.phone = user.phone or ''

                    # 同步姓名
                    if user.full_name:
                        if ' ' in user.full_name:
                            parts = user.full_name.split(' ', 1)
                            student.first_name = parts[0]
                            student.last_name = parts[1] if len(parts) > 1 else ''
                        else:
                            student.first_name = user.full_name
                            student.last_name = ''

                    synced_count += 1
                else:
                    error_count += 1

            except Exception as e:
                print(f"同步用户 {user.username} 时出错: {e}")
                error_count += 1
                continue

        db.session.commit()

        message = f'数据同步完成！成功同步 {synced_count} 个学生，失败 {error_count} 个'
        if request.is_json:
            return jsonify({'success': True, 'message': message})

        flash(message, 'success')

    except Exception as e:
        db.session.rollback()
        error_message = f'数据同步失败: {str(e)}'
        if request.is_json:
            return jsonify({'success': False, 'message': error_message}), 500
        flash(error_message, 'error')

    return redirect(url_for('admin.users'))

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
            db.or_(
                User.username.like(f'%{search}%'),
                User.email.like(f'%{search}%'),
                User.full_name.like(f'%{search}%')
            )
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

            # If the user is a student, also update the student record
            if user.is_student():
                # Try to find student record by old email first, then by new email
                student = Student.query.filter_by(email=user.email).first()
                if not student:
                    # If not found by old email, try finding by new email
                    student = Student.query.filter_by(email=data['email']).first()

                if student:
                    # Update student record with the latest user information
                    student.email = data['email']
                    student.phone = data.get('phone', '')
                    # Split full_name into first_name and last_name
                    full_name = data['full_name']
                    if ' ' in full_name:
                        parts = full_name.split(' ', 1)
                        student.first_name = parts[0]
                        student.last_name = parts[1] if len(parts) > 1 else ''
                    else:
                        student.first_name = full_name
                        student.last_name = ''

            db.session.commit()

            if request.is_json:
                return jsonify({'success': True, 'message': '用户更新成功', 'user': user.to_dict()})

            flash('用户更新成功', 'success')
            return redirect(url_for('admin.users'))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'success': False, 'message': f'用户更新失败: {str(e)}'}), 500
            flash(f'用户更新失败: {str(e)}', 'error')

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

    # 获取所有用户邮箱，用于检查学生是否有登录账户
    user_emails = set(user.email for user in User.query.filter_by(role='student').all())

    return render_template('admin/students/index.html', students=students, search=search, user_emails=user_emails)

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

        if not data.get('username') or len(data['username']) < 4:
            errors['username'] = '用户名必须至少4个字符'

        if not data.get('password') or len(data['password']) < 6:
            errors['password'] = '密码必须至少6个字符'

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

        # Check if username already exists in users table
        if User.query.filter_by(username=data.get('username')).first():
            errors['username'] = '用户名已存在'

        if errors and request.is_json:
            return jsonify({'success': False, 'errors': errors}), 400

        if errors:
            for field, error in errors.items():
                flash(error, 'error')
            return render_template('admin/students/create.html')

        try:
            # First, create user account
            user = User(
                username=data['username'],
                email=data['email'],
                full_name=f"{data['first_name']} {data['last_name']}",
                phone=data.get('phone', ''),
                role='student',
                is_active=True
            )
            user.set_password(data['password'])
            db.session.add(user)
            db.session.flush()  # Get the user ID without committing

            # Create new student record
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
            db.session.add(student)
            db.session.commit()

            if request.is_json:
                return jsonify({
                    'success': True,
                    'message': '学生创建成功，用户账户已生成',
                    'student': student.to_dict(),
                    'user': user.to_dict()
                })

            flash('学生创建成功，用户账户已生成', 'success')
            return redirect(url_for('admin.students'))

        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'success': False, 'message': f'学生创建失败: {str(e)}'}), 500
            flash(f'学生创建失败: {str(e)}', 'error')

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

        # Check if username exists (if username is being updated)
        if data.get('username') and data.get('username') != student.email.split('@')[0]:
            if User.query.filter(User.username == data.get('username')).first():
                errors['username'] = '用户名已存在'

        if errors and request.is_json:
            return jsonify({'success': False, 'errors': errors}), 400

        if errors:
            for field, error in errors.items():
                flash(error, 'error')
            return render_template('admin/students/edit.html', student=student)

        try:
            # Update student record
            student.first_name = data['first_name']
            student.last_name = data['last_name']
            student.birth_date = data.get('birth_date')
            student.gender = data.get('gender')
            student.email = data['email']
            student.phone = data.get('phone')
            student.address = data.get('address')
            student.major = data.get('major')
            student.enrollment_year = data.get('enrollment_year')

            # Find and update the corresponding user account (if exists)
            user = User.query.filter_by(email=student.email).first()
            if user:
                # Update user info to match student info
                user.email = data['email']
                user.full_name = f"{data['first_name']} {data['last_name']}"
                user.phone = data.get('phone', '')

                # Update username if provided
                if data.get('username'):
                    user.username = data['username']

                # Update password if provided
                if data.get('password'):
                    user.set_password(data['password'])

            db.session.commit()

            if request.is_json:
                return jsonify({'success': True, 'message': '学生更新成功', 'student': student.to_dict()})

            flash('学生更新成功', 'success')
            return redirect(url_for('admin.students'))

        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'success': False, 'message': f'学生更新失败: {str(e)}'}), 500
            flash(f'学生更新失败: {str(e)}', 'error')

    return render_template('admin/students/edit.html', student=student)

@admin_bp.route('/students/<int:student_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)

    try:
        # Find and delete the corresponding user account (if exists)
        user = User.query.filter_by(email=student.email).first()
        if user:
            db.session.delete(user)

        db.session.delete(student)
        db.session.commit()

        if request.is_json:
            return jsonify({'success': True, 'message': '学生删除成功，相关用户账户已删除'})

        flash('学生删除成功，相关用户账户已删除', 'success')
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'message': f'学生删除失败: {str(e)}'}), 500
        flash(f'学生删除失败: {str(e)}', 'error')

    return redirect(url_for('admin.students'))

# Batch create user accounts for existing students
@admin_bp.route('/students/create-user-accounts', methods=['POST'])
@login_required
@admin_required
def create_user_accounts_for_students():
    """为没有用户账户的现有学生创建账户"""
    try:
        # 获取所有学生记录
        students = Student.query.all()
        created_count = 0
        skipped_count = 0

        for student in students:
            # 检查是否已有对应的用户账户（通过邮箱或学号查找）
            existing_user = User.query.filter(
                (User.email == student.email) | (User.username == student.student_id)
            ).first()

            if existing_user:
                skipped_count += 1
                continue

            # 生成默认用户名（优先使用学号）
            username = student.student_id

            # 如果学号作为用户名已存在，尝试其他方式
            if User.query.filter_by(username=username).first():
                # 尝试使用邮箱前缀
                email_prefix = student.email.split('@')[0]
                if not User.query.filter_by(username=email_prefix).first():
                    username = email_prefix
                else:
                    # 使用姓名拼音或简单组合
                    name_part = student.first_name.lower()
                    if student.last_name:
                        name_part += student.last_name.lower()

                    username = name_part
                    counter = 1
                    while User.query.filter_by(username=username).first():
                        username = f"{name_part}{counter}"
                        counter += 1

            # 创建用户账户
            user = User(
                username=username,
                email=student.email,
                full_name=student.full_name,
                phone=student.phone or '',
                role='student',
                is_active=True
            )
            # 设置默认密码为学号（确保学号不为空）
            default_password = student.student_id if student.student_id else "123456"
            user.set_password(default_password)

            db.session.add(user)
            created_count += 1

        db.session.commit()

        message = f'成功为 {created_count} 个学生创建用户账户，跳过 {skipped_count} 个已有账户的学生'
        if created_count > 0:
            message += f'。默认密码为学号，首次登录后请修改密码。'

        if request.is_json:
            return jsonify({'success': True, 'message': message})

        flash(message, 'success')

    except Exception as e:
        db.session.rollback()
        error_message = f'批量创建用户账户失败: {str(e)}'
        if request.is_json:
            return jsonify({'success': False, 'message': error_message}), 500
        flash(error_message, 'error')

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

    # 获取所有学生和课程数据
    students = Student.query.all()
    courses = Course.query.all()
    return render_template('admin/enrollments/edit.html', enrollment=enrollment, students=students, courses=courses)

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