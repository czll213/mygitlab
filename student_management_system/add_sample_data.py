#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加示例数据的脚本
"""

import os
import sys
from datetime import datetime, date

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import User, Student, Course, Enrollment, Administrator
from app import db
from flask_bcrypt import Bcrypt

def create_sample_data():
    """创建示例数据"""
    app = create_app()

    with app.app_context():
        bcrypt = Bcrypt(app)

        print("开始添加示例数据...")

        # 1. 添加示例学生
        print("\n1. 添加示例学生...")

        sample_students = [
            {
                'student_id': '2024001',
                'email': 'zhangsan@university.edu',
                'first_name': '张',
                'last_name': '三',
                'phone': '13800138001',
                'gender': 'Male',
                'major': '计算机科学与技术',
                'enrollment_year': 2024,
                'address': '北京市海淀区'
            },
            {
                'student_id': '2024002',
                'email': 'lisi@university.edu',
                'first_name': '李',
                'last_name': '四',
                'phone': '13800138002',
                'gender': 'Female',
                'major': '计算机科学与技术',
                'enrollment_year': 2024,
                'enrollment_date': date(2024, 9, 1),
                'address': '上海市浦东新区'
            },
            {
                'student_id': '2024003',
                'username': 'wangwu',
                'email': 'wangwu@university.edu',
                'password': '123456',
                'first_name': '王',
                'last_name': '五',
                'phone': '13800138003',
                'gender': 'Male',
                'major': '软件工程',
                'enrollment_year': 2024,
                'enrollment_date': date(2024, 9, 1),
                'address': '广州市天河区'
            },
            {
                'student_id': '2023001',
                'email': 'zhaoliu@university.edu',
                'first_name': '赵',
                'last_name': '六',
                'phone': '13800138004',
                'gender': 'Female',
                'major': '软件工程',
                'enrollment_year': 2023,
                'address': '深圳市南山区'
            },
            {
                'student_id': '2023002',
                'email': 'qianqi@university.edu',
                'first_name': '钱',
                'last_name': '七',
                'phone': '13800138005',
                'gender': 'Male',
                'major': '数据科学',
                'enrollment_year': 2023,
                'address': '成都市高新区'
            }
        ]

        created_students = []
        for student_data in sample_students:
            # 检查学生是否已存在
            existing_student = Student.query.filter_by(student_id=student_data['student_id']).first()
            if existing_student:
                print(f"学生 {student_data['student_id']} 已存在，跳过...")
                continue

            # 创建对应的用户账号
            username = student_data.get('username', student_data['student_id'])
            password = student_data.get('password', '123456')

            user = User(
                username=username,
                email=student_data['email'],
                full_name=f"{student_data['first_name']}{student_data['last_name']}",
                phone=student_data['phone'],
                role='student'
            )
            user.set_password(password)

            # 创建学生（Student模型和User模型是独立的）
            student = Student(
                student_id=student_data['student_id'],
                first_name=student_data['first_name'],
                last_name=student_data['last_name'],
                email=student_data['email'],
                phone=student_data['phone'],
                gender=student_data['gender'],
                major=student_data['major'],
                enrollment_year=student_data['enrollment_year'],
                address=student_data['address']
            )

            db.session.add(user)
            db.session.add(student)
            created_students.append(student)
            print(f"已创建学生: {student_data['student_id']} - {student_data['first_name']}{student_data['last_name']}")

        db.session.commit()
        print(f"成功添加 {len(created_students)} 个学生")

        # 2. 添加示例课程
        print("\n2. 添加示例课程...")

        sample_courses = [
            {
                'course_code': 'CS101',
                'name': '计算机科学导论',
                'credits': 3,
                'description': '本课程介绍计算机科学的基本概念、原理和方法，包括计算机组成、操作系统基础、程序设计思想等内容。',
                'instructor': '张教授',
                'classroom': '教学楼A301',
                'schedule': '周一、三 14:00-15:30',
                'semester': '2024-秋季',
                'max_students': 60,
                'is_active': True
            },
            {
                'course_code': 'CS201',
                'name': '数据结构与算法',
                'credits': 4,
                'description': '本课程系统介绍常用的数据结构和算法设计技术，包括线性表、树、图、排序算法、搜索算法等。',
                'instructor': '李教授',
                'classroom': '教学楼B201',
                'schedule': '周二、四 10:00-11:30',
                'semester': '2024-秋季',
                'max_students': 50,
                'is_active': True
            },
            {
                'course_code': 'CS202',
                'name': '数据库系统',
                'credits': 3,
                'description': '本课程介绍数据库系统的基本原理和设计方法，包括关系模型、SQL语言、事务管理、并发控制等内容。',
                'instructor': '王教授',
                'classroom': '教学楼C401',
                'schedule': '周三、五 8:00-9:30',
                'semester': '2024-秋季',
                'max_students': 45,
                'is_active': True
            },
            {
                'course_code': 'CS301',
                'name': '软件工程',
                'credits': 3,
                'description': '本课程介绍软件工程的原理和方法，包括软件生命周期、需求分析、系统设计、软件测试、项目管理等内容。',
                'instructor': '赵教授',
                'classroom': '教学楼D301',
                'schedule': '周一、四 16:00-17:30',
                'semester': '2024-秋季',
                'max_students': 40,
                'is_active': True
            },
            {
                'course_code': 'CS302',
                'name': '人工智能导论',
                'credits': 3,
                'description': '本课程介绍人工智能的基本概念和方法，包括搜索策略、知识表示、机器学习、自然语言处理等内容。',
                'instructor': '陈教授',
                'classroom': '教学楼E201',
                'schedule': '周二、五 14:00-15:30',
                'semester': '2024-秋季',
                'max_students': 55,
                'is_active': True
            },
            {
                'course_code': 'MATH101',
                'name': '高等数学',
                'credits': 4,
                'description': '本课程包括极限理论、微积分学、级数理论等内容，是理工科学生的重要基础课程。',
                'instructor': '刘教授',
                'classroom': '理科楼101',
                'schedule': '周一、三、五 10:00-11:00',
                'semester': '2024-秋季',
                'max_students': 80,
                'is_active': True
            },
            {
                'course_code': 'CS401',
                'name': '计算机网络',
                'credits': 3,
                'description': '本课程介绍计算机网络的基本原理和协议，包括网络体系结构、TCP/IP协议、网络安全等内容。',
                'instructor': '孙教授',
                'classroom': '教学楼F301',
                'schedule': '周三、五 16:00-17:30',
                'semester': '2024-秋季',
                'max_students': 45,
                'is_active': True
            },
            {
                'course_code': 'CS402',
                'name': '操作系统',
                'credits': 4,
                'description': '本课程介绍操作系统的设计和实现，包括进程管理、内存管理、文件系统、设备管理等内容。',
                'instructor': '周教授',
                'classroom': '教学楼G201',
                'schedule': '周二、四 14:00-15:30',
                'semester': '2024-秋季',
                'max_students': 50,
                'is_active': True
            }
        ]

        created_courses = []
        for course_data in sample_courses:
            # 检查课程是否已存在
            existing_course = Course.query.filter_by(course_code=course_data['course_code']).first()
            if existing_course:
                print(f"课程 {course_data['course_code']} 已存在，跳过...")
                continue

            course = Course(
                course_code=course_data['course_code'],
                course_name=course_data['name'],
                credits=course_data['credits'],
                description=course_data['description'],
                instructor=course_data['instructor'],
                department=course_data.get('department', '计算机科学与技术系')
            )

            db.session.add(course)
            created_courses.append(course)
            print(f"已创建课程: {course_data['course_code']} - {course_data['name']}")

        db.session.commit()
        print(f"成功添加 {len(created_courses)} 门课程")

        # 3. 添加示例选课记录
        print("\n3. 添加示例选课记录...")

        # 获取刚创建的学生和课程
        all_students = Student.query.all()
        all_courses = Course.query.all()

        sample_enrollments = []
        enrollment_date = date(2024, 9, 15)

        # 为每个学生随机选择3-5门课程
        import random
        random.seed(42)  # 固定随机种子，确保结果可重现

        for student in all_students:
            # 随机选择3-5门课程
            selected_courses = random.sample(all_courses, random.randint(3, 5))

            for course in selected_courses:
                # 检查是否已经选过这门课
                existing_enrollment = Enrollment.query.filter_by(
                    student_id=student.id,
                    course_id=course.id
                ).first()

                if existing_enrollment:
                    continue

                # 随机设置状态和成绩
                status = random.choice(['enrolled', 'completed', 'completed', 'completed'])  # 75%概率已完成
                grade = None
                if status == 'completed':
                    grade = random.randint(60, 100)  # 随机生成60-100的成绩

                enrollment = Enrollment(
                    student=student,
                    course=course,
                    enrollment_date=enrollment_date,
                    status=status,
                    grade=grade
                )

                db.session.add(enrollment)
                sample_enrollments.append(enrollment)
                print(f"已创建选课: {student.student_id} -> {course.course_code} (状态: {status}, 成绩: {grade if grade else '未录入'})")

        db.session.commit()
        print(f"成功添加 {len(sample_enrollments)} 条选课记录")

        print("\n=== 示例数据添加完成 ===")
        print(f"总计: {len(created_students)} 个学生, {len(created_courses)} 门课程, {len(sample_enrollments)} 条选课记录")
        print("\n学生账号信息:")
        for student_data in sample_students:
            print(f"  学号: {student_data['student_id']}, 姓名: {student_data['first_name']}{student_data['last_name']}")
        print("\n管理员账号: admin, 密码: admin123")

if __name__ == '__main__':
    create_sample_data()