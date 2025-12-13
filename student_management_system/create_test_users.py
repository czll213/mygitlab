#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试用户数据以验证分页功能
"""

from app import create_app, db
from app.models.user import User
import random

def create_test_users():
    """创建测试用户数据"""

    app = create_app()
    with app.app_context():
        print("=== 创建测试用户数据 ===")

        # 检查现有用户数量
        existing_users = User.query.count()
        print(f"当前用户数量: {existing_users}")

        # 生成更多测试用户
        first_names = ["张", "李", "王", "赵", "刘", "陈", "杨", "黄", "周", "吴", "徐", "孙", "马", "朱", "胡", "林", "郭", "何", "高", "罗"]
        last_names = ["伟", "芳", "娜", "敏", "静", "丽", "强", "磊", "洋", "艳", "勇", "军", "杰", "娟", "涛", "明", "超", "秀英", "霞", "平"]

        roles = ["admin", "student"]
        departments = ["计算机系", "数学系", "物理系", "化学系", "生物系", "经济系", "管理系", "文学系", "历史系", "哲学系"]

        new_users_count = 0
        for i in range(50):  # 创建50个新用户，确保超过每页限制
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)

            username = f"user{existing_users + new_users_count + 1:04d}"
            email = f"{username}@university.edu"
            full_name = f"{first_name}{last_name}"
            role = random.choice(roles)
            department = random.choice(departments)

            # 检查用户名是否已存在
            if User.query.filter_by(username=username).first():
                continue

            user = User(
                username=username,
                email=email,
                full_name=full_name,
                role=role,
                is_active=True,
                phone=f"138{random.randint(10000000, 99999999)}",  # 随机手机号
                password_hash="hashed_password"  # 简化的密码哈希
            )

            try:
                db.session.add(user)
                new_users_count += 1
            except Exception as e:
                print(f"创建用户 {username} 失败: {e}")
                db.session.rollback()

        try:
            db.session.commit()
            print(f"成功创建 {new_users_count} 个新用户")

            # 检查最终用户数量
            final_users = User.query.count()
            print(f"最终用户数量: {final_users}")

            # 计算应该有多少页
            per_page = 20
            total_pages = (final_users + per_page - 1) // per_page
            print(f"每页显示 {per_page} 条记录")
            print(f"应该有 {total_pages} 页")

            if total_pages > 1:
                print("✅ 用户列表现在应该显示分页功能！")
            else:
                print("⚠️ 用户数量仍然不足以显示分页")

        except Exception as e:
            print(f"提交数据失败: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_test_users()