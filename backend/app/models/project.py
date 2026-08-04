# projects 表 ORM 模型
# 字段：id, project_name, description
# 用于对知识库文件进行项目归档与分类，例如项目名称和项目介绍

from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)

from app.database.connection import Base

# 创建项目表
# 用来保存用户管理的不同项目
class Project(Base):

    # 数据库表名
    __tablename__ = "projects"

    # 项目编号
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # 所属用户ID
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # 项目名称
    # 例如：毕业设计、AI助手项目
    project_name = Column(
        String(100),
        nullable=False
    )

    # 项目描述
    description = Column(
        Text,
        nullable=True
    )

    # 创建时间
    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )