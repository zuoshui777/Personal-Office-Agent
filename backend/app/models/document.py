# user_documents 表 ORM 模型
# 字段：id, project_id, file_name, file_path, file_type, created_at
# 记录用户上传的每个文件的基本元信息，例如文件名称和保存位置

from datetime import datetime

from sqlalchemy import Column, Integer, String, Text,DateTime, ForeignKey

from app.database.connection import Base

# 创建文件表
# 用来保存用户上传的文档信息
class Document(Base):

    # 数据库表名
    __tablename__ = "documents"

    # 文件编号
    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # 所属项目编号
    # 一个项目可以包含多个文件
    project_id = Column(
        Integer,
        ForeignKey("projects.id"),
        nullable=False
    )

    # 文件名称
    # 例如：论文.pdf
    file_name = Column(
        String(255),
        nullable=False
    )

    # 文件保存路径
    file_path = Column(
        String(500),
        nullable=False
    )

    # 文件类型
    # 例如：pdf、docx、txt
    file_type = Column(
        String(50),
        nullable=True
    )
    # 保存解析后的文本内容
    content = Column(
        Text,
        nullable=True
    )

    # 创建时间
    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
