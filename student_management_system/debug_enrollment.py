#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试选课功能的详细脚本
"""

import requests
import json
from datetime import datetime

def debug_enrollment():
    """详细调试选课功能"""

    session = requests.Session()

    print("=== 开始调试选课功能 ===")
    print(f"时间: {datetime.now()}")

    try:
        # 1. 登录
        print("\n1. 尝试登录...")
        # 使用学生账户登录
        login_data = {
            'username': 'wangwu',
            'password': '123456'
        }

        login_response = session.post('http://localhost:5000/auth/login', data=login_data)
        print(f"登录响应状态码: {login_response.status_code}")

        if login_response.status_code == 200:
            print("[OK] 登录成功")

            # 2. 获取课程页面
            print("\n2. 获取课程页面...")
            courses_response = session.get('http://localhost:5000/student/courses')
            print(f"课程页面状态码: {courses_response.status_code}")

            if courses_response.status_code == 200:
                print("[OK] 成功获取课程页面")

                # 3. 检查是否有可用的课程
                if 'enroll-course' in courses_response.text:
                    print("[OK] 找到选课按钮")

                    # 尝试提取课程ID
                    import re
                    course_ids = re.findall(r'data-course-id="(\d+)"', courses_response.text)
                    if course_ids:
                        course_id = course_ids[0]
                        print(f"[OK] 找到课程ID: {course_id}")

                        # 4. 执行选课请求
                        print(f"\n4. 执行选课请求 (课程ID: {course_id})...")
                        enroll_response = session.post(
                            f'http://localhost:5000/student/courses/{course_id}/enroll',
                            headers={
                                'X-Requested-With': 'XMLHttpRequest',  # 模拟AJAX请求
                                'Content-Type': 'application/json'      # 设置JSON内容类型
                            }
                        )

                        print(f"选课响应状态码: {enroll_response.status_code}")
                        print(f"选课响应头: {dict(enroll_response.headers)}")

                        try:
                            response_json = enroll_response.json()
                            print(f"选课响应JSON: {json.dumps(response_json, ensure_ascii=False, indent=2)}")

                            # 分析响应
                            if 'success' in response_json:
                                if response_json['success']:
                                    print("[SUCCESS] 选课成功")
                                else:
                                    print(f"[ERROR] 选课失败: {response_json.get('message', '未知错误')}")
                            else:
                                print("[WARNING] 响应中没有success字段")

                        except ValueError as e:
                            print(f"[ERROR] 响应不是有效的JSON: {e}")
                            print(f"响应内容: {enroll_response.text[:500]}...")

                    else:
                        print("[ERROR] 没有找到课程ID")
                else:
                    print("[ERROR] 没有找到选课按钮")

            elif courses_response.status_code == 302:
                print("[WARNING] 重定向响应，可能是权限问题")
                location = courses_response.headers.get('Location', '')
                print(f"重定向到: {location}")
            else:
                print(f"[ERROR] 获取课程页面失败: {courses_response.status_code}")

        else:
            print(f"[ERROR] 登录失败: {login_response.status_code}")
            print(f"登录响应: {login_response.text[:200]}...")

    except requests.exceptions.ConnectionError:
        print("[ERROR] 无法连接到服务器，请确保应用正在运行")
    except Exception as e:
        print(f"[ERROR] 调试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_enrollment()