# 检查用户登录状态，获取当前登录用户

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.models.project import Project
from app.core.security import decode_access_token


# 定义Token获取方式
# 前端登录后会把Token放在请求头
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)

# 获取当前登录用户
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    # 解析Token
    payload = decode_access_token(token)


    # 获取用户ID
    user_id = payload.get(
        "user_id"
    )

    # Token无效
    if user_id is None:
        raise HTTPException(
            status_code=401,
            detail="登录状态无效"
        )

    # 根据ID查询用户
    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    # 用户不存在
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="用户不存在"
        )

    return user


def get_user_project_or_404(
    db: Session,
    current_user: User,
    project_id: int
):
    """校验项目属于当前用户，并返回项目对象。"""

    project = (
        db.query(Project)
        .filter(
            Project.id == project_id,
            Project.user_id == current_user.id
        )
        .first()
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="项目不存在"
        )

    return project


def resolve_project_id(
    db: Session,
    current_user: User,
    project_id: int | None
):
    """解析当前项目，未传时默认使用用户第一个项目。"""

    if project_id is not None:
        return get_user_project_or_404(
            db,
            current_user,
            project_id
        ).id

    project = (
        db.query(Project)
        .filter(Project.user_id == current_user.id)
        .order_by(Project.id.asc())
        .first()
    )

    return project.id if project else None
