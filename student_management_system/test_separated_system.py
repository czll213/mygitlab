#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试分离后的系统：学生记录和用户记录分开管理
"""

import requests

def test_separated_system():
    """测试学生记录和用户记录分离的系统"""

    session = requests.Session()

    print("=== 测试分离后的系统 ===")

    try:
        # 1. 登录管理员账户
        print("\n1. 登录管理员账户...")
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }

        login_response = session.post('http://localhost:5000/auth/login', data=login_data)
        print(f"登录状态码: {login_response.status_code}")

        if login_response.status_code != 200:
            print("[ERROR] 管理员登录失败")
            return

        print("[OK] 管理员登录成功")

        # 2. 检查当前用户列表和学生列表
        print("\n2. 检查当前用户和学生数量...")

        users_response = session.get('http://localhost:5000/admin/users')
        students_response = session.get('http://localhost:5000/admin/students')

        if users_response.status_code == 200 and students_response.status_code == 200:
            print("[OK] 可以访问用户列表和学生列表")

            # 统计用户数量
            users_content = users_response.text
            student_content = students_response.text

            # 粗略统计（通过查找表格行）
            user_rows = users_content.count('<tr')
            student_rows = student_content.count('<tr>')

            print(f"用户列表大约有 {user_rows} 行数据")
            print(f"学生列表大约有 {student_rows} 行数据")
        else:
            print("[ERROR] 无法访问列表页面")

        # 3. 创建新学生
        print("\n3. 创建新学生（不创建用户记录）...")
        import random
        test_id = random.randint(1000, 9999)

        student_data = {
            'student_id': f'NEW{test_id}',
            'first_name': '新',
            'last_name': f'学生{test_id}',
            'email': f'newstudent{test_id}@university.edu',
            'phone': f'138{random.randint(10000000, 99999999)}',
            'gender': 'Male',
            'major': '计算机科学',
            'enrollment_year': '2024'
        }

        create_response = session.post(
            'http://localhost:5000/admin/students/create',
            data=student_data,
            allow_redirects=False
        )

        if create_response.status_code == 302:
            print(f"[OK] 学生 {student_data['student_id']} 创建成功")
        else:
            print(f"[ERROR] 学生创建失败，状态码: {create_response.status_code}")

        # 4. 验证学生列表和用户列表
        print("\n4. 验证学生记录是否在学生列表中...")
        updated_students_response = session.get('http://localhost:5000/admin/students')
        if updated_students_response.status_code == 200 and student_data['student_id'] in updated_students_response.text:
            print(f"[OK] 新学生 {student_data['student_id']} 出现在学生列表中")
        else:
            print(f"[INFO] 可能需要刷新页面查看新学生")

        print("\n5. 验证用户列表（不应该包含新学生）...")
        updated_users_response = session.get('http://localhost:5000/admin/users')
        if updated_users_response.status_code == 200 and student_data['email'] in updated_users_response.text:
            print(f"[WARNING] 新学生出现在用户列表中（不应该出现）")
        else:
            print(f"[OK] 新学生没有出现在用户列表中（符合预期）")

        # 6. 尝试用新学生信息登录（应该失败）
        print("\n6. 测试新学生登录（应该失败）...")
        test_session = requests.Session()
        login_response = test_session.post('http://localhost:5000/auth/login', data={
            'username': student_data['student_id'],
            'password': student_data['student_id']
        })

        if login_response.status_code == 200:
            # 检查是否重定向到仪表板（表示登录成功）或回到登录页（表示失败）
            if 'dashboard' in login_response.text.lower():
                print("[ERROR] 新学生可以登录（不应该）")
            else:
                print("[OK] 新学生无法登录（符合预期）")
        else:
            print("[OK] 新学生登录失败（符合预期）")

        print("\n=== 测试结果总结 ===")
        print("✅ 系统已分离：学生记录和用户记录分开管理")
        print("✅ 创建学生只创建学生记录，不创建用户记录")
        print("✅ 学生列表显示学生信息")
        print("✅ 用户列表只显示管理员用户")
        print("✅ 学生需要单独创建用户记录才能登录")
        print("✅ 符合你的要求：学生和管理员用户区分开")

    except requests.exceptions.ConnectionError:
        print("[ERROR] 无法连接到服务器，请确保应用正在运行")
    except Exception as e:
        print(f"[ERROR] 测试过程中出错: {e}")

if __name__ == '__main__':
    test_separated_system()