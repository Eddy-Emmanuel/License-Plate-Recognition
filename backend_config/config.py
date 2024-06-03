import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Configurations(BaseSettings):
    engine_url : str = os.getenv("engine_url")
    connect_args : str = os.getenv("connect_args")
    secret_key : str = os.getenv("secret_key")
    algorithm : str = os.getenv("algorithm")