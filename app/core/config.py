import os
import yaml
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from typing import Dict, List, Any

# Load environment variables from .env file
load_dotenv()

class DBSettings(BaseModel):
    db_type: str = "sqlite"
    host: str = "localhost"
    port: int = 5432
    user: str = "user"
    password: str = "password"
    dbname: str = "pythagoras_db.sqlite"

class LLMSettings(BaseModel):
    model: str = "gpt-4-turbo"
    api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    base_url: str = "https://api.openai.com/v1"
    temperature: float = 0.0
    timeout: int = 60

class CacheSettings(BaseModel):
    max_size: int = 1000
    ttl: int = 3600

class RBACSettings(BaseModel):
    roles: Dict[str, Any]

class UserSettings(BaseModel):
    users: Dict[str, Any]

class Settings(BaseModel):
    database: DBSettings
    llm: LLMSettings
    cache: CacheSettings
    rbac: RBACSettings
    users: UserSettings

def load_config(path: str = "config/config.yaml") -> Settings:
    """Loads configuration from a YAML file and environment variables."""
    try:
        with open(path, "r") as f:
            config_data = yaml.safe_load(f)
        
        # Validate and structure the config using Pydantic models
        return Settings(**config_data)
    except FileNotFoundError:
        raise RuntimeError(f"Configuration file not found at {path}")
    except Exception as e:
        raise RuntimeError(f"Error loading or parsing configuration: {e}")

# Global settings instance
settings = load_config()
