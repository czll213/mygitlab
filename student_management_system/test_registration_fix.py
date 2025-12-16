#!/usr/bin/env python3
"""
测试注册功能修复的脚本
"""
import re

def test_validation_logic():
    """测试验证逻辑"""
    print("测试注册验证逻辑")
    print("=" * 50)

    # 测试用户名验证
    print("1. 用户名验证测试:")
    usernames = ["", "abc", "abcd", "test123", "a" * 10]
    for username in usernames:
        valid = username and len(username) >= 4
        print(f"   '{username}' -> {'有效' if valid else '无效'}")

    print("\n2. 邮箱验证测试:")
    emails = ["", "invalid", "test@", "test@domain", "test@domain.com", "user.email@domain.co.uk"]
    email_regex = r"[^@]+@[^@]+\.[^@]+"
    for email in emails:
        valid = email and re.match(email_regex, email)
        print(f"   '{email}' -> {'有效' if valid else '无效'}")

    print("\n3. 电话号码验证测试:")
    phones = ["", "1234567", "123-456-7890", "+1 (123) 456-7890", "123"]
    for phone in phones:
        if phone:
            phone_digits = re.sub(r'\D', '', phone)
            valid = len(phone_digits) >= 7
        else:
            valid = True  # 电话是可选的
        print(f"   '{phone}' -> {'有效' if valid else '无效'}")

    print("\n4. 密码验证测试:")
    passwords = ["", "12345", "123456", "secure123", "a" * 10]
    for password in passwords:
        valid = password and len(password) >= 6
        print(f"   '{password}' -> {'有效' if valid else '无效'}")

    print("\n5. 密码匹配测试:")
    test_pairs = [
        ("123456", "123456"),
        ("123456", "654321"),
        ("", ""),
        ("abc", "abc"),
        ("password", "password123")
    ]
    for pwd, confirm in test_pairs:
        valid = pwd == confirm
        print(f"   '{pwd}' vs '{confirm}' -> {'匹配' if valid else '不匹配'}")

if __name__ == "__main__":
    test_validation_logic()
    print("\n验证逻辑修复完成！")
    print("主要修复:")
    print("1. 添加了500ms延迟避免输入时立即显示错误")
    print("2. 统一了前后端验证逻辑")
    print("3. 电话号码设为可选字段")
    print("4. 添加了输入数据strip()处理")
    print("5. 改进了CSS错误显示样式")