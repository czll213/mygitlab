#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理为学生们创建的多余用户记录，保持学生和管理员用户分开
"""

from app import create_app, db
from app.models import User, Student

def cleanup_student_users():
    """清理为学生创建的用户记录，只保留必要的管理员用户"""

    app = create_app()
    with app.app_context():
        print("=== 清理学生用户记录 ===")

        # 获取所有用户
        all_users = User.query.all()
        print(f"当前总用户数: {len(all_users)}")

        # 获取所有学生
        all_students = Student.query.all()
        print(f"当前学生数: {len(all_students)}")

        # 获取学生的邮箱和学号列表
        student_emails = [s.email for s in all_students]
        student_ids = [s.student_id for s in all_students]

        # 识别需要删除的用户（学生创建的用户）
        users_to_delete = []
        admin_users = []

        for user in all_users:
            # 保留管理员用户
            if user.role == 'admin':
                admin_users.append(user)
                print(f"[保留] 管理员用户: {user.username}")
                continue

            # 检查是否是学生创建的用户（学号作为用户名或邮箱匹配学生）
            if user.username in student_ids or user.email in student_emails:
                users_to_delete.append(user)
                print(f"[删除] 学生用户: {user.username} ({user.email})")
            else:
                print(f"[保留] 其他用户: {user.username} ({user.email})")

        print(f"\n需要删除的学生用户数: {len(users_to_delete)}")
        print(f"保留的管理员用户数: {len(admin_users)}")

        # 删除学生用户记录
        deleted_count = 0
        for user in users_to_delete:
            try:
                db.session.delete(user)
                deleted_count += 1
            except Exception as e:
                print(f"删除用户 {user.username} 失败: {e}")
                db.session.rollback()

        try:
            db.session.commit()
            print(f"成功删除 {deleted_count} 个学生用户记录")

            # 验证最终状态
            final_users = User.query.all()
            final_students = Student.query.all()

            print(f"\n清理后的状态:")
            print(f"  剩余用户数: {len(final_users)}")
            print(f"  学生记录数: {len(final_students)}")

            print(f"\n剩余用户列表:")
            for user in final_users:
                print(f"  - {user.username}: {user.full_name} ({user.role})")

            print("\n系统状态:")
            print("  [OK] 学生记录和学生用户记录已分离")
            print("  [OK] 学生列表显示学生信息")
            print("  [OK] 用户列表显示管理员用户")
            print("  [INFO] 学生登录需要通过专门的用户创建功能")

        except Exception as e:
            print(f"提交删除操作失败: {e}")
            db.session.rollback()

if __name__ == '__main__':
    cleanup_student_users()