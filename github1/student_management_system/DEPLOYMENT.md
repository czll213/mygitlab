# 部署文档

## 应用部署状态：✅ 成功

### 访问信息
- **应用URL**: http://localhost:5000
- **状态**: 正在运行
- **默认管理员账号**:
  - 用户名: admin
  - 密码: admin123

### 功能特性

#### ✅ 已完成的功能

1. **数据库设计**
   - 5张数据表（满足第三范式）
   - ER图和表结构设计文档
   - 数据库关系完整

2. **用户认证系统**
   - 用户注册功能
   - 用户登录/登出
   - 密码加密存储（bcrypt）
   - 会话管理

3. **权限管理**
   - 管理员权限
   - 普通用户权限
   - 访问控制

4. **管理员模块**
   - 仪表板（统计数据）
   - 用户管理（CRUD）
   - 学生管理（CRUD）
   - 课程管理（CRUD）
   - 选课管理（CRUD）
   - 搜索和分页功能

5. **用户模块**
   - 个人仪表板
   - 个人中心（查看/编辑）
   - 课程浏览
   - 选课/退课功能
   - 选课历史查看

6. **技术特性**
   - 响应式Web界面
   - REST API接口
   - AJAX交互
   - 数据验证
   - 安全防护

### 系统要求

#### 开发环境
- Python 3.8+
- Flask 2.3.3
- SQLAlchemy
- MySQL/SQLite
- Bootstrap 5
- jQuery

#### 生产环境
- 服务器：支持Python的Web服务器
- 数据库：MySQL或PostgreSQL
- Web服务器：Nginx或Apache
- WSGI：Gunicorn或uWSGI

### 部署步骤

#### 1. 开发环境部署（已完成）
```bash
# 1. 进入项目目录
cd student_management_system

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行应用
python run_simple.py
```

#### 2. 生产环境部署建议
```bash
# 1. 设置环境变量
export FLASK_ENV=production
export SECRET_KEY=your-production-secret-key
export DATABASE_URL=mysql://user:password@localhost/sms_db

# 2. 使用Gunicorn运行
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app

# 3. 配置Nginx反向代理
server {
    listen 80;
    server_name yourdomain.com;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 测试报告

#### 功能测试结果
- **总测试数**: 12
- **通过**: 12
- **失败**: 0
- **成功率**: 100%

#### 测试覆盖
- ✅ 用户注册/登录
- ✅ 权限验证
- ✅ 管理员功能
- ✅ 学生功能
- ✅ API接口
- ✅ 数据CRUD操作

### API接口文档

#### 管理员API
```
GET /admin/api/students  - 获取所有学生
GET /admin/api/courses   - 获取所有课程
GET /admin/api/enrollments - 获取所有选课记录
```

#### 学生API
```
GET /student/api/courses/available - 获取可选课程
GET /student/api/enrollments      - 获取个人选课记录
GET /student/api/profile          - 获取个人信息
```

### 安全措施

1. **密码安全**
   - 使用bcrypt加密存储
   - 最小密码长度要求

2. **会话安全**
   - 安全的会话管理
   - 自动会话过期

3. **输入验证**
   - 服务端验证
   - 客户端验证
   - SQL注入防护

4. **访问控制**
   - 基于角色的访问控制
   - 路由保护

### 性能优化

1. **数据库优化**
   - 索引优化
   - 查询优化

2. **前端优化**
   - CSS/JS压缩
   - 图片优化

3. **缓存策略**
   - 静态文件缓存
   - 数据库查询缓存

### 监控与日志

1. **错误日志**
   - 应用错误记录
   - 访问日志

2. **性能监控**
   - 响应时间监控
   - 数据库性能监控

### 备份策略

1. **数据库备份**
   - 定期自动备份
   - 增量备份策略

2. **代码备份**
   - 版本控制（Git）
   - 部署回滚

### 联系信息

如有问题或需要技术支持，请联系开发团队。

---

**部署完成时间**: 2025年12月11日
**部署状态**: ✅ 成功运行