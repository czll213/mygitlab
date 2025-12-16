from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.student import Student
from app.models.course import Course
from app.models.enrollment import Enrollment
from datetime import date
from functools import wraps

student_bp = Blueprint('student', __name__)

def student_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.is_admin():
            flash('访问被拒绝。需要学生权限。', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@student_bp.route('/dashboard')
@login_required
@student_only
def dashboard():
    # Get or create student record for current user
    student = Student.query.filter_by(email=current_user.email).first()

    if not student:
        # Create student record automatically
        student = Student(
            student_id=f"STU{current_user.id:05d}",
            first_name=current_user.full_name.split()[0] if current_user.full_name else '',
            last_name=' '.join(current_user.full_name.split()[1:]) if len(current_user.full_name.split()) > 1 else '',
            email=current_user.email,
            phone=current_user.phone or ''
        )
        db.session.add(student)
        db.session.commit()

    # Get student's enrollments
    enrollments = Enrollment.query.filter_by(student_id=student.id).all()

    # Calculate statistics
    total_courses = len(enrollments)
    completed_courses = len([e for e in enrollments if e.status == 'completed'])
    current_courses = len([e for e in enrollments if e.status == 'enrolled'])

    # Calculate average grade
    completed_with_grades = [e for e in enrollments if e.status == 'completed' and e.grade is not None]
    avg_grade = sum(e.grade for e in completed_with_grades) / len(completed_with_grades) if completed_with_grades else 0

    stats = {
        'total_courses': total_courses,
        'completed_courses': completed_courses,
        'current_courses': current_courses,
        'avg_grade': round(avg_grade, 2)
    }

    return render_template('student/dashboard.html', student=student, enrollments=enrollments, stats=stats)

@student_bp.route('/profile')
@login_required
@student_only
def profile():
    student = Student.query.filter_by(email=current_user.email).first()
    if not student:
        flash('未找到学生记录。请联系管理员。', 'error')
        return redirect(url_for('student.dashboard'))

    # Get student's enrollments for statistics
    enrollments = Enrollment.query.filter_by(student_id=student.id).all()

    # Calculate statistics
    total_courses = len(enrollments)
    completed_courses = len([e for e in enrollments if e.status == 'completed'])
    current_courses = len([e for e in enrollments if e.status == 'enrolled'])

    # Calculate average grade and total credits
    completed_with_grades = [e for e in enrollments if e.status == 'completed' and e.grade is not None]
    avg_grade = sum(e.grade for e in completed_with_grades) / len(completed_with_grades) if completed_with_grades else 0
    total_credits = sum(e.course.credits for e in enrollments if e.status == 'completed')

    stats = {
        'total_courses': total_courses,
        'completed_courses': completed_courses,
        'current_courses': current_courses,
        'avg_grade': round(avg_grade, 1),
        'total_credits': total_credits
    }

    return render_template('student/profile.html', student=student, enrollments=enrollments, stats=stats)

@student_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@student_only
def edit_profile():
    student = Student.query.filter_by(email=current_user.email).first()

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form

        # Validation
        errors = {}

        if not data.get('first_name'):
            errors['first_name'] = '名字是必填项'

        if not data.get('last_name'):
            errors['last_name'] = '姓氏是必填项'

        if not data.get('email') or '@' not in data.get('email'):
            errors['email'] = '请输入有效的邮箱地址'

        # Check if email already exists (excluding current student)
        if Student.query.filter(Student.email == data.get('email'), Student.id != student.id).first():
            errors['email'] = '邮箱已存在'

        if errors and request.is_json:
            return jsonify({'success': False, 'errors': errors}), 400

        if errors:
            for field, error in errors.items():
                flash(error, 'error')
            return render_template('student/profile_edit.html', student=student)

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
            # Also update the corresponding user account
            current_user.email = data['email']
            current_user.full_name = f"{data['first_name']} {data['last_name']}"
            current_user.phone = data.get('phone', '')

            db.session.commit()

            if request.is_json:
                return jsonify({'success': True, 'message': '个人资料更新成功', 'student': student.to_dict()})

            flash('个人资料更新成功', 'success')
            return redirect(url_for('student.profile'))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'success': False, 'message': f'个人资料更新失败: {str(e)}'}), 500
            flash(f'个人资料更新失败: {str(e)}', 'error')

    return render_template('student/profile_edit.html', student=student)

@student_bp.route('/courses')
@login_required
@student_only
def courses():
    student = Student.query.filter_by(email=current_user.email).first()
    if not student:
        flash('未找到学生记录。请联系管理员。', 'error')
        return redirect(url_for('student.dashboard'))

    # Get search parameter
    search_term = request.args.get('search', '').strip()

    # Build query for courses
    query = Course.query

    # Apply search filter if provided
    if search_term:
        # Search in course_code and course_name
        query = query.filter(
            db.or_(
                Course.course_code.contains(search_term),
                Course.course_name.contains(search_term)
            )
        )

    # Get courses based on search
    all_courses = query.all()

    # Get courses the student is already enrolled in
    enrolled_course_ids = [e.course_id for e in Enrollment.query.filter_by(student_id=student.id).all()]

    # Separate available and enrolled courses
    available_courses = [c for c in all_courses if c.id not in enrolled_course_ids]
    enrolled_courses = [c for c in all_courses if c.id in enrolled_course_ids]

    return render_template('student/courses.html',
                         available_courses=available_courses,
                         enrolled_courses=enrolled_courses,
                         search_term=search_term)

@student_bp.route('/courses/<int:course_id>/enroll', methods=['POST'])
@login_required
@student_only
def enroll_course(course_id):
    # 判断是否是AJAX请求
    is_ajax = request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    student = Student.query.filter_by(email=current_user.email).first()
    if not student:
        if is_ajax:
            return jsonify({'success': False, 'message': '未找到学生记录'}), 400
        flash('未找到学生记录。请联系管理员。', 'error')
        return redirect(url_for('student.dashboard'))

    course = Course.query.get_or_404(course_id)

    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(
        student_id=student.id,
        course_id=course_id
    ).first()

    if existing_enrollment:
        if is_ajax:
            return jsonify({'success': False, 'message': '已经选修了这门课程'}), 400
        flash('您已经选修了这门课程', 'error')
        return redirect(url_for('student.courses'))

    # Create new enrollment
    enrollment = Enrollment(
        student_id=student.id,
        course_id=course_id,
        enrollment_date=date.today(),
        status='enrolled'
    )

    try:
        db.session.add(enrollment)
        db.session.commit()

        if is_ajax:
            return jsonify({
                'success': True,
                'message': f'成功选修课程：{course.course_name}',
                'enrollment': enrollment.to_dict()
            })

        flash(f'成功选修课程：{course.course_name}', 'success')
    except Exception as e:
        db.session.rollback()
        error_msg = f'选课失败：{str(e)}' if str(e) else '选课失败'
        if is_ajax:
            return jsonify({'success': False, 'message': error_msg}), 500
        flash(error_msg, 'error')

    return redirect(url_for('student.courses'))

@student_bp.route('/courses/<int:course_id>/drop', methods=['POST'])
@login_required
@student_only
def drop_course(course_id):
    # 判断是否是AJAX请求
    is_ajax = request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    student = Student.query.filter_by(email=current_user.email).first()
    if not student:
        if is_ajax:
            return jsonify({'success': False, 'message': '未找到学生记录'}), 400
        flash('未找到学生记录。请联系管理员。', 'error')
        return redirect(url_for('student.dashboard'))

    enrollment = Enrollment.query.filter_by(
        student_id=student.id,
        course_id=course_id
    ).first_or_404()

    course_name = enrollment.course.course_name

    try:
        db.session.delete(enrollment)
        db.session.commit()

        if is_ajax:
            return jsonify({
                'success': True,
                'message': f'成功退选课程：{course_name}'
            })

        flash(f'成功退选课程：{course_name}', 'success')
    except Exception as e:
        db.session.rollback()
        error_msg = f'退选课程失败：{str(e)}' if str(e) else '退选课程失败'
        if is_ajax:
            return jsonify({'success': False, 'message': error_msg}), 500
        flash(error_msg, 'error')

    return redirect(url_for('student.courses'))

@student_bp.route('/enrollments')
@login_required
@student_only
def enrollments():
    student = Student.query.filter_by(email=current_user.email).first()
    if not student:
        flash('未找到学生记录。请联系管理员。', 'error')
        return redirect(url_for('student.dashboard'))

    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    search_term = request.args.get('search', '').strip()

    # Build base query for student's enrollments
    query = Enrollment.query.filter_by(student_id=student.id).join(Course)

    # Apply status filter if provided
    if status_filter:
        query = query.filter(Enrollment.status == status_filter)

    # Apply search filter if provided
    if search_term:
        query = query.filter(
            db.or_(
                Course.course_code.contains(search_term),
                Course.course_name.contains(search_term),
                Course.instructor.contains(search_term)
            )
        )

    enrollments = query.paginate(
        page=page,
        per_page=10,
        error_out=False
    )

    # 计算统计数据（基于所有记录，不仅仅是当前页）
    all_enrollments = query.all()
    completed_count = len([e for e in all_enrollments if e.status == 'completed'])
    enrolled_count = len([e for e in all_enrollments if e.status == 'enrolled'])

    # 计算平均成绩
    completed_grades = [e.grade for e in all_enrollments if e.status == 'completed' and e.grade is not None]
    avg_grade = sum(completed_grades) / len(completed_grades) if completed_grades else 0

    stats = {
        'total': len(all_enrollments),
        'completed': completed_count,
        'enrolled': enrolled_count,
        'avg_grade': round(avg_grade, 1)
    }

    return render_template('student/enrollments.html',
                         enrollments=enrollments,
                         status_filter=status_filter,
                         search_term=search_term,
                         stats=stats)

@student_bp.route('/enrollments/<int:enrollment_id>')
@login_required
@student_only
def view_enrollment(enrollment_id):
    student = Student.query.filter_by(email=current_user.email).first()
    if not student:
        flash('未找到学生记录。请联系管理员。', 'error')
        return redirect(url_for('student.dashboard'))

    enrollment = Enrollment.query.filter_by(
        id=enrollment_id,
        student_id=student.id
    ).first_or_404()

    return render_template('student/enrollment_detail.html', enrollment=enrollment)

@student_bp.route('/grades')
@login_required
@student_only
def grades():
    student = Student.query.filter_by(email=current_user.email).first()
    if not student:
        flash('未找到学生记录。请联系管理员。', 'error')
        return redirect(url_for('student.dashboard'))

    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    semester_filter = request.args.get('semester', '')
    search_query = request.args.get('search', '').strip()

    # 构建基础查询：只显示有成绩的记录
    query = Enrollment.query.filter_by(student_id=student.id).filter(Enrollment.grade.isnot(None)).join(Course)

    # 应用搜索过滤器（按课程名称或课程代码）
    if search_query:
        query = query.filter(
            db.or_(
                Course.course_code.contains(search_query),
                Course.course_name.contains(search_query)
            )
        )

    # 应用状态过滤器
    if status_filter:
        query = query.filter(Enrollment.status == status_filter)

    # 应用学期过滤器
    if semester_filter:
        if '春季' in semester_filter:
            year = semester_filter.replace('春季', '')
            query = query.filter(
                db.extract('year', Enrollment.enrollment_date) == year,
                db.extract('month', Enrollment.enrollment_date) <= 6
            )
        elif '秋季' in semester_filter:
            year = semester_filter.replace('秋季', '')
            query = query.filter(
                db.extract('year', Enrollment.enrollment_date) == year,
                db.extract('month', Enrollment.enrollment_date) > 6
            )

    enrollments = query.order_by(Enrollment.updated_at.desc()).paginate(
        page=page,
        per_page=10,
        error_out=False
    )

    # 获取所有可用学期（用于下拉菜单）
    all_enrollments = Enrollment.query.filter_by(student_id=student.id).filter(Enrollment.grade.isnot(None)).all()
    available_semesters = []
    for enrollment in all_enrollments:
        if enrollment.enrollment_date:
            year = enrollment.enrollment_date.year
            if enrollment.enrollment_date.month <= 6:
                semester = f"{year}春季"
            else:
                semester = f"{year}秋季"
            if semester not in available_semesters:
                available_semesters.append(semester)
    available_semesters.sort(reverse=True)  # 最新的学期在前

    # 计算统计信息（基于搜索和过滤后的结果）
    filtered_enrollments = query.all()
    all_grades = [e.grade for e in filtered_enrollments if e.grade is not None]
    stats = {
        'total_courses': len(all_grades),
        'average_grade': sum(all_grades) / len(all_grades) if all_grades else 0,
        'highest_grade': max(all_grades) if all_grades else 0,
        'lowest_grade': min(all_grades) if all_grades else 0
    }

    return render_template('student/grades.html',
                         enrollments=enrollments,
                         status_filter=status_filter,
                         semester_filter=semester_filter,
                         search_query=search_query,
                         available_semesters=available_semesters,
                         stats=stats)

# API endpoints
@student_bp.route('/api/courses/available')
@login_required
@student_only
def api_available_courses():
    student = Student.query.filter_by(email=current_user.email).first()
    if not student:
        return jsonify({'error': '未找到学生记录'}), 400

    enrolled_course_ids = [e.course_id for e in Enrollment.query.filter_by(student_id=student.id).all()]
    available_courses = Course.query.filter(~Course.id.in_(enrolled_course_ids)).all()

    return jsonify([c.to_dict() for c in available_courses])

@student_bp.route('/api/enrollments')
@login_required
@student_only
def api_enrollments():
    student = Student.query.filter_by(email=current_user.email).first()
    if not student:
        return jsonify({'error': '未找到学生记录'}), 400

    enrollments = Enrollment.query.filter_by(student_id=student.id).all()
    return jsonify([e.to_dict() for e in enrollments])

@student_bp.route('/api/profile')
@login_required
@student_only
def api_profile():
    student = Student.query.filter_by(email=current_user.email).first()
    if not student:
        return jsonify({'error': '未找到学生记录'}), 400

    return jsonify(student.to_dict())