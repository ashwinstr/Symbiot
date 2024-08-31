import os.path

from dotenv import load_dotenv

if os.path.exists("config.env"):
    load_dotenv("config.env")

from .core.client import Sym
from .core import Message

sym_dir = os.path.dirname(__file__)
