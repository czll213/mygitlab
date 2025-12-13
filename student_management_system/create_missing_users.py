#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为没有用户记录的学生创建对应的用户账户
"""

from app import create_app, db
from app.models import User, Student

def create_missing_users():
    """为没有用户记录的学生创建对应的用户账户"""

    app = create_app()
    with app.app_context():
        print("=== 为学生创建用户账户 ===")

        # 获取所有学生
        students = Student.query.all()
        print(f"找到 {len(students)} 个学生记录")

        # 获取所有用户
        users = User.query.all()
        user_emails = [user.email for user in users]
        user_usernames = [user.username for user in users]

        created_count = 0
        skipped_count = 0

        for student in students:
            # 检查是否已经有对应的用户记录
            if student.email in user_emails or student.student_id in user_usernames:
                print(f"跳过 {student.student_id} ({student.full_name}) - 已有用户记录")
                skipped_count += 1
                continue

            print(f"为 {student.student_id} ({student.full_name}) 创建用户记录")

            # 创建用户记录
            user = User(
                username=student.student_id,  # 使用学号作为用户名
                email=student.email,
                full_name=student.full_name,
                phone=student.phone,
                role='student',
                is_active=True
            )

            # 设置默认密码（学号）
            user.set_password(student.student_id)

            try:
                db.session.add(user)
                created_count += 1
                print(f"  [OK] 创建成功，默认密码: {student.student_id}")
            except Exception as e:
                print(f"  [ERROR] 创建失败: {e}")
                db.session.rollback()

        # 提交所有更改
        try:
            db.session.commit()
            print(f"\n成功创建 {created_count} 个用户账户")
            print(f"跳过 {skipped_count} 个已有账户的学生")

            # 验证结果
            final_users = User.query.count()
            final_students = Student.query.count()

            print(f"\n最终统计:")
            print(f"  用户记录总数: {final_users}")
            print(f"  学生记录总数: {final_students}")

            # 检查是否还有缺失的
            updated_users = User.query.all()
            updated_user_emails = [user.email for user in updated_users]

            still_missing = [s for s in students if s.email not in updated_user_emails]
            if still_missing:
                print(f"  仍有 {len(still_missing)} 个学生没有用户记录")
            else:
                print(f"  [OK] 所有学生都有对应的用户记录")

        except Exception as e:
            print(f"提交失败: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_missing_users()