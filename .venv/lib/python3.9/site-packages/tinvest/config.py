from pydantic import BaseSettings

__all__ = (
    'Config',
    'config',
)


class Config(BaseSettings):
    USE_ORJSON: bool = True
    USE_UVLOOP: bool = True

    class Config:
        env_prefix = 'TINVEST_'


config = Config()
