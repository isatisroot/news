
from redis import StrictRedis


class Config(object):
    DEBUG = True

    # 通过ORM连接mysql
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/imformation"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #配置redis
    redis_host = '127.0.0.1'
    redis_port = 6379

    SECRET_KEY = "EjpNVSNQTyGi1VvWECj9TvC/+kq3oujee2kTfQUs8yCM6xX9Yjq52v54g+HVoknA"
    # 将Session保存到redis中
    SESSION_TYPE = "redis"  # 指定 session 保存到 redis 中
    SESSION_USE_SIGNER = True  # 让 cookie 中的 session_id 被加密签名处理
    SESSION_PERMANENT = False  # 如果设置为True，则关闭浏览器session就失效。
    SESSION_REDIS = StrictRedis(host=redis_host, port=redis_port)  # 使用 redis 的实例
    PERMANENT_SESSION_LIFETIME = 86400  # session 的有效期，单位是秒

class DevelopementConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False


config = {
    "dev": DevelopementConfig,
    'pro': ProductionConfig
}