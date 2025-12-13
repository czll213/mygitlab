#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的数据库清理脚本
"""

from app import create_app, db
from sqlalchemy import text

def simple_cleanup():
    """清理有问题的用户数据"""

    app = create_app()
    with app.app_context():
        print("=== 数据库清理 ===")

        try:
            # 检查当前用户数量
            total = db.session.execute(text("SELECT COUNT(*) FROM users")).scalar()
            print(f"清理前用户数量: {total}")

            # 删除用户名以user开头的用户
            result = db.session.execute(text("DELETE FROM users WHERE username LIKE 'user%'"))
            deleted = result.rowcount
            print(f"删除了 {deleted} 个测试用户")

            # 提交更改
            db.session.commit()

            # 检查剩余用户数量
            remaining = db.session.execute(text("SELECT COUNT(*) FROM users")).scalar()
            print(f"清理后用户数量: {remaining}")

            # 列出剩余用户
            users = db.session.execute(text("SELECT id, username, role FROM users ORDER BY id")).fetchall()
            print("\n剩余用户:")
            for user in users:
                print(f"  ID: {user[0]}, 用户名: {user[1]}, 角色: {user[2]}")

            print("\n清理完成！")

        except Exception as e:
            print(f"清理失败: {e}")
            db.session.rollback()

if __name__ == '__main__':
    simple_cleanup()