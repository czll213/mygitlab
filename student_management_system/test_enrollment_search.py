#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试选课记录搜索功能
"""

import requests
import re
from datetime import datetime

def test_enrollment_search():
    """测试选课记录搜索功能"""

    session = requests.Session()

    print("=== 开始测试选课记录搜索功能 ===")
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

            # 2. 获取选课记录页面（无搜索）
            print("\n2. 获取所有选课记录...")
            enrollments_response = session.get('http://localhost:5000/student/enrollments')
            print(f"选课页面状态码: {enrollments_response.status_code}")

            if enrollments_response.status_code == 200:
                print("[OK] 成功获取选课记录页面")

                # 提取所有选课记录的课程信息
                course_codes = re.findall(r'<strong>([^<]+)</strong>', enrollments_response.text)
                course_names = re.findall(r'<td>([^<]+)</td>', enrollments_response.text)

                # 过滤出课程名称
                filtered_course_names = []
                for name in course_names:
                    if any(code in name for code in course_codes) or len(name) > 5:
                        filtered_course_names.append(name)

                print(f"[INFO] 找到 {len(course_codes)} 个选课记录:")
                for i, code in enumerate(course_codes[:5], 1):
                    print(f"  {i}. 课程代码: {code}")

                if course_codes:
                    # 3. 测试课程代码搜索
                    search_code = course_codes[0][:3] if course_codes else 'MATH'
                    print(f"\n3. 测试搜索课程代码 '{search_code}'...")

                    search_response = session.get(f'http://localhost:5000/student/enrollments?search={search_code}')
                    print(f"搜索响应状态码: {search_response.status_code}")

                    if search_response.status_code == 200:
                        print("[OK] 课程代码搜索成功")

                        # 检查搜索结果
                        search_content = search_response.text
                        if search_code in search_content:
                            print("[OK] 搜索结果包含匹配的课程代码")
                        else:
                            print("[WARNING] 搜索结果可能不包含匹配内容")

                    # 4. 测试状态筛选
                    print(f"\n4. 测试状态筛选 'completed'...")
                    status_response = session.get('http://localhost:5000/student/enrollments?status=completed')
                    print(f"状态筛选响应状态码: {status_response.status_code}")

                    if status_response.status_code == 200:
                        print("[OK] 状态筛选成功")
                        if '已完成' in status_response.text:
                            print("[OK] 筛选结果显示已完成课程")
                        else:
                            print("[INFO] 当前没有已完成的课程")

                    # 5. 测试组合搜索（关键词 + 状态）
                    print(f"\n5. 测试组合搜索...")
                    if course_codes:
                        combined_search = f'http://localhost:5000/student/enrollments?search={search_code}&status=enrolled'
                        combined_response = session.get(combined_search)
                        print(f"组合搜索响应状态码: {combined_response.status_code}")

                        if combined_response.status_code == 200:
                            print("[OK] 组合搜索成功")

                    # 6. 测试无结果搜索
                    print(f"\n6. 测试无结果搜索 'XYZ999'...")
                    not_found_response = session.get('http://localhost:5000/student/enrollments?search=XYZ999')
                    print(f"无结果搜索状态码: {not_found_response.status_code}")

                    if not_found_response.status_code == 200:
                        if '未找到匹配的选课记录' in not_found_response.text:
                            print("[OK] 无结果提示显示正确")
                        else:
                            print("[WARNING] 无结果提示可能未显示")

            else:
                print(f"[ERROR] 获取选课记录页面失败: {enrollments_response.status_code}")

        else:
            print(f"[ERROR] 登录失败: {login_response.status_code}")

    except requests.exceptions.ConnectionError:
        print("[ERROR] 无法连接到服务器，请确保应用正在运行")
    except Exception as e:
        print(f"[ERROR] 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_enrollment_search()