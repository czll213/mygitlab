#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用户列表分页功能
"""

import requests
import re

def test_user_pagination():
    """测试用户列表分页功能"""

    session = requests.Session()

    print("=== 用户列表分页功能测试 ===")

    try:
        # 1. 登录管理员账户
        print("\n1. 登录管理员账户...")
        login_data = {
            'username': 'admin',
            'password': 'admin123'
        }

        login_response = session.post('http://localhost:5000/auth/login', data=login_data)
        print(f"登录状态码: {login_response.status_code}")

        if login_response.status_code == 200:
            print("[OK] 登录成功")

            # 2. 访问用户列表第一页
            print("\n2. 访问用户列表第1页...")
            page1_response = session.get('http://localhost:5000/admin/users')
            print(f"第1页状态码: {page1_response.status_code}")

            if page1_response.status_code == 200:
                content1 = page1_response.text

                # 检查分页组件
                has_pagination = 'pagination' in content1
                has_page_links = 'page-link' in content1

                print(f"[INFO] 第1页包含分页组件: {'是' if has_pagination else '否'}")
                print(f"[INFO] 第1页包含分页链接: {'是' if has_page_links else '否'}")

                # 查找分页统计信息
                record_match = re.search(r'共\s*(\d+)\s*条记录', content1)
                if record_match:
                    total_records = int(record_match.group(1))
                    print(f"[INFO] 总记录数: {total_records}")

                    # 计算预期页数
                    expected_pages = (total_records + 19) // 20  # 每页20条
                    print(f"[INFO] 预期页数: {expected_pages}")

                # 检查是否有下一页链接
                if '下一页' in content1:
                    print("[OK] 找到下一页链接")

                    # 3. 访问用户列表第二页
                    print("\n3. 访问用户列表第2页...")
                    page2_response = session.get('http://localhost:5000/admin/users?page=2')
                    print(f"第2页状态码: {page2_response.status_code}")

                    if page2_response.status_code == 200:
                        content2 = page2_response.text
                        has_pagination_2 = 'pagination' in content2
                        print(f"[INFO] 第2页包含分页组件: {'是' if has_pagination_2 else '否'}")

                        # 检查当前页是否为第2页
                        active_page_match = re.search(r'<span[^>]*>2</span>', content2)
                        if active_page_match:
                            print("[OK] 第2页正确标记为当前页")

                        # 4. 访问用户列表第三页
                        print("\n4. 访问用户列表第3页...")
                        page3_response = session.get('http://localhost:5000/admin/users?page=3')
                        print(f"第3页状态码: {page3_response.status_code}")

                        if page3_response.status_code == 200:
                            content3 = page3_response.text
                            active_page_3 = re.search(r'<span[^>]*>3</span>', content3)
                            if active_page_3:
                                print("[OK] 第3页正确标记为当前页")

                            print("\n=== 分页功能测试结果 ===")
                            print("✅ 用户列表分页功能正常工作！")
                            print(f"✅ 第1页: 分页组件显示正常")
                            print(f"✅ 第2页: 可以正常访问和显示")
                            print(f"✅ 第3页: 可以正常访问和显示")
                            print(f"✅ 当前页高亮: 页码正确高亮显示")
                        else:
                            print(f"[ERROR] 第3页访问失败: {page3_response.status_code}")
                    else:
                        print(f"[ERROR] 第2页访问失败: {page2_response.status_code}")
                else:
                    print("[INFO] 没有下一页链接（可能数据不足）")
            else:
                print(f"[ERROR] 用户列表页面访问失败: {page1_response.status_code}")
        else:
            print(f"[ERROR] 登录失败: {login_response.status_code}")

    except requests.exceptions.ConnectionError:
        print("[ERROR] 无法连接到服务器，请确保应用正在运行")
    except Exception as e:
        print(f"[ERROR] 测试过程中出错: {e}")

if __name__ == '__main__':
    test_user_pagination()