# 数据库初始化脚本
# 运行 SQLAlchemy 基类的元数据创建所有表
# 可选：插入默认管理员用户与种子数据
# 这个文件用来创建数据库表，让项目第一次运行时自动初始化数据库

# from app.models import *
from sqlalchemy import text

from app.database.connection import Base, engine

# 导入所有数据表模型
# 如果不导入，SQLAlchemy不知道有哪些表需要创建
from app.models.user import User
from app.models.project import Project
from app.models.document import Document
from app.models.task import Task
from app.models.memory import Memory
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.models.notification import Notification


def ensure_missing_columns():
    """为已存在的表补充后续新增的列。"""

    with engine.begin() as conn:
        conn.execute(
            text(
                "ALTER TABLE chat_sessions "
                "ADD COLUMN IF NOT EXISTS project_id INTEGER"
            )
        )
        conn.execute(
            text(
                "ALTER TABLE tasks "
                "ADD COLUMN IF NOT EXISTS user_id INTEGER"
            )
        )
        conn.execute(
            text(
                "ALTER TABLE tasks "
                "ADD COLUMN IF NOT EXISTS project_id INTEGER"
            )
        )
        conn.execute(
            text(
                "ALTER TABLE memories "
                "ADD COLUMN IF NOT EXISTS user_id INTEGER"
            )
        )

# 创建所有数据表
def init_database():
    """
    根据定义好的模型创建数据库表

    如果表已经存在，不会重复创建
    """

    Base.metadata.create_all(
        bind=engine
    )

    ensure_missing_columns()

    print("数据库初始化完成")
    print("已创建数据表:")
    print("- users")
    print("- projects")
    print("- documents")
    print("- tasks")
    print("- memories")
    print("- chat_sessions")
    print("- chat_messages")
    print("- notifications")

# 直接运行此文件时执行初始化
if __name__ == "__main__":

    init_database()
