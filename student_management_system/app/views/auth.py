from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.models.admin import Administrator
from functools import wraps
import re

auth_bp = Blueprint('auth', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('访问被拒绝。需要管理员权限。', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Handle JSON requests
        if request.is_json:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': '无效的请求数据'}), 400

            # Strip whitespace from inputs
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            full_name = data.get('full_name', '').strip()
            phone = data.get('phone', '').strip()
            password = data.get('password', '')
            confirm_password = data.get('confirm_password', '')

            # Validation
            errors = {}

            if not username or len(username) < 4:
                errors['username'] = '用户名必须至少4个字符'

            if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                errors['email'] = '请输入有效的邮箱地址'

            # Phone validation (optional field)
            if phone:
                phone_digits = re.sub(r'\D', '', phone)
                if len(phone_digits) < 7:
                    errors['phone'] = '请输入有效的电话号码'

            if not password or len(password) < 6:
                errors['password'] = '密码必须至少6个字符'

            if password != confirm_password:
                errors['confirm_password'] = '两次输入的密码不匹配'

            if not full_name:
                errors['full_name'] = '请输入全名'

            # Check if username or email already exists
            if username and User.query.filter_by(username=username).first():
                errors['username'] = '用户名已存在'

            if email and User.query.filter_by(email=email).first():
                errors['email'] = '邮箱已存在'

            if errors:
                return jsonify({'success': False, 'errors': errors}), 400

            # Create new user
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                phone=phone,
                role=data.get('role', 'student')
            )
            user.set_password(password)

            try:
                db.session.add(user)
                db.session.commit()

                return jsonify({
                    'success': True,
                    'message': '注册成功！请登录。',
                    'user': user.to_dict()
                })
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'message': '注册失败，请重试。'}), 500

        # Handle form submissions
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        role = request.form.get('role', 'student')

        # Validation
        if not username or len(username) < 4:
            flash('用户名必须至少4个字符', 'error')
            return render_template('auth/register.html')

        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('请输入有效的邮箱地址', 'error')
            return render_template('auth/register.html')

        # Phone validation (optional field)
        if phone:
            # Remove all non-digit characters for validation
            phone_digits = re.sub(r'\D', '', phone)
            if len(phone_digits) < 7:
                flash('请输入有效的电话号码', 'error')
                return render_template('auth/register.html')

        if not password or len(password) < 6:
            flash('密码必须至少6个字符', 'error')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('两次输入的密码不匹配', 'error')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'error')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('邮箱已存在', 'error')
            return render_template('auth/register.html')

        # Create new user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            phone=phone,
            role=role
        )
        user.set_password(password)

        try:
            db.session.add(user)
            db.session.commit()
            flash('注册成功！请登录。', 'success')
            return redirect(url_for('auth.login'))
        except:
            db.session.rollback()
            flash('注册失败，请重试。', 'error')

    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle JSON requests
        if request.is_json:
            data = request.get_json()

            username = data.get('username')
            password = data.get('password')
            remember = data.get('remember', False)

            if not username or not password:
                return jsonify({'success': False, 'message': '用户名和密码为必填项'}), 400

            user = User.query.filter(
                (User.username == username) | (User.email == username)
            ).first()

            if user and user.check_password(password) and user.is_active:
                login_user(user, remember=remember)
                return jsonify({
                    'success': True,
                    'message': '登录成功',
                    'user': user.to_dict(),
                    'redirect_url': url_for('main.dashboard')
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '用户名或密码错误'
                }), 401

        # Handle form submissions
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'

        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()

        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember)

            # Redirect based on role
            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('student.dashboard'))
        else:
            flash('用户名或密码错误', 'error')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已成功退出登录', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html', user=current_user)

@auth_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    if not current_user.check_password(current_password):
        flash('当前密码不正确', 'error')
        return redirect(url_for('auth.profile'))

    if len(new_password) < 6:
        flash('新密码必须至少6个字符', 'error')
        return redirect(url_for('auth.profile'))

    if new_password != confirm_password:
        flash('两次输入的新密码不匹配', 'error')
        return redirect(url_for('auth.profile'))

    current_user.set_password(new_password)

    try:
        db.session.commit()
        flash('密码修改成功', 'success')
    except:
        db.session.rollback()
        flash('密码修改失败', 'error')

    return redirect(url_for('auth.profile'))