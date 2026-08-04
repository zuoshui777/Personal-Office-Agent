# 数据库连接管理（创建数据库连接，让程序可以操作数据库）
# 创建 SQLAlchemy 异步引擎与 Session 工厂
# 提供 get_db 依赖注入函数供路由层使用

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

# 创建数据库连接地址
# 格式：
# 数据库类型://用户名:密码@地址:端口/数据库名
DATABASE_URL = (
    f"postgresql://"
    f"{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@"
    f"{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/"
    f"{settings.POSTGRES_DB}"
)

# 创建数据库连接对象
engine = create_engine(
    DATABASE_URL,
    # 开发阶段开启日志，方便查看SQL执行情况
    echo=True
)

# 创建数据库操作对象
# 后续每次操作数据库都会通过它
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 创建数据表的基础类
# 后面的用户表、文件表都会继承它
Base = declarative_base()

# 提供数据库连接
# API接口需要数据库时调用这个函数
def get_db():
    """
    获取数据库连接

    使用完成后自动关闭连接
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()