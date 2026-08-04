# memories 表 ORM 模型
# 字段：id, key, value, source
# 存储用户长期记忆（专业、项目经历、偏好等键值对）


from sqlalchemy import Column, Integer, String, Text

from app.database.connection import Base

# 创建记忆表
# 用来保存AI需要长期记住的信息
class Memory(Base):

    # 数据库表名
    __tablename__ = "memories"

    # 记忆编号
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        nullable=False,
        index=True
    )

    # 记忆名称
    # 例如：技术栈、项目经验
    key = Column(
        String(100),
        nullable=False
    )

    # 记忆内容
    # 保存具体信息
    value = Column(
        Text,
        nullable=False
    )

    # 信息来源
    # 例如：用户输入、文件分析
    source = Column(
        String(100),
        nullable=True
    )
