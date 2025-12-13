#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试退课功能
"""

import requests
import json
from datetime import datetime

def test_drop_course():
    """测试退课功能"""

    session = requests.Session()

    print("=== 开始测试退课功能 ===")
    print(f"时间: {datetime.now()}")

    try:
        # 1. 登录学生账户
        print("\n1. 登录学生账户...")
        login_data = {
            'username': 'wangwu',
            'password': '123456'
        }

        login_response = session.post('http://localhost:5000/auth/login', data=login_data)
        print(f"登录响应状态码: {login_response.status_code}")

        if login_response.status_code == 200:
            print("[OK] 登录成功")

            # 2. 获取选课记录页面
            print("\n2. 获取选课记录页面...")
            enrollments_response = session.get('http://localhost:5000/student/enrollments')
            print(f"选课页面状态码: {enrollments_response.status_code}")

            if enrollments_response.status_code == 200:
                print("[OK] 成功获取选课页面")

                # 3. 查找已选课程
                if 'drop-course' in enrollments_response.text:
                    print("[OK] 找到退课按钮")

                    # 提取课程ID
                    import re
                    course_ids = re.findall(r'data-course-id="(\d+)"', enrollments_response.text)
                    enrollment_ids = re.findall(r'data-enrollment-id="(\d+)"', enrollments_response.text)
                    course_names = re.findall(r'data-course-name="([^"]+)"', enrollments_response.text)

                    if course_ids and enrollment_ids:
                        course_id = course_ids[0]
                        enrollment_id = enrollment_ids[0]
                        course_name = course_names[0] if course_names else "未知课程"

                        print(f"[OK] 找到可退课程:")
                        print(f"  - 课程ID: {course_id}")
                        print(f"  - 选课ID: {enrollment_id}")
                        print(f"  - 课程名: {course_name}")

                        # 4. 执行退课请求
                        print(f"\n3. 执行退课请求 (课程ID: {course_id})...")
                        drop_response = session.post(
                            f'http://localhost:5000/student/courses/{course_id}/drop',
                            headers={
                                'X-Requested-With': 'XMLHttpRequest',
                                'Content-Type': 'application/json'
                            }
                        )

                        print(f"退课响应状态码: {drop_response.status_code}")
                        print(f"退课响应头: {dict(drop_response.headers)}")

                        try:
                            response_json = drop_response.json()
                            print(f"退课响应JSON: {json.dumps(response_json, ensure_ascii=False, indent=2)}")

                            if 'success' in response_json:
                                if response_json['success']:
                                    print("[SUCCESS] 退课成功")
                                else:
                                    print(f"[ERROR] 退课失败: {response_json.get('message', '未知错误')}")
                            else:
                                print("[WARNING] 响应中没有success字段")

                        except ValueError as e:
                            print(f"[ERROR] 响应不是有效的JSON: {e}")
                            print(f"响应内容: {drop_response.text[:500]}...")

                    else:
                        print("[ERROR] 没有找到可退的课程")
                else:
                    print("[ERROR] 没有找到退课按钮")
            else:
                print(f"[ERROR] 获取选课页面失败: {enrollments_response.status_code}")
        else:
            print(f"[ERROR] 登录失败: {login_response.status_code}")

    except requests.exceptions.ConnectionError:
        print("[ERROR] 无法连接到服务器，请确保应用正在运行")
    except Exception as e:
        print(f"[ERROR] 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_drop_course()