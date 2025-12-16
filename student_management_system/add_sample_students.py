#!/usr/bin/env python3
"""
添加学生测试数据脚本
"""
from app import create_app, db
from app.models import Student, User, Course, Enrollment
from datetime import datetime, date
import random

def create_sample_students():
    """创建示例学生数据"""

    # 示例学生数据
    sample_students = [
        {
            'student_id': '2021001',
            'first_name': '张',
            'last_name': '伟',
            'birth_date': date(2003, 5, 15),
            'gender': 'Male',
            'email': 'zhangwei@example.com',
            'phone': '13800138001',
            'address': '北京市朝阳区某某街道123号',
            'major': '计算机科学与技术',
            'enrollment_year': 2021
        },
        {
            'student_id': '2021002',
            'first_name': '李',
            'last_name': '娜',
            'birth_date': date(2003, 8, 22),
            'gender': 'Female',
            'email': 'lina@example.com',
            'phone': '13800138002',
            'address': '上海市浦东新区某某路456号',
            'major': '软件工程',
            'enrollment_year': 2021
        },
        {
            'student_id': '2021003',
            'first_name': '王',
            'last_name': '强',
            'birth_date': date(2002, 12, 10),
            'gender': 'Male',
            'email': 'wangqiang@example.com',
            'phone': '13800138003',
            'address': '广州市天河区某某大道789号',
            'major': '信息安全',
            'enrollment_year': 2021
        },
        {
            'student_id': '2022001',
            'first_name': '刘',
            'last_name': '芳',
            'birth_date': date(2004, 3, 8),
            'gender': 'Female',
            'email': 'liufang@example.com',
            'phone': '13800138004',
            'address': '深圳市南山区某某街321号',
            'major': '数据科学',
            'enrollment_year': 2022
        },
        {
            'student_id': '2022002',
            'first_name': '陈',
            'last_name': '杰',
            'birth_date': date(2004, 7, 19),
            'gender': 'Male',
            'email': 'chenjie@example.com',
            'phone': '13800138005',
            'address': '杭州市西湖区某某路654号',
            'major': '人工智能',
            'enrollment_year': 2022
        },
        {
            'student_id': '2022003',
            'first_name': '杨',
            'last_name': '静',
            'birth_date': date(2003, 11, 25),
            'gender': 'Female',
            'email': 'yangjing@example.com',
            'phone': '13800138006',
            'address': '成都市武侯区某某大道987号',
            'major': '计算机科学与技术',
            'enrollment_year': 2022
        },
        {
            'student_id': '2023001',
            'first_name': '赵',
            'last_name': '磊',
            'birth_date': date(2005, 2, 14),
            'gender': 'Male',
            'email': 'zhaolei@example.com',
            'phone': '13800138007',
            'address': '武汉市洪山区某某路147号',
            'major': '软件工程',
            'enrollment_year': 2023
        },
        {
            'student_id': '2023002',
            'first_name': '黄',
            'last_name': '婷',
            'birth_date': date(2005, 6, 30),
            'gender': 'Female',
            'email': 'huangting@example.com',
            'phone': '13800138008',
            'address': '西安市雁塔区某某大街258号',
            'major': '网络工程',
            'enrollment_year': 2023
        },
        {
            'student_id': '2023003',
            'first_name': '周',
            'last_name': '军',
            'birth_date': date(2004, 9, 5),
            'gender': 'Male',
            'email': 'zhoujun@example.com',
            'phone': '13800138009',
            'address': '南京市江宁区某某路369号',
            'major': '物联网工程',
            'enrollment_year': 2023
        },
        {
            'student_id': '2024001',
            'first_name': '吴',
            'last_name': '梅',
            'birth_date': date(2006, 1, 20),
            'gender': 'Female',
            'email': 'wumei@example.com',
            'phone': '13800138010',
            'address': '重庆市渝北区某某大道741号',
            'major': '数据科学',
            'enrollment_year': 2024
        }
    ]

    app = create_app()

    with app.app_context():
        # 检查是否已有学生数据
        existing_count = Student.query.count()
        print(f"当前数据库中有 {existing_count} 名学生")

        if existing_count > 0:
            print("数据库中已有学生数据，继续添加新学生...")

        # 添加学生数据
        added_count = 0
        for student_data in sample_students:
            # 检查学号是否已存在
            existing_student = Student.query.filter_by(student_id=student_data['student_id']).first()
            if existing_student:
                print(f"学号 {student_data['student_id']} 已存在，跳过")
                continue

            # 检查邮箱是否已存在
            existing_email = Student.query.filter_by(email=student_data['email']).first()
            if existing_email:
                print(f"邮箱 {student_data['email']} 已存在，跳过")
                continue

            # 创建学生记录
            student = Student(**student_data)
            db.session.add(student)
            added_count += 1
            print(f"添加学生: {student.full_name} ({student.student_id})")

        try:
            db.session.commit()
            print(f"\n成功添加 {added_count} 名学生！")

            # 显示统计信息
            total_count = Student.query.count()
            print(f"数据库中现有 {total_count} 名学生")

        except Exception as e:
            db.session.rollback()
            print(f"添加学生时出错: {e}")

if __name__ == '__main__':
    create_sample_students()