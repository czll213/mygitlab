#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试成绩录入和显示问题
"""

import requests
import re
from datetime import datetime

def test_grade_issue():
    """测试成绩录入和显示问题"""

    session = requests.Session()

    print("=== 开始测试成绩录入和显示问题 ===")
    print(f"时间: {datetime.now()}")

    try:
        # 1. 登录管理员账户
        print("\n1. 登录管理员账户...")
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }

        login_response = session.post('http://localhost:5000/auth/login', data=login_data)
        print(f"登录响应状态码: {login_response.status_code}")

        if login_response.status_code == 200:
            print("[OK] 登录成功")

            # 2. 获取成绩管理页面
            print("\n2. 获取成绩管理页面...")
            grades_response = session.get('http://localhost:5000/admin/grades')
            print(f"成绩页面状态码: {grades_response.status_code}")

            if grades_response.status_code == 200:
                print("[OK] 成功获取成绩管理页面")

                # 检查当前的成绩记录数量
                content = grades_response.text
                if '总成绩记录' in content:
                    total_records = re.search(r'<h3 class="mb-0">(\d+)</h3>', content)
                    if total_records:
                        total_count = total_records.group(1)
                        print(f"[INFO] 当前总成绩记录数: {total_count}")
                    else:
                        print("[WARNING] 无法解析总成绩记录数")

                # 检查是否有成绩记录
                if '暂无成绩记录' in content:
                    print("[INFO] 当前暂无成绩记录")
                elif 'table' in content:
                    print("[INFO] 找到成绩表格")

                # 3. 获取选课管理页面
                print("\n3. 检查选课记录...")
                enrollments_response = session.get('http://localhost:5000/admin/enrollments')
                print(f"选课页面状态码: {enrollments_response.status_code}")

                if enrollments_response.status_code == 200:
                    print("[OK] 成功获取选课管理页面")

                    # 检查选课记录的状态分布
                    enroll_content = enrollments_response.text

                    # 统计不同状态的选课记录
                    enrolled_count = enroll_content.count('进行中')
                    completed_count = enroll_content.count('已完成')
                    dropped_count = enroll_content.count('已退课')

                    print(f"[INFO] 选课记录状态统计:")
                    print(f"  - 进行中: {enrolled_count}")
                    print(f"  - 已完成: {completed_count}")
                    print(f"  - 已退课: {dropped_count}")

                    # 检查是否有成绩的记录
                    grade_entries = re.findall(r'<span class="badge bg-info">([^<]+)</span>', enroll_content)
                    if grade_entries:
                        print(f"[INFO] 找到 {len(grade_entries)} 个有成绩的记录:")
                        for grade in grade_entries[:5]:
                            print(f"  - 成绩: {grade}")

                    # 4. 测试创建带成绩的选课记录
                    print("\n4. 测试创建带成绩的选课记录...")

                    # 先获取学生和课程信息
                    students_response = session.get('http://localhost:5000/admin/create_enrollment')
                    if students_response.status_code == 200:
                        # 提取学生ID和课程ID
                        student_ids = re.findall(r'value="(\d+)"[^>]*>.*?学生', students_response.text)
                        course_ids = re.findall(r'value="(\d+)"[^>]*>.*?课程', students_response.text)

                        if student_ids and course_ids:
                            student_id = student_ids[0] if student_ids else "1"
                            course_id = course_ids[1] if len(course_ids) > 1 else "1"

                            print(f"[INFO] 使用学生ID: {student_id}, 课程ID: {course_id}")

                            # 创建测试数据
                            test_data = {
                                'student_id': student_id,
                                'course_id': course_id,
                                'grade': '85.5',
                                'status': 'enrolled',
                                'enrollment_date': '2024-09-01'
                            }

                            create_response = session.post('http://localhost:5000/admin/enrollments/create', data=test_data)
                            print(f"创建选课记录状态码: {create_response.status_code}")

                            if create_response.status_code == 302:
                                print("[OK] 成功创建带成绩的选课记录")

                                # 5. 再次检查成绩页面
                                print("\n5. 检查新增成绩是否出现在成绩列表...")
                                grades_check_response = session.get('http://localhost:5000/admin/grades')

                                if '85.5' in grades_check_response.text:
                                    print("[OK] 新成绩出现在成绩列表中")
                                else:
                                    print("[ERROR] 新成绩未出现在成绩列表中")

                                    # 检查是否有筛选问题
                                    if '已完成' not in grades_check_response.text and '进行中' in grades_check_response.text:
                                        print("[INFO] 可能是因为状态筛选问题")
                                        print("[建议] 尝试将状态筛选改为'所有状态'或'已完成'")

                            else:
                                print(f"[ERROR] 创建选课记录失败: {create_response.status_code}")

            else:
                print(f"[ERROR] 获取成绩管理页面失败: {grades_response.status_code}")

        else:
            print(f"[ERROR] 登录失败: {login_response.status_code}")

    except requests.exceptions.ConnectionError:
        print("[ERROR] 无法连接到服务器，请确保应用正在运行")
    except Exception as e:
        print(f"[ERROR] 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_grade_issue()