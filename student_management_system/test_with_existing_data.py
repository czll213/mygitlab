#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试已有数据的学生课程API
"""

import requests
import json

def test_with_existing_data():
    """测试已有学生的课程数据"""

    session = requests.Session()

    print("=== 测试已有数据的API ===")

    try:
        # 1. 登录管理员账户
        print("\n1. 登录管理员账户...")
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }

        login_response = session.post('http://localhost:5000/auth/login', data=login_data)

        if login_response.status_code == 200:
            print("[OK] 登录成功")

            # 2. 获取学生列表
            print("\n2. 获取学生列表...")
            students_response = session.get('http://localhost:5000/admin/students')

            if students_response.status_code == 200:
                # 简单查找学生ID
                import re
                student_ids = re.findall(r'value="(\d+)"[^>]*>.*?学生', students_response.text)

                if student_ids:
                    print(f"[INFO] 找到学生ID: {student_ids[:5]}")  # 显示前5个

                    # 3. 测试每个学生的课程API
                    for student_id in student_ids[:3]:  # 测试前3个学生
                        print(f"\n3. 测试学生 {student_id} 的课程API...")

                        api_response = session.get(f'http://localhost:5000/admin/api/student-courses/{student_id}')
                        print(f"学生 {student_id} API响应状态码: {api_response.status_code}")

                        if api_response.status_code == 200:
                            try:
                                data = api_response.json()
                                courses = data.get('courses', [])
                                print(f"  [OK] 找到 {len(courses)} 门课程")

                                # 显示课程信息
                                if courses:
                                    for course in courses[:2]:  # 显示前2门课程
                                        print(f"    - {course.get('course_code')} - {course.get('course_name')}")
                                        print(f"      成绩状态: {'已录入' if course.get('has_grade') else '未录入'}")

                            except json.JSONDecodeError as e:
                                print(f"  [ERROR] JSON解析失败: {e}")
                        else:
                            print(f"  [ERROR] API调用失败: {api_response.status_code}")
                            if api_response.status_code == 500:
                                print("  [CRITICAL] 仍然存在服务器错误，修复未完全生效")

                else:
                    print("[INFO] 未找到学生数据")
            else:
                print(f"[ERROR] 获取学生列表失败: {students_response.status_code}")

        else:
            print(f"[ERROR] 登录失败: {login_response.status_code}")

    except Exception as e:
        print(f"[ERROR] 测试过程中出错: {e}")

if __name__ == '__main__':
    test_with_existing_data()