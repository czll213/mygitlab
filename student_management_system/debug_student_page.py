#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试学生选课页面
"""

import requests

def debug_student_page():
    """调试学生选课页面的实际内容"""

    session = requests.Session()

    try:
        # 登录学生账户
        login_data = {
            'username': 'wangwu',
            'password': 'student123'
        }

        login_response = session.post('http://localhost:5000/auth/login', data=login_data)

        if login_response.status_code == 200:
            print("登录成功")

            # 获取课程页面
            courses_response = session.get('http://localhost:5000/student/courses')

            if courses_response.status_code == 200:
                content = courses_response.text

                # 保存页面内容到文件以便检查
                with open('student_courses_debug.html', 'w', encoding='utf-8') as f:
                    f.write(content)

                print("页面内容已保存到 student_courses_debug.html")

                # 检查关键元素
                print("\n=== 页面内容分析 ===")

                if '已选课程' in content:
                    print("[OK] 页面包含'已选课程'文本")
                else:
                    print("[MISSING] 页面不包含'已选课程'文本")

                if '可选课程' in content:
                    print("[OK] 页面包含'可选课程'文本")
                else:
                    print("[MISSING] 页面不包含'可选课程'文本")

                # 检查课程卡片
                import re
                course_cards = re.findall(r'<div class="card[^"]*"[^>]*>.*?<h6[^>]*>([^<]+)</h6>', content, re.DOTALL)
                print(f"\n找到课程卡片数量: {len(course_cards)}")

                for i, card in enumerate(course_cards[:5], 1):
                    print(f"  课程 {i}: {card.strip()}")

                # 检查是否有选课按钮
                enroll_buttons = re.findall(r'enroll-course-\d+', content)
                print(f"\n找到选课按钮数量: {len(enroll_buttons)}")

                # 检查是否包含JavaScript错误
                if 'console.error' in content or 'error' in content.lower():
                    print("[WARNING] 页面可能包含JavaScript错误")

            else:
                print(f"获取课程页面失败: {courses_response.status_code}")
        else:
            print(f"登录失败: {login_response.status_code}")

    except Exception as e:
        print(f"调试过程中出错: {e}")

if __name__ == '__main__':
    debug_student_page()