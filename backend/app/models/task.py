# tasks 表 ORM 模型
# 字段：id, task_name, status, result, created_at
# 记录 Agent 后台任务的执行状态与结果


from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime

from app.database.connection import Base

# 创建任务表
# 用来记录系统执行的各种任务
class Task(Base):

    # 数据库表名
    __tablename__ = "tasks"


    # 任务编号
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

    project_id = Column(
        Integer,
        nullable=True,
        index=True
    )

    # 任务名称
    # 例如：解析论文、生成PPT
    task_name = Column(
        String(100),
        nullable=False
    )

    # 任务状态
    # 例如：pending、running、success、failed
    status = Column(
        String(50),
        default="pending"
    )

    # 任务执行结果
    # 保存AI生成内容或错误信息
    result = Column(
        Text,
        nullable=True
    )

    # 创建时间
    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
