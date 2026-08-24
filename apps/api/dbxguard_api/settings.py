from functools import lru_cache
from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    model_config=SettingsConfigDict(env_file=".env",env_prefix="DBXGUARD_",extra="ignore")
    env:str="development"; database_url:str="sqlite:///./dbxguard.db"; redis_url:str="redis://localhost:6379/0"; secret_key:str="development-only-secret"; log_level:str="INFO"; fail_closed:bool=True; cors_origins:str="http://localhost:3000"; api_key:str|None=None
    @property
    def cors_origin_list(self)->list[str]: return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

@lru_cache
def get_settings()->Settings: return Settings()
