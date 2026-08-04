# 应用全局配置（读取项目配置，例如数据库地址、密钥等信息）
# 使用 pydantic-settings 从环境变量 / .env 读取配置项
# 包括数据库连接串、Redis 地址、Qdrant 地址、JWT 密钥、DeepSeek API Key 等


from pydantic_settings import BaseSettings, SettingsConfigDict

# 创建配置类，读取.env中的配置
class Settings(BaseSettings):
    # 项目名称
    PROJECT_NAME: str = "Personal Office Agent"

    # AI模型服务地址
    LLM_BASE_URL: str = ""

    # AI模型接口密钥
    LLM_API_KEY: str = ""

    # 使用的模型名称
    LLM_MODEL: str = ""

    # HF_ENDPOINT: str = "https://hf-mirror.com"


    # PostgreSQL数据库配置
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "poa"
    POSTGRES_PASSWORD: str = "poa"
    POSTGRES_DB: str = "poa"


    # Redis配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379


    # Qdrant配置
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333

    # 企业微信机器人 Webhook
    WECHAT_WEBHOOK_URL: str = ""


    # JWT登录安全配置
    JWT_SECRET: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440


    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env")
    )


# 创建配置对象
settings = Settings()
