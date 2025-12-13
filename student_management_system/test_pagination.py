#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试所有列表页面的分页功能
"""

import requests
import re
from datetime import datetime

def test_pagination_pages():
    """测试所有列表页面的分页功能"""

    session = requests.Session()

    print("=== 分页功能测试 ===")
    print(f"时间: {datetime.now()}")

    # 要测试的页面列表
    pages_to_test = [
        {
            'name': '学生列表',
            'url': '/admin/students',
            'login_data': {'username': 'admin', 'password': 'admin123'}
        },
        {
            'name': '课程列表',
            'url': '/admin/courses',
            'login_data': {'username': 'admin', 'password': 'admin123'}
        },
        {
            'name': '选课列表',
            'url': '/admin/enrollments',
            'login_data': {'username': 'admin', 'password': 'admin123'}
        },
        {
            'name': '成绩列表',
            'url': '/admin/grades',
            'login_data': {'username': 'admin', 'password': 'admin123'}
        },
        {
            'name': '用户列表',
            'url': '/admin/users',
            'login_data': {'username': 'admin', 'password': 'admin123'}
        },
        {
            'name': '学生成绩',
            'url': '/student/grades',
            'login_data': {'username': 'wangwu', 'password': 'student123'}
        },
        {
            'name': '学生选课',
            'url': '/student/enrollments',
            'login_data': {'username': 'wangwu', 'password': 'student123'}
        }
    ]

    results = []

    for page_info in pages_to_test:
        print(f"\n{'='*50}")
        print(f"测试页面: {page_info['name']}")
        print(f"URL: {page_info['url']}")

        try:
            # 登录
            login_response = session.post('http://localhost:5000/auth/login',
                                        data=page_info['login_data'],
                                        allow_redirects=False)

            if login_response.status_code not in [200, 302]:
                print(f"[ERROR] 登录失败: {login_response.status_code}")
                results.append({
                    'page': page_info['name'],
                    'status': 'failed',
                    'reason': '登录失败'
                })
                continue

            # 访问页面
            page_response = session.get(f'http://localhost:5000{page_info["url"]}',
                                       allow_redirects=False)

            if page_response.status_code == 302:
                print(f"[REDIRECT] 被重定向到: {page_response.headers.get('Location', '未知')}")
                results.append({
                    'page': page_info['name'],
                    'status': 'redirected',
                    'reason': '页面重定向'
                })
                continue

            if page_response.status_code != 200:
                print(f"[ERROR] 页面访问失败: {page_response.status_code}")
                results.append({
                    'page': page_info['name'],
                    'status': 'failed',
                    'reason': f'HTTP {page_response.status_code}'
                })
                continue

            content = page_response.text

            # 检查分页功能
            has_pagination = 'pagination' in content
            has_page_nav = 'page-link' in content or 'page-item' in content

            print(f"[INFO] 页面访问成功")
            print(f"[INFO] 包含分页: {'是' if has_pagination else '否'}")
            print(f"[INFO] 包含分页导航: {'是' if has_page_nav else '否'}")

            # 查找分页相关的文本
            if '共' in content and '条记录' in content:
                print(f"[OK] 找到分页统计信息")
                # 尝试提取记录数量
                record_match = re.search(r'共\s*(\d+)\s*条记录', content)
                if record_match:
                    record_count = record_match.group(1)
                    print(f"[INFO] 总记录数: {record_count}")
            else:
                print(f"[INFO] 未找到分页统计信息")

            # 检查是否有数据表格
            has_table = 'table' in content
            has_data = has_table and ('<td>' in content or '<th>' in content)

            if has_data:
                print(f"[OK] 页面包含数据表格")
            else:
                print(f"[INFO] 页面暂无数据")

            # 检查是否需要分页（数据是否超过一页）
            if has_pagination:
                if 'page-link' in content:
                    page_links = re.findall(r'<[^>]*page-link[^>]*>(\d+)</[^>]*>', content)
                    if len(page_links) > 1:
                        print(f"[OK] 分页功能正常，找到 {len(page_links)} 个页码")
                    else:
                        print(f"[INFO] 数据量较少，未显示多页")
                else:
                    print(f"[INFO] 分页组件存在但可能未激活")
            else:
                print(f"[INFO] 该页面可能不需要分页")

            results.append({
                'page': page_info['name'],
                'status': 'success' if (has_pagination or not has_data) else 'needs_pagination',
                'has_pagination': has_pagination,
                'has_data': has_data,
                'details': f"分页: {'是' if has_pagination else '否'}, 数据: {'是' if has_data else '否'}"
            })

        except requests.exceptions.ConnectionError:
            print(f"[ERROR] 无法连接到服务器")
            results.append({
                'page': page_info['name'],
                'status': 'failed',
                'reason': '连接失败'
            })
        except Exception as e:
            print(f"[ERROR] 测试过程中出错: {e}")
            results.append({
                'page': page_info['name'],
                'status': 'failed',
                'reason': str(e)
            })

    # 输出总结
    print(f"\n{'='*60}")
    print("分页功能测试总结:")
    print(f"{'='*60}")

    success_count = 0
    need_pagination_count = 0
    failed_count = 0

    for result in results:
        status_icon = ""
        if result['status'] == 'success':
            status_icon = "✅"
            success_count += 1
        elif result['status'] == 'needs_pagination':
            status_icon = "⚠️"
            need_pagination_count += 1
        else:
            status_icon = "❌"
            failed_count += 1

        print(f"{status_icon} {result['page']:<15} - {result.get('details', result.get('reason', '未知状态'))}")

    print(f"\n统计:")
    print(f"  成功: {success_count}")
    print(f"  需要分页: {need_pagination_count}")
    print(f"  失败: {failed_count}")
    print(f"  总计: {len(results)}")

    if need_pagination_count == 0 and failed_count == 0:
        print(f"\n🎉 所有页面分页功能正常！")
    elif failed_count == 0:
        print(f"\n✅ 主要功能正常，{need_pagination_count}个页面可能需要优化分页")
    else:
        print(f"\n⚠️ 有 {failed_count} 个页面需要修复")

if __name__ == '__main__':
    test_pagination_pages()