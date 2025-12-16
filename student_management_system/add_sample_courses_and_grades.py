#!/usr/bin/env python3
"""
添加课程和选课成绩数据脚本
"""
from app import create_app, db
from app.models import Student, Course, Enrollment
from datetime import datetime, date
import random

def create_sample_courses():
    """创建示例课程数据"""

    sample_courses = [
        {
            'course_code': 'CS101',
            'course_name': '计算机科学导论',
            'description': '计算机科学基础概念和编程入门',
            'credits': 3,
            'department': '计算机科学系',
            'instructor': '张教授'
        },
        {
            'course_code': 'CS201',
            'course_name': '数据结构与算法',
            'description': '常用数据结构和算法设计与分析',
            'credits': 4,
            'department': '计算机科学系',
            'instructor': '李教授'
        },
        {
            'course_code': 'CS202',
            'course_name': '面向对象程序设计',
            'description': '面向对象编程思想和实践',
            'credits': 3,
            'department': '计算机科学系',
            'instructor': '王副教授'
        },
        {
            'course_code': 'CS301',
            'course_name': '数据库系统',
            'description': '数据库设计、实现和管理',
            'credits': 4,
            'department': '计算机科学系',
            'instructor': '陈教授'
        },
        {
            'course_code': 'CS302',
            'course_name': '操作系统',
            'description': '操作系统原理和设计',
            'credits': 4,
            'department': '计算机科学系',
            'instructor': '刘教授'
        },
        {
            'course_code': 'CS303',
            'course_name': '计算机网络',
            'description': '计算机网络原理和应用',
            'credits': 3,
            'department': '计算机科学系',
            'instructor': '赵副教授'
        },
        {
            'course_code': 'CS401',
            'course_name': '软件工程',
            'description': '软件开发方法和项目管理',
            'credits': 3,
            'department': '软件工程系',
            'instructor': '黄教授'
        },
        {
            'course_code': 'CS402',
            'course_name': '人工智能导论',
            'description': '人工智能基础概念和应用',
            'credits': 3,
            'department': '人工智能系',
            'instructor': '周教授'
        },
        {
            'course_code': 'CS403',
            'course_name': '机器学习',
            'description': '机器学习算法和实践',
            'credits': 4,
            'department': '人工智能系',
            'instructor': '吴教授'
        },
        {
            'course_code': 'MATH101',
            'course_name': '高等数学',
            'description': '微积分和数学分析基础',
            'credits': 4,
            'department': '数学系',
            'instructor': '郑教授'
        },
        {
            'course_code': 'MATH201',
            'course_name': '离散数学',
            'description': '离散数学基础理论',
            'credits': 3,
            'department': '数学系',
            'instructor': '孙副教授'
        },
        {
            'course_code': 'MATH202',
            'course_name': '概率论与数理统计',
            'description': '概率统计理论和应用',
            'credits': 3,
            'department': '数学系',
            'instructor': '钱教授'
        },
        {
            'course_code': 'ENG101',
            'course_name': '大学英语',
            'description': '英语听说读写训练',
            'credits': 2,
            'department': '外语系',
            'instructor': '杨老师'
        },
        {
            'course_code': 'PHY101',
            'course_name': '大学物理',
            'description': '物理学基础理论',
            'credits': 3,
            'department': '物理系',
            'instructor': '徐教授'
        }
    ]

    app = create_app()

    with app.app_context():
        # 检查是否已有课程数据
        existing_count = Course.query.count()
        print(f"当前数据库中有 {existing_count} 门课程")

        added_count = 0
        for course_data in sample_courses:
            # 检查课程代码是否已存在
            existing_course = Course.query.filter_by(course_code=course_data['course_code']).first()
            if existing_course:
                print(f"课程代码 {course_data['course_code']} 已存在，跳过")
                continue

            # 创建课程记录
            course = Course(**course_data)
            db.session.add(course)
            added_count += 1
            print(f"添加课程: {course.course_name} ({course.course_code})")

        try:
            db.session.commit()
            print(f"\n成功添加 {added_count} 门课程！")
        except Exception as e:
            db.session.rollback()
            print(f"添加课程时出错: {e}")

def create_sample_enrollments_and_grades():
    """为学生创建选课记录和成绩"""

    app = create_app()

    with app.app_context():
        # 获取所有学生和课程
        students = Student.query.all()
        courses = Course.query.all()

        if not students:
            print("没有找到学生数据，请先添加学生")
            return

        if not courses:
            print("没有找到课程数据，请先添加课程")
            return

        print(f"找到 {len(students)} 名学生和 {len(courses)} 门课程")

        # 为每个学生随机选择几门课程并生成成绩
        enrollment_count = 0
        grade_count = 0

        for student in students:
            # 根据学生入学年份决定可选课程
            available_courses = []

            # 基础课程，所有学生都可以选
            basic_courses = ['CS101', 'MATH101', 'ENG101', 'PHY101']
            for course in courses:
                if course.course_code in basic_courses:
                    available_courses.append(course)

            # 根据入学年份添加更多课程
            if student.enrollment_year <= 2021:  # 高年级学生
                advanced_courses = ['CS201', 'CS202', 'CS301', 'CS302', 'CS303', 'CS401', 'CS402', 'CS403', 'MATH201', 'MATH202']
                for course in courses:
                    if course.course_code in advanced_courses:
                        available_courses.append(course)
            elif student.enrollment_year == 2022:  # 中年级学生
                intermediate_courses = ['CS201', 'CS202', 'MATH201']
                for course in courses:
                    if course.course_code in intermediate_courses:
                        available_courses.append(course)

            # 随机选择4-8门课程
            num_courses = random.randint(4, min(8, len(available_courses)))
            selected_courses = random.sample(available_courses, num_courses)

            for course in selected_courses:
                # 检查是否已存在选课记录
                existing_enrollment = Enrollment.query.filter_by(
                    student_id=student.id,
                    course_id=course.id
                ).first()

                if existing_enrollment:
                    continue

                # 创建选课记录
                enrollment = Enrollment(
                    student_id=student.id,
                    course_id=course.id,
                    enrollment_date=date(2024, 9, 1)  # 假设都是2024年9月1日选课
                )

                # 随机决定课程状态和成绩
                status_options = ['enrolled', 'completed']
                weights = [0.3, 0.7]  # 30%在修，70%已完成

                status = random.choices(status_options, weights=weights)[0]
                enrollment.status = status

                # 如果已完成，生成成绩
                if status == 'completed':
                    # 生成正态分布的成绩（平均75分，标准差10分）
                    grade = max(60, min(100, random.gauss(75, 10)))
                    enrollment.grade = round(grade, 1)
                    grade_count += 1

                db.session.add(enrollment)
                enrollment_count += 1
                print(f"学生 {student.full_name} 选修了 {course.course_name} (状态: {status}, 成绩: {enrollment.grade if enrollment.grade else '未出分'})")

        try:
            db.session.commit()
            print(f"\n成功创建 {enrollment_count} 条选课记录，其中 {grade_count} 条已有成绩！")

            # 显示统计信息
            total_enrollments = Enrollment.query.count()
            completed_enrollments = Enrollment.query.filter_by(status='completed').count()
            enrolled_enrollments = Enrollment.query.filter_by(status='enrolled').count()

            print(f"\n数据库统计:")
            print(f"- 总选课记录: {total_enrollments}")
            print(f"- 已完成课程: {completed_enrollments}")
            print(f"- 在修课程: {enrolled_enrollments}")

        except Exception as e:
            db.session.rollback()
            print(f"添加选课记录时出错: {e}")

if __name__ == '__main__':
    print("=== 步骤1: 创建课程数据 ===")
    create_sample_courses()

    print("\n=== 步骤2: 创建选课和成绩数据 ===")
    create_sample_enrollments_and_grades()