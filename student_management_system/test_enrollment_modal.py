#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试选课成功弹窗功能
"""

import requests
import json

def test_enrollment_api():
    """测试选课API是否正确返回成功响应"""

    # 先登录获取session
    session = requests.Session()

    # 登录数据
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }

    try:
        # 登录
        login_response = session.post('http://localhost:5000/auth/login', data=login_data)
        print(f"登录状态: {login_response.status_code}")

        if login_response.status_code == 200:
            # 获取课程列表
            courses_response = session.get('http://localhost:5000/student/courses')
            print(f"课程页面状态: {courses_response.status_code}")

            # 检查页面是否包含成功模态框的HTML
            if 'successModal' in courses_response.text:
                print("[OK] 成功模态框已添加到页面")
            else:
                print("[ERROR] 成功模态框未找到")

            if 'fas fa-check-circle' in courses_response.text:
                print("[OK] 成功图标已添加")
            else:
                print("[ERROR] 成功图标未找到")

            if 'enrollSpinner' in courses_response.text:
                print("[OK] 加载动画已添加")
            else:
                print("[ERROR] 加载动画未找到")

            print("\n检查JavaScript代码:")
            if 'successCourseName' in courses_response.text:
                print("[OK] 成功弹窗课程名称设置代码已添加")
            else:
                print("[ERROR] 成功弹窗课程名称设置代码未找到")

            if '$(\'#successModal\').modal(\'show\')' in courses_response.text:
                print("[OK] 显示成功弹窗的代码已添加")
            else:
                print("[ERROR] 显示成功弹窗的代码未找到")

        else:
            print("[ERROR] 登录失败")

    except requests.exceptions.ConnectionError:
        print("[ERROR] 无法连接到服务器，请确保应用正在运行")
    except Exception as e:
        print(f"[ERROR] 测试出错: {e}")

if __name__ == '__main__':
    print("开始测试选课成功弹窗功能...")
    test_enrollment_api()