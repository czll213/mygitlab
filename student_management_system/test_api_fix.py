#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的学生课程API
"""

import requests
import json

def test_student_courses_api():
    """测试学生课程API是否正常工作"""

    session = requests.Session()

    print("=== 测试学生课程API修复 ===")

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

            # 2. 测试学生课程API
            print("\n2. 测试学生课程API...")

            # 测试学生ID为1的课程
            api_response = session.get('http://localhost:5000/admin/api/student-courses/1')
            print(f"API响应状态码: {api_response.status_code}")

            if api_response.status_code == 200:
                try:
                    data = api_response.json()
                    courses = data.get('courses', [])
                    print(f"[OK] API调用成功！找到 {len(courses)} 门课程")

                    # 显示前3门课程信息
                    if courses:
                        print("\n课程信息预览:")
                        for i, course in enumerate(courses[:3], 1):
                            print(f"  课程 {i}:")
                            print(f"    - ID: {course.get('id')}")
                            print(f"    - 代码: {course.get('course_code')}")
                            print(f"    - 名称: {course.get('course_name')}")
                            print(f"    - 已有成绩: {'是' if course.get('has_grade') else '否'}")
                            if course.get('has_grade'):
                                print(f"    - 成绩: {course.get('grade')}")
                        print("\n[SUCCESS] API修复成功，参数传递正常！")
                    else:
                        print("[INFO] 该学生暂无选课记录")

                except json.JSONDecodeError as e:
                    print(f"[ERROR] JSON解析失败: {e}")
                    print(f"响应内容: {api_response.text[:200]}...")

            elif api_response.status_code == 500:
                print(f"[ERROR] 服务器内部错误，参数修复可能未完全生效")
                print(f"响应内容: {api_response.text[:200]}...")

            else:
                print(f"[ERROR] API调用失败，状态码: {api_response.status_code}")
                print(f"响应内容: {api_response.text[:200]}...")

        else:
            print(f"[ERROR] 登录失败，状态码: {login_response.status_code}")

    except requests.exceptions.ConnectionError:
        print("[ERROR] 无法连接到服务器，请确保应用正在运行")
    except Exception as e:
        print(f"[ERROR] 测试过程中出错: {e}")

if __name__ == '__main__':
    test_student_courses_api()