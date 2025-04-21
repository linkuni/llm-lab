import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
    AWS_REGION = os.getenv("AWS_REGION")
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    CORS_ORIGIN = os.getenv("CORS_ORIGIN", "https://api.linkuni.in")
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    CORS_ORIGIN = "*"  # Allow all origins in development

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    CORS_ORIGIN = "*"

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Use environment variables for production settings

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig
} 