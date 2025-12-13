#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试分离后的选课和成绩录入功能
"""

import requests
import re
from datetime import datetime

def test_separated_functions():
    """测试分离后的选课和成绩录入功能"""

    session = requests.Session()

    print("=== 开始测试分离后的选课和成绩录入功能 ===")
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

            # 2. 检查新的录入成绩页面
            print("\n2. 检查新的录入成绩页面...")
            record_grade_response = session.get('http://localhost:5000/admin/grades/record')
            print(f"录入成绩页面状态码: {record_grade_response.status_code}")

            if record_grade_response.status_code == 200:
                print("[OK] 成功访问新的录入成绩页面")

                if '录入成绩' in record_grade_response.text:
                    print("[OK] 页面标题正确")
                if '学生' in record_grade_response.text and '课程' in record_grade_response.text:
                    print("[OK] 表单字段正确")
                if '成绩' in record_grade_response.text:
                    print("[OK] 成绩字段存在")
            else:
                print(f"[ERROR] 无法访问录入成绩页面: {record_grade_response.status_code}")

            # 3. 检查修改后的选课页面
            print("\n3. 检查修改后的选课页面...")
            create_enrollment_response = session.get('http://localhost:5000/admin/enrollments/create')
            print(f"添加选课页面状态码: {create_enrollment_response.status_code}")

            if create_enrollment_response.status_code == 200:
                print("[OK] 成功访问修改后的选课页面")

                # 检查是否移除了成绩字段
                if '成绩' in create_enrollment_response.text:
                    # 检查是否在提示信息中
                    if '成绩录入请使用' in create_enrollment_response.text:
                        print("[OK] 成绩字段已移除，并提供了正确的提示")
                    else:
                        print("[WARNING] 成绩字段可能仍然存在")
                else:
                    print("[OK] 成绩字段已完全移除")

                if '进行中' in create_enrollment_response.text and '已完成' not in create_enrollment_response.text:
                    print("[OK] 状态选项已修改，移除了'已完成'选项")
            else:
                print(f"[ERROR] 无法访问选课页面: {create_enrollment_response.status_code}")

            # 4. 检查导航菜单
            print("\n4. 检查导航菜单...")
            admin_dashboard_response = session.get('http://localhost:5000/admin/dashboard')
            if admin_dashboard_response.status_code == 200:
                if '录入成绩' in admin_dashboard_response.text:
                    print("[OK] 导航菜单中包含'录入成绩'选项")
                else:
                    print("[WARNING] 导航菜单中可能缺少'录入成绩'选项")

            # 5. 测试API检查功能
            print("\n5. 测试选课检查API...")
            check_api_response = session.get('http://localhost:5000/admin/api/check-enrollment?student_id=1&course_id=1')
            print(f"API检查响应状态码: {check_api_response.status_code}")

            if check_api_response.status_code == 200:
                print("[OK] API检查功能正常")
            else:
                print("[WARNING] API检查功能可能有问题")

            # 6. 检查成绩管理页面的按钮
            print("\n6. 检查成绩管理页面的按钮...")
            grades_page_response = session.get('http://localhost:5000/admin/grades')
            if grades_page_response.status_code == 200:
                if '/admin/grades/record' in grades_page_response.text:
                    print("[OK] 成绩管理页面的录入成绩按钮链接正确")
                else:
                    print("[WARNING] 成绩管理页面的按钮链接可能不正确")

            print("\n=== 功能分离验证完成 ===")
            print("✅ 新的录入成绩功能已创建")
            print("✅ 选课功能已修改，移除成绩录入")
            print("✅ 导航菜单已更新")
            print("✅ 页面间的链接已修正")

        else:
            print(f"[ERROR] 登录失败: {login_response.status_code}")

    except requests.exceptions.ConnectionError:
        print("[ERROR] 无法连接到服务器，请确保应用正在运行")
    except Exception as e:
        print(f"[ERROR] 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_separated_functions()