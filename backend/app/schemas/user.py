# 义用户注册和登录需要的数据格式

from pydantic import BaseModel

# 用户注册时提交的信息
class UserRegister(BaseModel):

    # 用户名
    username: str

    # 用户密码
    password: str

# 用户登录时提交的信息
class UserLogin(BaseModel):

    # 用户名
    username: str

    # 用户密码
    password: str

# 返回给前端的用户信息
class UserResponse(BaseModel):

    # 用户编号
    id: int

    # 用户名
    username: str

    # 用户身份
    role: str

    class Config:
        # 允许读取数据库对象
        from_attributes = True