
from .decorators import Decorator
from .handlers import Listener
from .types import Message
from .database import Collection
from .logger import Logger
from .handlers import Load

class CustomClient(Decorator, Logger, Listener, Load):
    """ Custom client for Symbiot """