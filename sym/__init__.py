import os.path

from dotenv import load_dotenv

from .core.client import Sym

if os.path.exists("config.env"):
    load_dotenv("config.env")

sym = Sym()