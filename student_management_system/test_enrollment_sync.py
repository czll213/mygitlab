#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试选课信息同步问题
"""

import requests
import json
from datetime import datetime

def test_enrollment_sync():
    """测试选课后的信息同步"""

    session = requests.Session()

    print("=== 选课信息同步测试 ===")
    print(f"时间: {datetime.now()}")

    try:
        # 1. 登录学生账户
        print("\n1. 登录学生账户...")
        login_data = {
            'username': 'wangwu',  # 使用实际存在的学生账号
            'password': 'student123'
        }

        login_response = session.post('http://localhost:5000/auth/login', data=login_data)
        print(f"登录响应状态码: {login_response.status_code}")

        if login_response.status_code == 200:
            print("[OK] 学生登录成功")

            # 2. 获取初始选课状态
            print("\n2. 获取初始选课状态...")
            courses_response = session.get('http://localhost:5000/student/courses')
            print(f"课程页面状态码: {courses_response.status_code}")

            if courses_response.status_code == 200:
                content = courses_response.text

                # 检查是否有"已选课程"部分
                if '已选课程' in content:
                    print("[INFO] 页面包含已选课程部分")
                    # 简单统计已选课程数量
                    enrolled_count = content.count('已选课</span>')
                    print(f"[INFO] 当前已选课程数量: {enrolled_count}")
                else:
                    print("[WARNING] 页面未显示已选课程部分")

                # 3. 执行选课操作
                print("\n3. 执行选课操作...")

                # 寻找可选课程的ID
                import re
                course_ids = re.findall(r'enroll-course-(\d+)', content)
                if course_ids:
                    course_id = course_ids[0]
                    print(f"[INFO] 尝试选修课程ID: {course_id}")

                    enroll_response = session.post(
                        f'http://localhost:5000/student/courses/{course_id}/enroll',
                        headers={'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json'}
                    )
                    print(f"选课API状态码: {enroll_response.status_code}")

                    if enroll_response.status_code == 200:
                        try:
                            response_data = enroll_response.json()
                            print(f"[OK] 选课API响应: {response_data}")

                            if response_data.get('success'):
                                print("[SUCCESS] 选课操作成功")

                                # 4. 立即检查选课页面是否同步
                                print("\n4. 检查选课页面同步状态...")

                                # 等待一秒模拟页面刷新
                                import time
                                time.sleep(1)

                                updated_courses_response = session.get('http://localhost:5000/student/courses')
                                if updated_courses_response.status_code == 200:
                                    updated_content = updated_courses_response.text
                                    updated_enrolled_count = updated_content.count('已选课</span>')
                                    print(f"[INFO] 选课后页面显示的已选课程数量: {updated_enrolled_count}")

                                    if updated_enrolled_count > enrolled_count:
                                        print("[SUCCESS] 选课信息已同步到页面")
                                    else:
                                        print("[ISSUE] 选课信息未同步到页面")
                                else:
                                    print(f"[ERROR] 获取更新后的选课页面失败: {updated_courses_response.status_code}")

                            else:
                                print(f"[ERROR] 选课失败: {response_data.get('message')}")

                        except json.JSONDecodeError as e:
                            print(f"[ERROR] 解析选课API响应失败: {e}")
                            print(f"原始响应: {enroll_response.text}")
                    else:
                        print(f"[ERROR] 选课API调用失败: {enroll_response.status_code}")
                        print(f"错误信息: {enroll_response.text}")

                else:
                    print("[INFO] 未找到可选的课程")

            else:
                print(f"[ERROR] 获取课程页面失败: {courses_response.status_code}")

        else:
            print(f"[ERROR] 学生登录失败: {login_response.status_code}")

    except requests.exceptions.ConnectionError:
        print("[ERROR] 无法连接到服务器，请确保应用正在运行")
    except Exception as e:
        print(f"[ERROR] 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_enrollment_sync()