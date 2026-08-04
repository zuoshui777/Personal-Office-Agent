# users 表 ORM 模型
# 字段：id, username, password_hash, role, created_at
# 存储用户账户信息与角色（admin / user）例如用户名和密码信息

from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from app.database.connection import Base

# 创建用户表
# 后续登录功能会使用这个表保存用户信息
class User(Base):

    # 数据库表名
    __tablename__ = "users"

    # 用户编号
    # 主键，自动增加
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # 用户名
    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    # 加密后的密码
    # 不保存用户原密码
    password_hash = Column(
        String(255),
        nullable=False
    )

    # 用户身份
    # 例如：user、admin
    role = Column(
        String(20),
        default="user"
    )

    # 创建时间
    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )