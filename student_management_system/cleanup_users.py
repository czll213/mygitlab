#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理有问题的用户数据
"""

from app import create_app, db
from sqlalchemy import text

def cleanup_users():
    """通过SQL直接删除有问题的用户数据"""

    app = create_app()
    with app.app_context():
        print("=== 清理有问题的用户数据 ===")

        try:
            # 使用原始SQL删除有问题的用户
            # 先删除所有测试用户（用户名以user开头的）
            sql = text("DELETE FROM users WHERE username LIKE 'user%'")
            result = db.session.execute(sql)
            deleted_count = result.rowcount
            print(f"通过SQL删除了 {deleted_count} 个测试用户")

            db.session.commit()

            # 检查剩余用户数量
            remaining_users = db.session.execute("SELECT COUNT(*) FROM users").scalar()
            print(f"剩余用户数量: {remaining_users}")

            # 检查是否有无效的角色值
            invalid_roles = db.session.execute(
                "SELECT COUNT(*) FROM users WHERE role NOT IN ('admin', 'student')"
            ).scalar()

            if invalid_roles > 0:
                print(f"发现 {invalid_roles} 个用户有无效的角色值")
                # 删除无效角色的用户
                result = db.session.execute(
                    "DELETE FROM users WHERE role NOT IN ('admin', 'student')"
                )
                deleted_invalid = result.rowcount
                print(f"删除了 {deleted_invalid} 个无效角色的用户")
                db.session.commit()

            # 最终检查
            final_users = db.session.execute("SELECT COUNT(*) FROM users").scalar()
            print(f"最终用户数量: {final_users}")

            # 列出所有剩余用户
            users = db.session.execute(
                "SELECT id, username, full_name, role FROM users ORDER BY id"
            ).fetchall()

            print("\n剩余用户列表:")
            for user in users:
                print(f"  ID: {user[0]}, 用户名: {user[1]}, 姓名: {user[2]}, 角色: {user[3]}")

            print("\n数据库清理完成！")

        except Exception as e:
            print(f"清理过程中出错: {e}")
            db.session.rollback()

if __name__ == '__main__':
    cleanup_users()