# 实现用户注册和登录功能

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from fastapi.responses import JSONResponse
from app.database.connection import get_db
from app.models.user import User
from app.models.project import Project
from app.schemas.user import UserRegister, UserLogin, UserResponse

# 用于接收Swagger登录表单
from fastapi.security import OAuth2PasswordRequestForm

# 导入密码处理和Token生成功能
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

from app.core.dependencies import get_current_user


# 创建用户接口路由
router = APIRouter(
    prefix="/auth",
    tags=["用户认证"]
)

# 用户注册接口
@router.post("/register", response_model=UserResponse)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):

    # 查询用户名是否已经存在
    existing_user = (
        db.query(User)
        .filter(User.username == user_data.username)
        .first()
    )

    # 如果存在，返回错误
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="用户名已经存在"
        )

    # 创建新用户
    new_user = User(
        username=user_data.username,

        # 密码不能直接保存
        # 保存加密后的密码
        password_hash=hash_password(
            user_data.password
        ),

        role="user"
    )

    # 保存到数据库
    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    db.add(
        Project(
            user_id=new_user.id,
            project_name="默认项目",
            description="默认个人知识库"
        )
    )
    db.commit()

    return new_user


# 获取当前登录用户信息
@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user

# 用户登录接口
@router.post("/login")
def login(
    # 接收Swagger用户名密码
    form_data: OAuth2PasswordRequestForm = Depends(),

    # 获取数据库
    db: Session = Depends(get_db)
):
    # 根据用户名查询用户
    user = (
        db.query(User)
        .filter(User.username == form_data.username)
        .first()
    )

    # 用户不存在
    if not user:
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误"
        )

    # 检查密码是否正确
    if not verify_password(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误"
        )

    # 创建登录Token
    token = create_access_token(
        {
            "user_id": user.id,
            "username": user.username
        }
    )

    # 返回登录结果
    return {
        "access_token": token,
        "token_type": "bearer"
    }
