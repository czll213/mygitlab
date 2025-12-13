#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试选课功能的脚本
"""

import os
import sys
from datetime import datetime, date

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import Student, Course, Enrollment
from app import db

def test_enrollment_creation():
    """测试选课创建"""
    app = create_app()

    with app.app_context():
        print("检查数据库中的学生和课程...")

        # 检查学生数量
        student_count = Student.query.count()
        print(f"当前学生数量: {student_count}")

        # 检查课程数量
        course_count = Course.query.count()
        print(f"当前课程数量: {course_count}")

        # 如果没有学生，创建一个测试学生
        if student_count == 0:
            print("创建测试学生...")
            test_student = Student(
                student_id='TEST001',
                first_name='测试',
                last_name='学生',
                email='test@student.edu',
                phone='123456789',
                gender='Male',
                major='计算机科学'
            )
            db.session.add(test_student)
            db.session.commit()
            print("测试学生创建成功")

        # 如果没有课程，创建一门测试课程
        if course_count == 0:
            print("创建测试课程...")
            test_course = Course(
                course_code='TEST101',
                course_name='测试课程',
                credits=3,
                instructor='测试教师'
            )
            db.session.add(test_course)
            db.session.commit()
            print("测试课程创建成功")

        # 获取第一个学生和课程
        student = Student.query.first()
        course = Course.query.first()

        print(f"\n测试学生: {student.student_id} - {student.first_name}{student.last_name}")
        print(f"测试课程: {course.course_code} - {course.course_name}")

        # 检查是否已经存在选课记录
        existing_enrollment = Enrollment.query.filter_by(
            student_id=student.id,
            course_id=course.id
        ).first()

        if existing_enrollment:
            print(f"选课记录已存在: {existing_enrollment}")
        else:
            # 创建选课记录
            print("\n创建测试选课记录...")
            test_enrollment = Enrollment(
                student_id=student.id,
                course_id=course.id,
                enrollment_date=date.today(),
                status='enrolled'
            )

            try:
                db.session.add(test_enrollment)
                db.session.commit()
                print("测试选课记录创建成功!")
                print(f"选课ID: {test_enrollment.id}")
                print(f"学生ID: {test_enrollment.student_id}")
                print(f"课程ID: {test_enrollment.course_id}")
                print(f"选课日期: {test_enrollment.enrollment_date}")
                print(f"状态: {test_enrollment.status}")
            except Exception as e:
                db.session.rollback()
                print(f"创建选课记录失败: {e}")

if __name__ == '__main__':
    test_enrollment_creation()