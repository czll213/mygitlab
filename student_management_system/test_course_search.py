#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试课程搜索功能
"""

import requests
import re
from datetime import datetime

def test_course_search():
    """测试课程搜索功能"""

    session = requests.Session()

    print("=== 开始测试课程搜索功能 ===")
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

            # 2. 获取课程列表页面（无搜索）
            print("\n2. 获取所有课程...")
            courses_response = session.get('http://localhost:5000/student/courses')
            print(f"课程页面状态码: {courses_response.status_code}")

            if courses_response.status_code == 200:
                print("[OK] 成功获取课程页面")

                # 提取所有课程名称
                course_names = re.findall(r'<h5 class="card-title">([^<]+)</h5>', courses_response.text)
                print(f"[INFO] 找到 {len(course_names)} 个课程:")
                for i, name in enumerate(course_names[:5], 1):
                    print(f"  {i}. {name}")

                if course_names:
                    # 3. 测试搜索功能
                    search_term = course_names[0][:3]  # 使用第一个课程的前3个字符
                    print(f"\n3. 测试搜索 '{search_term}'...")

                    search_response = session.get(f'http://localhost:5000/student/courses?search={search_term}')
                    print(f"搜索响应状态码: {search_response.status_code}")

                    if search_response.status_code == 200:
                        print("[OK] 搜索请求成功")

                        # 检查搜索结果
                        search_content = search_response.text

                        # 提取搜索结果中的课程名称
                        search_results = re.findall(r'<h5 class="card-title">([^<]+)</h5>', search_content)
                        print(f"[INFO] 搜索结果: {len(search_results)} 个课程")

                        for result in search_results:
                            print(f"  - {result}")
                            if search_term.lower() in result.lower():
                                print(f"    [OK] 包含搜索关键词")
                            else:
                                print(f"    [WARNING] 不包含搜索关键词")

                        # 检查是否显示搜索提示
                        if f'搜索 "{search_term}" 的结果' in search_content:
                            print("[OK] 搜索提示显示正确")

                    else:
                        print(f"[ERROR] 搜索请求失败: {search_response.status_code}")

                # 4. 测试不存在的课程
                print(f"\n4. 测试搜索不存在的课程 'XYZ123'...")
                not_found_response = session.get('http://localhost:5000/student/courses?search=XYZ123')
                print(f"搜索响应状态码: {not_found_response.status_code}")

                if not_found_response.status_code == 200:
                    if '未找到匹配的课程' in not_found_response.text:
                        print("[OK] 空结果提示显示正确")
                    else:
                        print("[WARNING] 空结果提示可能有问题")

                # 5. 测试中文搜索
                print(f"\n5. 测试中文搜索 '数学'...")
                math_response = session.get('http://localhost:5000/student/courses?search=数学')
                print(f"中文搜索响应状态码: {math_response.status_code}")

                if math_response.status_code == 200:
                    math_results = re.findall(r'<h5 class="card-title">([^<]+)</h5>', math_response.text)
                    print(f"[INFO] '数学' 搜索结果: {len(math_results)} 个课程")
                    for result in math_results:
                        print(f"  - {result}")

            else:
                print(f"[ERROR] 获取课程页面失败: {courses_response.status_code}")

        else:
            print(f"[ERROR] 登录失败: {login_response.status_code}")

    except requests.exceptions.ConnectionError:
        print("[ERROR] 无法连接到服务器，请确保应用正在运行")
    except Exception as e:
        print(f"[ERROR] 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_course_search()