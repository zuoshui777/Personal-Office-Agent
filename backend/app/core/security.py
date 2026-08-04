# 安全与认证模块（负责用户密码加密和登录身份验证功能）
# 提供 JWT Token 生成与验证、密码哈希（passlib + bcrypt）等功能

from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings


# 创建密码加密工具
# 使用bcrypt算法保存密码，不直接保存原密码
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# 加密用户密码
def hash_password(password: str) -> str:
    """
    把用户输入的密码转换成加密字符串
    参数:
        password: 用户原始密码
    返回:
        加密后的密码
    """
    return pwd_context.hash(password)

# 验证密码是否正确
def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    比较用户输入密码和数据库保存的密码

    返回:
        True  表示密码正确
        False 表示密码错误
    """

    return pwd_context.verify(
        plain_password,
        hashed_password
    )

# 创建登录令牌
def create_access_token(
    data: dict
) -> str:
    """
    创建用户登录凭证

    参数:
        data:
            用户信息，例如用户ID

    返回:
        JWT字符串
    """

    # 复制数据，避免修改原数据
    to_encode = data.copy()

    # 设置过期时间
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_EXPIRE_MINUTES
    )

    # 写入过期时间
    to_encode.update(
        {
            "exp": expire
        }
    )

    # 生成JWT
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt

# 解析登录令牌
def decode_access_token(
    token: str
):
    """
    检查用户登录凭证是否有效

    返回:
        用户信息
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[
            settings.JWT_ALGORITHM
        ]
    )